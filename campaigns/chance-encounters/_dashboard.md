---
title: "Chance Encounters — Prep Dashboard"
type: dashboard
party: chance-encounters
---

# Chance Encounters — Prep Dashboard

Live board for running and prepping sessions. Tables auto-update from frontmatter (Dataview).
Narrative state lives in [[overview]]; this is the operational layer.

> **Up next:** the inland expedition on [[ariels-island]] — the party moves into the interior at
> first light from Group A's camp, picking up from the end of [[session-018]]. See [[planning]] for the full prep.

## Open threads for tonight

The beach fight is resolved; the party pushes inland with [[ollo]] in tow. Carry these:

- **The interior.** Spar Field → the Hollowed Hull (Group B's last camp) → toward the Circled Zone where [[ariel]] is bound and [[edrin-vael]] keeps her.
- **The treeline captain.** Group A's old captain, sighted at the treeline — alive and watching, or the island's trick. (Decide: is he Edrin or distinct?)
- **The crew that left.** Some survivors walked inland weeks ago and never came back.
- **The surviving draugr** watch from offshore — present, not hostile.
- **[[dessa]]** gave patterns, not truth; **[[ollo]]** is eager and naive; **[[marek]]** is the open one.
- **[[ariel]]'s unfinished sentence** to [[coriac]] — still hanging.
- **The White Gull captain** still missing; [[grimvald]]'s Suggestion still unacknowledged — powder keg.
- **[[elara-venn]] and [[wrenn]]** left on the beached ship — crew-loyalty clock ticking.

See [[overview#Active Threads]] for the full standing thread list (Shalindra's pact, the Circle, Liriel's ring, the Pendant).

## Party

```dataview
TABLE WITHOUT ID
  link(file.link) AS PC,
  player AS Player,
  class_level AS Class,
  pc_race AS Race
FROM "campaigns/chance-encounters/pcs"
SORT file.name ASC
```

## NPC roster

```dataview
TABLE WITHOUT ID
  link(file.link) AS NPC,
  role AS Role,
  attitude AS Attitude,
  choice(location, link(location), "—") AS Location
FROM "campaigns/chance-encounters/npcs"
SORT file.name ASC
```

## Consequence ledger

```dataview
TABLE WITHOUT ID
  link(file.link) AS Entry,
  choice AS Choice,
  choice(session, link(session), "—") AS Session
FROM "campaigns/chance-encounters/ledger"
WHERE type = "ledger-entry"
SORT session ASC
```

## Sessions

```dataview
TABLE WITHOUT ID
  link(file.link) AS Session,
  session_number AS "#",
  session_date AS Date
FROM "campaigns/chance-encounters/sessions"
WHERE type = "session"
SORT session_number DESC
LIMIT 8
```

## Locations & items in play

```dataview
LIST
FROM "campaigns/chance-encounters/locations" OR "campaigns/chance-encounters/items"
SORT file.folder ASC, file.name ASC
```
