#!/usr/bin/env python3
"""session-stats.py — fun stats from a Memir session transcript.

Reads the merged transcript JSON produced by transcribe-session.py and
reports talk time, longest monologues, and name drops (proper nouns from
transcribe-session.py's PROPER_NOUNS list).

Usage:
    python session-stats.py session_audio/session-22-transcript.json
    python session-stats.py session_audio/session-22-transcript.json --top 8
    python session-stats.py session_audio/session-22-transcript.json --json > session-22-stats.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def _load_transcribe_module():
    """Load transcribe-session.py by path (hyphenated filename isn't a valid
    module name) so the proper-noun list and time formatting stay
    single-sourced there."""
    spec = importlib.util.spec_from_file_location("transcribe_session", REPO_ROOT / "transcribe-session.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["transcribe_session"] = mod  # needed before exec: dataclasses resolves types via sys.modules
    spec.loader.exec_module(mod)
    return mod


ts = _load_transcribe_module()


def load_transcript(path: Path) -> list[dict]:
    return json.loads(path.read_text())


def talk_time(segments: list[dict]):
    totals: dict[str, float] = defaultdict(float)
    labels: dict[str, str] = {}
    for s in segments:
        totals[s["speaker"]] += s["end"] - s["start"]
        labels[s["speaker"]] = s["label"]
    span = max(s["end"] for s in segments) - min(s["start"] for s in segments)
    rows = sorted(totals.items(), key=lambda kv: -kv[1])
    return rows, labels, span


def longest_monologues(segments: list[dict], top: int) -> list[dict]:
    ranked = sorted(segments, key=lambda s: -(s["end"] - s["start"]))
    return ranked[:top]


def build_name_patterns(names: list[str]):
    return [(name, re.compile(r"\b" + re.escape(name) + r"\b", re.IGNORECASE)) for name in names]


def name_drops(segments: list[dict], names: list[str]):
    patterns = build_name_patterns(names)
    totals: dict[str, int] = defaultdict(int)
    by_speaker: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for s in segments:
        text = s["text"]
        for name, pat in patterns:
            n = len(pat.findall(text))
            if n:
                totals[name] += n
                by_speaker[s["label"]][name] += n
    return totals, by_speaker


def print_report(transcript_path: Path, segments: list[dict], top: int):
    session_id = transcript_path.stem.replace("-transcript", "")

    print(f"=== Session stats: {session_id} ===\n")

    rows, labels, span = talk_time(segments)
    print(f"-- Talk time (session span {ts.fmt_ts(span)}) --")
    for handle, secs in rows:
        pct = 100 * secs / span if span else 0
        print(f"  {labels[handle]:24s} {ts.fmt_ts(secs):>8s}  ({pct:4.1f}%)")

    print(f"\n-- Longest monologues (top {top}) --")
    for s in longest_monologues(segments, top):
        dur = s["end"] - s["start"]
        snippet = s["text"][:90] + ("..." if len(s["text"]) > 90 else "")
        print(f"  {ts.fmt_ts(dur):>6s}  [{ts.fmt_ts(s['start'])}] {s['label']:20s} {snippet!r}")

    totals, by_speaker = name_drops(segments, ts.PROPER_NOUNS)
    ranked_names = sorted(totals.items(), key=lambda kv: -kv[1])
    print(f"\n-- Name drops (top {top}) --")
    if not ranked_names:
        print("  (none matched)")
    for name, count in ranked_names[:top]:
        top_speaker = max(
            (label for label in by_speaker if name in by_speaker[label]),
            key=lambda label: by_speaker[label][name],
            default=None,
        )
        extra = f"  (most by {top_speaker})" if top_speaker else ""
        print(f"  {name:20s} {count:3d}{extra}")


def build_json_report(transcript_path: Path, segments: list[dict], top: int) -> dict:
    session_id = transcript_path.stem.replace("-transcript", "")
    rows, labels, span = talk_time(segments)
    totals, by_speaker = name_drops(segments, ts.PROPER_NOUNS)

    return {
        "session_id": session_id,
        "span_seconds": span,
        "talk_time": [
            {"speaker": handle, "label": labels[handle], "seconds": secs, "pct": 100 * secs / span if span else 0}
            for handle, secs in rows
        ],
        "longest_monologues": [
            {"speaker": s["speaker"], "label": s["label"], "start": s["start"], "end": s["end"],
             "duration": s["end"] - s["start"], "text": s["text"]}
            for s in longest_monologues(segments, top)
        ],
        "name_drops": sorted(
            [
                {
                    "name": name,
                    "count": count,
                    "by_speaker": {label: counts[name] for label, counts in by_speaker.items() if name in counts},
                }
                for name, count in totals.items()
            ],
            key=lambda r: -r["count"],
        ),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("transcript", type=Path, help="Path to a *-transcript.json produced by transcribe-session.py")
    ap.add_argument("--top", type=int, default=5, help="Top-N rows for monologues/name-drops (default: 5)")
    ap.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of a text report")
    args = ap.parse_args()

    path = args.transcript.expanduser().resolve()
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        sys.exit(1)
    segments = load_transcript(path)

    if args.json:
        print(json.dumps(build_json_report(path, segments, args.top), indent=2))
    else:
        print_report(path, segments, args.top)


if __name__ == "__main__":
    main()
