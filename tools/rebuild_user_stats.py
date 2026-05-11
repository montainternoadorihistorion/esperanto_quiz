#!/usr/bin/env python3
"""
Rebuild UserStats/UserStatsSentence worksheets from Scores worksheet.

Default behavior is dry-run (no write). Use --apply to persist changes.
This tool is intended as a safe maintenance fallback when UserStats sheets
become stale due transient write failures.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import gspread
import pandas as pd

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

# Allow importing project modules when script is launched outside repo root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from score_row_utils import normalize_score_rows  # noqa: E402


def load_gsheets_secret(secrets_path: Path) -> Dict:
    if not secrets_path.exists():
        raise FileNotFoundError(f"Secrets file not found: {secrets_path}")
    with secrets_path.open("rb") as f:
        data = tomllib.load(f)
    conn = data.get("connections", {}).get("gsheets")
    if not isinstance(conn, dict):
        raise KeyError("Missing [connections.gsheets] in secrets.toml")
    return conn


def build_client(conn: Dict) -> gspread.Client:
    credential_keys = {
        "type",
        "project_id",
        "private_key_id",
        "private_key",
        "client_email",
        "client_id",
        "auth_uri",
        "token_uri",
        "auth_provider_x509_cert_url",
        "client_x509_cert_url",
        "universe_domain",
    }
    creds = {k: v for k, v in conn.items() if k in credential_keys and v}
    if not creds:
        raise ValueError("No service-account credentials found in [connections.gsheets].")
    return gspread.service_account_from_dict(creds)


def open_spreadsheet(client: gspread.Client, conn: Dict, spreadsheet: str | None):
    target = spreadsheet or conn.get("spreadsheet") or conn.get("spreadsheet_url")
    if not target:
        raise ValueError("Spreadsheet not specified (arg or [connections.gsheets].spreadsheet).")
    target = str(target)
    if target.startswith("http://") or target.startswith("https://"):
        return client.open_by_url(target)
    return client.open_by_key(target)


def get_rows(ws: gspread.Worksheet) -> Tuple[List[str], List[Dict]]:
    values = ws.get_all_values()
    if not values:
        return [], []
    headers = [str(h).strip() for h in values[0]]
    rows: List[Dict] = []
    for line in values[1:]:
        row = {headers[i]: (line[i] if i < len(line) else "") for i in range(len(headers))}
        rows.append(row)
    return headers, rows


def build_stats(scores_rows: List[Dict], sentence_only: bool, ts: str) -> pd.DataFrame:
    normalized = normalize_score_rows(scores_rows, fallback_mode="vocab")
    df = pd.DataFrame(normalized)
    columns = ["user", "total_points", "last_updated"]
    if df.empty or "user" not in df.columns:
        return pd.DataFrame(columns=columns)

    df["user"] = df["user"].fillna("").astype(str).str.strip()
    df = df[df["user"] != ""]
    if df.empty:
        return pd.DataFrame(columns=columns)

    if "mode" not in df.columns:
        df["mode"] = "vocab"
    df["mode"] = df["mode"].fillna("").astype(str).str.strip().str.lower()
    if sentence_only:
        df = df[df["mode"] == "sentence"]
    if df.empty:
        return pd.DataFrame(columns=columns)

    if "points" not in df.columns:
        df["points"] = 0.0
    df["points"] = pd.to_numeric(df["points"], errors="coerce").fillna(0.0)

    agg = df.groupby("user", as_index=False)["points"].sum().rename(columns={"points": "total_points"})
    agg["last_updated"] = ts
    return agg[columns]


def backup_sheet(ws: gspread.Worksheet, backup_dir: Path, prefix: str) -> Path:
    headers, rows = get_rows(ws)
    backup_dir.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = backup_dir / f"{prefix}_{now}.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if headers:
            writer.writerow(headers)
            for row in rows:
                writer.writerow([row.get(h, "") for h in headers])
    return out


def write_stats(ws: gspread.Worksheet, stats_df: pd.DataFrame) -> None:
    headers = ["user", "total_points", "last_updated"]
    values: List[List[str]] = [headers]
    if not stats_df.empty:
        for _, row in stats_df.iterrows():
            values.append(
                [
                    str(row.get("user", "")),
                    str(row.get("total_points", 0.0)),
                    str(row.get("last_updated", "")),
                ]
            )
    ws.update(values=values, range_name="A1", value_input_option="RAW")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rebuild UserStats/UserStatsSentence worksheets from Scores."
    )
    parser.add_argument("--secrets", default=".streamlit/secrets.toml", help="Path to secrets.toml")
    parser.add_argument("--spreadsheet", default=None, help="Spreadsheet key or URL (optional)")
    parser.add_argument("--scores-sheet", default="Scores", help="Scores worksheet name")
    parser.add_argument("--main-sheet", default="UserStats", help="Main UserStats worksheet name")
    parser.add_argument(
        "--sentence-sheet",
        default="UserStatsSentence",
        help="Sentence-only UserStats worksheet name",
    )
    parser.add_argument(
        "--backup-dir",
        default="tools/backups",
        help="Directory for backups when --apply is used",
    )
    parser.add_argument("--apply", action="store_true", help="Write changes (default: dry-run)")
    args = parser.parse_args()

    try:
        conn = load_gsheets_secret(Path(args.secrets))
        client = build_client(conn)
        ss = open_spreadsheet(client, conn, args.spreadsheet)
        ws_scores = ss.worksheet(args.scores_sheet)
        ws_main = ss.worksheet(args.main_sheet)
        ws_sentence = ss.worksheet(args.sentence_sheet)
    except Exception as e:
        print(f"[ERROR] Failed to connect worksheets: {e}", file=sys.stderr)
        return 2

    _, score_rows = get_rows(ws_scores)
    ts = dt.datetime.utcnow().isoformat()
    main_df = build_stats(score_rows, sentence_only=False, ts=ts)
    sentence_df = build_stats(score_rows, sentence_only=True, ts=ts)

    print(f"[INFO] Scores rows: {len(score_rows)}")
    print(f"[INFO] Rebuilt {args.main_sheet}: {len(main_df)} rows")
    print(f"[INFO] Rebuilt {args.sentence_sheet}: {len(sentence_df)} rows")
    if not args.apply:
        print("[INFO] Dry-run only. Re-run with --apply to persist.")
        return 0

    backup_dir = Path(args.backup_dir)
    try:
        main_backup = backup_sheet(ws_main, backup_dir, f"{args.main_sheet}_before_rebuild")
        sentence_backup = backup_sheet(
            ws_sentence,
            backup_dir,
            f"{args.sentence_sheet}_before_rebuild",
        )
        print(f"[INFO] Backup created: {main_backup}")
        print(f"[INFO] Backup created: {sentence_backup}")
    except Exception as e:
        print(f"[ERROR] Failed to backup sheets: {e}", file=sys.stderr)
        return 3

    try:
        write_stats(ws_main, main_df)
        write_stats(ws_sentence, sentence_df)
    except Exception as e:
        print(f"[ERROR] Failed to write stats sheets: {e}", file=sys.stderr)
        return 4

    print("[OK] UserStats sheets rebuilt successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
