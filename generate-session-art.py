#!/usr/bin/env python3
"""generate-session-art.py — Ideogram art for Memir sessions.

Pre-session (default): reads a session prep file and proposes scene art
and character-in-context reveals for tonight.

Post-session (--post): reads a completed session record and proposes art
for memorable moments — action freeze-frames and, when a genuine group
moment happened, a party shot.

Visual style and character reference images (PC portraits) live in
`art-style.md` at the vault root. Character refs are attached to every
generated image for visual consistency across the campaign.

Usage:
    python generate-session-art.py campaigns/.../session-020-prep.md
    python generate-session-art.py campaigns/.../session-020.md --post
    python generate-session-art.py <file> --scene circled-zone
    python generate-session-art.py <file> --only scene
    python generate-session-art.py <file> --yes        # skip deselect
    python generate-session-art.py <file> --dry-run    # no API calls

Dependencies: requests, python-dotenv.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import requests
from dotenv import load_dotenv
import os

API_URL = "https://api.ideogram.ai/v1/ideogram-v3/generate"
STYLE_TYPE = "GENERAL"

# Rough estimates — verify at ideogram.ai/pricing before a large run
COST_ESTIMATE = {"FLASH": 0.02, "TURBO": 0.04, "DEFAULT": 0.06, "QUALITY": 0.08}

FALLBACK_STYLE = {
    "base_style": (
        "painterly digital painting, dark atmospheric Norse fantasy, moody and weathered, "
        "textured visible brushwork, muted cold palette with warm firelight accents"
    ),
    "scene_style": (
        "cinematic wide composition, dramatic directional light, "
        "depth of fog and weather, a sense of something watching"
    ),
    "character_style": (
        "wide action shot showing the full body mid-motion within their environment, "
        "character caught mid-gesture or mid-reaction, props and setting integral to the frame, "
        "strong single directional light source, expressive body language over facial expression "
        "— not a portrait, not facing the camera directly, never standing still"
    ),
    "character_reference_images": "",
    "negative": (
        "no text, no words, no letters, no numbers, no UI, no watermark, "
        "no signature, no border, no labels, no frame"
    ),
}

MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}

CATEGORY_ASPECT = {"scene": "16x9", "char": "4x3", "party": "16x9"}
CATEGORY_LABEL = {"scene": "Scenes", "char": "Characters", "party": "Party Moments"}

PARTY_THRESHOLD = 4  # min distinct PCs mentioned in a section to propose a party shot

DRAMATIC_WORDS = frozenset([
    "fell", "struck", "revealed", "chose", "broke", "wept", "laughed",
    "confronted", "embraced", "shattered", "defeated", "died", "promised",
    "failed", "succeeded", "saved", "lost", "freed", "bound", "called",
    "reached", "stood", "knelt", "smiled", "finally", "silent", "alone",
    "together", "last", "first time", "turned away", "stepped forward",
])

# Used to find the most physically active sentence in a prose block
ACTION_VERBS = frozenset([
    "threw", "throw", "struck", "strike", "cast", "step", "stepped", "reach", "reached",
    "grabbed", "grab", "pulled", "pull", "spun", "spin", "lunged", "lunge", "drew", "draw",
    "raised", "raise", "fell", "leap", "leapt", "caught", "catch", "blocked", "block",
    "charged", "charge", "slammed", "slam", "pushed", "push", "knelt", "kneel", "bowed",
    "bow", "erupted", "shattered", "swept", "dove", "ran", "run", "turned", "flinched",
    "recoiled", "sprinted", "leaned", "lean", "extended", "extend", "fired", "fire",
    "snapped", "snap", "rushed", "rush", "pivoted", "pivot", "surged", "surge",
])


# ─────────────────────────────────────────────────────────────────────────────
# Markdown / frontmatter helpers
# ─────────────────────────────────────────────────────────────────────────────

def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Return (frontmatter_dict, body). Parses simple `key: value` scalar lines only."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_block = text[3:end].strip("\n")
    body = text[end + 4:].lstrip("\n")
    fm: dict[str, str] = {}
    for line in fm_block.splitlines():
        if not line.strip() or line.lstrip().startswith("-"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        val = val.strip().strip('"').strip("'")
        if val:
            fm[key.strip()] = val
    return fm, body


def frontmatter_list(raw_fm: str, key: str) -> list[str]:
    """Extract a YAML list field like `pcs_present: [a, b, c]` from raw frontmatter text."""
    m = re.search(rf"^{re.escape(key)}\s*:\s*\[([^\]]*)\]", raw_fm, flags=re.M)
    if m:
        return [v.strip() for v in m.group(1).split(",") if v.strip()]
    lines: list[str] = []
    in_key = False
    for line in raw_fm.splitlines():
        if re.match(rf"^{re.escape(key)}\s*:", line):
            in_key = True
            continue
        if in_key:
            if line.startswith("  -") or line.startswith("- "):
                lines.append(line.lstrip("- ").strip())
            elif line and not line.startswith(" "):
                break
    return lines


def kebab(text: str) -> str:
    text = re.sub(r"^the\s+", "", text.strip(), flags=re.I)
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_]+", "-", text).strip("-")


def strip_wikilinks(text: str) -> str:
    """`[[slug|Display]]` -> `Display`, `[[slug]]` -> `slug`, drop bold/italic markers."""
    text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = text.replace("**", "").replace("*", "")
    return text.strip()


def first_paragraph(body: str) -> str:
    for chunk in body.split("\n\n"):
        chunk = chunk.strip()
        if chunk and not chunk.startswith("#"):
            return strip_wikilinks(" ".join(chunk.splitlines()))
    return ""


def section(body: str, header_pattern: str) -> str:
    """Return the text under the first heading matching `header_pattern`."""
    lines = body.splitlines()
    out: list[str] = []
    capturing = False
    level = 0
    for line in lines:
        m = re.match(r"^(#{2,4})\s+(.*)$", line)
        if m:
            this_level = len(m.group(1))
            if capturing and this_level <= level:
                break
            if not capturing and re.search(header_pattern, m.group(2), flags=re.I):
                capturing = True
                level = this_level
                continue
        if capturing:
            out.append(line)
    return "\n".join(out).strip()


def action_snippet(text: str, context: int = 2) -> str:
    """Return the most physically active sentence plus `context` surrounding sentences."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    if len(sentences) <= context + 1:
        return " ".join(sentences)
    best_idx, best_score = 0, -1
    for i, s in enumerate(sentences):
        s_low = s.lower()
        score = sum(1 for v in ACTION_VERBS if re.search(rf"\b{re.escape(v)}\b", s_low))
        if score > best_score:
            best_score, best_idx = score, i
    start = max(0, best_idx - 1)
    end = min(len(sentences), best_idx + context)
    return " ".join(sentences[start:end])


