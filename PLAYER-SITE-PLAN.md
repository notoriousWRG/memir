# Player-facing site on GitHub Pages (Quartz) — milestone roadmap

## Context

Sessions of *Chance Encounters* feel disjointed between meetings. Players need a clean,
read-only, **DM-verified** record of the world they've shaped: the party's story, each
character's personal arc, notes on NPCs they've met, and the items they carry — with the DM
able to **slightly augment** what didn't land at the table, while keeping unearned material hidden.

Hard problem: player-known facts are woven through the **main prose** of every file, not isolated
in `## DM Note` blocks. So the site publishes a curated/flagged set, never the raw vault.

**Governing rule — the session-occurrence test:** if a fact wasn't revealed *at the table*, it is
hidden by default. "Augmentation" enriches what players *did* experience; it never reveals unearned
meaning (the obsidian cypher's true nature stays hidden).

We execute **one milestone at a time, testing at each checkpoint before moving on.**

## Decisions (locked with the DM)

- **Tool:** Quartz (Obsidian-native `[[wikilinks]]`, backlinks, graph, search → GH Pages).
- **Hosting:** public GH Pages (`https://notoriousWRG.github.io/memir/`); player layer is
  player-safe by construction.
- **Content model — hybrid:** party story + per-PC stories = hand-curated, **in-world** voice in a
  new `player/` tree; NPCs met + items carried = derived from existing files, **neutral** voice,
  hidden spans stripped.
- **Hidden notation:** Obsidian comments `%%secret%%` (native; Quartz strips; no config). Hidden in
  Obsidian reading view too — visible only in edit/source.
- **Publish selection:** Quartz `Plugin.ExplicitPublish()` — only `publish: true` notes render.
- **Player stories:** one page per PC. **Trigger:** GH Action on push to `party/**`.

## Target layout

```
campaigns/chance-encounters/player/   index.md, party-story.md, pcs/<pc>.md ×6  (curated, publish:true)
campaigns/chance-encounters/npcs|items/<slug>.md   existing files; slice gets publish:true + %%secrets%%
site/                                 Quartz toolchain (node_modules/public/cache gitignored)
.github/workflows/deploy-player-site.yml
PLAYER-SITE.md                        workflow + notation docs
PLAYER-SITE-PLAN.md                   this roadmap
```

---

## Milestone 0 — Persist the plan + repo prep  ✅
**Goal:** this roadmap lives in the repo so we can track progress.
- Save this document to repo root as `PLAYER-SITE-PLAN.md`.
- Add `site/node_modules`, `site/public`, `site/.quartz-cache` to `.gitignore`.

**Checkpoint:** `PLAYER-SITE-PLAN.md` renders in Obsidian; gitignore updated.

---

## Milestone 1 — Quartz scaffold + local preview
**Goal:** Quartz builds and serves the vault locally with **nothing leaked** by default.
- Scaffold Quartz v4 in `site/` (Node 20), self-contained.
- `quartz.config.ts`: `baseUrl: "notoriousWRG.github.io/memir"`,
  `pageTitle: "Chance Encounters — Party Records"`;
  `ignorePatterns: ["site", ".obsidian", ".claude", "session_audio", "**/node_modules"]`;
  plugins incl. `Plugin.ObsidianFlavoredMarkdown({ comments: true })` and the
  `Plugin.ExplicitPublish()` filter; graph + backlinks + search on.
- `quartz.layout.ts`: left explorer + search; right graph + backlinks + TOC; clean default theme.
- Build content from vault root: `npx quartz build -d .. --serve`.

**Checkpoint:** `http://localhost:8080` loads; with no `publish: true` notes yet, the site is
**empty of campaign content** — confirming ExplicitPublish gates everything by default.

---

## Milestone 2 — Notation convention + leak-safety proof
**Goal:** prove the two strip mechanisms work, and document the rules.
- `PLAYER-SITE.md`: how to preview/publish, the `%%...%%` convention, the `publish: true` flag, the
  session-occurrence rule, and the Pages "Source = GitHub Actions" one-time setting.
- Short "Player-site fields" note in `schema-reference.md` (`publish` flag — real need, documented).
- Add a throwaway test note with `publish: true` containing a `%%LEAK-CANARY%%` span and a
  wikilink to an unpublished DM file.

**Checkpoint:** rebuild; the test note appears, the `LEAK-CANARY` text is **absent** from rendered
HTML, the wikilink to the unpublished file does not expose its content. Then delete the test note.

---

## Milestone 3 — Curated narrative surfaces (in-world)
**Goal:** the player-authored heart of the site.
- `player/index.md` — landing/MOC: in-world framing + links to Party Story, PC roster, NPCs, Items.
- `player/party-story.md` — in-world chronicle from `journal.md` + player-safe spine of
  `overview.md`, filtered by the session-occurrence test.
- `player/pcs/<pc>.md` ×6 — one in-world page per PC, player-known only, cross-linking carried
  items / met NPCs. All `publish: true`.

**Checkpoint:** local site shows landing + party story + 6 PC pages; wikilinks/backlinks/graph work;
voice reads in-world; DM eyeballs for any unearned fact.

---

## Milestone 4 — NPC/item slice conversion (flag + strip)
**Goal:** prove the hybrid derive-from-existing path on a representative slice.
- **NPCs:** `marek`, `dessa`, `ollo`, `lady-grimhook` (hide true motive/next move), `ariel` (hard
  case — published view = storm presence + unfinished vision only).
- **Items:** `mjolnirs-fury`, `artcoths-gloves`, `forge-shard`.
- Per file: add `publish: true`; wrap every not-yet-revealed fact in `%%...%%`; neutralize
  DM-directive phrasing in the visible remainder; add any DM "augmentation" prose.

**Checkpoint:** rebuild; slice reachable; **leak-grep** of `site/public/` for known secrets
(`unfinished grief`, `King-slayer`, Grimhook's motive, `Nicholas`/`Coal`, cypher meaning) returns
**zero hits**. DM reviews each published note.

---

## Milestone 5 — GitHub Action + live Pages
**Goal:** auto-deploy on push to the party branch.
- `.github/workflows/deploy-player-site.yml`: trigger `push` to `party/**` + `workflow_dispatch`;
  checkout (full history) → Node 20 → `cd site && npm ci` → `npx quartz build -d ..` →
  upload-pages-artifact → `actions/deploy-pages`.
- Enable Pages "Source = GitHub Actions" (one-time, documented in `PLAYER-SITE.md`).
- Update/retire `ISSUE-player-facing-site.md`.

**Checkpoint:** push `party/chance`; Action builds + deploys; visit
`https://notoriousWRG.github.io/memir/`; repeat reachability + leak-grep against the **live** site.

---

## Future (not in this roadmap)
- Expand NPC/item coverage beyond the slice.
- Fold "update the player layer" into the `wrap-session` skill (DM-approved).
- Richer knownness taxonomy if binary shown/hidden proves too coarse.
- Out of scope: per-player access control (site is intentionally public + player-safe); any change
  to canon, the consequence ledger, or DM files beyond the slice conversion.
