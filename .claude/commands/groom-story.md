You are auditing a story for internal consistency and canon alignment.

The story to audit is: $ARGUMENTS

If no story name is provided, list the available stories in `./stories/` and ask which one to audit.

Read these files:
- All files in `./stories/$ARGUMENTS/` (overview, npcs, encounters, locations, hooks)
- All canon files the story references (check frontmatter and wikilinks)
- `./campaigns/chance-encounters/planning.md` — to check if this story is active or upcoming

---

**Do not make any edits.** Report only.

Produce a report with four sections:

## Canon Conflicts
Where the story contradicts established canon — a location described differently, an NPC whose history doesn't match, a faction acting outside their defined character. Cite both files for each conflict.

## Internal Inconsistencies
Where the story contradicts itself — an NPC characterized one way in the overview and another in a scene, a timeline that doesn't add up, an encounter that assumes something the story never establishes.

## Unexploited Hooks
Hooks defined in the story's hooks/ folder that aren't connected to encounters or NPCs. Setup that has no payoff. NPCs introduced but never given a role in the encounters. Flag these as loose ends, not failures — they're opportunities.

## Missing Infrastructure
Things the story references that don't have files: a location mentioned in an encounter but not defined, a monster used in a fight but not in the monsters folder, an NPC named in a scene who has no NPC file.

---

End with: "X canon conflicts, Y internal inconsistencies, Z unexploited hooks, W missing files." Then ask what to dig into.
