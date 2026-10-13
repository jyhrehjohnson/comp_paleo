# Business Rules — Hominin Character State Database
**Author:** Jyhreh Johnson
**Date:** 10/12/2026

## 4a — Rule inventory

| #  | Rule                                                                                      | Enforceable in SQL? | Constraint type     | SQL expression or note                                                                            |
|----|-------------------------------------------------------------------------------------------|---------------------|---------------------|---------------------------------------------------------------------------------------------------|
| 1  | A specimen must have a catalog number before it can be entered                            | Yes                 | NOT NULL + CHECK    | `catalog_number TEXT NOT NULL CHECK (length(trim(catalog_number)) > 0)`                           |
| 2  | No two specimens may share a catalog number                                               | Yes                 | UNIQUE              | `catalog_number TEXT NOT NULL UNIQUE`                                                             |
| 3  | Every observation and every taxon assignment must cite a source                           | Yes                 | NOT NULL + FK       | `source_id INTEGER NOT NULL REFERENCES source(source_id)`                                         |
| 4  | A taxon name may appear only once, at either rank                                         | Yes                 | UNIQUE index        | `CREATE UNIQUE INDEX taxon_name_unique ON taxon (genus, coalesce(species, ''))`                   |
| 5  | A taxon cannot have been named before 1758, the starting point of zoological nomenclature | Yes                 | CHECK (range)       | `CHECK (year_named BETWEEN 1758 AND 2100)`                                                        |
| 6  | Earliest age must be ≥ latest age (deeper in time = higher Ma value)                      | Yes                 | CHECK (cross-field) | `CHECK (earliest_age_ma >= latest_age_ma)`                                                        |
| 7  | Character type, dating method, side, other vocabularies must come from a fixed list       | Yes                 | CHECK (enum)        | e.g. `CHECK (character_type IN ('binary', 'multistate', 'continuous'))`                           |
| 8  | Each observation records exactly one of: a state or a measurement                         | Yes                 | CHECK (cross-field) | `CHECK ((state_id IS NOT NULL) + (value_numeric IS NOT NULL) + (missing_reason IS NOT NULL) = 1)` |

## 4b — Cross-field constraints

```sql

-- character: ordering applies only to multistate characters
CHECK (character_type = 'multistate' OR is_ordered IS NULL)

-- character: units apply only to continuous characters
CHECK (character_type = 'continuous' OR units IS NULL)

```
