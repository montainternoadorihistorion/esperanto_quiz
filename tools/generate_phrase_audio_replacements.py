#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import csv
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate replacement phrase audio files for updated Esperanto sentences."
    )
    parser.add_argument(
        "--candidate-csv",
        default="fuyou_/phrases_audio_replacement_candidates_20260306.csv",
        help="CSV listing replacement candidates.",
    )
    parser.add_argument(
        "--audio-dir",
        default="Esperanto例文5000文_収録音声",
        help="Directory where phrase audio files live.",
    )
    parser.add_argument(
        "--voice",
        default="it-IT-GiuseppeMultilingualNeural",
        help="Edge TTS voice to use for generation.",
    )
    parser.add_argument(
        "--report-csv",
        default="fuyou_/phrases_audio_replacement_generation_20260306.csv",
        help="Write generation results here.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite exact-key audio files if they already exist.",
    )
    return parser.parse_args()


def load_candidates(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


async def synthesize_mp3(text: str, voice: str, out_mp3: Path) -> None:
    try:
        import edge_tts
    except ImportError as exc:
        raise RuntimeError(
            "edge_tts is required. Install it first, e.g. "
            "`python -m pip install --target /tmp/edge_tts_pkg edge-tts` "
            "and run with `PYTHONPATH=/tmp/edge_tts_pkg`."
        ) from exc

    communicator = edge_tts.Communicate(text, voice=voice)
    await communicator.save(str(out_mp3))


def convert_to_wav(src_mp3: Path, out_wav: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required but was not found in PATH.")
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(src_mp3),
            "-ac",
            "1",
            "-ar",
            "24000",
            "-sample_fmt",
            "s16",
            str(out_wav),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


async def main() -> int:
    args = parse_args()
    candidate_csv = Path(args.candidate_csv)
    audio_dir = Path(args.audio_dir)
    report_csv = Path(args.report_csv)

    candidates = load_candidates(candidate_csv)
    results: list[dict[str, str]] = []

    for row in candidates:
        phrase_id = row["PhraseID"]
        phrase = row["current_phrase"]
        key = row["current_audio_key"]
        out_wav = audio_dir / f"{key}.wav"

        if out_wav.exists() and not args.overwrite:
            results.append(
                {
                    "PhraseID": phrase_id,
                    "phrase": phrase,
                    "voice": args.voice,
                    "output_file": out_wav.name,
                    "status": "skipped_exists",
                }
            )
            continue

        try:
            with tempfile.TemporaryDirectory(prefix="phrase-audio-") as tmpdir:
                tmpdir_path = Path(tmpdir)
                tmp_mp3 = tmpdir_path / f"{key}.mp3"
                await synthesize_mp3(phrase, args.voice, tmp_mp3)
                convert_to_wav(tmp_mp3, out_wav)
            results.append(
                {
                    "PhraseID": phrase_id,
                    "phrase": phrase,
                    "voice": args.voice,
                    "output_file": out_wav.name,
                    "status": "generated",
                }
            )
            print(f"generated {phrase_id}: {out_wav.name}")
        except Exception as exc:  # pragma: no cover - one-off utility
            results.append(
                {
                    "PhraseID": phrase_id,
                    "phrase": phrase,
                    "voice": args.voice,
                    "output_file": out_wav.name,
                    "status": f"error: {exc}",
                }
            )
            print(f"error {phrase_id}: {exc}", file=sys.stderr)

    with report_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["PhraseID", "phrase", "voice", "output_file", "status"],
        )
        writer.writeheader()
        writer.writerows(results)

    error_count = sum(1 for row in results if row["status"].startswith("error:"))
    print(f"done: {len(results)} rows, errors={error_count}, report={report_csv}")
    return 1 if error_count else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
