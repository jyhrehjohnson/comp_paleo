-- schema_draft.sql
-- Hominin Character State Database — Preliminary Schema
-- Week07 Design Assignment


-- Publications and other sources that define characters, score specimens,
-- or assign specimens to taxa
CREATE TABLE source (
    source_id   INTEGER PRIMARY KEY,
    citation    TEXT NOT NULL,
    pub_year    INTEGER,            -- 'year' avoided; reserved in some SQL dialects
    doi         TEXT UNIQUE
);

-- Places where specimens were found, with stratigraphic and age context
CREATE TABLE locality (
    locality_id      INTEGER PRIMARY KEY,
    site_name        TEXT NOT NULL,
    country          TEXT,
    formation        TEXT,
    member           TEXT,
    dating_method    TEXT
);

-- Individual fossil specimens
CREATE TABLE specimen (
    specimen_id         INTEGER PRIMARY KEY,
    catalog_number      TEXT NOT NULL UNIQUE,
    locality_id         INTEGER REFERENCES locality(locality_id),
    elements_preserved  TEXT,       -- verbatim description; see design document
    ontogenetic_stage   TEXT,
    sex                 TEXT,
    notes               TEXT
);

-- Named taxa (genus or species rank)
CREATE TABLE taxon (
    taxon_id          INTEGER PRIMARY KEY,
    genus             TEXT NOT NULL,
    species           TEXT,         -- NULL for genus-rank taxa
    rank              TEXT NOT NULL, -- 'rank' avoided; reserved in some SQL dialects
    named_by          TEXT,
    year_named        INTEGER,
    type_specimen_id  INTEGER REFERENCES specimen(specimen_id),
    UNIQUE (genus, species)
);

-- Junction table: which source assigns which specimen to which taxon
CREATE TABLE taxon_assignment (
    assignment_id  INTEGER PRIMARY KEY,
    specimen_id    INTEGER NOT NULL REFERENCES specimen(specimen_id),
    taxon_id       INTEGER NOT NULL REFERENCES taxon(taxon_id),
    source_id      INTEGER NOT NULL REFERENCES source(source_id),
    UNIQUE (specimen_id, taxon_id, source_id)
);

-- Morphological characters as defined in the literature
CREATE TABLE character (
    character_id           INTEGER PRIMARY KEY,
    character_description  TEXT,
    anatomical_region      TEXT,
    character_type         TEXT NOT NULL,   -- binary / multistate / continuous
    is_ordered             INTEGER,         -- 0/1; NULL when not applicable
    units                  TEXT,            -- continuous characters only
    measurement_protocol   TEXT,
    source_id              INTEGER NOT NULL REFERENCES source(source_id)
);

-- The possible states of each discrete character
CREATE TABLE character_state (
    state_id           INTEGER PRIMARY KEY,
    character_id       INTEGER NOT NULL REFERENCES character(character_id),
    state_code         INTEGER NOT NULL,
    state_description  TEXT NOT NULL
);

-- One score of one character on one specimen, as reported by one source
CREATE TABLE observation
(
    observation_id INTEGER PRIMARY KEY,
    specimen_id    INTEGER NOT NULL REFERENCES specimen (specimen_id),
    character_id   INTEGER NOT NULL REFERENCES character (character_id),
    state_id       INTEGER, -- discrete characters
    side           TEXT,
    source_id      INTEGER NOT NULL REFERENCES source (source_id),
    observed_by    TEXT,
    scored_from    TEXT,
    notes          TEXT,
    -- the state must belong to the character being scored
    FOREIGN KEY (character_id, state_id)
        REFERENCES character_state (character_id, state_id)
);
