#!/usr/bin/env python3
"""Build mobile JSON data and update the diagnostic app version."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "version",
        nargs="?",
        help="Version string for APP_VERSION, for example 2026-06-06-mobile-data-1.",
    )
    parser.add_argument(
        "--label",
        default="mobile-build",
        help="Label for the generated version when version is omitted. Default: mobile-build.",
    )
    parser.add_argument(
        "--with-drive-manifest",
        action="store_true",
        help="Also rebuild mobile_app/data/audio_manifest.json from Google Drive.",
    )
    return parser.parse_args()


def run_step(label: str, command: list[str]) -> None:
    print(f"[INFO] {label}", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    args = parse_args()
    try:
        run_step("Building mobile JSON data", [sys.executable, str(TOOLS / "build_mobile_data.py")])
        if args.with_drive_manifest:
            run_step(
                "Building Google Drive audio manifest",
                [sys.executable, str(TOOLS / "build_drive_audio_manifest.py")],
            )

        version_command = [sys.executable, str(TOOLS / "update_mobile_version.py")]
        if args.version:
            version_command.append(args.version)
        else:
            version_command.extend(["--label", args.label])
        run_step("Updating mobile app version", version_command)
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] Step failed with exit code {exc.returncode}: {' '.join(exc.cmd)}", file=sys.stderr)
        return exc.returncode or 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
