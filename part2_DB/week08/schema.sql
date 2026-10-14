-- ============================================================================
-- schema.sql
-- Hominin Character State Database — Revised Schema (week08)
-- Author: Jyhreh Johnson
-- Date:   10/12/2026
-- ============================================================================

PRAGMA foreign_keys = ON;

-- Drop in reverse dependency order (children before parents)
DROP TABLE IF EXISTS sources;
DROP TABLE IF EXISTS observations;
DROP TABLE IF EXISTS localities;
DROP TABLE IF EXISTS taxon_assignments;
DROP TABLE IF EXISTS taxa;
DROP TABLE IF EXISTS fossil_specimens;
DROP TABLE IF EXISTS character_states;
DROP TABLE IF EXISTS characters;

-- ── characters ───────────────────────────────────────────────────────────────
-- A morphological character as defined in the literature.
CREATE TABLE characters (
    -- Primary key
    character_id           INTEGER PRIMARY KEY,

    -- Required fields
    character_description  TEXT    NOT NULL,

    -- Optional fields
    is_ordered             INTEGER                      -- NULL permitted: not applicable / not stated
                           CHECK (is_ordered IN (0, 1)),
    measurement_protocol   TEXT,

    -- Controlled vocabulary
    character_type         TEXT    NOT NULL
                           CHECK (character_type IN ('multistate', 'discrete', 'continuous')),
    anatomical_region      TEXT
                           CHECK (anatomical_region IN ('Cranial', 'Craniofacial', 'Dental', 'Postcranial')),
    units                  TEXT
                           CHECK (units IN ('mm', 'degrees')),

    -- Foreign keys
    source_id              INTEGER NOT NULL
                           REFERENCES sources(source_id)
                           ON DELETE RESTRICT
                           ON UPDATE CASCADE,

    -- Cross-field business rules
    -- only multistate characters can be ordered or unordered
    CHECK (character_type = 'multistate' OR is_ordered IS NULL),
    -- only continuous characters have units
    CHECK (character_type = 'continuous' OR units IS NULL)
);


-- ── character_states ─────────────────────────────────────────────────────────
-- One possible state of a discrete character.
CREATE TABLE character_states (
    -- Primary key
    state_id           INTEGER PRIMARY KEY,

    -- Required fields
    state_code         INTEGER NOT NULL
                       CHECK (state_code BETWEEN 0 AND 9),
    state_description  TEXT    NOT NULL,

    -- Foreign keys
    character_id       INTEGER NOT NULL
                       REFERENCES characters(character_id)
                       ON DELETE CASCADE
                       ON UPDATE CASCADE,

     UNIQUE (character_id, state_code),
     UNIQUE (character_id, state_id)

);


-- ── fossil_specimens ────────────────────────────────────────────────────────────────
-- An individual fossil specimen.
CREATE TABLE fossil_specimens (
    -- Primary key
    specimen_id         INTEGER PRIMARY KEY,

    -- Required fields
    catalog_number      TEXT    NOT NULL UNIQUE,

    -- Optional fields
    elements_preserved  TEXT,
    notes               TEXT,

    -- Controlled vocabulary
    ontogenetic_stage   TEXT                            -- NULL permitted: indeterminate
                        CHECK (ontogenetic_stage IN ('infant', 'juvenile', 'subadult', 'adult')),
    sex                 TEXT                            -- NULL permitted: indeterminate
                        CHECK (sex IN ('female', 'male')),

    -- Foreign keys
    locality_id         INTEGER                         -- NULL permitted: area unknown
                        REFERENCES localities(locality_id)
                        ON DELETE RESTRICT
                        ON UPDATE CASCADE
);


-- ── taxa ───────────────────────────────────────────────────────────────────
-- A named taxon at genus or species rank.
CREATE TABLE taxa (
    -- Primary key
    taxon_id          INTEGER PRIMARY KEY,

    -- Required fields
    genus             TEXT    NOT NULL,

    -- Optional fields
    species           TEXT                              -- NULL for genus-rank taxa
                      CHECK (species = lower(species)),
    named_by          TEXT,
    year_named        INTEGER
                      CHECK (year_named BETWEEN 1758 AND 2100),

    -- Controlled vocabulary
    taxon_rank        TEXT    NOT NULL
                      CHECK (taxon_rank IN ('genus', 'species')),

    -- Foreign keys
    type_specimen_id  INTEGER                           -- NULL permitted: type not in database
                      REFERENCES fossil_specimens(specimen_id)
                      ON DELETE SET NULL
                      ON UPDATE CASCADE
);

