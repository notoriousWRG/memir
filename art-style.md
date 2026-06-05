---
title: "Art Style"
type: reference
base_style: "painterly digital painting, dark atmospheric Norse fantasy, moody and weathered, textured visible brushwork, muted cold palette with warm firelight accents"
scene_style: "cinematic wide composition, dramatic directional light, depth of fog and weather, a sense of something watching"
character_style: "three-quarter portrait, weathered realism, expressive lived-in face, simple desaturated backdrop, strong rim light"
battlemap_style: "high-fidelity photorealistic prerendered tabletop RPG battle map in the style of a Roll20 / Dungeondraft / Foundry VTT map, a perfectly flat directly-overhead satellite/drone view straight down — absolutely no 3D, no isometric angle, no camera tilt, no oblique view — richly detailed realistic natural textures (sand grain, wet wood planking, foam, moss, stone, water depth), varied terrain laid out in distinct zones with natural asymmetry, even ambient daylight with soft contact shadows only, a faint regular square grid overlay across the whole map"
battlemap_style_type: "REALISTIC"
battlemap_reference_images: ""
negative: "no text, no words, no letters, no numbers, no UI, no watermark, no signature, no border, no labels, no frame"
---

# Memir Visual Style

The single source of truth for AI-generated session art. `generate-session-art.py` reads the
frontmatter fields above; edit them here and every generated image follows. The body is for the
humans — the *why* behind the look.

## The world's eye

Ældor is a cold, sea-bitten Norse-fantasy world where the supernatural arrives as **weather and pressure**, not spectacle. Art should feel **painted, not rendered** — visible brushwork, grain, the sense of a human hand. Lean dark and atmospheric: fog that moves like water, storm-grey stone,
black sand, firelight as the only warmth.

- **Palette** — desaturated cold base (slate, sea-green, bone, ash) with sparing warm accents
  (firelight amber, lightning teal-white, blood red used *once*).
- **Mood** — wonder edged with dread. The island "gives to those who witness and takes from those
  who seize" — images should feel like they're offering something and withholding something at once.
- **Light** — directional and low; rim light and god-rays through fog over flat fill light.
- **Influences** — Norse saga illustration, Zdzisław Beksiński's atmosphere (not his body-horror),
  Greg Rutkowski composition, plein-air seascape texture.

## Per-category intent

- **Scenes** (`scene_style`) — establishing read-aloud moments. Wide, cinematic, weather-forward.
  The frame should answer "what does the table see when I read this aloud?"
- **Characters** (`character_style`) — reveal portraits. Faces that carry their history; backdrop
  stays simple so the person reads instantly at the table.
- **Battlemaps** (`battlemap_style`) — **photoreal, high-fidelity, top-down.** These do *not*
  inherit the painterly `base_style` (painterly brushwork reads as mush from straight overhead).
  They render REALISTIC (`battlemap_style_type`) with rich natural textures and distinct terrain
  zones, grid-aligned for D&D Beyond import. Readability and material detail beat drama.

## Style reference images (optional — currently off)

Ideogram v3 can take **style reference images** that transfer *look and texture* (not layout) onto a
generation. `battlemap_reference_images` (vault-relative paths, comma-separated) points every
generated battlemap at one or more exemplar maps. It's **empty by default**: an exemplar with VTT
tokens or text labels on it bleeds that text into the output, so a reference only helps if it's
**token-free and label-free**. With it off, maps render `REALISTIC` from the prompt alone.

Important: a style reference transfers **fidelity and materials, not composition**. Ideogram has no
layout/structural conditioning — dynamic blocking comes from the per-scene **Battlemap layout** brief
in the prep (see below), not from an uploaded image.

`--style-ref PATH` on the command line adds an ad-hoc reference for a single run.

## Battlemap layout briefs (where dynamic composition comes from)

Because look ≠ layout, each combat/puzzle scene in a session prep may carry a `**Battlemap layout:**`
line — 2–3 sentences describing the space *as a top-down plan*: zones, entrances/edges, the focal
feature, and deliberate asymmetry. The art script feeds that verbatim as the map's terrain brief
(falling back to the scene read-aloud + location notes when absent). This is the old hand-built HTML
map's real value — the blocking — captured as prose the prompt can use.

## Changing the look

Edit the frontmatter fields, then re-run the script with `--dry-run` to see the new prompts before
spending any API calls. Keep `negative` strict — Ideogram will happily stamp text and borders onto
a battlemap otherwise.
