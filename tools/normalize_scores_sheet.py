#!/usr/bin/env python3
"""
Normalize legacy rows in Google Sheets "Scores" worksheet.

Default behavior is dry-run (no write). Use --apply to persist changes.
This script only fills/normalizes:
  - mode (inferred via score_row_utils.infer_mode)
  - save_id (uuid4 when missing)
"""

from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Tuple

import gspread

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

# Allow importing project modules when script is launched outside repo root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from score_row_utils import normalize_score_row


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


def normalize_rows(rows: List[Dict]) -> Tuple[List[Dict], int]:
    normalized_rows: List[Dict] = []
    changed = 0
    for row in rows:
        before = dict(row)
        after = normalize_score_row(before, fallback_mode="vocab")
        if not str(after.get("save_id", "")).strip():
            after["save_id"] = str(uuid.uuid4())
        if after != before:
            changed += 1
        normalized_rows.append(after)
    return normalized_rows, changed


def ensure_headers(headers: List[str], rows: List[Dict]) -> List[str]:
    header_set = set(headers)
    for row in rows:
        for key in row.keys():
            if key not in header_set:
                headers.append(key)
                header_set.add(key)
    return headers


def to_values(headers: List[str], rows: List[Dict]) -> List[List[str]]:
    matrix: List[List[str]] = [headers]
    for row in rows:
        matrix.append([str(row.get(h, "")) for h in headers])
    return matrix


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize Scores worksheet rows (mode/save_id).")
    parser.add_argument("--secrets", default=".streamlit/secrets.toml", help="Path to secrets.toml")
    parser.add_argument("--spreadsheet", default=None, help="Spreadsheet key or URL (optional)")
    parser.add_argument("--worksheet", default="Scores", help="Worksheet name")
    parser.add_argument("--apply", action="store_true", help="Write changes (default: dry-run)")
    args = parser.parse_args()

    try:
        conn = load_gsheets_secret(Path(args.secrets))
        client = build_client(conn)
        ss = open_spreadsheet(client, conn, args.spreadsheet)
        ws = ss.worksheet(args.worksheet)
    except Exception as e:
        print(f"[ERROR] Failed to connect to worksheet: {e}", file=sys.stderr)
        return 2

    headers, rows = get_rows(ws)
    if not headers:
        print("[INFO] Worksheet is empty. Nothing to normalize.")
        return 0

    normalized_rows, changed = normalize_rows(rows)
    headers = ensure_headers(headers, normalized_rows)

    print(f"[INFO] Rows scanned: {len(rows)}")
    print(f"[INFO] Rows to normalize: {changed}")
    if changed == 0:
        print("[INFO] No changes required.")
        return 0
    if not args.apply:
        print("[INFO] Dry-run only. Re-run with --apply to persist.")
        return 0

    values = to_values(headers, normalized_rows)
    try:
        ws.update(values=values, range_name="A1", value_input_option="RAW")
    except Exception as e:
        print(f"[ERROR] Failed to write worksheet: {e}", file=sys.stderr)
        return 3

    print(f"[OK] Updated {changed} row(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
