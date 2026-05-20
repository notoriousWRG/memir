# Memir — Claude Code Guide

A living lore system for homebrew D&D. The DM is the source of truth. Claude is the collaborator. Markdown is the database.

Read `intent.md` for the full origin story. This file covers working conventions and guardrails.

---

## The mental model

Three layers, one-way dependencies:

```
Canon → Stories → Campaigns
```

- **Canon** — immutable world facts (pantheon, history, races, locations, NPCs, items, monsters). Edit deliberately.
- **Stories** — reusable playable adventures rooted in canon. Have their own NPCs, encounters, locations, hooks.
- **Campaigns** — a story activated by a specific party. Holds sessions, party state, consequence ledger, overrides.

**Divergence is local.** A campaign-level override inherits from canon but records its own facts. Canon stays clean. Promotion (override → canon) is manual, explicit, and rare.

---

## Repo layout

```
canon/
  pantheon/, history/, races/, npcs/, locations/, items/, monsters/
stories/<story-name>/
  overview.md, npcs/, encounters/, locations/, hooks/
campaigns/<party-name>/
  overview.md, pcs/, sessions/, ledger/, overrides/, journal.md
src/
  content/config.ts     ← Zod schemas, one per entity type
```

Overrides: `campaigns/<party>/overrides/<entity>.md` — frontmatter points at the canon entity + records changed facts.

---

## Data format

Plain markdown with YAML frontmatter. Frontmatter = structured fields. Body = prose. The same file is the DB row and the narrative entry.

Add frontmatter fields when their absence hurts, not before. The schema list for v1 is: **npc, location, item, monster, story, session, pc, ledger-entry**. No others until real friction demands them.

### Location schema note

Locations are **first-class entities** (BLeeM-influenced). They carry: `voice`, `tier`, `escalation_triggers`, `active_clocks`. Hollowmere isn't a backdrop — it's a character. Enforce this in the Zod schema.

### Consequence ledger

Each campaign ledger entry carries: `choice`, `cost`, `ripple`, `session`, `pcs_involved`. This is the weight-bearing record for creative-pain mechanics. Keep it structured.

---

## Tech stack

- **Astro + Starlight** — rendered site. Content collections with Zod schemas. A missing required field fails the build; that's the point.
- **Pagefind** — client-side search. Ships with Starlight, no custom work needed.
- **SQLite index** — generated on each build from frontmatter. Lets you run `SELECT name, voice FROM npcs WHERE location='Hollowmere'` mid-session, and lets Claude do the same.
- **Git** — history + labeled snapshots (e.g. `end-campaign-1`).
- **VS Code / Claude Code** — only edit surfaces. No in-app edit mode.

---

## V1 scope

**In:**
- Astro + Starlight scaffold with typed schemas
- One sample entity of each type
- One complete small story (overview, 3 NPCs, 1 location with environment fields, 2 encounters)
- SQLite dump step wired into the build
- One one-shot session run from that story

**Out:**
- Player-facing site (same content, different Astro build — defer)
- Automated canon promotion (manual `git mv` + edit is fine)
- Custom search or UI (use Starlight's)
- Schemas beyond the v1 list above
- Migrating the current campaign's content (do this after the system proves out)

---

## Guardrails

**Don't add schemas ahead of need.** Add a field when its absence causes a real problem, not when you can imagine it might.

**Don't auto-promote overrides to canon.** That's a deliberate human act. Never write tooling that does it silently.

**Canon files are edited deliberately.** If a task touches canon, flag it — don't make silent changes.

**Prose matters.** The body of every file is narrative, not boilerplate. Don't fill it with placeholders or templated filler. Leave it blank rather than fake it.

**The consequence ledger is sacred.** Don't restructure or normalize it without explicit direction. Its format is the thing that makes the creative-pain mechanic land.

---

## Opportunities to lean into

These aren't tasks yet — they're where the system's value lives once the scaffold is up.

**Session prep prompt.** Claude reads story + campaign state + party comp → produces encounter variants, NPC voice samples, "things established earlier that matter tonight." Shape it as a slash command once its form stabilizes.

**Continuity-keeper.** Pre-session: Claude surfaces established facts that might get contradicted tonight. Single biggest pain point in long campaigns.

**Session-to-canon diff proposal.** Post-session: scrappy notes → structured summary → proposed canon diffs for human review.

**Post-campaign narrative.** `git diff end-campaign-0 end-campaign-1` → show players the world they entered vs. the world they shaped.

None of these need infrastructure yet. Note them when relevant, implement when asked.

---

## Working conventions

- Build errors are signals, not annoyances. If a Zod schema fails, fix the content, not the schema.
- When in doubt about canon, ask. Don't infer.
- Git commits at logical checkpoints (schema done, first story done, SQLite wired). Not after every file.
- The rendered site is the source of truth for readability. Build and check before calling a content task done.
