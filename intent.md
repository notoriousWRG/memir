# Memir: D&D Lore System — Intent

## Why this exists

Notion stopped serving the work. Rich app UIs encourage premature structure, and the cost of maintaining the schema started exceeding the value of the content. Meanwhile, Claude has become the primary creative partner for both software work and DM prep. The tools should match the workflow.

This is a long-term system for the homebrew world and its future campaigns, not a tool for the current one. It will be tested on a fresh story before any existing content gets migrated in. The aim is a clean, fluid, living repo of canon, stories, and campaigns — optimized for Claude as collaborator and the DM as the source of truth.

The bottom line being served is connection: with the world, with players, with the stories that emerge at the table. Everything else is plumbing.

## The model

Three layers, one-way dependencies.

**Canon** is what's true about the world. Pantheon, history, races, locations, recurring NPCs, custom mechanics. Mostly static. Edited deliberately.

**Stories** are playable adventures rooted somewhere in canon. Each has its own NPCs, encounters, hooks, monsters, locations. Reusable across campaigns and parties.

**Campaigns** are stories activated by a specific party. They hold sessions, party-level state, the consequence ledger, and any divergences from the underlying story or canon. The most mutable layer.

Dependencies flow downward: campaigns reference stories; stories reference canon. Divergence is local — a campaign-level override inherits from a canon entity but records its own facts. Canon stays clean until promoted manually. Promotion is a deliberate act, not an automatic merge, and shouldn't happen often.

## Data and tooling

Plain markdown with YAML frontmatter. Frontmatter holds structured fields; the body holds prose. The same file is the database row and the narrative entry.

The stack:

- **Astro + Starlight** for the rendered site. Typed content collections (Zod schemas) enforce rigor — a missing required field fails the build. Pagefind for client-side search. Clean nav, breadcrumbs, dark mode out of the box.
- **VS Code or Claude Code** for editing. No in-app edit mode.
- **Generated SQLite index** on each build, dumped from frontmatter. Enables real SQL queries mid-session: `SELECT name, voice FROM npcs WHERE location='Hollowmere'`. Claude can query it too.
- **Git** for history and labeled snapshots (e.g. "end of Campaign 1 canon state").

Repo shape:

```
canon/
  pantheon/, history/, races/, npcs/, locations/, items/, monsters/
stories/<story-name>/
  overview.md, npcs/, encounters/, locations/, hooks/
campaigns/<party-name>/
  overview.md, pcs/, sessions/, ledger/, overrides/, journal.md
src/content/config.ts   ← typed schemas
```

Overrides work like this: a file in `campaigns/<party>/overrides/<entity>.md` carries frontmatter pointing at the canon entity and records the changed facts. Two layers, one source of truth per layer.

## Design decisions that shape the schema

Two things bake into v1 because they're foundational, not features bolted on later.

**Environments are first-class entities.** Following the BLeeM influence, locations carry their own voice, tier, escalation triggers, and active clocks. Locations have turns. Hollowmere isn't a setting — it's a character. The schema reflects this.

**Consequence ledger is structured.** Each campaign carries a ledger of meaningful choices and their costs. Frontmatter on each entry: choice, cost, ripple, session, PCs involved. Creative-pain mechanics need a visible record to carry weight. Eventually surfaceable to players.

## How Claude fits

The repo is designed assuming Claude is the primary collaborator. Workflows to lean into as the system matures:

- **Session prep.** Claude reads the relevant story, the campaign state, the party comp, and produces encounter variants, NPC voice samples, and "things established earlier that matter tonight."
- **Continuity-keeper.** Before each session, Claude surfaces "established facts you might contradict tonight." Single biggest pain in long campaigns.
- **Session-to-canon diff proposal.** Post-session, Claude turns scrappy notes into a summary, then asks "what should this change canonically?" and proposes the diffs for review.
- **Post-campaign narrative.** Use git diff between snapshots to show players the before-and-after canon. The world they entered vs. the world they shaped.

These are conventions and prompts, not infrastructure. Package them as Claude Code skills or slash commands once their shape stabilizes. Premature now.

## Out of scope for v1

- Player-facing site. Same content, different Astro build, defer until a campaign needs it.
- Automated canon promotion. Manual `git mv` + edit is fine.
- Custom search or UI. Use what Starlight ships with.
- Schemas beyond NPC, location, item, monster, story, session, PC, ledger entry. Add fields when their absence hurts, not before.
- The current campaign's content. Migrate selectively once the system has proven out on a fresh story.

## First steps

1. Stand up the Astro + Starlight scaffold with content collection schemas. One sample of each entity type.
2. Bring in the canon notes from notion
3. Draft one small story end-to-end in the system — overview, three NPCs, a location with proper environment fields, two encounters. Catch what hurts.
4. Wire the SQLite dump step. Confirm it queries cleanly.
5. Run a one-shot session from that story. See what's missing or annoying mid-game.
6. Iterate from real friction, not imagined needs.


