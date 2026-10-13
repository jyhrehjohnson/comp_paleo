# Design Reflection, Version 2 — Hominin Character State Database
**Author:** Jyhreh Johnson
**Date:** 10/12/2026

## What changed from the week07 draft

The largest change is in the character table. I removed `character_name`, because the same name is used by different authors for differently defined characters, and made `character_description` required, since it is now the only human-readable way to tell characters apart. Every table also gained CHECK constraints for its controlled vocabularies, and every foreign key now has an explicit ON DELETE and ON UPDATE rule. I added cross-field rules that the Week 7 draft lacked: the age bounds of a locality, paired coordinates, and the requirement that only multistate characters can be ordered and only continuous characters have units.

[PEER REVIEW: add one or two sentences on what your reviewer flagged and what you changed in response.]

## The hardest constraint

The rule that a taxon name appears only once was harder than it looked. My first version was `UNIQUE (genus, species)`. Constraint testing showed it would accept two genus-rank rows for *Paranthropus*, because species is NULL for genus-rank taxa and SQL treats two NULLs as distinct. I considered storing an empty string instead of NULL, which would make "no epithet" look like a value, and a single `scientific_name` column, which would lose the ability to query by genus. The solution was a unique index on `(genus, coalesce(species, ''))`, which treats a missing epithet as one shared value only for the purpose of uniqueness. A CHECK then ties `species` to `taxon_rank`, so the NULL is always deliberate.

## What cannot be enforced in SQL

Two rules in particular fall outside the database. First, a score transcribed from the literature must match the original publication. SQL can require that a source is cited, but it cannot judge whether the state was copied correctly; that takes a second person checking entries against the paper. Second, before a duplicate specimen record is deleted, its observations must be moved to the surviving record. Because observations cascade on delete, the database will do exactly what it is told and remove them. The safeguard has to be a data-cleaning procedure.

## Connection to the readings

DB Mortals Ch 8 says that a primary key's values should rarely, if ever, change. That is why every table in my schema uses a surrogate key, even where a natural candidate exists. Catalog numbers and binomials both change, and taxonomic revision is the subject of my research. The natural candidates survive as UNIQUE fields instead.

Ch 10's discussion of the deletion rule for each relationship, whether to restrict, cascade or nullify, shaped my foreign keys. I made one deliberate departure from the usual pattern. Linking tables normally cascade, but deleting a taxon should not erase every published assignment to it, so `taxon_assignment.taxon_id` uses RESTRICT. A specimen can be deleted, taking its assignments with it, but a name cannot be deleted while the literature still uses it.