-- ── taxon_assignments ────────────────────────────────────────────────────────
-- Linking table: one source assigning one specimen to one taxon.
-- Resolves the many-to-many relationship between specimen and taxon.
CREATE TABLE taxon_assignments (
    -- Primary key
    assignment_id  INTEGER PRIMARY KEY,

    -- Controlled vocabulary
    confidence     TEXT,                                 -- NULL permitted: source did not qualify it

    -- Foreign keys
    specimen_id    INTEGER NOT NULL
                   REFERENCES fossil_specimens(specimen_id)
                   ON DELETE CASCADE
                   ON UPDATE CASCADE,
    taxon_id       INTEGER NOT NULL
                   REFERENCES taxa(taxon_id)
                   ON DELETE RESTRICT
                   ON UPDATE CASCADE,
    source_id      INTEGER NOT NULL
                   REFERENCES sources(source_id)
                   ON DELETE RESTRICT
                   ON UPDATE CASCADE

);

-- ── localities ────────────────────────────────────────────────────────────────
-- A site or collecting locality, with its stratigraphic and age context.
CREATE TABLE localities (
    -- Primary key
    locality_id      INTEGER PRIMARY KEY,

    -- Required fields
    site_name        TEXT    NOT NULL,

    -- Optional fields
    country          TEXT,                              -- NULL permitted: not yet entered
    formation        TEXT,                              -- NULL permitted: many cave sites have no formal formation
    member           TEXT,                              -- NULL permitted: no member assigned
    verbatim_age     TEXT,
    earliest_age_ma  NUMERIC CHECK (earliest_age_ma > 0),
    latest_age_ma    NUMERIC CHECK (latest_age_ma >= 0),

    -- Controlled vocabulary
    dating_method    TEXT
                     CHECK (dating_method IN ('Ar-Ar', 'K-Ar', 'U-Pb', 'U-series',
                                              'ESR', 'biochronology'))

);

-- ── observations ─────────────────────────────────────────────────────────────
-- One score of one character on one specimen, as reported by one source.
CREATE TABLE observations (
    -- Primary key
    observation_id  INTEGER PRIMARY KEY,

    -- Optional fields
    observed_by     TEXT,
    notes           TEXT,

    -- Controlled vocabulary
    side            TEXT                                 -- NULL permitted: midline or not reported
                    CHECK (side IN ('left', 'right')),
    scored_from     TEXT
                    CHECK (scored_from IN ('original', 'cast', 'CT scan',
                                           'photograph', 'literature')),

    -- Foreign keys
    specimen_id     INTEGER NOT NULL
                    REFERENCES fossil_specimens(specimen_id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
    character_id    INTEGER NOT NULL
                    REFERENCES characters(character_id)
                    ON DELETE RESTRICT
                    ON UPDATE CASCADE,
    state_id        INTEGER,
    source_id       INTEGER NOT NULL
                    REFERENCES sources(source_id)
                    ON DELETE RESTRICT
                    ON UPDATE CASCADE,

    -- the state must belong to the character being scored
    FOREIGN KEY (character_id, state_id)
        REFERENCES character_states(character_id, state_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- ── sources ──────────────────────────────────────────────────────────────────
-- A publication or other source that defines characters, scores specimens,
-- or assigns specimens to taxa.
CREATE TABLE sources (
    -- Primary key
    source_id   INTEGER PRIMARY KEY,

    -- Required fields
    citation    TEXT    NOT NULL,

    -- Optional fields
    pub_year    INTEGER                                 -- NULL permitted: in press / unpublished
                CHECK (pub_year BETWEEN 1800 AND 2100),
    doi         TEXT    UNIQUE                          -- NULL permitted: older literature has no DOI
);