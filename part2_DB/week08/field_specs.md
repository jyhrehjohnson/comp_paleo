# Field Specifications — Hominin Character State Database
**Author:** Jyhreh Johnson
**Date:** 10/12/2026

[//]: # (Required columns:)
[//]: # (Column	            What to write)
[//]: # (Field name	        Exact name as it will appear in SQL &#40;snake_case)
[//]: # (Data type	        INTEGER, TEXT, REAL, NUMERIC, DATE — be specific)
[//]: # (PK / FK	        Mark PK if primary key, FK → table.field if foreign key)
[//]: # (NOT NULL	        YES if the field must always have a value; NO if NULL is permitted)
[//]: # (UNIQUE	            YES if no two rows may share this value; NO otherwise)
[//]: # (DEFAULT	        The default value, or — if none)
[//]: # (CHECK constraint	The expression &#40;e.g., age_ma > 0&#41;, or — if none)
[//]: # (Rationale	        One sentence: why this type, why this constraint)

---

### Table: characters

| FIELD NAME            | DATA TYPE | PK/FK                  | NOT NULL | UNIQUE | DEFAULT | CHECK                                                                       | RATIONALE                                                                                                                                    |
|-----------------------|-----------|------------------------|----------|--------|---------|-----------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| character_id          | INTEGER   | PK                     | YES      | YES    | —       | —                                                                           | Surrogate key; auto-increment. No natural identifier is unique across sources for characters. They have different ids in different matrices. |
| character_description | TEXT      | —                      | YES      | NO     | —       | —                                                                           | Character definition from the source; required because it is the only human-readable way to tell characters apart                            |
| anatomical_region     | TEXT      | —                      | NO       | NO     | —       | `anatomical_region IN ('Cranial', 'Craniofacial', 'Dental', 'Postcranial')` | Controlled vocabulary (Cranial, Craniofacial, Dental, Postcranial); NULL if not yet identified                                               |
| character_type        | TEXT      | —                      | YES      | NO     | —       | `character_type IN ('discrete', 'continuous')`                              | Controlled vocabulary (discrete, continuous); required because it decides whether an observation records a state or a measurement            |
| is_ordered            | INTEGER   | —                      | NO       | NO     | —       | `is_ordered IN (0, 1)`                                                      | (1 = ordered, 0 = unordered); NULL for continuous characters                                                                                 |
| units                 | TEXT      | —                      | NO       | NO     | —       | `units IN ('mm', 'degrees')`                                                | Controlled vocabulary (mm, degrees); NULL for discrete characters                                                                            |
| measurement_protocol  | TEXT      | —                      | NO       | NO     | —       | —                                                                           | How the measurement is taken, as described by the source; NULL for discrete characters                                                       |
| source_id             | INTEGER   | FK → sources.source_id | YES      | NO     | —       | —                                                                           | Every character must be traceable to the source; one source defines many characters                                                          |

### Table: character_states

| FIELD NAME        | DATA TYPE | PK/FK                        | NOT NULL | UNIQUE | DEFAULT | CHECK                        | RATIONALE                                                           |
|-------------------|-----------|------------------------------|----------|--------|---------|------------------------------|---------------------------------------------------------------------|
| state_id          | INTEGER   | PK                           | YES      | YES    | —       | —                            | Surrogate key; auto-increment                                       |
| character_id      | INTEGER   | FK → characters.character_id | YES      | NO     | —       | —                            | Every state belongs to one character; one character has many states |
| state_code        | INTEGER   | —                            | YES      | NO     | —       | `state_code BETWEEN 0 AND 9` | The numeric code in the character matrix; unique within a character |
| state_description | TEXT      | —                            | YES      | NO     | —       | —                            | A state code is nothing without its description                     |

### Table: fossil_specimens

| FIELD NAME         | DATA TYPE | PK/FK                       | NOT NULL | UNIQUE | DEFAULT | CHECK                                                              | RATIONALE                                                                                  |
|--------------------|-----------|-----------------------------|----------|--------|---------|--------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| specimen_id        | INTEGER   | PK                          | YES      | YES    | —       | —                                                                  | Surrogate key; auto-increment. Catalog numbers can be renumbered                           |
| catalog_number     | TEXT      | —                           | YES      | YES    | —       | —                                                                  | Natural candidate key; TEXT because it mixes letters, numbers and spaces                   |
| locality_id        | INTEGER   | FK → localities.locality_id | NO       | NO     | —       | —                                                                  | NULL when the locality is unknown or not entered                                           |
| elements_preserved | TEXT      | —                           | NO       | NO     | —       | —                                                                  | Verbatim description from the source (femur, humerus, M2); NULL when not entered           |
| ontogenetic_stage  | TEXT      | —                           | NO       | NO     | —       | `ontogenetic_stage IN ('infant', 'juvenile', 'subadult', 'adult')` | Controlled vocabulary (infant, juvenile, subadult, adult); NULL if undetermined or unknown |
| sex                | TEXT      | —                           | NO       | NO     | —       | `sex IN ('female', 'male')`                                        | Controlled vocabulary (female of male); NULL when undetermined, the usual case for fossils |
| notes              | TEXT      | —                           | NO       | NO     | —       | —                                                                  | Notes from the source                                                                      |

### Table: taxa

| FIELD NAME     | DATA TYPE | PK/FK | NOT NULL | UNIQUE | DEFAULT | CHECK                                    | RATIONALE                                                                                            |
|----------------|-----------|-------|----------|--------|---------|------------------------------------------|------------------------------------------------------------------------------------------------------|
| taxon_id       | INTEGER   | PK    | YES      | YES    | —       | —                                        | Surrogate key; names can change during taxonomic revision                                            |
| genus          | TEXT      | —     | YES      | NO     | —       | —                                        | Every taxon has a genus                                                                              |
| species        | TEXT      | —     | NO       | NO     | —       | —                                        | NULL for genus-rank taxa; a species-rank taxon must have an epithet                                  |
| taxonomic_rank | TEXT      | —     | YES      | NO     | —       | `taxonomic_rank IN ('genus', 'species')` | Controlled vocabulary (genus, species)                                                               |
| named_by       | TEXT      | —     | NO       | NO     | —       | —                                        | Who named the taxon; NULL until entered                                                              |
| year_named     | INTEGER   | —     | NO       | NO     | —       | `year_named BETWEEN 1758 AND 2100`       | 1758 is the starting point of zoological nomenclature, so no valid name is older; NULL until entered | 

### Table: type_specimens

| FIELD NAME       | DATA TYPE | PK/FK                             | NOT NULL | UNIQUE | DEFAULT | CHECK                                                               | RATIONALE                                                                                                                     |
|------------------|-----------|-----------------------------------|----------|--------|---------|---------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| type_specimen_id | INTEGER   | PK                                | YES      | YES    | —       | —                                                                   | Surrogate key; auto-increment                                                                                                 |
| specimen_id      | INTEGER   | FK → fossil_specimens.specimen_id | YES      | NO     | —       | —                                                                   | Each type record points to one specimen                                                                                       |
| taxon_id         | INTEGER   | FK → taxa.taxon_id                | YES      | YES    | —       | —                                                                   | Each type record belongs to one taxon; a taxon can have several (a holotype and paratypes)                                    |
| type_category    | TEXT      | —                                 | YES      | NO     | —       | `type_category IN ('holotype', 'paratype', 'lectotype', 'neotype')` | Controlled vocabulary (holotype, paratype, lectotype, neotype); distinguishes the name-bearing type from supporting specimens |

### Table: taxonomic_assignments

| FIELD NAME    | DATA TYPE | PK/FK                             | NOT NULL | UNIQUE | DEFAULT | CHECK | RATIONALE                                                                       |
|---------------|-----------|-----------------------------------|----------|--------|---------|-------|---------------------------------------------------------------------------------|
| assignment_id | INTEGER   | PK                                | YES      | YES    | —       | —     | Surrogate key; auto-increment, so other tables can refer to a single assignment |
| specimen_id   | INTEGER   | FK → fossil_specimens.specimen_id | YES      | YES    | —       | —     | An assignment must have a specimen                                              |
| taxon_id      | INTEGER   | FK → taxa.taxon_id                | YES      | YES    | —       | —     | An assignment must name a taxon                                                 |
| source_id     | INTEGER   | FK → sources.source_id            | YES      | YES    | —       | —     | Every assignment must have a source                                             |


### Table: localities

| FIELD NAME                | DATA TYPE | PK/FK | NOT NULL | UNIQUE | DEFAULT | CHECK                                                                   | RATIONALE                                                               |
|---------------------------|-----------|-------|----------|--------|---------|-------------------------------------------------------------------------|-------------------------------------------------------------------------|
| locality_id               | INTEGER   | PK    | YES      | YES    | —       | —                                                                       | Surrogate key; auto-increment. Site names are not unique across regions |
| site_name                 | TEXT      | —     | YES      | NO     | —       | —                                                                       | A locality without a name cannot be identified                          |
| country                   | TEXT      | —     | NO       | NO     | —       | —                                                                       | Free text (Ethiopia, Kenya, Tanzania); NULL until entered               |
| formation                 | TEXT      | —     | NO       | NO     | —       | —                                                                       | NULL if there is no formal formation                                    |
| member                    | TEXT      | —     | NO       | NO     | —       | —                                                                       | NULL if no member is assigned                                           |
| verbatim_chronometric_age | TEXT      | —     | NO       | NO     | —       | —                                                                       | Age exactly as written in the source ("ca. 2.0–2.6 Ma")                 |
| earliest_chronometric_age | NUMERIC   | —     | NO       | NO     | —       | `earliest_chronometric_age > 0`                                         | Older bound in Ma; NULL when undated                                    |
| latest_chronometric_age   | NUMERIC   | —     | NO       | NO     | —       | `latest_chronometric_age >= 0`                                          | Younger bound in Ma; NULL when undated                                  |
| dating_method             | TEXT      | —     | NO       | NO     | —       | `dating_method IN ('Ar-Ar', 'K-Ar', 'paleomagnetism', 'biochronology')` | Controlled vocabulary (argon-argon, etc.); NULL when undated            |

### Table: observations

| FIELD NAME     | DATA TYPE | PK/FK                             | NOT NULL | UNIQUE | DEFAULT | CHECK                                                                        | RATIONALE                                                                   |
|----------------|-----------|-----------------------------------|----------|--------|---------|------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| observation_id | INTEGER   | PK                                | YES      | YES    | —       | —                                                                            | Surrogate key; auto-increment                                               |
| specimen_id    | INTEGER   | FK → fossil_specimens.specimen_id | YES      | NO     | —       | —                                                                            | Every score belongs to a specimen                                           |
| character_id   | INTEGER   | FK → characters.character_id      | YES      | NO     | —       | —                                                                            | Every score is of one character                                             |
| state_id       | INTEGER   | FK → character_states.state_id    | NO       | NO     | —       | —                                                                            | NULL if the character is continuous                                         |
| side           | TEXT      | —                                 | NO       | NO     | —       | `side IN ('left', 'right')`                                                  | Controlled vocabulary (left, right, midline); NULL when not reported        |
| source_id      | INTEGER   | FK → sources.source_id            | YES      | NO     | —       | —                                                                            | Every score must be attributed to the source that reported it               |
| observed_by    | TEXT      | —                                 | NO       | NO     | —       | —                                                                            | Person who scored it, when different from the source authors                |
| scored_from    | TEXT      | —                                 | NO       | NO     | —       | `scored_from IN ('original', 'cast', 'CT scan', 'photograph', 'literature')` | Controlled vocabulary (original, cast, CT scan, etc.); NULL if not reported |
| notes          | TEXT      | —                                 | NO       | NO     | —       | —                                                                            | Free text                                                                   |

### Table: sources

| FIELD NAME | DATA TYPE | PK/FK | NOT NULL | UNIQUE | DEFAULT | CHECK                            | RATIONALE                                                         |
|------------|-----------|-------|----------|--------|---------|----------------------------------|-------------------------------------------------------------------|
| source_id  | INTEGER   | PK    | YES      | YES    | —       | —                                | Surrogate key; auto-increment. Older literature has no DOI        |
| citation   | TEXT      | —     | YES      | NO     | —       | —                                | Every source must have a citation                                 |
| pub_year   | INTEGER   | —     | NO       | NO     | —       | `pub_year BETWEEN 1800 AND 2100` | NULL if unpublished or in press                                   |
| doi        | TEXT      | —     | NO       | YES    | —       | —                                | Natural candidate key when present; NULL if the source has no DOI |

