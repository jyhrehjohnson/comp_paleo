# Foreign Key Referential Integrity — Hominin Character State Database
**Author:** Jyhreh Johnson
**Date:** 10/12/2026

<!--
RESTRICT / NO ACTION — Deletion is blocked if any dependent rows exist. Use when the referenced row is a prerequisite for the dependent rows (deleting a locality that has specimens assigned to it should be blocked, not silently orphaned).

CASCADE — Deletion of the parent row automatically deletes all dependent rows. Use for linking table rows and other "part-of" relationships where the dependent row has no independent meaning (deleting a specimen should delete its specimen_publication links).

SET NULL — The FK field is set to NULL when the parent row is deleted. Use when the dependent row can exist without its parent (a specimen can exist even if its taxon identification is withdrawn — the taxon_id becomes NULL, not deleted).

SET DEFAULT — The FK field reverts to its DEFAULT value. Rare; use only when a meaningful default reference exists.
-->

## 3a — Relationship inventory

| FK FIELD                 | IN TABLE         | REFERENCE                    | CARDINALITY | ON DELETE | ON UPDATE |
|--------------------------|------------------|------------------------------|-------------|-----------|-----------|
| locality_id              | fossil_specimens | localities.locality_id       | ∞:1         | RESTRICT  | CASCADE   |
| type_specimen_id         | taxa             | specimen.specimen_id         | ∞:1         | SET NULL  | CASCADE   |
| specimen_id              | taxon_assignment | fossil_specimens.specimen_id | ∞:1         | CASCADE   | CASCADE   |
| taxon_id                 | taxon_assignment | taxa.taxon_id                | ∞:1         | RESTRICT  | CASCADE   |
| source_id                | taxon_assignment | sources.source_id            | ∞:1         | RESTRICT  | CASCADE   |
| source_id                | characters       | sources.source_id            | ∞:1         | RESTRICT  | CASCADE   |
| character_id             | character_states | characters.character_id      | ∞:1         | CASCADE   | CASCADE   |
| specimen_id              | observations     | fossil_specimens.specimen_id | ∞:1         | CASCADE   | CASCADE   |
| character_id             | observations     | characters.character_id      | ∞:1         | RESTRICT  | CASCADE   |
| source_id                | observations     | sources.source_id            | ∞:1         | RESTRICT  | CASCADE   |

`taxon_assignments` is a linking table resolving the many-to-many relationship between specimen and taxon. `observations` resolves the many-to-many relationship between specimen and character; because it carries its own attributes it can be treated as entity.


## 3b — Justifications

**fossil_specimens.locality_id → locality (RESTRICT).**
A locality will always have specimens found there. Deleting a locality that still has specimens would erase their area information, and with it the age context of every observation on them. RESTRICT forces the specimens to be reassigned to another locality before it can be removed. SET NULL was rejected because it would turn a known area into an unknown are without any record of the change.

**taxa.type_specimen_id → specimen (SET NULL).**
A taxon exists independently of its type specimen. If a type specimen row is deleted, for example because it was entered twice, the taxon should remain, and only the link should be cleared. RESTRICT would make it impossible to remove a type specimen.

**taxon_assignments.specimen_id → specimen (CASCADE).**
An assignment of a specimen to a taxon has no meaning once the specimen itself is gone, it is a part of the specimen's record. CASCADE removes these linking rows together with the specimen.

**taxon_assignments.taxon_id → taxon (RESTRICT).**
Deleting a taxon would erase every published assignment to it, and the history of how specimens have been classified is the core data for species delimitation. When a taxon is synonymised, its assignments should be kept, and new assignments to the valid name added as new rows with their own source. RESTRICT makes that the only possible path.

**taxon_assignments.source_id → source (RESTRICT).**
Every assignment must be attributed to a source. Deleting a source would leave assignments that can't be traced to any publication, which defeats the purpose of recording the source. RESTRICT blocks the deletion.

**characters.source_id → source (RESTRICT).**
A character is defined within a publication, and the definition is meaningless without its author and date. RESTRICT prevents a source from being deleted while any character still depends on it.

**character_states.character_id → character (CASCADE).**
States are part of their character. Deleting a character that has never been scored should remove its states. If the character has been scored, the RESTRICT on observation.character_id blocks the deletion first.

**observation.specimen_id → specimen (CASCADE).**
An observation is a score or description on a particular specimen and cannot exist without it. If a specimen record is deleted, its observations are deleted too. CASCADE makes sure the check matters.

**observations.character_id → character (RESTRICT).**
A character that has been used to score specimens is part of the published data and can't be delted. RESTRICT ensures that a character can only be deleted once no observation uses it.

**observations.(character_id, state_id) → character_state (RESTRICT).**
A state can't be deleted while observations record it, because those scores would lose their meaning. 

**observations.source_id → source (RESTRICT).**
As with taxon assignments, every score must remain attributed to the source. RESTRICT blocks deletion of any source that still supports observations.

## 3c — Recursive and self-referential relationships

The schema has no self-referential relationships. 