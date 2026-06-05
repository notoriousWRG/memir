You are building the runnable session document for the next session of Chance Encounters.

This is the fusion the DM asked for: the spine and at-the-table support of a published adventure chapter (*Dragons of Stormwreck Isle* is the model — keyed scenes, short read-aloud openers, monster blocks, things to find, a clear "happy path"), loaded with the creative-tension mechanics this world runs on (loaded scenes, clocks, NPC wants, trigger tables, creative pain). The DM is not an improv master and has limited headspace. Give a path to follow and pre-load every reaction — *and* leave the seams open so play can diverge without breaking. Support without rails.

---

## Read first

- `dm-philosophy.md` — the creative principles. Non-negotiable framing for everything below.
- `CLAUDE.md` — repo conventions, the Canon → Stories → Campaigns model, the theme.
- `campaigns/chance-encounters/planning.md` — the living state: clocks, NPC wants, trigger table, active threads, and the "Next Session" seed in Raw Notes. This is what's actually loaded right now.
- `campaigns/chance-encounters/overview.md` — party roster and current campaign state.
- All PC files in `campaigns/chance-encounters/pcs/` — for character-specific threads.
- The location file(s) for where the session opens and is likely to go (e.g. `campaigns/chance-encounters/locations/ariels-island.md`). These already key sub-locations and carry `voice` / `escalation_triggers` / `active_clocks` — build scenes on top of them, don't reinvent them.

Do not read the full session history. The planning doc and the relevant location files are the current state — trust them. Pull other entity files (NPCs, monsters, items) on demand, only when a scene actually needs one.

---

## Theme guardrails (always on)

- **The world is Norse-flavored** — Aesir/Vanir pantheon, draugr / jotunborn / valkyrborn / fenirun, a cold-salt-storm aesthetic. **Default to Norse skins on monsters.** Reskin any standard stat block in this idiom (a zombie is a draugr; a fire elemental is a surtur-touched ember) and note what it's reskinned from so the DM can find the numbers fast.
- **Homebrew is welcome.** Custom mechanics tied to the world's forces — storm, memory, binding, the forge — are encouraged, not avoided. Flag each as homebrew and give it one clean, table-ready rule the DM can read aloud and adjudicate without prep.
- **Keep the cast tight.** The DM cannot run 100 NPCs. Cap the night at the NPCs already in play plus at most one or two new ones, and only if a scene genuinely needs them. Reuse before you invent.

---

## Establish direction first

Before drafting, pin down the night's intent:

1. Check the planning doc's "Next Session" seed and Active Threads for the obvious spine.
2. If a **story plan** is in use — the story file the campaign points to (its `story:` slug under `stories/`), or one the DM names — read it for the intended arc and beats, and build toward them. The story plan is the source of *direction*; the planning doc is the source of *current state*. Reconcile them: if the story plan and the live state disagree, follow the live state and flag the drift.
3. If neither gives a clear spine, ask the DM a short, deliberate set of questions — **no more than three**, high-leverage only:
   - Where does the party end up tonight (the destination scene)?
   - What's the one set-piece you want to land (a fight, a reveal, a choice)?
   - What must be true by the end (what resolves or advances)?

   Three questions, then build. Don't interrogate — the DM has limited headspace.

---

## Build the session document

Produce one runnable doc, written to `campaigns/chance-encounters/sessions/session-<N>-prep.md` (where `<N>` is the next session number). Format for scanning at the table, not for reading. Stream prose and full stat blocks live in linked sub-docs — this doc is the **spine plus the loaded reactions**. Link out with `[[slug]]` wikilinks so it stays streamlined.

Frontmatter: `type: session`, `session_number: <N>`, `story:` (the story-plan slug if one is in use), `party: chance-encounters`, `pcs_present:` (the roster), and a one-line note that this is a prep/run doc, not the post-session record.

Then these sections:

**1 — The Charge.** One tight present-tense paragraph: what is already in motion when the session opens. No backstory. Then a single line — *If they do nothing:* — the honest answer, decided now.

