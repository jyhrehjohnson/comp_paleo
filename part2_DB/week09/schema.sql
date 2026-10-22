-- ============================================================================
-- schema.sql modified from week08 for simplicity
-- Hominin Character State Database
-- ============================================================================

-- Drop in reverse dependency order (children before parents)
DROP TABLE IF EXISTS character_states;
DROP TABLE IF EXISTS characters;
DROP TABLE IF EXISTS sources;

-- ── sources ──────────────────────────────────────────────────────────────────
-- A publication or other source that defines characters, scores specimens,
-- or assigns specimens to taxa.  (Created first: characters references it.)
CREATE TABLE sources (
    source_id   SERIAL PRIMARY KEY,

    citation    TEXT    NOT NULL,

    pub_year    INTEGER                                 -- NULL permitted: in press / unpublished
                CHECK (pub_year BETWEEN 1800 AND 2100),
    doi         TEXT    UNIQUE                          -- NULL permitted: older literature has no DOI
);

-- ── characters ───────────────────────────────────────────────────────────────
-- A morphological character as defined in the literature.
CREATE TABLE characters (
    character_id           SERIAL PRIMARY KEY,

    character_description  TEXT    NOT NULL,

    is_ordered             INTEGER                      -- NULL permitted: not applicable / not stated
                           CHECK (is_ordered IN (0, 1)),
    measurement_protocol   TEXT,

    character_type         TEXT    NOT NULL
                           CHECK (character_type IN ('multistate', 'discrete', 'continuous')),
    anatomical_region      TEXT
                           CHECK (anatomical_region IN ('Cranial', 'Craniofacial', 'Dental', 'Postcranial')),
    units                  TEXT
                           CHECK (units IN ('mm', 'degrees')),

    source_id              INTEGER NOT NULL
                           REFERENCES sources(source_id)
                           ON DELETE RESTRICT
                           ON UPDATE CASCADE,

    -- only multistate characters can be ordered or unordered
    CHECK (character_type = 'multistate' OR is_ordered IS NULL),
    -- only continuous characters have units
    CHECK (character_type = 'continuous' OR units IS NULL)
);

-- ── character_states ─────────────────────────────────────────────────────────
-- One possible state of a discrete character.
CREATE TABLE character_states (
    state_id           SERIAL PRIMARY KEY,

    state_code         INTEGER NOT NULL
                       CHECK (state_code BETWEEN 0 AND 9),
    state_description  TEXT    NOT NULL,

    character_id       INTEGER NOT NULL
                       REFERENCES characters(character_id)
                       ON DELETE CASCADE
                       ON UPDATE CASCADE,

    UNIQUE (character_id, state_code)
);