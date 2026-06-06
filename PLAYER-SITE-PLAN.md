# Player-facing site — round 2 roadmap (restyle, landing, level tracking)

## Context

The Quartz player site is live (`https://notoriousWRG.github.io/memir/`) but the experience is
busy and un-fantasy. Three problems to fix:

1. **Cluttered shell.** The graph view is the de-facto entry surface, the left sidebar exposes the
   raw 4-level folder path (`campaigns → chance-encounters → player → pcs`), and the default theme
   reads generic. Players want a clean, themed, player-centered front door.
2. **No level visibility.** There's no at-a-glance sense of where each character stands.
3. **Leveling isn't data.** DM notes track level only as a freeform `class` string
   (`"Wizard 6–7"`) plus a hand-kept table in `overview.md` — nothing structured to drive a visual.

We execute **one milestone at a time, verifying at each checkpoint before moving on.**

## Decisions (locked with the DM)

- **Leveling display:** XP + level with **progress bars** (not milestone-only).
- **Palette:** **Storm & Bronze** — storm-slate background, sea-foam text, tide-green links,
  weathered-bronze accent; **Cinzel** display serif for headers, Source Sans Pro body.
- **Sidebar:** keep a **file-tree explorer** but make it shallow + tidy (not a hand-curated nav).
- **Constraint — no Dataview on the site.** Quartz does **not** run Dataview; the DM
  `_dashboard.md` party table can't be reused. The player level visual must be a small **custom
  Quartz component** reading PC frontmatter.
- **Publish gating unchanged.** `Plugin.ExplicitPublish()` still requires `publish: true`; the
  session-occurrence rule and `%%secret%%` stripping still govern player content.

## Baseline (shipped, M0–M5)

Quartz v4 scaffold in `site/`, explicit-publish gating, `%%secret%%` leak-proofing, the curated
`campaigns/chance-encounters/player/` tree (index, party-story, 6 PC pages), an NPC/item slice
pattern, and the `deploy-player-site.yml` GH Action on `party/**`. This roadmap builds on that.

## Data needed from you (blocks M6 + M9)

Current **level** and **total XP** per PC. Levels inferable from `overview.md` if you don't
override (Casus 6, Grimvald 6, Coriac 7, Artcoth 7, Shah Doh 7, Gareth 7); **XP unknown — please
provide**, or say "seed at each level's threshold floor" and adjust later.

---

## Milestone 6 — DM-side XP/Level as structured data
**Goal:** leveling becomes real frontmatter, visible in the DM dashboard. (Obsidian-only; no site build.)
- `schema-reference.md` (pc section): add `level: integer` and `xp: integer` to the contract; keep
  `class` for the human-readable multiclass string.
- `.obsidian/templates/pc.md`: add `level:` and `xp:` lines.
- `campaigns/chance-encounters/pcs/{artcoth,casus,coriac,gareth,grimvald,shah-doh}.md`: add
  `level:` + `xp:` to frontmatter (values from "Data needed from you").
- `_dashboard.md` party Dataview query: add `level AS Level`, `xp AS XP` columns.
- `overview.md` Party Roster table: add an XP column so canon prose matches the data.

**Checkpoint:** in Obsidian, all 6 PCs carry `level`/`xp`; the `_dashboard.md` party table renders
the new columns with correct values; `overview.md` table matches. No site changes yet.

---

## Milestone 7 — Storm & Bronze theme
**Goal:** the site reads as a fantasy artifact, independent of any layout/content change.
- `site/quartz.config.ts` `theme.colors`: Storm & Bronze for darkMode (primary) — `light:#1c2530`,
  sea-foam text (`darkgray:#cdd6dd`/`dark:#e6ebef`), `secondary:#6fb3a8` (tide green),
  `tertiary:#c08a4e` (bronze), `lightgray:#2c3744`, `gray:#5a6b78`,
  `highlight:rgba(111,179,168,0.12)`, `textHighlight:#c08a4e55`; a parchment-leaning lightMode
  companion so the toggle stays intentional.
- `site/quartz.config.ts` `theme.typography`: `header:"Cinzel"`, keep `body:"Source Sans Pro"`,
  `code:"IBM Plex Mono"` (loads via existing `fontOrigin:"googleFonts"`).
