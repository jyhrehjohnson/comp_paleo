-- ============================================================================
-- constraint_tests.sql
-- Hominin Character State Database — Constraint Tests (week08)
-- Author: Jyhreh Johnson
-- ============================================================================

PRAGMA foreign_keys = ON;   -- must be set on every new connection in SQLite

-- ── Setup: parent rows used by later tests ──────────────────────────────────

INSERT INTO sources (source_id, citation, pub_year, doi)
VALUES (1, 'Test Author A. 2004. Test character analysis. J Test Evol 1:1-10.', 2004, '10.1000/test.001');

INSERT INTO sources (source_id, citation, pub_year)
VALUES (2, 'Test Author B. 1955. Older monograph without a DOI.', 1955);

INSERT INTO localities (locality_id, site_name, country, earliest_age_ma, latest_age_ma, dating_method)
VALUES (1, 'Test Site One', 'South Africa', 2.6, 2.0, 'U-Pb');

INSERT INTO localities (locality_id, site_name, country)
VALUES (2, 'Test Site Two', 'Kenya');


-- ── NOT NULL on fossil_specimens.catalog_number ─────────────────────────────

-- SHOULD SUCCEED
INSERT INTO fossil_specimens (specimen_id, catalog_number, locality_id)
VALUES (1, 'TST 1', 1);

-- SHOULD FAIL: catalog_number is NOT NULL
-- Expected error: NOT NULL constraint failed: fossil_specimens.catalog_number
INSERT INTO fossil_specimens (catalog_number, locality_id)
VALUES (NULL, 1);


-- ── NOT NULL on characters.character_description ────────────────────────────

-- SHOULD SUCCEED
INSERT INTO characters (character_id, character_description, character_type, source_id)
VALUES (1, 'Sagittal crest: absent (0); present (1)', 'discrete', 1);

-- SHOULD FAIL: a character with no description cannot be identified
-- Expected error: NOT NULL constraint failed: characters.character_description
INSERT INTO characters (character_description, character_type, source_id)
VALUES (NULL, 'discrete', 1);


-- ── UNIQUE on fossil_specimens.catalog_number ───────────────────────────────

-- SHOULD SUCCEED: first use of this catalog number
INSERT INTO fossil_specimens (specimen_id, catalog_number, locality_id)
VALUES (2, 'TST 2', 1);

-- SHOULD FAIL: same catalog number entered a second time
-- Expected error: UNIQUE constraint failed: fossil_specimens.catalog_number
INSERT INTO fossil_specimens (catalog_number, locality_id)
VALUES ('TST 2', 2);


-- ── UNIQUE on sources.doi ───────────────────────────────────────────────────

-- SHOULD SUCCEED: a new DOI
INSERT INTO sources (source_id, citation, pub_year, doi)
VALUES (3, 'Test Author C. 2015. A second test paper.', 2015, '10.1000/test.002');

-- SHOULD FAIL: the same DOI as source 1
-- Expected error: UNIQUE constraint failed: sources.doi
INSERT INTO sources (citation, pub_year, doi)
VALUES ('Duplicate entry of Test Author A 2004', 2004, '10.1000/test.001');


-- ── CHECK (enum) on characters.character_type ───────────────────────────────

-- SHOULD SUCCEED
INSERT INTO characters (character_id, character_description, character_type, units, source_id)
VALUES (2, 'Mesiodistal length of M1', 'continuous', 'mm', 1);

-- SHOULD FAIL: 'binary' is not in the controlled vocabulary
-- Expected error: CHECK constraint failed: character_type IN ('discrete', 'continuous')
INSERT INTO characters (character_description, character_type, source_id)
VALUES ('Test character', 'binary', 1);


-- ── CHECK (enum) on localities.dating_method ────────────────────────────────

-- SHOULD SUCCEED
INSERT INTO localities (locality_id, site_name, country, dating_method)
VALUES (3, 'Test Site Three', 'Ethiopia', 'Ar-Ar');

-- SHOULD FAIL: 'carbon-14' is not in the controlled vocabulary
-- Expected error: CHECK constraint failed: dating_method IN (...)
INSERT INTO localities (site_name, dating_method)
VALUES ('Bad Method Site', 'carbon-14');


-- ── CHECK (enum) on fossil_specimens.ontogenetic_stage ──────────────────────

-- SHOULD SUCCEED
INSERT INTO fossil_specimens (specimen_id, catalog_number, locality_id, ontogenetic_stage)
VALUES (3, 'TST 3', 3, 'juvenile');

-- SHOULD FAIL: 'child' is not in the controlled vocabulary
-- Expected error: CHECK constraint failed: ontogenetic_stage IN (...)
INSERT INTO fossil_specimens (catalog_number, ontogenetic_stage)
VALUES ('TST 99', 'child');


-- ── CHECK (range) on taxa.year_named ────────────────────────────────────────

-- SHOULD SUCCEED
INSERT INTO taxa (taxon_id, genus, species, taxon_rank, year_named)
VALUES (1, 'Australopithecus', 'africanus', 'species', 1925);

INSERT INTO taxa (taxon_id, genus, species, taxon_rank, year_named)
VALUES (2, 'Paranthropus', 'robustus', 'species', 1938);

