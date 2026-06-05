You are auditing the magical items of the Chance Encounters campaign — reconciling what has a formal record against what the players actually hold and what the notes merely reference.

The DM's input is: $ARGUMENTS

By default the reference scan only covers sessions newer than the last audit (see Step 1). The DM can override this:
- `full` / `all` — re-scan every session from the beginning, ignore the audit log
- a session number or range (e.g. `17` or `16-19`) — scan only those
- a single item slug (e.g. `obsidian-cypher`) — audit just that record's completeness, skip the reference scan

---

## Step 0 — Read the contract and the records

Read before doing anything:
- `schema-reference.md` → the `item` section (the frontmatter contract: `rarity`, `attunement`, `item_type`; plus `title`/`type` common to all). Note the convention that the `current_holder` cross-reference is a **bare slug**.
- Every file in `./canon/items/` and `./campaigns/chance-encounters/items/`
- Every PC sheet in `./campaigns/chance-encounters/pcs/`
- `./campaigns/chance-encounters/audit-log.md` if it exists (the audit state — see Step 1)

## Step 1 — Determine scope from the audit log

The audit log lives at `./campaigns/chance-encounters/audit-log.md`. It holds one section per audit type; the relevant one is `## Item audit`, which records `Sessions reviewed through:` and the date of the last run.

- If the log or the `## Item audit` section is missing, this is a first run: scan **all** sessions, and create the log at the end (Step 6).
- Otherwise, scan only sessions numbered **higher** than `Sessions reviewed through:`.
- If the DM passed `full`/`all` or an explicit range/session, honor that instead and say so.

**The item-file completeness check (Step 2) always runs over every item file regardless of scope** — a record can be incomplete no matter when it was last looked at. The audit log only gates the *reference scan* (Step 3).

## Step 2 — Completeness check on existing item files

For every file in both item folders, flag a record as incomplete if:
- It is missing expected frontmatter: `rarity`, `attunement`, or `item_type`. (`current_holder` is expected on any item a PC or NPC is actually carrying; absence is a gap when the body says someone holds it.)
- `current_holder` disagrees with the PC sheets — the file names a holder the PC sheet doesn't mention, or a PC sheet claims an item whose file points elsewhere or has no holder.
- The body is empty, placeholder, or has mechanics marked `TBD`/`pending`/unresolved that a recent session has since resolved.
- The item changed hands, was destroyed, or was reforged in a session but the file wasn't updated.
- The file is an **orphan** — no PC sheet, session, ledger, or other file references it anymore. Flag for possible retirement; don't delete.

## Step 3 — Reference scan of session and player notes

Across the in-scope sessions (`./campaigns/chance-encounters/sessions/session-0XX.md`, skipping `*-prep.md`) and **always** the PC sheets, find references to magical items that have no file of their own.

Search for named or clearly-magical objects: anything with a proper-noun item name, plus keywords like *enchanted, attuned, +1/+2, command word, charges, rune, scroll, potion, amulet, ring, blade, glove, shard, bone, stone, sigil, relic, artifact, ward*. Use judgment — distinguish a real item the party gained or carries from set dressing, sold loot, or an object that stayed with an NPC. For each candidate, note: the item name, where it's referenced, who holds it (if anyone), and whether it reads like a keepsake, a plot key, or a mechanical item.

## Step 4 — Report, then fix gaps interactively

Present a single report in three buckets, mirroring the manual audit:
1. **Incomplete records** — existing files with gaps (from Step 2)
2. **Held but unrecorded** — items a PC carries with no file (from Step 3)
3. **Referenced, no record** — everything else worth a file, plus plot objects and orphans

Then resolve gaps **one at a time, interactively** — do not batch-edit. For each incomplete existing record, propose the specific frontmatter or body change and ask the DM to confirm, adjust, or skip before writing it.

**Canon items are edited deliberately.** If a gap is in `./canon/items/`, flag it and ask explicitly — never edit a canon file silently. New campaign items always go to `./campaigns/chance-encounters/items/`.

## Step 5 — Create new files through dialogue

Present the list of candidate new items (buckets 2 and 3) and ask **which ones the DM wants added** — not all candidates deserve a file. Plot keys and keepsakes may warrant a stub; sold or NPC-retained loot usually doesn't.

For each one the DM picks:
1. Create the file immediately at `./campaigns/chance-encounters/items/<slug>.md` with a unique kebab-case basename and valid frontmatter (mark unknown fields as `TBD` rather than inventing). Set `current_holder` to the bare slug of whoever carries it.
2. Then fill it out through a **brief dialogue** — ask the DM one or two focused questions about what it does, where it came from, and what it costs or threatens. Write the body from their answers in the voice of the existing item files: specific prose, no templated filler. **Do not invent mechanics** — if the DM doesn't define a property, leave it open (`*Properties: TBD at table.*`) rather than fabricate one.
3. Move to the next picked item.

## Step 6 — Update the audit log

After the DM is done, update `./campaigns/chance-encounters/audit-log.md` (creating it if absent). In the `## Item audit` section record:
- `Sessions reviewed through:` the highest session number scanned this run (only advance it — never lower it, even on a partial-range run; if a range left earlier sessions un-scanned, note that)
- `Last run:` today's date
- a one-line summary of what changed (records fixed, files created)

If the run used `full` or an explicit override, still update the pointer to the highest session actually scanned.

End with a short summary: X records fixed, Y files created, and the new `reviewed through` watermark.
