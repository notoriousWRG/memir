You are writing an issue of **The Session Skald**: a Skimm-style newsletter about Chance Encounters for Sarah, the DM's wife, who doesn't play. Three of the party are her family.

Arguments: `$ARGUMENTS`. Either:
- a session number (e.g. `24`) for a **session edition**, normally run after `/wrap-session` and `/sync-player-site`, or
- `recap <N>` (e.g. `recap 23`) for the one-off **recap edition** covering sessions 1–N.

Output: `campaigns/chance-encounters/skald/skald-<NNN>.md` (session, zero-padded) or `campaigns/chance-encounters/skald/skald-recap-001-<NNN>.md`.

---

## Read first

- `skald-style.md` (repo root): voice, behind-the-screen rules, family mapping, and the section skeleton for both editions. **Follow it exactly.** Its frontmatter is the settings.
- The previous issue in `campaigns/chance-encounters/skald/`, if one exists: for the last `quiz_answer`, running jokes, and to avoid repeating bits.

**Session edition:**
- `campaigns/chance-encounters/sessions/session-<NNN>.md`: what happened. The source of truth.
- `campaigns/chance-encounters/player/index.md` and the latest section of `player/party-story.md`: the player-safe framing of the same events.
- `session_audio/session-<N>-transcript.md`, if present: for table moments (Step 2).
- `campaigns/chance-encounters/ledger/` entries with `session: <N>`: the choices that cost something; good lead-story material.
- `campaigns/chance-encounters/sessions/art/` or the session's `art/` folder: images that could illustrate the issue.
- **Behind-the-screen sources:** `sessions/session-<NNN>-prep.md` (what was planned vs. what happened), `planning.md` (clocks, threads, NPC wants), and the DM files for NPCs/PCs/items/canon that appeared this session.

**Recap edition:**
- `campaigns/chance-encounters/player/party-story.md`: the backbone. Already player-safe and organized by arc.
- `campaigns/chance-encounters/player/pcs/`: for Meet the Party.
- `campaigns/chance-encounters/sessions/session-001.md` … `session-<NNN>.md`: skim for greatest-hits moments the chronicle compressed away.
- `campaigns/chance-encounters/ledger/`: the big choices.
- **Behind-the-screen sources:** `campaigns/chance-encounters/pcs/` (secret threads the players don't know), `planning.md` (active threads and clocks), key NPC files, and `canon/` where it explains something the party ran into.

---

## Step 1: Story budget

Before writing anything, propose the issue's content as a short list:

- **Lead story**: the one event the issue is built around, plus its headline and kicker.
- **Second story** (session edition) or the **arc list** with proposed headlines (recap).
- **News in N**: the smaller beats, one line each.
- **Family Watch / Meet the Party**: one line per family PC on what they'll be credited with.
- **Behind the Screen**: 3–6 candidate 🤫 items (session) or 6–10 (recap): dramatic irony, prep vs. reality, lore under a scene, hints of what's coming. One line each, with the source file. The DM picks which go in; some secrets stay his.
- **Calendar**: next session date (ask if you don't know it) and in-world deadlines.

Tag every item that the party doesn't know with 🤫, so the DM can see at a glance what's table knowledge and what isn't.

Present the budget. DM cuts, adds, and confirms before Step 2.

---

## Step 2: Table moments

*(Skip if there's no transcript. The recap edition skips this unless the DM supplies quotes.)*

Scan the transcript for 6–10 candidate moments:
- Out-of-character lines that got (or deserved) a laugh
- In-character lines that landed: threats, one-liners, declarations
- Running bits (Bramwell, Gareth eating the canapés)
- Moments a family PC's player will recognise as theirs

For each, show the timestamp, speaker label, the exact transcript text, and a cleaned version if needed. Flag anything that may be a Whisper garble. **The DM confirms every quote word for word**: a misquote in a family newsletter is worse than no quote.

DM picks one as **Quote of the Night** and which others feed Quick Hits.

---

## Step 3: Draft

Write the full issue following the matching skeleton in `skald-style.md`:
- Frontmatter: `title`, `type: skald`, `edition`, `sessions`, `issue_date`, `subject_line`, `quiz_answer`.
- Hit the word budget from `skald-style.md` frontmatter. Under is fine; padding is not.
- Every section must be earned. If the session had no loot, there's no loot item; if a family PC was absent, Family Watch says so in one line.
- The "Last issue's answer" line comes from the previous issue's `quiz_answer`. Omit it for the first issue.
- Wikilinks: none. This is read outside Obsidian. Plain text names.

Present the full draft. DM edits. Write only after confirmation.

---

## Step 4: 🤫 check

Before writing the file, list every DM-side fact in the draft, and confirm each one is (a) marked 🤫 and (b) one the DM picked in Step 1. Catch any that slipped into the play-by-play unmarked, as if the party knew it. DM signs off.

---

## Step 5: Write and render

1. Write the markdown to `campaigns/chance-encounters/skald/`.
2. Render the email HTML: `python render-skald.py campaigns/chance-encounters/skald/skald-<NNN>.md` (writes `skald-<NNN>.html` next to it; inline CSS only, so it survives pasting into an email). The renderer only understands the markdown shapes in the `skald-style.md` skeletons — stick to them. Avoid very new emoji (🪶, 🐦‍⬛): they render as empty boxes in many mail clients.
3. Tell the DM where both files are and that the HTML can be opened in a browser and copied into an email.

Do not send anything. Delivery is the DM's.

---

## Step 6: Commit

Draft a commit message:
```
feat(skald): session <N> issue — <subject_line>
```
(or `feat(skald): recap issue, sessions 1–<N>`). Show it with the file list. Commit only after the DM confirms. Don't push unless asked.

---

When done: "Skald issue ready. Opening the HTML in a browser is the readability check."