# ─────────────────────────────────────────────────────────────────────────────
# Vault helpers
# ─────────────────────────────────────────────────────────────────────────────

def find_vault_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "CLAUDE.md").exists():
            return p
    return start.parent


def build_index(vault: Path) -> dict[str, Path]:
    """Map kebab basename -> file path for every markdown file in the vault."""
    index: dict[str, Path] = {}
    for path in vault.rglob("*.md"):
        if any(part in (".git", ".obsidian", ".trash") for part in path.parts):
            continue
        index.setdefault(path.stem, path)
    return index


def is_new_entity(path: Path, vault: Path) -> bool:
    """True if the file is git-untracked or newly added (a reveal added this prep)."""
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain", "--", str(path)],
            cwd=vault, capture_output=True, text=True, timeout=10,
        ).stdout
    except (subprocess.SubprocessError, OSError):
        return False
    if not out:
        return False
    return "?" in out[:2] or "A" in out[:2]


def load_style(vault: Path) -> dict[str, str]:
    style = dict(FALLBACK_STYLE)
    style_file = vault / "art-style.md"
    if style_file.exists():
        fm, _ = split_frontmatter(style_file.read_text(encoding="utf-8"))
        for key in FALLBACK_STYLE:
            if fm.get(key):
                style[key] = fm[key]
    return style


def load_char_refs(vault: Path, style: dict[str, str]) -> list[Path]:
    """Load PC portrait paths from the character_reference_images config."""
    refs = [vault / p.strip()
            for p in style.get("character_reference_images", "").split(",") if p.strip()]
    return [p for p in refs if p.exists()]


