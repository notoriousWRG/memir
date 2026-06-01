---
title: "Chance Encounters — Prep Dashboard"
type: dashboard
party: chance-encounters
---

# Chance Encounters — Prep Dashboard

Live board for running and prepping sessions. Tables auto-update from frontmatter (Dataview).
Narrative state lives in [[overview]]; this is the operational layer.

> **Up next — Session 19:** Round 2 of the Storm Draugr fight on [[ariels-island]], picking up
> mid-combat from [[session-018]].

## Open threads for tonight

Pulled from [[session-018]] (carry these in your head):

- **Storm Draugr — Round 2.** 5 draugr on the board. Draugr A turned by [[coriac]] (may return); D & E at the waterline adjacent to Coriac — the pressure point.
- **The missing captain.** No body found. [[grimvald]]'s Suggestion on him before the grounding is unacknowledged and unresolved — powder keg.
- **[[ariel]]'s unfinished sentence** to [[coriac]] — still hanging.
- **[[casus]]'s [[ovaltine-potion]]** — island is saturated with Ariel's presence; using it here reacts to *her* specifically.
- **The missing anchor** — [[gareth]]'s problem; leaving the island needs a solution they don't have.
- **[[elara-venn]] and [[wrenn]]** on the [[white-gull-captain|White Gull]] — crew-loyalty thread, off-map.

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
