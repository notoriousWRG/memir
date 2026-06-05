#!/usr/bin/env python3
"""generate-session-art.py — Ideogram art for a Memir session prep file.

Reads a session prep markdown file, proposes a focused set of artwork —
big-moment scenes, reveal/new characters, and a top-down battlemap per scene —
lets you de-select interactively, then generates PNGs via the Ideogram v3 API
into the session's `art/` folder.

Visual style is read from `art-style.md` at the vault root (single source of
truth). The Ideogram API key comes from $IDEOGRAM_API_KEY or a repo-root `.env`.

Usage:
    python generate-session-art.py campaigns/chance-encounters/sessions/session-019-prep.md
    python generate-session-art.py <prep.md> --scene spar-field   # only matching item(s)
    python generate-session-art.py <prep.md> --yes                # skip the de-select menu
    python generate-session-art.py <prep.md> --dry-run            # print plan, no API calls

Dependencies beyond the standard library: requests, python-dotenv.
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
# style_type must be one of: AUTO, GENERAL, REALISTIC, DESIGN (FICTION exists in the
# docs but is rejected by the generate endpoint). GENERAL lets the prompt text drive
# the painterly look without forcing photoreal (REALISTIC) or graphic (DESIGN) output.
STYLE_TYPE = "GENERAL"

# Built-in fallback style, used only if art-style.md is missing or incomplete.
FALLBACK_STYLE = {
    "base_style": "painterly digital painting, dark atmospheric fantasy, moody, textured brushwork",
    "scene_style": "cinematic wide composition, dramatic directional light, fog and weather",
    "character_style": "three-quarter portrait, weathered realism, expressive face, simple backdrop",
    "battlemap_style": (
        "high-fidelity photorealistic top-down tabletop battle map, richly detailed natural "
        "textures, strict 90-degree overhead view, distinct terrain zones, faint square grid"
    ),
    "battlemap_style_type": "REALISTIC",
    "battlemap_reference_images": "",
    "negative": "no text, no words, no UI, no watermark, no border, no labels",
}

MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}

CATEGORY_ASPECT = {"scene": "16x9", "char": "3x4", "map": "16x9"}
CATEGORY_LABEL = {"scene": "Scenes", "char": "Characters", "map": "Battlemaps"}


# ─────────────────────────────────────────────────────────────────────────────
# Small markdown / frontmatter helpers (no PyYAML dependency)
# ─────────────────────────────────────────────────────────────────────────────

def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Return (frontmatter_dict, body). Only simple `key: value` scalar lines are
    parsed; list lines and nested structures are ignored (we don't need them)."""
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
    """Return the text under the first heading matching `header_pattern`, up to the
    next heading of the same-or-higher level."""
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


# ─────────────────────────────────────────────────────────────────────────────
# Vault model
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
    code = out[:2]
    return "?" in code or "A" in code


def load_style(vault: Path) -> dict[str, str]:
    style = dict(FALLBACK_STYLE)
    style_file = vault / "art-style.md"
    if style_file.exists():
        fm, _ = split_frontmatter(style_file.read_text(encoding="utf-8"))
        for key in FALLBACK_STYLE:
            if fm.get(key):
                style[key] = fm[key]
    return style


# ─────────────────────────────────────────────────────────────────────────────
# Plan items
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ArtItem:
    category: str          # scene | char | map
    slug: str
    title: str
    prompt: str
    new: bool = False
    aspect: str = field(default="1x1")
    style_type: str = STYLE_TYPE
    style_refs: list = field(default_factory=list)  # vault-relative reference image paths

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