# ─────────────────────────────────────────────────────────────────────────────
# Art item
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ArtItem:
    category: str          # scene | char | party
    slug: str
    title: str
    prompt: str
    why: str = ""
    new: bool = False
    aspect: str = field(default="1x1")
    style_type: str = STYLE_TYPE
    style_refs: list = field(default_factory=list)

    def filename(self, session_no: str) -> str:
        return f"session-{session_no}-{self.category}-{self.slug}.png"


WIKILINK = re.compile(r"\[\[([^\]|#]+)")


def wikilinks_in(text: str) -> list[str]:
    seen: list[str] = []
    for m in WIKILINK.finditer(text):
        slug = m.group(1).strip()
        if slug not in seen:
            seen.append(slug)
    return seen


# ─────────────────────────────────────────────────────────────────────────────
# Pre-session plan (reads prep file)
# ─────────────────────────────────────────────────────────────────────────────

def parse_scenes(body: str) -> list[dict]:
    """Extract scenes from the prep file. Each scene: title, read-aloud, location slug."""
    scenes: list[dict] = []
    headers = list(re.finditer(r"^###\s+Scene\s+(\d+)\s+—\s+(.+)$", body, flags=re.M))
    for i, h in enumerate(headers):
        start = h.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(body)
        block = body[start:end]
        scene_num = int(h.group(1))
        title = h.group(2).split("·")[0].strip()
        ra = re.search(r"\*\*Read-aloud[^:]*:\*\*\s*(.+)", block)
        read_aloud = strip_wikilinks(ra.group(1).strip()) if ra else ""
        loc = wikilinks_in(block)
        is_climax = bool(re.search(r"CLIMAX", block, flags=re.I))
        scenes.append({
            "title": title,
            "num": scene_num,
            "read_aloud": read_aloud,
            "location": loc[0] if loc else None,
            "is_climax": is_climax,
            "is_last": False,
        })
    if scenes:
        scenes[-1]["is_last"] = True
    return scenes


def build_pre_plan(prep_path: Path, vault: Path, style: dict[str, str],
                   char_refs: list[Path]) -> tuple[str, list[ArtItem]]:
    text = prep_path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    session_no = str(fm.get("session_number", "000")).zfill(3)

    index = build_index(vault)
    neg = style["negative"]
    items: list[ArtItem] = []

    # ── Scenes ──
    all_scenes = parse_scenes(body)
    total = len(all_scenes)
    for sc in all_scenes:
        if not sc["read_aloud"]:
            continue
        slug = kebab(sc["title"])
        if sc["is_climax"]:
            why = "climax scene"
        elif sc["is_last"]:
            why = f"closing scene ({sc['num']}/{total})"
        else:
            why = f"scene {sc['num']}/{total}"
        items.append(ArtItem(
            category="scene", slug=slug, title=sc["title"], why=why,
            aspect=CATEGORY_ASPECT["scene"],
            prompt=f"{sc['read_aloud']} {style['base_style']}, {style['scene_style']}. {neg}.",
            style_refs=list(char_refs),
        ))

    # ── Characters: cast tonight + encounter bank, reveals first ──
    cast_text = "\n".join(x for x in (
        section(body, r"the cast tonight"),
        section(body, r"encounter bank"),
    ) if x)
    chars: list[ArtItem] = []
    for slug in wikilinks_in(cast_text):
        path = index.get(slug)
        if not path:
            continue
        cfm, cbody = split_frontmatter(path.read_text(encoding="utf-8"))
        if cfm.get("type") not in ("npc", "monster"):
            continue
        title = cfm.get("title", slug).strip('"')
        descriptor = " ".join(x for x in (
            cfm.get("race", ""),
            cfm.get("role", "") or cfm.get("monster_type", ""),
        ) if x).strip()
        lede = first_paragraph(cbody)
        article = "an" if descriptor[:1].lower() in "aeiou" else "a"
        subject = f"{title}, {article} {descriptor}" if descriptor else title
        new = is_new_entity(path, vault)
        why = "first reveal tonight — not yet seen by players" if new else "returning NPC"
        chars.append(ArtItem(
            category="char", slug=slug, title=title, why=why,
            new=new, aspect=CATEGORY_ASPECT["char"],
            prompt=(f"{subject} caught mid-action. {lede} "
                    f"{style['base_style']}, {style['character_style']}. {neg}."),
            style_refs=list(char_refs),
        ))
    chars.sort(key=lambda it: (not it.new, it.title.lower()))

    return session_no, items + chars


