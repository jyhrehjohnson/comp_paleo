# Primary Key Justifications — Hominin Character State Database
**Author:** Jyhreh Johnson
**Date:** 10/12/2026

### Table: characters

Key field(s): character_id
Key type: Surrogate

Justification:
Characters have multiple ids across published matrices. An integer surrogate key is used to ensure that the key is unique to the database.

### Table: character_states

Key field(s): state_id
Key type: Surrogate

Justification:
Character states don't have a unique identifier. They are identified by their character and state code. The state_id creates an identifier for the database and is attached to each character state for reference. 

### Table: fossil_specimens

Key field(s): specimen_id
Key type: Surrogate

Justification:
Because catalog numbers can change, the database needs a unique identifier to refer to each fossil specimen locally. Normally a catalog number is the unique identifier for a fossil specimen and is how specimens are cited and referenced in the literature.


### Table: taxa

Key field(s): taxon_id
Key type: Surrogate

Justification:
Taxa names and acceptance status can change with taxonomic revisions. Species are often moved between genera, split, or lumped. A taxon_id is used to identify each taxon in the database.

### Table: type_specimens

Key field(s): type_specimen_id
Key type: Surrogate

Justification:
To stay consistent with the rest of the database, type specimens are assigned a unique identifier. Also following specimen_ids, if a given type specimen is identified differently across multiple organzations, this creates a unique identifier for the database alone. 

### Table: taxonomic_assignments

Key field(s): assignment_id
Key type: Surrogate

Justification:
Taxonomic assignments can change the same as taxa through taxonomic revisions. I can utilize this key to identify where sources differ in their assignments. 

### Table: localities

Key field(s): locality_id
Key type: Surrogate

Justification:
Site names are not unique across regions, are spelled differently in different publications, and are sometimes subdivided or renamed during excavations. Coordinates are unpublished for many sites and are remeasured over time. A surrogate key lets a site's name or coordinates be corrected with, each specimen.

### Table: observations

Key field(s): observation_id
Key type: Surrogate

Justification:
An observation records an event (one source scoring one character on one specimen), so it has no natural identifier. A surrogate key guarantees unique value for every row.

### Table: sources

Key field(s): source_id
Key type: Surrogate

Justification:
A DOI is the identifier for a publication, but much of the hominin literature don't have DOIs. The source_id creates a unique identifier for all publications. 

