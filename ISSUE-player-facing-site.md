# [Tracked] Player-facing site on GitHub Pages

> Not yet filed on GitHub — this repo has no remote configured. Once a remote exists, file this
> with: `gh issue create --title "Player-facing site on GitHub Pages" --body-file ISSUE-player-facing-site.md`
> (then delete this file).

## Goal

Publish a **read-only, player-safe** view of the vault to GitHub Pages so players can browse the
world they've shaped between sessions.

## Approach

Now that Astro is removed, the leading candidate is **[Quartz](https://quartz.jzhao.xyz/)** —
purpose-built to publish an Obsidian vault to GitHub Pages, with native support for `[[wikilinks]]`,
backlinks, and graph view. Alternative: **Obsidian Publish** (paid, zero-config).

## Critical constraint — publish a subset, not the whole vault

Players must **not** see DM-only material. Exclude:

- the consequence `ledger/` (creative-pain mechanic; DM-facing)
- `campaigns/*/planning.md`
- `_dashboard.md` and any `_`-prefixed meta notes
- DM-only NPC secrets and unrevealed canon

Publish (initially): the campaign `journal.md` + a hand-picked subset of canon.

## Open questions

- **Selection mechanism:** per-note `publish: true` frontmatter flag vs. an explicit allowlist
  folder/build config. (Quartz supports both an `publish` frontmatter flag and ignore patterns.)
- **Secrets within published notes:** some NPC/location notes mix player-known and DM-only prose.
  Need a convention (e.g. a `## DM notes` section stripped at publish, or split files).
- **Update cadence:** manual publish after each session vs. GitHub Action on push.

## Acceptance

- A GitHub Pages site renders a chosen subset with working wikilinks and graph.
- No excluded content (ledger, planning, dashboards, DM secrets) is reachable in the published output.
