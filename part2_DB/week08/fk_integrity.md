# Foreign Key Referential Integrity — Hominin Character State Database
**Author:** Jyhreh Johnson
**Date:** 10/12/2026

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

`taxon_assignments` is a linking table resolving the many-to-many relationship between specimen and taxon. `observations` resolves the many-to-many relationship between specimen and character; it is treated as an entity rather than a pure linking table because it carries its own attributes.

**ON UPDATE.** Every foreign key uses ON UPDATE CASCADE. All the referenced keys are surrogate integers that should never change.

## 3b — Justifications

**fossil_specimens.locality_id → locality (RESTRICT).**
A locality will always have specimens found there. Deleting a locality that still has specimens would erase their area information, and with it the age context of every observation on them. RESTRICT forces the specimens to be reassigned to another locality, or the locality merged, before it can be removed. SET NULL was rejected because it would turn a known area into an unknown one without any record of the change.

**taxa.type_specimen_id → specimen (SET NULL).**
A taxon exists independently of whether its type specimen is in the database. If a type specimen row is deleted, for example because it was entered twice, the taxon should remain, and only the link should be cleared. SET NULL does this; RESTRICT would make it impossible to remove a specimen record because it happens to be a type.

**taxon_assignments.specimen_id → specimen (CASCADE).**
An assignment of a specimen to a taxon has no meaning once the specimen itself is gone; it is a part of the specimen's record, not an independent fact. CASCADE removes these linking rows together with the specimen, as the textbook recommends for linking tables.

**taxon_assignments.taxon_id → taxon (RESTRICT).**
Here I depart from the usual CASCADE for linking tables. Deleting a taxon would otherwise erase every published assignment to it, and the history of how specimens have been classified is the core data for species delimitation. When a taxon is synonymised, its assignments should be kept, and new assignments to the valid name added as new rows with their own source. RESTRICT makes that the only possible path.

**taxon_assignments.source_id → source (RESTRICT).**
Every assignment must be attributable. Deleting a source would leave assignments that cannot be traced to any publication, which defeats the purpose of recording the source at all. RESTRICT blocks the deletion until the assignments are dealt with.

**characters.source_id → source (RESTRICT).**
A character is defined by a publication, and the definition is meaningless without its author and date. RESTRICT prevents a source from being deleted while any character still depends on it.

**character_states.character_id → character (CASCADE).**
States are part of their character: "state 1 = present" has no meaning without the character it describes. Deleting a character that has never been scored should therefore remove its states as well. If the character has been scored, the RESTRICT on observation.character_id blocks the deletion first, so this CASCADE can never orphan an observation.

**observation.specimen_id → specimen (CASCADE).**
An observation is a score or description on a particular specimen and cannot exist without it. If a specimen record is deleted, its observations are deleted too. CASCADE makes sure the check matters.

**observations.character_id → character (RESTRICT).**
A character that has been used to score specimens is part of the published data and should not disappear. RESTRICT ensures that a character can only be deleted once no observation uses it.

**observations.(character_id, state_id) → character_state (RESTRICT).**
A state cannot be deleted while observations record it, because those scores would lose their meaning. 

**observations.source_id → source (RESTRICT).**
As with taxon assignments, every score must remain attributed to the source that reported it. RESTRICT blocks deletion of any source that still supports observations.

## 3c — Recursive and self-referential relationships

The schema has no self-referential relationships. 