- `site/quartz/styles/custom.scss` (currently empty): fantasy layer via theme CSS vars — Cinzel
  heading treatment + bronze underline rule, link/accent tuning, blockquote-as-scroll, subtle
  content border/shadow.

**Checkpoint:** `cd site && npx quartz build -d .. --serve`; toggle dark/light — Storm & Bronze
colors and Cinzel headers apply; links tide-green, accents bronze; nothing else changed.

---

## Milestone 8 — Sidebar cleanup + shallow tree
**Goal:** kill the graph-as-entry clutter and the deep folder dropdowns.
- `site/quartz.layout.ts`: remove `Component.Graph()` and `Component.Backlinks()` from the right
  sidebar; keep `DesktopOnly(TableOfContents())`. Drop `ReaderMode()` from the left Flex row.
- `Explorer()` options: `title:"Party Records"`, `folderDefaultState:"open"`, `mapFn`/`sortFn` to
  relabel folders (e.g. `pcs` → "The Party") and order entries.
- **Shallow the tree by changing the build content root to the player folder** (removes the
  `campaigns/chance-encounters/player` prefix chain and eliminates DM/player basename collisions,
  retiring the full-path-wikilink workaround inside player content):
  - `.github/workflows/deploy-player-site.yml` build step →
    `npx quartz build -d ../campaigns/chance-encounters/player`.
  - `PLAYER-SITE.md`: update the documented local-preview command to the same `-d` path.
  - Rewrite player-internal wikilinks root-relative (e.g. index "The Party" list →
    `[[pcs/artcoth|Artcoth]]`); bare links to unpublished canon are unaffected.
  - `campaigns/chance-encounters/player/index.md` becomes the site root (`/`).

**Checkpoint:** rebuild with the new `-d` path; sidebar tree is shallow (no campaign prefix chain),
folders auto-open with friendly labels; Graph/Backlinks/ReaderMode gone; all internal links resolve;
leak check still clean (DM files now outside the build root entirely).

---

## Milestone 9 — Party level visual (custom component)
**Goal:** the at-a-glance "where everyone stands" centerpiece. Depends on M6 data + M8 build root.
- `campaigns/chance-encounters/player/pcs/*.md`: add `level:` + `xp:` (player-safe mechanical
  facts mirroring M6 values).
- New `site/quartz/components/PartyRoster.tsx`: reads `allFiles`, filters `type==="pc"` under
  `pcs/`; per PC renders name (link), `class`, a **level badge**, and an **XP progress bar**
  computed against embedded 5e thresholds (1:0,2:300,3:900,4:2700,5:6500,6:14000,7:23000,8:34000,
  9:48000,10:64000,…20:355000); progress `(xp−t[level])/(t[level+1]−t[level])`. Inline `.css` like
  `TagList.tsx`, richer styling in `custom.scss`.
- Register in `site/quartz/components/index.ts` (mirror `TagList`).
- `site/quartz.layout.ts` `beforeBody`: render via
  `ConditionalRender({ component: PartyRoster(), condition: (p)=>p.fileData.slug==="index" })`.

**Checkpoint:** rebuild; landing page shows the roster with correct level badges and XP bars;
spot-check one PC's bar against the threshold math; component appears only on the landing page.

---

## Milestone 10 — Player-centered landing page
**Goal:** replace the graph entry experience with a real front door. Depends on M8 + M9.
- `campaigns/chance-encounters/player/index.md` (now site root) restructured:
  hero tagline → *(PartyRoster injects above body)* → **Where the Party Stands** (player-safe
  snapshot from `overview.md` "Current State") → **The Story So Far** (`[[party-story]]` + one-line
  recent hook) → **People They've Met** / **What They Carry** (existing stubs or wired slices).

**Checkpoint:** open the site root — it is the front door (no graph), roster + status + story read
cleanly, voice is in-world; leak-grep of `site/public/` for known secrets returns zero hits; DM
eyeballs for any unearned fact.

---

## Future (not in this roadmap)
- Per-session XP awards captured by `wrap-session` so level data updates itself.
- Expand NPC/item player coverage beyond the current slice.
- Out of scope: per-player access control (site is intentionally public + player-safe); changes to
  canon, the consequence ledger, or DM files beyond what M6/M9 require.
