---
title: "Vault Setup"
type: reference
---

# Vault Setup

Memir is an **Obsidian vault**. The repo root is the vault — there is no build step.

## Open it

1. Obsidian → **Open folder as vault** → select this repo's root directory.
2. Trust the vault when prompted (the committed `.obsidian/` config will load).

The graph view (left ribbon) shows the canon ↔ story ↔ campaign web. Start at [[Home]].
The prep board for the active campaign is [[_dashboard|Chance Encounters — Prep Dashboard]].

## Install these community plugins

Settings → Community plugins → Browse. The vault is pre-configured to enable them on install
(`.obsidian/community-plugins.json`):

| Plugin | Why |
|---|---|
| **Dataview** | Live queries over frontmatter — powers every dashboard table. Replaces the old SQLite index. |
| **Templater** | New entities from `.obsidian/templates/`. (The core Templates plugin also reads them.) |
| **Obsidian Git** | Auto-commit/sync; this vault is a git repo. Optional but recommended. |

Optional: **Breadcrumbs** (hierarchical canon→story→campaign nav), **Folder Notes**.

## Settings already applied (`.obsidian/app.json`)

- Use `[[Wikilinks]]`: **on** — matches existing content.
- New link format: **shortest path** — keeps links as bare slugs.
- Automatically update internal links on rename: **on**.
- Template folder: `.obsidian/templates`.

## Conventions

- **Unique kebab-case basenames.** Links resolve by name, so every note's basename must be unique.
- **Frontmatter** follows [[schema-reference]]. Cross-references (`location`, `party`, `session`,
  `pcs_*`, `story`) stay as **bare slugs**; Dataview turns them into links.
- **Prose in the body**, structured fields in frontmatter. Leave a section blank rather than fake it.
- Notes prefixed with `_` (e.g. `_dashboard`) are internal/meta boards, not lore entries.

## New entity

`Cmd/Ctrl-P` → *Templates: Insert template* (or Templater) into a fresh note named with the slug,
pick the entity type, fill the frontmatter. Templates live in `.obsidian/templates/`.

## Player-facing site

Deferred — tracked as a GitHub issue. The plan is to publish a player-safe subset
(journal + selected canon, **not** the ledger or DM secrets) to GitHub Pages, likely via Quartz.
