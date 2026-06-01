You are helping the DM create a new NPC for the Chance Encounters campaign.

The DM's input is: $ARGUMENTS

Read these files before generating anything:
- `src/content/config.ts` — the NPC Zod schema; the output must validate against it
- `./campaigns/chance-encounters/planning.md` — active threads; tie the NPC to one if it fits
- `./campaigns/chance-encounters/overview.md` — current party location and situation
- A sample of 3–4 existing NPC files from `./campaigns/chance-encounters/npcs/` — for voice and format reference
- Relevant canon NPC files if the new NPC has a canon connection

---

**Process:**

1. If the DM's input is vague or just a name, ask one focused clarifying question: what role does this NPC play (ally, obstacle, neutral, unknown)? Don't ask more than one question.

2. Generate the NPC file. Requirements:
   - Frontmatter must validate against the NPC schema in config.ts
   - Tie the NPC to the current campaign context — location, active threads, or known factions
   - If they conflict with or relate to an existing NPC, flag it
   - Voice must be distinct — don't write a generic tavern keeper
   - Body prose: specific, not templated. Leave it blank if you can't write something true to the character

3. Present the file for DM review before offering to write it. Say where you'd place it in the file system.

4. After DM approval, write the file to `./campaigns/chance-encounters/npcs/<slug>.md`.

5. Ask if the NPC should be added to the planning doc's NPC Whereabouts section.
