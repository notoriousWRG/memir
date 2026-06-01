You are closing out a session and updating the campaign record.

Arguments: `$ARGUMENTS` — session number, and optionally an audio file path separated by a space (e.g. `19 /path/to/recording.mp4`). Parse accordingly.

**Prerequisite:** Audio transcription requires `whisper` (`pip install openai-whisper`, needs `ffmpeg` for non-wav formats). If the audio path is provided but whisper isn't installed, say so, skip transcription, and continue notes-only.

Read these files before starting:
- `./campaigns/chance-encounters/planning.md` — especially the Raw Notes section
- `./campaigns/chance-encounters/sessions/session-<N>-prep.md` — the prep/run doc for this session (for scene rolloff in Step 5)
- The session record if it already exists: `./campaigns/chance-encounters/sessions/session-<N>.md`
- `./campaigns/chance-encounters/ledger/` — existing entries, for tone/format reference
- `./schema-reference.md` — frontmatter schemas for new entity stubs

Work through these steps in order. Pause for DM input at each step before moving to the next.

---

**Step 0 — Transcription** *(skip if no audio file provided)*

Run:
```
whisper "<audio-file>" --model medium --language English --output_format txt
```

Present a cleaned summary of the transcript — major beats, NPC interactions, decisions made, loot distributed. Do not dump the raw transcript. Ask the DM to flag anything wrong or missing before proceeding. This summary feeds every downstream step alongside the DM's written notes.

---

**Step 1 — Session record**

Draft `./campaigns/chance-encounters/sessions/session-<N>.md` using: transcript summary (if available) + DM's written notes + planning.md Raw Notes. Written notes confirm what mattered; transcript fills in detail.

Frontmatter schema:
```yaml
title: "Session <N> — <title>"
type: session
session_number: <N>
session_date: ""
story: ""
party: chance-encounters
pcs_present: []
```

Body: prose recap. Present the draft. Write only after DM confirms.

If the session file already exists, ask whether to update it or treat it as the source of truth and skip to Step 2.

---

**Step 2 — Ledger entries**

Identify significant choices from this session — moments with weight, a cost, a ripple forward. Propose each with fields: `choice`, `cost`, `ripple`, `session`, `pcs_involved`. Present all candidates at once. DM picks which to write and can edit fields. Write confirmed entries to `./campaigns/chance-encounters/ledger/`.

---

**Step 3 — New entity stubs**

From the transcript and notes, identify:
- **NPCs** newly named and interacted with (not already in `./campaigns/chance-encounters/npcs/`)
- **Items** distributed or found (not already in `./campaigns/chance-encounters/items/`)
- **Locations** newly visited that are significant enough to warrant a stub

For each, propose a frontmatter-only stub matching `schema-reference.md` with a blank body — prose is the DM's to write later. Present the full list at once; DM confirms which to create. Write confirmed stubs only. Use kebab-case basenames unique across the vault.

---

**Step 4 — XP suggestion**

Based on encounters resolved, roleplay beats, discoveries, and decisions from the session, suggest a per-player XP award. Break it down briefly: combat XP (monsters overcome) and roleplay/exploration award. Include 2–3 sentences of rationale. DM decides the final number. No file is written — this is advisory only.

---

**Step 5 — Planning doc update**

Two-part update to `./campaigns/chance-encounters/planning.md`. Present the full updated doc before writing anything. DM may edit before confirming.

**Part A — Roll off played scenes:**
Read `session-<N>-prep.md` to identify which scenes were played tonight. Distill them into a `## Established This Session` block and place it at the top of planning.md (or update the existing block if one is there). Format: 4–6 bullets, one sentence each — facts now locked in that future prep can't contradict. This block accumulates; prune oldest entries when they're no longer at contradiction risk.

**Part B — Update live state:**
- Scenes not reached: carry forward into Scene Stakes or Trigger Table as appropriate
- Active Clocks: tick or resolve based on what happened
- NPC Wants: update for NPCs whose situation changed
- Active Threads: mark resolved, evolve ongoing, add new threads
- Trigger Table: remove fired triggers, add new ones
- Open DM Questions: remove answered ones, add new ones that emerged

---

**Step 6 — DM Todos**

Compile a concrete action list for before next session:
- Entity stubs from Step 3 that need prose fleshed out
- Homebrew mechanics that came up but weren't resolved at the table
- Open questions that must be answered before next prep
- Any player follow-up needed

Write this as `### Before Next Session` in planning.md's Raw Notes (replace any prior instance). Present before writing.

---

**Step 7 — Flag canon/story updates**

List anything that might need to propagate upward: lore → canon, NPC behavior → NPC file, location detail → location file, story element improvised that should be recorded. Do not write these files. Give the DM the list and ask which to address now vs. later.

---

**Step 8 — Next session seed**

Add to planning.md Raw Notes: where we left off (one sentence), the most urgent active thread, and one open question to open from. This primes the next `/session-prep`.

---

When all steps are done: "Campaign record updated. Run `/session-prep` before next session."
