"""Render a Session Skald issue (markdown) to email-ready HTML.

Usage: python render-skald.py campaigns/chance-encounters/skald/skald-024.md
Writes skald-024.html next to the input. Inline CSS only, so it survives being pasted
into an email. Understands just the markdown subset the skeletons in skald-style.md use.
"""
import html
import re
import sys
from pathlib import Path

SANS = "Helvetica, Arial, sans-serif"
SERIF = "Georgia, 'Times New Roman', serif"
INK = "#1a1a1a"

S = {
    "p": f"margin:0 0 18px;font:16px/1.6 {SANS};color:{INK};",
    "date": f"margin:0 0 6px;font:13px {SANS};color:#666;text-align:center;",
    "mast": f"margin:0 0 28px;font:400 40px/1.1 {SERIF};letter-spacing:1px;text-align:center;color:#000;",
    "kicker": f"margin:28px 0 4px;font:12px {SANS};letter-spacing:1.5px;text-transform:uppercase;color:#555;",
    "h2": f"margin:0 0 16px;font:700 26px/1.25 {SANS};color:{INK};",
    "h3": f"margin:0 0 10px;font:700 20px/1.3 {SANS};color:{INK};",
    "quote_label": f"margin:24px 0 6px;font:12px {SANS};letter-spacing:1.5px;text-transform:uppercase;color:#555;text-align:center;",
    "quote": f"margin:0 0 10px;font:700 24px/1.3 {SANS};color:{INK};text-align:center;",
    "quote_by": f"margin:0 0 18px;font:15px/1.5 {SANS};color:{INK};text-align:center;",
    "hr": "border:0;border-top:1px solid #e2e2e2;margin:28px 0;",
    "bubble": f"display:inline-block;margin:8px 0 18px;padding:12px 24px;border-radius:28px;background:#d4f75a;font:400 26px/1.2 {SANS};color:#000;",
    "star": f"margin:28px 0 12px;font:12px {SANS};letter-spacing:1.5px;text-transform:uppercase;color:#555;",
    "option": f"margin:0 0 12px;padding:14px 22px;border:1px solid #2ec4b6;font:16px {SANS};color:{INK};",
    "foot": f"margin:0 0 6px;font:italic 14px/1.5 {SANS};color:#444;",
}

BUBBLES = ("behind the screen",)
LABELS = ("in our rotation", "on our calendar", "know it all")


def inline(text: str) -> str:
    text = html.escape(text, quote=False).replace("\\*", "\x00")
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"~~(.+?)~~", r"<s>\1</s>", text)
    return text.replace("\x00", "*")


def is_kicker(line: str) -> bool:
    return bool(re.fullmatch(r"[A-Z0-9 ',&!?\-]+", line.strip())) and not line.startswith("#")


def render(md: str) -> tuple[str, str]:
    meta, body = {}, md
    if md.startswith("---"):
        fm, body = md[3:].split("\n---", 1)
        for line in fm.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')

    out, seen_mast, after_quote_label = [], False, False
    for block in re.split(r"\n\s*\n", body.strip()):
        lines = [l.rstrip() for l in block.strip().splitlines()]
        first = lines[0]

        if first == "---":
            out.append(f'<hr style="{S["hr"]}">')
        elif first.startswith("# "):
            seen_mast = True
            out.append(f'<h1 style="{S["mast"]}">{inline(first[2:])}</h1>')
        elif not seen_mast:
            out.append(f'<p style="{S["date"]}">{inline(" ".join(lines))}</p>')
        elif first.startswith("### "):
            # "### QUOTE OF THE NIGHT" followed by "## "quote"" in the same block
            out.append(f'<p style="{S["quote_label"]}">{inline(first[4:])}</p>')
            if len(lines) > 1 and lines[1].startswith("## "):
                out.append(f'<p style="{S["quote"]}">{inline(lines[1][3:])}</p>')
                if len(lines) > 2:
                    out.append(f'<p style="{S["quote_by"]}">{inline(" ".join(lines[2:]))}</p>')
                after_quote_label = len(lines) == 2
            else:
                after_quote_label = False
        elif first.startswith("— ") and after_quote_label:
            out.append(f'<p style="{S["quote_by"]}">{inline(" ".join(lines))}</p>')
            after_quote_label = False
        elif len(lines) > 1 and is_kicker(first) and lines[1].startswith("## "):
            out.append(f'<p style="{S["kicker"]}">{inline(first)}</p>')
            out.append(f'<h2 style="{S["h2"]}">{inline(lines[1][3:])}</h2>')
        elif first.startswith("## "):
            title = first[3:]
            low = title.lower()
            if any(b in low for b in BUBBLES):
                out.append(f'<div><span style="{S["bubble"]}">{inline(title)}</span></div>')
            elif any(l in low for l in LABELS):
                star = "&#10036;&#xFE0E; " if "rotation" in low else ""
                label = title.replace("✴︎", "").strip()
                out.append(f'<p style="{S["star"]}"><span style="color:#f5a000;">{star}</span>{inline(label)}</p>')
            else:
                out.append(f'<h2 style="{S["h2"]}">{inline(title)}</h2>')
        elif all(re.match(r"[A-E]\. ", l) for l in lines):
            out.extend(f'<div style="{S["option"]}">{inline(l)}</div>' for l in lines)
        elif all(re.fullmatch(r"\*[^*].*\*", l) for l in lines) and "Skimm'd by" in block:
            out.extend(f'<p style="{S["foot"]}">{inline(l)}</p>' for l in lines)
        elif len(lines) == 1 and re.fullmatch(r"\*\*[^*—]+\*\*", first):
            out.append(f'<h3 style="{S["h3"]}">{inline(first[2:-2])}</h3>')
        else:
            out.append(f'<p style="{S["p"]}">{"<br>".join(inline(l) for l in lines)}</p>')

    title = meta.get("subject_line") or meta.get("title", "The Session Skald")
    page = f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title></head>
<body style="margin:0;padding:0;background:#ffffff;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#ffffff;">
<tr><td align="center" style="padding:32px 16px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">
<tr><td style="text-align:left;">
{chr(10).join(out)}
</td></tr></table>
</td></tr></table>
</body></html>
"""
    return title, page


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    title, page = render(src.read_text(encoding="utf-8"))
    dest = src.with_suffix(".html")
    dest.write_text(page, encoding="utf-8")
    print(f"Wrote {dest}  (subject: {title})")


if __name__ == "__main__":
    main()
