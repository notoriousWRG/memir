# Player Site — Workflow & Notation

The player-facing site lives at `https://notoriousWRG.github.io/memir/` and is built from
this vault by Quartz. Only notes explicitly marked `publish: true` are included. Everything
else — all DM notes, session prep, planning, and the main campaign files — is excluded by
default.

## Local preview

```bash
cd site
npx quartz build -d ../campaigns/chance-encounters/player --serve
```

Then open `http://localhost:8080/memir/`. The `/memir` prefix comes from the `baseUrl` in
`quartz.config.ts` — the root URL will 404; the site lives one level down.

The build reads from the player folder only — DM files are outside the build root entirely.

## Publish gate — `publish: true`

Add `publish: true` to a note's frontmatter to include it on the site. No flag = excluded.

```yaml
---
title: "Dessa Mirebrook"
type: npc
publish: true
---
```

The `player/` tree, the NPC/item slice, and any future additions all need this flag. When
in doubt, leave it off.

## Hiding secrets — `%%...%%`

Wrap any text that shouldn't reach players in Obsidian comment syntax:

```
The merchant's real name is %%Nicholas Coal, wanted in three kingdoms%%, known to the party as Barnaby.
```

In Obsidian's reading view and in the Quartz-built site, the `%%...%%` span is invisible.
It is only visible in edit/source mode. Use this to keep a single canonical file rather
than splitting into player/DM versions.

**Nesting is not supported.** Don't put comments inside comments.

## Session-occurrence rule

A fact belongs in the visible text only if it was revealed at the table. "Revealed at the
table" means: players witnessed it, learned it through play, or the DM told them directly.

Augmentation is allowed — enriching the texture of what players *did* experience (a
description, a voice note, an emotional beat). Augmentation never plants new lore that
players haven't earned.

When in doubt, hide it.

## One-time GitHub Pages setup

Before the GitHub Action can deploy, enable Pages in the repo settings:

1. Go to **Settings → Pages**
2. Under **Source**, select **GitHub Actions** (not a branch)
3. Save

This only needs to be done once. The workflow (`deploy-player-site.yml`) handles the rest.
