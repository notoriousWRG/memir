---
title: "Art Style"
type: reference
base_style: "painterly digital painting, dark atmospheric Norse fantasy, moody and weathered, textured visible brushwork, muted cold palette with warm firelight accents"
scene_style: "cinematic wide composition, dramatic directional light, depth of fog and weather, a sense of something watching"
character_style: "wide action shot showing the full body mid-motion within their environment, character caught mid-gesture or mid-reaction, props and setting integral to the frame, strong single directional light source, expressive body language over facial expression — not a portrait, not facing the camera directly, never standing still"
character_reference_images: "art/characters/casus.png, art/characters/coriac.png, art/characters/grimvald.jpeg, art/characters/artcoth.png, art/characters/gareth.png, art/characters/shah.png"
negative: "no text, no words, no letters, no numbers, no UI, no watermark, no signature, no border, no labels, no frame"
---

# Memir Visual Style

The single source of truth for AI-generated session art. `generate-session-art.py` reads the
frontmatter fields above; edit them here and every generated image follows. The body is for
the humans — the *why* behind the look.

## The world's eye

Ældor is a cold, sea-bitten Norse-fantasy world where the supernatural arrives as **weather and
pressure**, not spectacle. Art should feel **painted, not rendered** — visible brushwork, grain,
the sense of a human hand. Lean dark and atmospheric: fog that moves like water, storm-grey stone,
black sand, firelight as the only warmth.

- **Palette** — desaturated cold base (slate, sea-green, bone, ash) with sparing warm accents
  (firelight amber, lightning teal-white, blood red used *once*).
- **Mood** — wonder edged with dread. Images should feel like they're offering something and
  withholding something at once.
- **Light** — directional and low; rim light and god-rays through fog over flat fill light.
- **Influences** — Norse saga illustration, Zdzisław Beksiński's atmosphere (not his body-horror),
  Greg Rutkowski composition, plein-air seascape texture.

## Per-category intent

- **Scenes** (`scene_style`) — establishing read-aloud moments. Wide, cinematic, weather-forward.
  The frame should answer "what does the table see when I read this aloud?"

- **Characters** (`character_style`) — NPC reveals and PC spotlight moments. **Not portraits.**
  Characters are shown in context — within their environment, with props, atmosphere, and setting
  that tells you who they are and what they're about. Think: Edrin stepping from the treeline,
  not Edrin's face on a blank backdrop. A character reveal should feel like a scene still, not
  a headshot. Aspect ratio 4:3 (landscape) to give room for context.

- **Party moments** — post-session group shots when the session had a genuine shared moment.
  Wide, 16:9, full group in frame. Same painterly style as scenes; the group is within the world,
  not posed against a backdrop.

## Character reference images

Drop PC portrait images into `art/characters/` at the vault root, named by PC slug
(e.g. `art/characters/casus.png`, `art/characters/grimvald.png`). Then list them in
`character_reference_images` above (vault-relative paths, comma-separated):

```
character_reference_images: "art/characters/casus.png, art/characters/grimvald.png, ..."
```

These attach to every generated image as Ideogram style references. They transfer *aesthetic
and visual language* — not exact likenesses — so the whole campaign's art stays in the same
visual register as the player-created character images. With refs attached, `style_type` is
set to `AUTO` automatically (the reference drives the look).

## Changing the look

Edit the frontmatter fields, then re-run the script with `--dry-run` to preview the new prompts
before spending any API calls. Keep `negative` strict — Ideogram will happily stamp text and
borders otherwise.