# ─────────────────────────────────────────────────────────────────────────────
# Post-session plan (reads completed session record)
# ─────────────────────────────────────────────────────────────────────────────

def load_pc_names(vault: Path, slugs: list[str], index: dict[str, Path]) -> dict[str, str]:
    """Map pc slug -> display name (title frontmatter, or title-cased slug as fallback)."""
    names: dict[str, str] = {}
    for slug in slugs:
        path = index.get(slug)
        if path:
            pfm, _ = split_frontmatter(path.read_text(encoding="utf-8"))
            names[slug] = pfm.get("title", slug).strip('"')
        else:
            names[slug] = "-".join(p.capitalize() for p in slug.split("-"))
    return names


def split_into_sections(body: str) -> list[tuple[str, str]]:
    """Return list of (header_title, section_text). Ungrouped leading text gets title ''."""
    result: list[tuple[str, str]] = []
    header_re = re.compile(r"^#{1,3}\s+(.+)$", re.M)
    positions = [(m.start(), m.group(1).strip(), m.end()) for m in header_re.finditer(body)]

    if not positions:
        for para in body.split("\n\n"):
            para = para.strip()
            if para:
                result.append(("", para))
        return result

    if positions[0][0] > 0:
        lead = body[:positions[0][0]].strip()
        if lead:
            result.append(("", lead))

    for i, (start, title, end) in enumerate(positions):
        next_start = positions[i + 1][0] if i + 1 < len(positions) else len(body)
        text = body[end:next_start].strip()
        result.append((title, text))

    return result


def score_section(text: str, pc_display_names: list[str]) -> tuple[int, set[str]]:
    """Score a block for art-worthiness. Returns (score, set of mentioned PC names)."""
    score = 0
    mentioned: set[str] = set()
    text_lower = text.lower()

    for name in pc_display_names:
        if name.lower() in text_lower:
            score += 2
            mentioned.add(name)

    for word in DRAMATIC_WORDS:
        if word in text_lower:
            score += 1
            break  # one dramatic-word bonus per section

    if len(text.split()) > 60:
        score += 1

    return score, mentioned


def build_post_plan(session_path: Path, vault: Path, style: dict[str, str],
                    char_refs: list[Path]) -> tuple[str, list[ArtItem]]:
    text = session_path.read_text(encoding="utf-8")

    # Extract pcs_present from raw frontmatter text (split_frontmatter drops list fields)
    raw_fm_end = text.find("\n---", 3)
    raw_fm = text[3:raw_fm_end] if raw_fm_end != -1 else ""
    pc_slugs = frontmatter_list(raw_fm, "pcs_present")

    fm, body = split_frontmatter(text)
    session_no = str(fm.get("session_number", "000")).zfill(3)

    index = build_index(vault)
    neg = style["negative"]
    pc_names_map = load_pc_names(vault, pc_slugs, index)
    pc_display = list(pc_names_map.values())

    sections = split_into_sections(body)

    scored: list[tuple[int, str, str, set[str]]] = []
    for title, text_block in sections:
        if len(text_block.split()) < 20:
            continue
        s, mentioned = score_section(text_block, pc_display)
        if s > 0:
            scored.append((s, title, text_block, mentioned))

    scored.sort(key=lambda x: -x[0])

    # Pick top moments — cap at 5, try to spread across different PCs
    chosen: list[tuple[int, str, str, set[str]]] = []
    used_pcs: set[str] = set()
    party_pcs: set[str] = set()
    party_prose: str = ""

    for s, title, text_block, mentioned in scored:
        if len(chosen) >= 5:
            break
        if s >= 4 or not (mentioned & used_pcs) or len(chosen) < 2:
            chosen.append((s, title, text_block, mentioned))
            used_pcs |= mentioned
            if len(mentioned) >= PARTY_THRESHOLD:
                party_pcs = mentioned
                party_prose = text_block

    items: list[ArtItem] = []

    for _, title, text_block, mentioned in chosen:
        slug = kebab(title) if title else f"moment-{len(items) + 1}"
        display_title = title if title else "Untitled moment"

        snippet = action_snippet(strip_wikilinks(text_block))

        if len(mentioned) == 1:
            why = f"{next(iter(mentioned))} spotlight moment"
        elif len(mentioned) >= 2:
            why = f"shared moment — {', '.join(sorted(mentioned))}"
        else:
            why = "key moment"

        items.append(ArtItem(
            category="scene", slug=slug, title=display_title, why=why,
            aspect=CATEGORY_ASPECT["scene"],
            prompt=(f"Action freeze-frame: {snippet} "
                    f"{style['base_style']}, {style['scene_style']}, "
                    f"figures caught mid-motion, dynamic pose, poster-worthy framing. {neg}."),
            style_refs=list(char_refs),
        ))

    # Party shot — only when a genuine group moment is found
    if party_pcs:
        names_str = ", ".join(sorted(party_pcs))
        party_snippet = action_snippet(strip_wikilinks(party_prose))
        items.append(ArtItem(
            category="party", slug="party", title="Party together",
            why=f"group moment — {names_str}",
            aspect=CATEGORY_ASPECT["party"],
            prompt=(f"Action freeze-frame, full group in frame: {party_snippet} "
                    f"Wide shot, all figures visible and mid-action. "
                    f"{style['base_style']}, {style['scene_style']}, "
                    f"dynamic group composition, poster-worthy. {neg}."),
            style_refs=list(char_refs),
        ))

    return session_no, items