-- SHOULD FAIL: before 1758, the starting point of zoological nomenclature
-- Expected error: CHECK constraint failed: year_named BETWEEN 1758 AND 2100
INSERT INTO taxa (genus, species, taxon_rank, year_named)
VALUES ('Homo', 'testus', 'species', 1700);


-- ── CHECK (range) on character_states.state_code ────────────────────────────

-- SHOULD SUCCEED
INSERT INTO character_states (state_id, character_id, state_code, state_description)
VALUES (1, 1, 0, 'absent');

INSERT INTO character_states (state_id, character_id, state_code, state_description)
VALUES (2, 1, 1, 'present');

-- SHOULD FAIL: matrix codes are single digits
-- Expected error: CHECK constraint failed: state_code BETWEEN 0 AND 9
INSERT INTO character_states (character_id, state_code, state_description)
VALUES (1, 12, 'out of range');


-- ── CHECK (cross-field) on characters: only continuous characters have units ─

-- SHOULD SUCCEED: a continuous character with units (character 2 above),
-- and a discrete character without units (character 1 above)

-- SHOULD FAIL: a discrete character cannot have units
-- Expected error: CHECK constraint failed: character_type = 'continuous' OR units IS NULL
INSERT INTO characters (character_description, character_type, units, source_id)
VALUES ('Test discrete character with units', 'discrete', 'mm', 1);


-- ── Composite FK: the state must belong to the character being scored ───────
-- Requires UNIQUE (character_id, state_id) in character_states.

-- SHOULD SUCCEED: state 2 belongs to character 1
INSERT INTO observations (observation_id, specimen_id, character_id, state_id, source_id, side)
VALUES (1, 1, 1, 2, 1, 'left');

-- SHOULD FAIL: state 1 belongs to character 1, not character 2
-- Expected error: FOREIGN KEY constraint failed
INSERT INTO observations (specimen_id, character_id, state_id, source_id)
VALUES (1, 2, 1, 1);


-- ── Taxon assignment used by the cascade tests below ───────────────────────

INSERT INTO taxon_assignments (assignment_id, specimen_id, taxon_id, source_id, confidence)
VALUES (1, 1, 1, 1, 'confident');


-- ── FK RESTRICT: fossil_specimens.locality_id → localities ──────────────────

-- SHOULD SUCCEED: locality 2 has no specimens
DELETE FROM localities WHERE locality_id = 2;
SELECT count(*) AS locality_2_rows_remaining FROM localities WHERE locality_id = 2;

-- SHOULD FAIL: locality 1 still has specimens assigned to it
-- Expected error: FOREIGN KEY constraint failed
DELETE FROM localities WHERE locality_id = 1;
SELECT count(*) AS locality_1_rows_remaining FROM localities WHERE locality_id = 1;


-- ── FK RESTRICT: characters.source_id → sources ─────────────────────────────

-- SHOULD SUCCEED: source 2 is not cited anywhere
DELETE FROM sources WHERE source_id = 2;
SELECT count(*) AS source_2_rows_remaining FROM sources WHERE source_id = 2;

-- SHOULD FAIL: source 1 defines characters and supports assignments
-- Expected error: FOREIGN KEY constraint failed
DELETE FROM sources WHERE source_id = 1;
SELECT count(*) AS source_1_rows_remaining FROM sources WHERE source_id = 1;


-- ── FK SET NULL: taxa.type_specimen_id → fossil_specimens ───────────────────

-- Make specimen 3 the type of taxon 2, then delete specimen 3
UPDATE taxa SET type_specimen_id = 3 WHERE taxon_id = 2;
SELECT taxon_id, genus, species, type_specimen_id FROM taxa WHERE taxon_id = 2;

-- SHOULD SUCCEED: the taxon survives with type_specimen_id set to NULL
DELETE FROM fossil_specimens WHERE specimen_id = 3;
SELECT taxon_id, genus, species, type_specimen_id FROM taxa WHERE taxon_id = 2;


-- ── FK CASCADE: observations and taxon_assignments → fossil_specimens ───────

-- Before: specimen 1 has one observation and one taxon assignment
SELECT
    (SELECT count(*) FROM observations      WHERE specimen_id = 1) AS observations_before,
    (SELECT count(*) FROM taxon_assignments WHERE specimen_id = 1) AS assignments_before;

-- SHOULD SUCCEED: deleting specimen 1 removes its observations and assignments
DELETE FROM fossil_specimens WHERE specimen_id = 1;

SELECT
    (SELECT count(*) FROM observations      WHERE specimen_id = 1) AS observations_after,
    (SELECT count(*) FROM taxon_assignments WHERE specimen_id = 1) AS assignments_after;


-- ── FK CASCADE: character_states → characters ───────────────────────────────

-- Character 1 has two states and, after the delete above, no observations
SELECT count(*) AS states_before FROM character_states WHERE character_id = 1;

-- SHOULD SUCCEED: deleting the character removes its states
DELETE FROM characters WHERE character_id = 1;
SELECT count(*) AS states_after FROM character_states WHERE character_id = 1;
