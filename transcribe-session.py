#!/usr/bin/env python3
"""transcribe-session.py — speaker-attributed session transcription for Memir.

Takes a Craig (Discord recording bot) multi-track export — one isolated FLAC
per speaker — and produces a single merged, timestamped, speaker-labeled
transcript for /wrap-session.

Why per-track instead of a mixed-down file: Craig already separates speakers
at the source. Mixing them down (e.g. in GarageBand) throws that away and
forces Whisper to do acoustic speaker separation on overlapping table talk,
which it's bad at. Transcribing each isolated track separately sidesteps that
entirely — the only remaining problem is merging N independent timelines back
into one, which is a matter of sorting, not modeling.

Why VAD-gated (faster-whisper + Silero VAD) instead of plain whisper: session
audio is mostly silence (a typical player's track is >90% silence — checked
against the session 22 export). Plain Whisper computes timestamps relative to
internal 30-second windows, and across long silence those windows drift from
wall-clock time; merging several independently-drifted tracks scrambles
cross-speaker ordering. VAD finds actual speech regions first and anchors
timestamps to those boundaries, and skips silence entirely (~7x less compute,
also fewer silence-hallucinated lines).

Usage:
    python transcribe-session.py ~/Downloads/session22_audio --session 22
    python transcribe-session.py ~/Downloads/session22_audio --session 22 --start 20:00 --end 30:00
    python transcribe-session.py ~/Downloads/session22_audio --session 22 --model medium
    python transcribe-session.py ~/Downloads/session22_audio --session 22 --dry-run

Output (written to session_audio/, already gitignored):
    session_audio/session-<N>-transcript.md    human-readable, speaker-labeled
    session_audio/session-<N>-transcript.json  structured segments
    session_audio/raw/<session_id>/<handle>.json   cached per-track transcripts

Dependencies: faster-whisper (in .venv), ffmpeg on PATH.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from difflib import get_close_matches
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTDIR = REPO_ROOT / "session_audio"
SPEAKERS_PATH = REPO_ROOT / "speakers.json"

# Fed to Whisper as initial_prompt to bias rare proper-noun recognition.
# Pulled from campaigns/chance-encounters + stories/storm-that-remembers +
# canon/pantheon. Keep this list current as new NPCs/locations get introduced.
PROPER_NOUNS = [
    # PCs
    "Casus", "Coriac", "Gareth", "Grimvald", "Artcoth", "Shah Doh",
    # campaign NPCs
    "Ariel", "Amelia", "Dessa", "Edrin Vael", "Elara Venn", "Eleanor Bellwether",
    "Jimmy Quickhands", "Lady Grimhook", "Liriel Baenre", "Lord Thorne", "Marek",
    "Ollo", "Önund", "Ovaltine Jenkins", "Shalindra", "Tide-Tongue", "Tjorvi",
    "Tom Rell", "Wrenn", "Zal Goroth", "Charlie Bones",
    # locations
    "Ravencrest", "Ariel's Island", "Bellwether House", "Starlight Watchtower",
    # pantheon
    "Thor", "Odin", "Baldr", "Nidhogg", "Yggdrasil", "Feanoro",
]
INITIAL_PROMPT = "Characters and places in this D&D session: " + ", ".join(PROPER_NOUNS) + "."

# Known Whisper hallucination artifacts — dropped outright regardless of confidence.
# Short filler tokens are matched exactly (substring matching would false-positive
# on real speech); YouTube-outro-style phrases are matched as a substring since
# Whisper often appends extra invented text after them (e.g. "...and I'll see you
# in the next video.").
HALLUCINATION_EXACT = {".", "you", "bye", "bye.", "bye bye"}
HALLUCINATION_SUBSTRINGS = {
    "thank you for watching",
    "thanks for watching",
    "please subscribe",
    "like and subscribe",
    "subscribe to my channel",
    "translated by",
    "subtitles by",
    "amara.org",
}

# Recurring ASR mishears of this campaign's PC/NPC names — corrected post-transcription
# rather than relying on initial_prompt alone, which doesn't fully suppress them.
NAME_CORRECTIONS = {
    "olara van": "Elara Venn",
    "cassius": "Casus",
    "cassis": "Casus",
    "cassus": "Casus",
    "cass": "Casus",
    "ravenquest": "Ravencrest",
    "corian": "Coriac",
    "jorvi": "Tjorvi",
    "grimbald": "Grimvald",
    "grimwald": "Grimvald",
    "grimball": "Grimvald",
    "olara": "Elara",
    "awara": "Elara",
    "merrick": "Marek",
    "ren": "Wrenn",
    "olo": "Ollo",
    "onan": "Önund",
    "unand": "Önund",
    "tavori": "Tjorvi",
    "oval team": "Ovaltine",
    "oval old teen": "Ovaltine",
    "oval teen": "Ovaltine",
}

NO_SPEECH_PROB_MAX = 0.6
AVG_LOGPROB_MIN = -1.0
COALESCE_GAP_SECONDS = 2.0
SILENCE_MARKER_SECONDS = 60.0

# faster-whisper occasionally reports a segment's end far past when its words
# could plausibly have been spoken -- typically when VAD merges a long,
# mostly-silent stretch (background hiss/bleed never quite hitting the
# silence threshold) into one "speech" region and Whisper decodes only a
# short phrase for the whole thing. Confidence scores don't catch this (the
# text itself is transcribed fine, e.g. "Yes." at avg_logprob -0.89); only
# the implied word rate does.
MIN_PLAUSIBLE_WORDS_PER_SEC = 0.6
DURATION_ESTIMATE_WORDS_PER_SEC = 2.0
DURATION_ESTIMATE_PAD_SECONDS = 0.3
MIN_SEGMENT_SECONDS = 0.4

# Flagging (not filtering): segments kept in the transcript but worth a human
# glance before /wrap-session runs off of them. Two independent signals:
#   1. a word/bigram that's *close* to a known proper noun but doesn't match
#      exactly (catches the next "ravenquest"/"Ravencrest" before it ships,
#      the way an exact NAME_CORRECTIONS entry only catches ones we already know)
#   2. confidence right at the edge of the hard drop thresholds -- not bad
#      enough to discard, but not clearly good either
FUZZY_NAME_CUTOFF = 0.8
REVIEW_NO_SPEECH_PROB_MIN = 0.5   # NO_SPEECH_PROB_MAX is 0.6 -- this is the last 0.1 before drop
REVIEW_AVG_LOGPROB_MAX = -0.9      # AVG_LOGPROB_MIN is -1.0 -- same idea

TRACK_RE = re.compile(r"^(\d+)-(.+)\.flac$")


@dataclass
class Segment:
    start: float
    end: float
    text: str
    speaker: str  # Craig handle
    label: str  # display label, e.g. "Casus (Chris)"
    no_speech_prob: float
    avg_logprob: float


@dataclass
class Track:
    handle: str
    path: Path
    label: str


def fmt_ts(seconds: float) -> str:
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def parse_mmss(s: str) -> float:
    parts = [float(p) for p in s.split(":")]
    if len(parts) == 2:
        m, sec = parts
        return m * 60 + sec
    if len(parts) == 3:
        h, m, sec = parts
        return h * 3600 + m * 60 + sec
    return float(s)


def discover_tracks(craig_dir: Path, speakers: dict) -> list[Track]:
    tracks = []
    unknown = []
    for f in sorted(craig_dir.glob("[0-9]*-*.flac")):
        m = TRACK_RE.match(f.name)
        if not m:
            continue
        handle = m.group(2)
        if handle not in speakers:
            unknown.append(handle)
            continue
        tracks.append(Track(handle=handle, path=f, label=speakers[handle]["label"]))
    if unknown:
        print(f"ERROR: unknown speaker handle(s) not in {SPEAKERS_PATH.name}: {unknown}", file=sys.stderr)
        print("Add them before continuing, e.g.:", file=sys.stderr)
        for h in unknown:
            print(f'  "{h}": {{ "pc": "???", "player": "???", "label": "??? (???)" }},', file=sys.stderr)
        sys.exit(1)
    if not tracks:
        print(f"ERROR: no [N]-<handle>.flac tracks found in {craig_dir}", file=sys.stderr)
        sys.exit(1)
    return tracks


def slice_pilot(track: Track, start: float, end: float, tmp_dir: Path) -> Path:
    """Cut a pilot window out of a track for fast iteration. Returns the sliced path."""
    tmp_dir.mkdir(parents=True, exist_ok=True)
    out = tmp_dir / f"{track.handle}_pilot.wav"
    cmd = [
        "ffmpeg", "-y", "-ss", str(start), "-to", str(end),
        "-i", str(track.path), "-ac", "1", "-ar", "16000",
        str(out),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return out


def sanitize_duration(start: float, end: float, text: str) -> tuple[float, bool]:
    """Correct an implausible segment end time based on implied word rate.
    Returns (corrected_end, was_corrected)."""
    duration = end - start
    if duration <= 0:
        return end, False
    word_count = max(len(text.split()), 1)
    if word_count / duration >= MIN_PLAUSIBLE_WORDS_PER_SEC:
        return end, False
    estimated = max(
        word_count / DURATION_ESTIMATE_WORDS_PER_SEC + DURATION_ESTIMATE_PAD_SECONDS,
        MIN_SEGMENT_SECONDS,
    )
    return start + estimated, True


def transcribe_track(model, track: Track, audio_path: Path, offset: float, cache_path: Path, force: bool) -> list[Segment]:
    if cache_path.exists() and not force:
        raw = json.loads(cache_path.read_text())
    else:
        segments_iter, _info = model.transcribe(
            str(audio_path),
            language="en",
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500, speech_pad_ms=200),
            condition_on_previous_text=False,
            initial_prompt=INITIAL_PROMPT,
        )
        raw = [
            {
                "start": s.start, "end": s.end, "text": s.text.strip(),
                "no_speech_prob": s.no_speech_prob, "avg_logprob": s.avg_logprob,
            }
            for s in segments_iter
        ]
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(raw, indent=2))

    out = []
    corrected = 0
    for s in raw:
        seg_start, seg_end = s["start"] + offset, s["end"] + offset
        seg_end, was_corrected = sanitize_duration(seg_start, seg_end, s["text"])
        corrected += was_corrected
        out.append(Segment(
            start=seg_start, end=seg_end, text=apply_name_corrections(s["text"]),
            speaker=track.handle, label=track.label,
            no_speech_prob=s["no_speech_prob"], avg_logprob=s["avg_logprob"],
        ))
    if corrected:
        print(f"    sanitized {corrected} implausible-duration segment(s)")
    return out


def is_hallucination(seg: Segment) -> bool:
    if seg.no_speech_prob > NO_SPEECH_PROB_MAX:
        return True
    if seg.avg_logprob < AVG_LOGPROB_MIN:
        return True
    norm = seg.text.strip().lower().strip(".! ")
    if not norm:
        return True
    if norm in HALLUCINATION_EXACT:
        return True
    if any(phrase in norm for phrase in HALLUCINATION_SUBSTRINGS):
        return True
    return False


NAME_CORRECTION_RE = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in NAME_CORRECTIONS) + r")\b",
    re.IGNORECASE,
)


def apply_name_corrections(text: str) -> str:
    return NAME_CORRECTION_RE.sub(lambda m: NAME_CORRECTIONS[m.group(0).lower()], text)


_PROPER_NOUNS_LOWER = {p.lower() for p in PROPER_NOUNS}
_ALREADY_CORRECTED_LOWER = set(NAME_CORRECTIONS.keys())
# Individual words that make up a multi-word proper noun (e.g. "Bellwether" out
# of "Bellwether House") are legitimate on their own -- referring to someone by
# surname isn't a mishear.
_KNOWN_SUBTOKENS = {
    w.lower() for p in PROPER_NOUNS for w in re.findall(r"[A-Za-z']+", p)
}


def find_name_mismatches(text: str) -> list[tuple[str, str]]:
    """Single words close to a known proper noun but not matching exactly, and
    not already handled by NAME_CORRECTIONS. Best-effort -- a candidate list
    for a human to glance at, not an auto-fix. Deliberately unigram-only with
    a tight cutoff: bigrams and loose cutoffs mostly catch coincidental
    matches on short common words ("are" ~ "Marek"), not real mishears."""
    words = [w for w in re.findall(r"[A-Za-z']+", text) if len(w) >= 4]
    found = []
    for cand in words:
        # Strip a trailing possessive ("Wrenn's" -> "Wrenn") before checking --
        # otherwise every possessive use of an already-correct name fuzzy-matches
        # against its own bare form and gets flagged as a false mishear.
        stripped = re.sub(r"'s?$", "", cand)
        low, low_stripped = cand.lower(), stripped.lower()
        if low in _PROPER_NOUNS_LOWER or low in _ALREADY_CORRECTED_LOWER or low in _KNOWN_SUBTOKENS:
            continue
        if low_stripped in _PROPER_NOUNS_LOWER or low_stripped in _ALREADY_CORRECTED_LOWER or low_stripped in _KNOWN_SUBTOKENS:
            continue
        close = get_close_matches(stripped, PROPER_NOUNS, n=1, cutoff=FUZZY_NAME_CUTOFF)
        if close:
            found.append((cand, close[0]))
    return found


def flag_reasons(seg: Segment) -> list[str]:
    reasons = []
    for cand, match in find_name_mismatches(seg.text):
        reasons.append(f'possible name mishear: "{cand}" ~ "{match}"')
    if seg.no_speech_prob >= REVIEW_NO_SPEECH_PROB_MIN:
        reasons.append(f"low confidence (no_speech_prob={seg.no_speech_prob:.2f})")
    if seg.avg_logprob <= REVIEW_AVG_LOGPROB_MAX:
        reasons.append(f"low confidence (avg_logprob={seg.avg_logprob:.2f})")
    return reasons


def dedupe_repeats(segments: list[Segment]) -> list[Segment]:
    """Drop a segment if it's an exact repeat of the immediately preceding one
    from the same speaker — classic Whisper stutter-loop artifact."""
    out: list[Segment] = []
    for seg in segments:
        if out and out[-1].speaker == seg.speaker and out[-1].text.strip().lower() == seg.text.strip().lower():
            continue
        out.append(seg)
    return out


def merge_and_coalesce(all_segments: list[Segment]) -> list[Segment]:
    ordered = sorted(all_segments, key=lambda s: s.start)
    coalesced: list[Segment] = []
    for seg in ordered:
        if coalesced and coalesced[-1].speaker == seg.speaker and seg.start - coalesced[-1].end <= COALESCE_GAP_SECONDS:
            prev = coalesced[-1]
            prev.text = (prev.text + " " + seg.text).strip()
            prev.end = max(prev.end, seg.end)
        else:
            coalesced.append(Segment(**vars(seg)))
    return coalesced


def apply_manual_overrides(segments: list[Segment], outdir: Path, session_id: str) -> int:
    """Apply one-off, DM-confirmed text fixes that don't belong in NAME_CORRECTIONS
    (not a recurring proper-noun mishear, just semantic garble the automated pass
    can't catch). Stored per-session at <outdir>/<session_id>-overrides.json as a
    list of {"find": "...", "replace": "..."} objects, applied as plain substring
    replacement across all segments. Exists so a confirmed fix survives re-running
    the script (e.g. to pick up a new NAME_CORRECTIONS entry) instead of being
    silently clobbered when the transcript regenerates from the raw cache."""
    path = outdir / f"{session_id}-overrides.json"
    if not path.exists():
        return 0
    overrides = json.loads(path.read_text())
    applied = 0
    for seg in segments:
        for o in overrides:
            if o["find"] in seg.text:
                seg.text = seg.text.replace(o["find"], o["replace"])
                applied += 1
    return applied


def write_outputs(segments: list[Segment], outdir: Path, session_id: str):
    outdir.mkdir(parents=True, exist_ok=True)
    md_path = outdir / f"{session_id}-transcript.md"
    json_path = outdir / f"{session_id}-transcript.json"
    flags_path = outdir / f"{session_id}-transcript-flags.md"

    lines = []
    flag_lines = []
    prev_end = None
    for seg in segments:
        if prev_end is not None and seg.start - prev_end > SILENCE_MARKER_SECONDS:
            gap_min = round((seg.start - prev_end) / 60)
            lines.append(f"\n--- {gap_min} min gap ---\n")
        lines.append(f"[{fmt_ts(seg.start)}] {seg.label}: {seg.text}")
        prev_end = seg.end

        reasons = flag_reasons(seg)
        if reasons:
            flag_lines.append(f"- [{fmt_ts(seg.start)}] {seg.label}: {seg.text}")
            for r in reasons:
                flag_lines.append(f"    - {r}")
    md_path.write_text("\n".join(lines) + "\n")

    json_path.write_text(json.dumps([
        {"start": s.start, "end": s.end, "speaker": s.speaker, "label": s.label, "text": s.text}
        for s in segments
    ], indent=2))

    if flag_lines:
        flags_path.write_text(
            f"# Flagged segments — {session_id}\n\n"
            "Kept in the transcript, but worth a human glance: a possible proper-noun "
            "mishear, or confidence right at the edge of the drop threshold. Not "
            "necessarily wrong -- /wrap-session should walk through these with the DM "
            "before presenting the session summary.\n\n"
            + "\n".join(flag_lines) + "\n"
        )
    elif flags_path.exists():
        flags_path.unlink()

    return md_path, json_path, (flags_path if flag_lines else None)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("craig_dir", type=Path, help="Directory containing Craig's exported [N]-<handle>.flac tracks")
    ap.add_argument("--session", help="Session number/id, used for output filenames (e.g. 22 -> session-22-transcript.md)")
    ap.add_argument("--model", default="large-v3", help="faster-whisper model size (default: large-v3)")
    ap.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR, help="Output directory (default: session_audio/)")
    ap.add_argument("--speakers", type=Path, default=SPEAKERS_PATH, help="Path to speakers.json")
    ap.add_argument("--start", help="Pilot mode: window start, MM:SS or HH:MM:SS")
    ap.add_argument("--end", help="Pilot mode: window end, MM:SS or HH:MM:SS")
    ap.add_argument("--force", action="store_true", help="Ignore cached per-track transcripts, re-run Whisper")
    ap.add_argument("--dry-run", action="store_true", help="Show discovered tracks and plan, do not transcribe")
    args = ap.parse_args()

    craig_dir = args.craig_dir.expanduser().resolve()
    speakers = json.loads(args.speakers.read_text())
    speakers = {k: v for k, v in speakers.items() if not k.startswith("_")}

    tracks = discover_tracks(craig_dir, speakers)

    session_id = f"session-{args.session}" if args.session else craig_dir.name
    pilot = bool(args.start or args.end)
    if pilot:
        if not (args.start and args.end):
            print("ERROR: --start and --end must both be given for pilot mode", file=sys.stderr)
            sys.exit(1)
        start_s, end_s = parse_mmss(args.start), parse_mmss(args.end)
        session_id += f"-pilot-{args.start.replace(':', '')}-{args.end.replace(':', '')}"

    print(f"Discovered {len(tracks)} tracks in {craig_dir}:")
    for t in tracks:
        print(f"  {t.handle:20s} -> {t.label}")
    print(f"Model: {args.model}   Session id: {session_id}   Pilot: {pilot}")

    if args.dry_run:
        print("(dry run — stopping here)")
        return

    from faster_whisper import WhisperModel
    print(f"Loading {args.model}...")
    model = WhisperModel(args.model, device="cpu", compute_type="int8")

    cache_dir = args.outdir / "raw" / session_id
    tmp_dir = args.outdir / "raw" / session_id / "_pilot_slices"

    all_segments: list[Segment] = []
    for i, track in enumerate(tracks, 1):
        print(f"[{i}/{len(tracks)}] Transcribing {track.handle} ({track.label})...")
        if pilot:
            audio_path = slice_pilot(track, start_s, end_s, tmp_dir)
            offset = start_s
        else:
            audio_path = track.path
            offset = 0.0
        cache_path = cache_dir / f"{track.handle}.json"
        segs = transcribe_track(model, track, audio_path, offset, cache_path, args.force)
        print(f"    {len(segs)} raw segments")
        all_segments.extend(segs)

    kept = [s for s in all_segments if not is_hallucination(s)]
    print(f"Kept {len(kept)}/{len(all_segments)} segments after hallucination filtering")

    kept = dedupe_repeats(sorted(kept, key=lambda s: (s.speaker, s.start)))
    merged = merge_and_coalesce(kept)
    print(f"{len(merged)} lines after merge + coalescing")

    overrides_applied = apply_manual_overrides(merged, args.outdir, session_id)
    if overrides_applied:
        print(f"Applied {overrides_applied} manual override(s) from {session_id}-overrides.json")

    md_path, json_path, flags_path = write_outputs(merged, args.outdir, session_id)
    print(f"Wrote:\n  {md_path}\n  {json_path}")
    if flags_path:
        print(f"  {flags_path}  ({sum(1 for l in flags_path.read_text().splitlines() if l.startswith('- ['))} flagged segments -- review before /wrap-session Step 1)")


if __name__ == "__main__":
    main()
