---
title: "Schema Reference"
type: reference
---

# Frontmatter Schema Reference

The frontmatter contract for every entity in the vault. This was formerly enforced at
build time by Zod (`src/content/config.ts`); since the move to an Obsidian-first vault there
is no build-time validator, so this file is the source of truth. Templater templates in
`.obsidian/templates/` mirror these fields.

**Convention:** Frontmatter holds structured fields; the body holds prose. Cross-references
(`location`, `party`, `session`, `pcs_*`, `story`) are stored as **bare slugs**, not
wikilinks — Dataview resolves them with `link()` in dashboards. Body prose uses
`[[slug]]` / `[[slug|display]]` wikilinks.

Every entity except bare `index.md` pages carries a `type`. Add a field when its absence
hurts, not before.

## Entity types

`npc`, `location`, `item`, `monster`, `story`, `session`, `pc`, `ledger-entry`,
`god`, `race`, `faction`, `history-entry` (last four added during the canon import).

## Fields by type

Common to all: `title` (string, required), `type` (one of the above).

### npc
- `race` — string
- `role` — string
- `voice` — string (how they speak)
- `attitude` — one of `friendly | neutral | wary | hostile`
- `location` — slug of their home location

### location
First-class entity (BLeeM-influenced) — locations have turns.
- `tier` — integer 1 (hamlet) → 5 (capital / dungeon final chamber)
- `region` — string
- `voice` — string (the place's narrative voice)
- `escalation_triggers` — list of strings
- `active_clocks` — list of strings

### item
- `rarity` — one of `common | uncommon | rare | very rare | legendary | artifact`
- `attunement` — boolean
- `item_type` — string (weapon, wondrous, etc.)

### monster
- `cr` — number or string
- `monster_type` — string (undead, beast, fiend, etc.)
- `habitat` — string

### story
- `premise` — string
- `canon_hooks` — list of strings
- `status` — one of `draft | ready | retired`

### session
- `session_number` — integer or string
- `session_date` — ISO date string
- `story` — slug of parent story
- `party` — slug of campaign/party
- `pcs_present` — list of pc slugs

### pc
- `player` — string (real-world player name)
- `class` — string, e.g. "Rogue 5 / Wizard 2"
- `level` — integer, current character level
- `xp` — integer, total earned XP
- `pc_race` — string (kept separate from npc `race`)

### ledger-entry
Every field here is load-bearing for the creative-pain mechanic. Do not restructure without
explicit direction.
- `choice` — string
- `cost` — string
- `ripple` — string
- `session` — slug of the session this came from
- `pcs_involved` — list of pc slugs

### god
- `domains` — list of strings
- `allegiance` — one of `Aesir | Vanir | Antagonist | Neutral | Primordial`
- `symbol` — string

### race
- `lineage` — string (ancestral origin, e.g. "Ice Giant")
- `homebrew` — boolean (true if custom to Ældor)

### faction
- `faction_alignment` — string
- `faction_goal` — string

### history-entry
- `era` — string (which age this belongs to)
- `period` — string (rough descriptor)

## Player-site fields

These fields apply to any entity type published to the player site. They sit alongside the
type-specific fields above.

- `publish` — boolean. `true` = included in the Quartz build; absent or `false` = excluded.
  Only set this after applying the session-occurrence test and wrapping any hidden spans.

No other player-site fields are needed at this time. The `%%...%%` comment notation is
handled at the markup level, not via frontmatter.