def parse_scenes(body: str) -> list[dict]:
    """Each scene: short title, read-aloud text, and the location slug linked under it."""
    scenes: list[dict] = []
    headers = list(re.finditer(r"^###\s+Scene\s+\d+\s+—\s+(.+)$", body, flags=re.M))
    for i, h in enumerate(headers):
        start = h.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(body)
        block = body[start:end]
        title = h.group(1).split("·")[0].strip()
        ra = re.search(r"\*\*Read-aloud:\*\*\s*(.+)", block)
        read_aloud = strip_wikilinks(ra.group(1).strip()) if ra else ""
        bl = re.search(r"\*\*Battlemap layout:\*\*\s*(.+)", block)
        layout = strip_wikilinks(bl.group(1).strip()) if bl else ""
        loc = wikilinks_in(block)
        scenes.append({
            "title": title,
            "read_aloud": read_aloud,
            "layout": layout,
            "location": loc[0] if loc else None,
        })
    return scenes


def location_blocking(loc_slug: str | None, scene_title: str,
                      index: dict[str, Path]) -> str:
    """Pull tactical blocking for a scene from the linked location file: the matching
    sub-location paragraph if present, else the location's opening description."""
    if not loc_slug or loc_slug not in index:
        return ""
    fm, lbody = split_frontmatter(index[loc_slug].read_text(encoding="utf-8"))
    key_locs = section(lbody, r"key locations")
    short = re.sub(r"^the\s+", "", scene_title, flags=re.I).strip()
    if key_locs:
        for para in re.split(r"\n(?=\*\*)", key_locs):
            if short.lower() in para.lower():
                return strip_wikilinks(" ".join(para.splitlines()))
    return first_paragraph(lbody)


def build_plan(prep_path: Path, vault: Path, style: dict[str, str]) -> tuple[str, list[ArtItem]]:
    text = prep_path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    session_no = str(fm.get("session_number", "000")).zfill(3)

    index = build_index(vault)
    neg = style["negative"]
    items: list[ArtItem] = []

    # Resolve configured battlemap style-reference images (vault-relative, comma-separated).
    map_refs = [vault / p.strip()
                for p in style.get("battlemap_reference_images", "").split(",") if p.strip()]
    map_refs = [p for p in map_refs if p.exists()]
    map_style_type = style.get("battlemap_style_type", "REALISTIC")

    # ── Scenes + their battlemaps ──
    for sc in parse_scenes(body):
        slug = kebab(sc["title"])
        if sc["read_aloud"]:
            items.append(ArtItem(
                category="scene", slug=slug, title=sc["title"],
                aspect=CATEGORY_ASPECT["scene"],
                prompt=f"{sc['read_aloud']} {style['base_style']}, {style['scene_style']}. {neg}.",
            ))
        loc_title = sc["title"]
        if sc["location"] and sc["location"] in index:
            lfm, _ = split_frontmatter(index[sc["location"]].read_text(encoding="utf-8"))
            loc_title = lfm.get("title", sc["title"]).strip('"')
        # Maps must read as a flat overhead floor plan, so lead hard with top-down
        # framing and feed the *spatial* blocking (not the cinematic read-aloud, which
        # is first-person and pulls the model toward a horizon view). Map-only negatives
        # (no horizon/sky/perspective/figures) stay inline so they don't affect scenes.
        # Prefer an authored top-down layout brief (zones/edges/focal feature) — that's what
        # makes maps dynamic. Fall back to derived blocking, stripping a leading "Name — "
        # label so the proper noun isn't rendered as title text.
        if sc["layout"]:
            terrain = sc["layout"]
        else:
            terrain = location_blocking(sc["location"], sc["title"], index) or sc["read_aloud"]
            terrain = re.sub(r"^[^—]{0,40}—\s*", "", terrain).strip()
        map_neg = (f"{neg}, no horizon, no sky, no perspective view, no isometric view, "
                   f"no 3D angle, no camera tilt, no oblique angle, no vanishing point, "
                   f"no first-person view, no character figures, no tokens")
        # Maps do NOT inherit the painterly base_style — battlemap_style is self-contained
        # and photoreal; a style-reference image (if configured) carries the fidelity. No
        # proper nouns in the framing clause — naming a place makes the model stamp a title.
        items.append(ArtItem(
            category="map", slug=slug, title=f"{sc['title']} (map)",
            aspect=CATEGORY_ASPECT["map"], style_type=map_style_type, style_refs=list(map_refs),
            prompt=(
                f"Overhead orthographic top-down tabletop RPG battle map, "
                f"seen straight down from directly above at 90 degrees, flat floor plan, "
                f"no perspective and no horizon. Terrain laid out from above: {terrain} "
                f"{style['battlemap_style']}. {map_neg}."
            ),
        ))

    # ── Characters: on-screen cast (§4) + encounter bank (§6), NEW reveals first ──
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
        chars.append(ArtItem(
            category="char", slug=slug, title=title,
            new=is_new_entity(path, vault), aspect=CATEGORY_ASPECT["char"],
            prompt=(f"Character portrait of {subject}. {lede} "
                    f"{style['base_style']}, {style['character_style']}. {neg}."),
        ))
    chars.sort(key=lambda it: (not it.new, it.title.lower()))

    # Order: scenes, characters (reveals first), battlemaps.
    scenes = [it for it in items if it.category == "scene"]
    maps = [it for it in items if it.category == "map"]
    return session_no, scenes + chars + maps


