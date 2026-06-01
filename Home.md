---
title: Memir
description: Lore system for homebrew D&D.
type: home
---

# Memir

A living lore system for homebrew D&D. **Canon → Stories → Campaigns**, one-way dependencies.
Markdown is the database; the DM is the source of truth.

> Graph view shows the world web. Press the graph icon in the left ribbon.

## The three layers

- [[canon/index|Canon]] — immutable world facts: pantheon, history, races, locations, NPCs, items, monsters, factions.
- [[stories/index|Stories]] — reusable playable adventures rooted in canon.
- [[campaigns/index|Campaigns]] — a story activated by a party. Sessions, PCs, the consequence ledger, overrides.

## Active campaign

- [[campaigns/chance-encounters/overview|Chance Encounters — Overview]]
- **[[_dashboard|Chance Encounters — Prep Dashboard]]** ← session prep board

## Reference

- [[schema-reference|Frontmatter schema reference]]
- [[SETUP|Vault setup & plugins]]
- [[intent|Origin & intent]] · [[CLAUDE|Working conventions]] · [[dm-philosophy|DM philosophy]]

## Recently edited

```dataview
TABLE WITHOUT ID
  link(file.link) AS Note,
  dateformat(file.mtime, "MMM dd, HH:mm") AS Edited
FROM ""
WHERE file.name != "Home"
SORT file.mtime DESC
LIMIT 12
```