**2 — The Happy Path.** The suggested spine as 3–5 numbered beats, one line each, each naming the keyed scene it maps to. Open with: *"A path, not the only one — the scaffold to fall back on when the table goes quiet. The scenes below stand on their own; players can leave the path and the prep still holds."* This is the rail the DM asked for — present it as a safety net, never as the required route.

**3 — Clocks Tonight.** Pull every active clock from the planning doc. For each: name, current stage, what advances it tonight, max outcome. Flag any clock at stage 2+ — it's close to firing.

**4 — The Cast Tonight.** A tight table (cap ~5 NPCs), only those likely to appear: `NPC ([[link]]) | Want tonight | Fear | Tell`. One line each. Voices must be Norse-true and distinct. If the planning doc is sparse on a want, fill it and flag it — underprepared NPC wants are the most common source of flat scenes.

**5 — Scenes.** The heart of the doc — the keyed locations, one block each, in likely order. For each scene:
   - `### Scene N — Name` followed by the `[[location-link]]`.
   - **Read-aloud:** 2–3 sentences, sensory, present tense — the digital equivalent of boxed text. Evocative, not a data dump.
   - **Loaded:** who wants what here, what's ticking, and what the *place* wants (environment-as-character — use the location's `voice` and `escalation_triggers`).
   - **Dig in:** 2–4 concrete things to find or investigate — discoveries, clues, what a closer look reveals. This is the exploration lean; make it reward curiosity.
   - **If it comes to a fight:** linked monster(s), a one-line tactic, and the Norse skin / reskinned-from note. Omit if combat is unlikely here.
   - **Triggers:** the scene-specific if/then lines. Honest and consequence-forward.
   - **Leads to:** where this scene opens onto the next (ties back to the happy path, or names the branch).

**6 — Encounter Bank.** Monsters likely tonight, each linked to its file. Include a usable stat line for any fight that's probable (don't make the DM derive it mid-session) and the reskinned-from note. If combat is genuinely unlikely tonight, say so rather than padding.

**7 — Things to Find.** Items, loot, and lore in reach tonight, linked to their item docs. State what each does — or *"mechanics TBD — decide before use"* if it's unresolved homebrew (see section 9).

**8 — Don't Contradict.** A short continuity list: established fact → where it was set → what tonight could step on. Surface the facts most at risk given the planned scenes.

**9 — Decide Before Play.** The open questions that can't be improvised cleanly at the table — NPC wants, homebrew item mechanics, who a figure actually is. Pull from the planning doc's Open DM Questions plus anything this prep surfaces. Flag the ones that *must* be settled before the session opens.

**10 — Ending Conditions.** What a satisfying stopping point looks like, the likely hand-off, and a one-line seed for the next prep. Mirror "Ending This Chapter" — resolution conditions, not a forced outcome.

---

## Linked sub-docs

To keep the session doc streamlined, full detail lives in entity files, not inline.

- **Reuse first.** If a monster, location, NPC, or item already has a file, link to it and don't duplicate.
- **When a scene needs something new,** create a stub that matches `schema-reference.md` and the prose voice of the existing files in that folder (`monsters/`, `locations/`, `npcs/`, `items/`). Norse skin on monsters by default. Keep basenames unique kebab-case so `[[slug]]` links resolve.
- **Never write a stub without DM confirmation.** Present the list of new files you'd create and what each holds, and let the DM approve, cut, or merge before anything is written.

---

## Process

1. Establish direction (story plan / planning seed / three questions).
2. Identify which sub-docs already exist and which the night needs new. Present that list.
3. Present the full session-doc draft for review. Write nothing yet.
4. On approval, write `session-<N>-prep.md` and the confirmed stubs.
5. Offer to sync the planning doc: "Want me to update planning.md's clocks / wants / triggers to match this prep, so `/run-session` reads the same state?" Update only on confirmation — and never restructure the consequence ledger.

When the doc is written: "Prep doc ready. Run `/run-session` when you sit down — it reads planning.md as the live state at the table, and this doc is your chapter to run from."