# ─────────────────────────────────────────────────────────────────────────────
# Selection + generation
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
        tags = f"  [{it.style_type}]" if it.category == "map" else ""
        if it.style_refs:
            tags += f"  [style-ref ×{len(it.style_refs)}]"
        print(f"    [{n:>2}] {it.filename(session_no)}{star}{tags}")
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


def generate(item: ArtItem, api_key: str, art_dir: Path, session_no: str,
             speed: str = "QUALITY") -> Path:
    """POST the prompt to Ideogram, download the result, write the PNG. Returns the path.

    NOTE: this function is the single place that speaks to the Ideogram API. The v3
    endpoint expects multipart/form-data; the (None, value) tuples make requests send
    each text field as a form part and set the multipart boundary automatically. Style
    reference images are repeated `style_reference_images` file parts.
    """
    # When a style reference is attached, the API requires style_type AUTO/GENERAL
    # (the reference drives the look); otherwise use the item's configured style_type.
    style_type = "AUTO" if item.style_refs else item.style_type
    # List-of-tuples form so a field name (style_reference_images) can repeat.
    parts: list = [
        ("prompt", (None, item.prompt)),
        ("rendering_speed", (None, speed)),
        ("style_type", (None, style_type)),
        ("aspect_ratio", (None, item.aspect)),
        # OFF = use our prompt verbatim; stops the auto-rewriter from stamping a
        # "title" onto the image (the stray text that leaks onto battle maps).
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
            # Non-JSON body (e.g. a Cloudflare HTML error page) — don't dump it.
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
    ap = argparse.ArgumentParser(description="Generate Ideogram art from a session prep file.")
    ap.add_argument("prep", type=Path, help="Path to the session prep markdown file.")
    ap.add_argument("--scene", metavar="NAME",
                    help="Generate only items whose slug/title contains NAME.")
    ap.add_argument("--only", choices=["scene", "char", "map"], action="append", default=[],
                    help="Restrict to one or more categories (repeatable). E.g. --only scene --only char.")
    ap.add_argument("--speed", choices=["flash", "turbo", "default", "quality"],
                    default="quality",
                    help="Rendering speed / cost tier (cheap→pricey). Default: quality.")
    ap.add_argument("--style-ref", metavar="PATH", action="append", default=[],
                    help="Add a style-reference image (look/texture, not layout) to every "
                         "selected item. Repeatable. Adds to any configured battlemap reference.")
    ap.add_argument("--yes", action="store_true", help="Skip the de-select menu; generate all.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print the plan and prompts without calling the API.")
    args = ap.parse_args()

    prep_path = args.prep.expanduser().resolve()
    if not prep_path.is_file():
        print(f"error: prep file not found: {prep_path}", file=sys.stderr)
        return 2

    vault = find_vault_root(prep_path)
    load_dotenv(vault / ".env")
    style = load_style(vault)

    session_no, items = build_plan(prep_path, vault, style)
    if not items:
        print("No scenes, characters, or battlemaps found in the prep file.", file=sys.stderr)
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

    art_dir = prep_path.parent / "art"
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