# ─────────────────────────────────────────────────────────────────────────────
# Selection + display
# ─────────────────────────────────────────────────────────────────────────────

def preview(prompt: str, width: int = 88) -> str:
    flat = re.sub(r"\s+", " ", prompt).strip()
    return flat if len(flat) <= width else flat[: width - 1] + "…"


def print_plan(items: list[ArtItem], session_no: str) -> None:
    print(f"\nPlanned artwork for session {session_no}:\n")
    n = 0
    last_cat = None
    for it in items:
        if it.category != last_cat:
            print(f"  {CATEGORY_LABEL[it.category]}")
            last_cat = it.category
        n += 1
        star = " ⭐NEW" if it.new else ""
        refs = f"  [style-ref ×{len(it.style_refs)}]" if it.style_refs else ""
        print(f"    [{n:>2}] {it.filename(session_no)}{star}{refs}")
        if it.why:
            print(f"         ↳ {it.why}")
        print(f"         {preview(it.prompt)}")
    print()


def choose(items: list[ArtItem], session_no: str) -> list[ArtItem]:
    print_plan(items, session_no)
    try:
        raw = input("Enter numbers to SKIP (space/comma separated), "
                    "'q' to cancel, Enter = generate all: ").strip()
    except EOFError:
        raw = ""
    if raw.lower() == "q":
        return []
    if not raw:
        return items
    skip = {int(tok) for tok in re.split(r"[,\s]+", raw) if tok.isdigit()}
    return [it for n, it in enumerate(items, 1) if n not in skip]


# ─────────────────────────────────────────────────────────────────────────────
# API generation
# ─────────────────────────────────────────────────────────────────────────────

