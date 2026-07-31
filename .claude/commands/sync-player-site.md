You are syncing the player-facing site after a session of Chance Encounters.

Arguments: `$ARGUMENTS` — session number (e.g. `12`).

The player site lives at `campaigns/chance-encounters/player/`. A push to the party branch triggers the GitHub Actions deploy automatically — your job is to get the content right and make the commit.

---

## Read first

- `campaigns/chance-encounters/sessions/session-<N>.md` — the session record just written by wrap-session. This is your source of truth for what happened.
- `campaigns/chance-encounters/player/index.md` — the current party status page ("Where the Party Stands").
- `campaigns/chance-encounters/player/party-story.md` — the running chronicle.
- `campaigns/chance-encounters/player/npcs/` — list of existing player-visible NPC pages.
- `campaigns/chance-encounters/player/items/` — list of existing player-visible item pages.
- `campaigns/chance-encounters/player/assets/` — list of existing player-visible asset pages.
- `campaigns/chance-encounters/player/pcs/` — list of existing PC pages.

Also scan:
- `campaigns/chance-encounters/npcs/` — all campaign NPCs, to find new ones not yet in player/npcs/
- `campaigns/chance-encounters/items/` — all campaign items, to find new ones not yet in player/items/
- `campaigns/chance-encounters/assets/` — all campaign assets (ships, HQs, standing crews), to find new ones not yet in player/assets/

---

## Step 1 — Party status update

Draft a revised `player/index.md`. Three sections to update:

**"Latest Updates"** — a short dated bullet list (session number + date) covering: any arc closing/opening, new NPC/item/asset pages added this sync (as links), and any major relationship changes. This section fully replaces the previous session's list — it's a rolling "what's new since last time," not a running log. Keep it to 2-4 bullets.

**"Where the Party Stands"** — one tight paragraph, present tense. Where are they physically, what's in motion right now, who's with them, any immediate stakes. Do not recap the arc — that belongs in party-story. This is the state of play *right now* as of the end of this session.

**"The Story So Far"** — one sentence pointing at [[party-story]], plus a *Most recently:* line: one sentence, what just happened this session. Replace the previous *Most recently:* line only.

Show the full revised file. Do not write until the DM confirms.

---

## Step 2 — Chronicle update

Draft an addition to `player/party-story.md`. Add a new paragraph or extend the current arc section to cover what happened this session. Match the existing voice: past tense, tight, consequential, no mechanical language. Two to four sentences unless the session had major arc-turning events. Use `[[slug]]` wikilinks for any NPCs, items, or locations already in the player site.

If a new arc is starting (the DM will know), start a new `---` section with a new `## Arc N — Name` header.

Show the proposed addition. Do not write until the DM confirms.

---

## Step 3 — New NPC pages

Compare `campaigns/chance-encounters/npcs/` against `campaigns/chance-encounters/player/npcs/`. List NPCs that:
- Appeared or were meaningfully referenced this session, AND
- Do not yet have a player-facing page

For each candidate, show the DM the campaign NPC file and ask: **player-visible? yes / no / not yet.** Present all candidates at once — DM decides in one pass.

For confirmed additions, draft a player-facing version:
- Strip anything that's DM-only (secret motivations, hidden allegiances, information the players don't have)
- Keep what the party has observed, heard, or could reasonably infer
- Frontmatter: `title`, `type: npc`, `role`, `attitude`, `publish: true`
- Body: player-observable facts only. Prose, not bullet points. Match the voice of existing player NPC files.

Filenames must match the campaign NPC basename exactly so `[[slug]]` wikilinks resolve.

Show all drafts together. Write only after DM confirms each.

---

## Step 4 — New item pages

Same process for items. Compare `campaigns/chance-encounters/items/` against `campaigns/chance-encounters/player/items/`. Items that changed hands, were found, or were identified this session and lack a player-facing page are candidates.

For confirmed additions, draft a player-facing version:
- Frontmatter: `title`, `type: item`, `rarity`, `attunement`, `item_type`, `current_holder`, `publish: true`
- Body: what the party knows about it — origin, properties, flavour. If unidentified, say so and withhold mechanics. Match the voice of existing player item files.

Show all drafts. Write only after DM confirms.

---

## Step 5 — New asset pages

Same process for assets (ships, HQs, standing crews — `type: asset`). Compare
`campaigns/chance-encounters/assets/` against `campaigns/chance-encounters/player/assets/`.
An asset that's new, changed status, or whose mechanic came into play this session is a
candidate — ask the DM **player-visible? yes / no / not yet** the same as NPCs/items.

For confirmed additions, draft a player-facing version:
- Frontmatter: `title`, `type: asset`, `asset_type`, `status`, `publish: true`. Omit `mechanic`
  and `crew` from the player-facing frontmatter if the DM wants the crunchy rule text kept
  DM-side — ask. If included, keep the mechanic description player-readable, not table jargon.
- Body: what the party would actually know about it — how they use it, what it's done for
  them, any flavor. Match the voice of existing player NPC/item files.

Filenames must match the campaign asset basename exactly so `[[slug]]` wikilinks resolve.

Show all drafts. Write only after DM confirms.

---

## Step 6 — PC file updates

Review each PC in `player/pcs/` against this session's record. Flag any PC whose file needs updating because:
- Their carried items changed (gained or lost something)
- A significant personal thread advanced or resolved
- A relationship was meaningfully established or changed
- `xp`/`level` changed — diff against `campaigns/chance-encounters/pcs/<pc>.md` (the source of truth, updated in wrap-session Step 4) and mirror any difference into `player/pcs/<pc>.md`'s frontmatter. This applies to every present PC every session, not just ones with a narrative update.

For each flagged PC, propose the specific edit (new paragraph, updated Carries line, frontmatter `xp`/`level` bump, etc.) — not a full rewrite. Show diffs, not full files. Write only after DM confirms.

---

## Step 7 — Commit and push

Once all content is confirmed and written:

1. Show the list of files changed.
2. Draft a commit message in the format:
   ```
   feat(player-site): session <N> sync — <one-line summary of what was added/updated>
   ```
3. Run:
   ```
   git add campaigns/chance-encounters/player/
   git commit -m "<message>"
   git push origin HEAD
   ```
4. Report: "Pushed. GitHub Actions will deploy in ~1–2 minutes."

Do not push until the DM confirms the file list and commit message.
