# Design Reflection V2 — Hominin Character State Database
**Author:** Jyhreh Johnson
**Date:** 10/12/2026

## What changed from your Week 7 draft?

The most significant changes from the week07 draft is that I created new a new table (type_speciemens) and adjusted fields in localities table. While working through everything the database needed I realized that I also needed to record the type specimen for each taxa. The type specimen is an important component for the theorectical and methodological portions of my dissertation making their character information highly important. As stated in my week07_answers.txt I chose to to follow the OTB database and adopt the `verbatim_chronometric_age`, `earliest_chronometric_age`, and `latest_chronometric_age` for my localities table. 

## Which constraint was hardest to specify?

The rule that a taxon name appears only once was more difficult than I thought it would be. My first version was `UNIQUE (genus, species)`. Constraint testing showed it would accept two genus-rank rows for *Paranthropus*, because species is NULL for genus-rank taxa and SQL treats two NULLs as distinct. I considered storing an empty string instead of NULL, if I did this I would lose the ability to query by genus. The solution was a unique index on `(genus, coalesce(species, ''))`, which treats a missing epithet as one shared value. A CHECK then ties `species` to `taxon_rank`.

## What cannot be enforced in SQL?

Two rules fall outside the database. 

1.) A character state score transcribed from the literature must match the original publication. SQL can require that a source is cited, but it cannot judge whether the state was copied correctly. I will have to checke entries against the source publication. 

2.) Before a duplicate specimen record is deleted, its observations must be moved to the surviving record. Because observations cascade on delete, the database will remove them. 

## Connection to readings

Ch 8 says that a primary key should rarely change. This is why every table in my schema has a surrogate key, even if there are natural candidates present in the table fields. I originally thought to use catalog numbers as the primary key in the fossil_specimens table, but because they can change during taxonomic revision, repatriation, or other institituional factors they were not used as primary keys. Natural candidates are labeled as UNIQUE fields. This links back to earlier in my reflection on adding a type_specimens table, both need to be recorded and are important to my research. 

When assigning my foreign keys, I noted Ch 10's discussion of the deletion rule for each relationship since it determined what happends to the RDBMS when a record is deleted from a parent table. It listed the five deletion rules: DENY, RESTRICT, CASCADE, NULLIFY, and SET DEFAULT. Linking tables normally CASCADE, but deleting a taxon would erase every published assignment to it, so for `taxon_assignments.taxon_id` I used RESTRICT. A fossil specimen and its assignment can be deleted, but a name should not be deleted while the literature still uses it.