def generate(item: ArtItem, api_key: str, art_dir: Path, session_no: str,
             speed: str = "QUALITY") -> Path:
    """POST to Ideogram v3, download the result, write to art_dir."""
    style_type = "AUTO" if item.style_refs else item.style_type
    parts: list = [
        ("prompt", (None, item.prompt)),
        ("rendering_speed", (None, speed)),
        ("style_type", (None, style_type)),
        ("aspect_ratio", (None, item.aspect)),
        ("magic_prompt", (None, "OFF")),
    ]
    for ref in item.style_refs:
        ref = Path(ref)
        parts.append(("style_reference_images",
                      (ref.name, ref.read_bytes(), MIME.get(ref.suffix.lower(), "image/png"))))

    resp = requests.post(API_URL, headers={"Api-Key": api_key}, files=parts, timeout=180)
    if not resp.ok:
        try:
            detail = resp.json().get("error") or resp.reason
        except ValueError:
            detail = resp.reason or "non-JSON error response"
        raise RuntimeError(f"HTTP {resp.status_code}: {detail}")
    url = resp.json()["data"][0]["url"]
    img = requests.get(url, timeout=180)
    img.raise_for_status()
    out = art_dir / item.filename(session_no)
    out.write_bytes(img.content)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description="Generate Ideogram art for a Memir session.")
    ap.add_argument("file", type=Path,
                    help="Session prep file (default) or completed session record (--post).")
    ap.add_argument("--post", action="store_true",
                    help="Post-session mode: read a completed session-N.md record.")
    ap.add_argument("--scene", metavar="NAME",
                    help="Generate only items whose slug/title contains NAME.")
    ap.add_argument("--only", choices=["scene", "char", "party"], action="append", default=[],
                    help="Restrict to one or more categories (repeatable).")
    ap.add_argument("--speed", choices=["flash", "turbo", "default", "quality"],
                    default="quality",
                    help="Rendering speed / cost tier (cheap→pricey). Default: quality.")
    ap.add_argument("--style-ref", metavar="PATH", action="append", default=[],
                    help="Add a style-reference image to every selected item. Repeatable.")
    ap.add_argument("--yes", action="store_true", help="Skip the deselect menu; generate all.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print the plan and prompts without calling the API.")
    args = ap.parse_args()

    file_path = args.file.expanduser().resolve()
    if not file_path.is_file():
        print(f"error: file not found: {file_path}", file=sys.stderr)
        return 2

    vault = find_vault_root(file_path)
    load_dotenv(vault / ".env")
    style = load_style(vault)
    char_refs = load_char_refs(vault, style)

    if args.post:
        session_no, items = build_post_plan(file_path, vault, style, char_refs)
    else:
        session_no, items = build_pre_plan(file_path, vault, style, char_refs)

    if not items:
        label = "session record" if args.post else "prep file"
        print(f"No art candidates found in the {label}.", file=sys.stderr)
        return 1

    if args.only:
        items = [it for it in items if it.category in args.only]
    if args.scene:
        needle = args.scene.lower()
        items = [it for it in items if needle in it.slug.lower() or needle in it.title.lower()]
    if not items:
        print("error: no items matched the given filters.", file=sys.stderr)
        return 1

    extra_refs = [Path(p).expanduser().resolve() for p in args.style_ref]
    missing = [p for p in extra_refs if not p.exists()]
    if missing:
        print("error: --style-ref file(s) not found: " + ", ".join(map(str, missing)),
              file=sys.stderr)
        return 2
    for it in items:
        it.style_refs = list(it.style_refs) + extra_refs

    if args.dry_run:
        print_plan(items, session_no)
        print(f"(dry run — {len(items)} item(s) would be generated, no API calls made)")
        return 0

    api_key = os.environ.get("IDEOGRAM_API_KEY")
    if not api_key:
        print("error: IDEOGRAM_API_KEY is not set (env var or repo-root .env).", file=sys.stderr)
        return 2

    if args.scene or args.yes:
        selected = items
        if not args.scene:
            print_plan(items, session_no)
    else:
        selected = choose(items, session_no)
    if not selected:
        print("Nothing selected — exiting.")
        return 0

    cost_per = COST_ESTIMATE.get(args.speed.upper(), 0.08)
    print(f"\n{len(selected)} image(s) selected. "
          f"Estimated cost: ~${cost_per * len(selected):.2f} "
          f"(~${cost_per:.2f}/image at {args.speed} tier — verify at ideogram.ai/pricing).")
    try:
        confirm = input("Generate? [y/N]: ").strip().lower()
    except EOFError:
        confirm = "n"
    if confirm not in ("y", "yes"):
        print("Cancelled.")
        return 0

    art_dir = file_path.parent / "art"
    art_dir.mkdir(parents=True, exist_ok=True)

    generated: list[Path] = []
    failures: list[tuple[ArtItem, str]] = []
    for i, it in enumerate(selected, 1):
        print(f"[{i}/{len(selected)}] generating {it.filename(session_no)} "
              f"({args.speed}) …", flush=True)
        try:
            generated.append(generate(it, api_key, art_dir, session_no, args.speed.upper()))
        except Exception as exc:  # noqa: BLE001 — keep the batch going
            failures.append((it, str(exc)))
            print(f"    ✗ failed: {exc}", file=sys.stderr)

    print(f"\nDone. {len(generated)} image(s) written to {art_dir}")
    for path in generated:
        print(f"  ✓ {path.name}")
    if failures:
        print(f"\n{len(failures)} failed:")
        for it, err in failures:
            print(f"  ✗ {it.filename(session_no)} — {err}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
