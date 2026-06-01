---
title: Canon
description: What is true about the world. Edited deliberately.
---

Immutable world facts — pantheon, history, races, locations, recurring NPCs, items, and monsters. Edit deliberately. When in doubt, ask rather than infer.

## Browse by type

```dataview
TABLE WITHOUT ID
  link(file.link) AS Name,
  type AS Type
FROM "canon"
WHERE type
SORT type ASC, file.name ASC
```

## Counts

```dataview
TABLE WITHOUT ID rows.type AS Type, length(rows) AS Count
FROM "canon"
WHERE type
GROUP BY type
SORT length(rows) DESC
```
