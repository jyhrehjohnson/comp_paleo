
# Hominin Character State Database — Preliminary Design Document
**Author:** Jyhreh Johnson
**Date:** 10/7/2026
**Domain:** Paleoanthropology 
**Research context:** A character state database of known/published characters and their associated states.


## PART 1 - MISSION STATEMENT

Hominin Character State Database

"The purpose of the Hominin Character & Character State Database is to provide a comprehensive 
catalog of all published hominin characters and character states for Plio-Pleistocene hominins. 
Paleoanthropologists will use the database for research on taxonomy, taphonomy, and phylogeny."

---

## PART 2 - OBJECTIVES

| # | Objective 						| SQL sketch 								|
|---|-----------------------------------------------------------|-----------------------------------------------------------------------|
| 1 | Track all characters associated with a specific taxon	|	SELECT DISTINCT c.character_id, c.character_name, c.data_type	|
|								|	FROM taxon t							|
|  								|	JOIN taxon_assignment ta ON ta.taxon_id = t.taxon_id		|
|								|	JOIN observation o       ON o.specimen_id = ta.specimen_id	|
|								|	JOIN character c         ON c.character_id = o.character_id	|
|								|	WHERE t.genus = 'Australopithecus'				|
| 								|		AND t.species = 'africanus'				|
| 								|		AND o.missing_reason IS NULL				|
|								|	ORDER BY c.character_name;					|
----------------------------------------------------------------------------------------------------------------------------------------|
| 2 | Track all character states for a given character 		|	SELECT cs.state_code, cs.state_description			|
|								|	FROM character_state cs						|
|								|	JOIN character c ON c.character_id = cs.character_id		|
|								|	WHERE c.character_name = 'sagittal crest'			|
|								|	ORDER BY cs.state_code;						|
----------------------------------------------------------------------------------------------------------------------------------------|
| 3 | Find characters that are used in taxonomic diagonoese	|	SELECT character_id, character_name, anatomical region		|
|								|	FROM character							|
|	but not in phylogenetic analyses			|	WHERE used_in_taxonomy = 1,					|
|    								|	  AND used_in_phylogenetics = 0,				|
|								|	ORDER BY character_name;					|
----------------------------------------------------------------|-----------------------------------------------------------------------|
| 4 | Count characters by type (binary, multistate, continuous	|	SELECT character_type, is_ordered, COUNT(*) AS n_characters	|
|	discrete) and whether they are ordered.			|	FROM character,							|
|    								|	GROUP BY character_type, is_ordered;				|
----------------------------------------------------------------|-----------------------------------------------------------------------|
| 5 | List all specimens assigned to a taxon, by a given source |	SELECT s.catalog_number, ta.confidence				|
|								|	FROM taxon_assignment ta					|
|								|	JOIN specimen s ON s.specimen_id = ta.specimen_id		|
|								|	JOIN taxon t    ON t.taxon_id = ta.taxon_id			|
|								|	WHERE t.genus = 'Paranthropus'					|
|  								|		AND t.species = 'robustus'				|
|  								|		AND ta.source_id = 3					|
|								|	ORDER BY s.catalog_number;					|				


---

## PART 3 - ENTITY IDENTIFICATION

| Entity 	 | 		Justification 						     	       | 	Example attributes 		|
|----------------|-------------------------------------------------------------------------------------|----------------------------------------|
| characters	 | What is primarily being catalogued; it is defined in the 		     	       | character type, character description	|
| character state| What is primarily being catalogued		    	      		     	       | state code, state description		|
| fossil	 | Each fossil has a catalog number regardless of which characters it possesses        | catalog number, preservation		|
| taxon		 | A taxonomic designation exists independently of any character or specimen 	       | scientific name, year named		|
| locality 	 | A locality exists independently of a character or specimen 		     	       | latitude, longitude, formation, member |
| observation 	 | An observation exists independently of a specimen 			     	       | description, source notes		|
| source 	 | A source or publication exists independently of character and specimen it describes | publication				|


---

## PART 4 - FIELD SPECIFICATIONS

### Table: characters
  [This table stores individual characters and their information.]

	| Field name	        | Data type        |	Required   |	Default	      |	Notes															|
	|-----------------------|------------------|---------------|------------------|-------------------------------------------------------------------------------------------------------------------------|
	| character_id	        |	INTEGER	   |	YES (PK)   |	-	      |	Surrogate key; auto-increment												|
	| character_description |	TEXT	   |	NO	   |	-	      |	Regular attribute. Character definition/description from source. NULL when definition is not entered or within source	|
	| anatomical_region     |	TEXT	   |	NO	   |	-	      |	Regular attribute. Controlled vocabulary (Dental, Cranial, Craniofacial. NULL if not classified or undetermined 	|
	| character_type	|	TEXT	   |	YES	   |	-	      |	Regular attribute. Controlled vocabulary (Continuous, Discrete)								|
	| is_ordered	        |	TEXT	   |	NO	   |	-	      |	Regular attribute. Controlled vocabulary (ordered, unordered) NULL when not applicable					|
	| units		        |	NUMERIC	   |	NO	   |	-             | Regular attribute. Controlled vocabulary (mm, cm) NULL for discrete characters						|
	| measurement_protocol  |	TEXT	   |	NO	   |	-             | Regular attribute. Source text. NULL for discrete characters								|
	| source_id	        |	INTEGER	   |	YES (FK)   |	-             | Foreign key. 														|


### Table: character states
  [This table stores character states and their information.]

	| Field name	        | Data type        |	Required   |	Default	      |	Notes						    |
	|-----------------------|------------------|---------------|------------------|-----------------------------------------------------|
	| state_id		|   INTEGER	   |	YES (PK)   |	-	      |	Surrogate key; auto-increment			    |
	| character_id		|   INTEGER	   |	YES (FK)   |	-             | Foreign key			  		    |
	| state_code		|   INTEGER	   |	YES	   |	-             | Regular attribute. Numeric code in character matrix |
	| state_description	|   TEXT	   |	YES	   |	-	      |	Regular attribute. 				    |


### Table: fossil specimen
  [This table stores fossil specimen information.]

	| Field name	        | Data type        |	Required   |	Default	      |	Notes						   			     				     |
	|-----------------------|------------------|---------------|------------------|--------------------------------------------------------------------------------------------------------------|
	| specimen_id		| INTEGER	   |	YES (PK)   |	-	      |	Surrogate key; auto-increment			   			    				     |
	| catalog_number	| TEXT		   |	YES 	   |	-	      |	Natural candidate key; Unique discovery number	  			     				     |
	| locality_id		| INTEGER	   |	NO (FK)	   |	-	      | Foreign key. NULL when locality is unknown or not entered		     				     |
	| elements_preserved	| TEXT		   |	NO	   |	-             | Regular attribute. NULL when not entered				     				     |
	| ontogenetic_stage	| TEXT		   |	NO         |	-             | Regular attribute. Controlled vocabulary (infant, juvenile, subadult, adult) NULL if undetermined or unknown |
	| sex			| TEXT		   |	NO	   |	-             | Regular attribute. Controlled vocabulary (female, male); NULL when undetermined  			     |
	| notes			| TEXT		   |	NO	   |	-             | Regular attribute. Notes from source					     				     |


### Table: locality
  [This table stores locality information.]

	| Field name	        | Data type        |	Required   |	Default	      |	Notes									|
	|-----------------------|------------------|---------------|------------------|-------------------------------------------------------------------------|
	| locality_id		| INTEGER	   |	YES (PK)   |	-	      |	Surrogate key; auto-increment						|
	| site_name		| TEXT		   |	YES	   |	- 	      | Regular attribute.							|
	| country		| TEXT		   |	NO	   |	-             | Regular attribute. Controlled vocabulary (Ethiopia, Kenya, Tanzania)	|
	| formation		| TEXT		   |	NO	   |	-             | Regular attribute. NULL if there is no formal formation			|
	| member		| TEXT		   |	NO	   |	-             | Regular attribute. NULL	if there is no member assigned			|
	| stratigraphic_age	| NUMERIC	   |	NO	   |	-             | Regular attribute. 							|
	| dating_method		| TEXT 		   |	NO	   |	-             | Regular attribute. Controlled vocabulary (argon-argon)			|


### Table: taxon
  [This table stores general taxon information.]

	| Field name	        | Data type        |	Required   |	Default	      |	Notes							    |
	|-----------------------|------------------|---------------|------------------|-------------------------------------------------------------|
	| taxon_id		| INTEGER	   |	YES (PK)   |	-	      |	Surrogate key; auto-increment				    |
	| genus			| TEXT		   | 	YES	   |	-             | Regular attribute. 					    |
	| species		| TEXT		   | 	NO	   |	-             | Regular attribute. 					    |
	| rank			| TEXT		   | 	YES	   |	-             | Regular attribute.			     		    |
	| discovered_by		| TEXT		   | 	NO	   | 	-             | Regular attribute.					    |
	| year_named		| INTEGER	   |	NO	   |	-             | Regular attribute.					    |
	| type_speciemen_id	| INTEGER 	   | 	NO  (FK)   |	-             | Foreign key. NULL when type specimen is not in database yet |


### Table: taxonomic_assignment
  [This table stores the taxonomic assignments for each specimen.]

	| Field name	   | Data type    | Required   | Defaul   | Notes			   |
	|------------------|--------------|------------|----------|--------------------------------|
	| assignment_id    | INTEGER      | YES (PK)   | -	  | Surrogate key; auto-increment  |
	| specimen_id	   | INTEGER      | YES (FK)   | -	  | Foreign key			   |
	| taxon_id	   | INTEGER      | YES (FK)   | -	  | Foreign key			   |
	| source_id        | INTEGER      | YES (FK)   | -	  | Foreign key			   |


### Table: sources
  [This table stores the source or publication information.]

	| Field name	        | Data type        |	Required   |	Default	      |	Notes					|
	|-----------------------|------------------|---------------|------------------|-----------------------------------------|
	| source_id		| INTEGER	   |	YES (PK)   |	-	      |	Surrogate key; auto-increment		|
	| citation		| TEXT		   |	YES	   |	-             | Regular attribute.			|
	| year			| INTEGER	   |	NO	   |	-             |	Regular attribute. NULL if unpublished	|
	| doi			| TEXT		   |	NO	   |	-             | Natural candidate key NULL if no doi	|


### Table: observations
  [This table stores observations or descriptions from the literature.]

	| Field name	        | Data type        |	Required   |	Default	      |	Notes									   			|
	|-----------------------|------------------|---------------|------------------|-------------------------------------------------------------------------------------------------|
	| observation_id	| INTEGER	   |	YES (PK)   |	-	      |	Surrogate key; auto-increment						   			|
	| specimen_id		| INTEGER	   |	YES (FK)   |	-	      |	Foreign key								   			|
	| character_id		| INTEGER	   |	YES (FK)   |	-	      |	Foreign key								   			|
	| state_id		| INTEGER	   | 	NO (FK)    |	-	      |	Foreign key NULL if continuous character				   			|
	| side			| TEXT		   |	NO	   |	-             | Regular attribute.							   			|
	| source_id		| INTEGER	   |	YES	   |	-	      |	Foreign key. NULL if midline element					  		 	|
	| observed_by		| TEXT		   |	NO	   |	-	      | Regular attribute.							   			|
	| scored_from		| TEXT		   |	NO	   |	-	      | Regular attribute. Controlled vocabulary (CT scan, photograph, literature) NULL if not reported |
	| notes			| TEXT		   |	NO	   |	-	      | Regular attribute. 							   			|


## PART 5 - RELATIONSHIPS AND KEYS

| Relationship 			 	 | Cardinality | Implementation 						|
|----------------------------------------|-------------|----------------------------------------------------------------|
| One locality --> many specimens	 | 1:∞	       | specimen.locality_id → locality.locality_id			|
| One character --> many character states| 1:∞	       | character_state.character_id → character.character_id		|
| One source --> many characters	 | 1:∞	       | character.source_id → source.source_id				|
| One specimen --> many observations     | 1:∞	       | observation.specimen_id → specimen.specimen_id			|
| One character → many observations	 | 1:∞	       | observation.character_id → character.character_id		|
| One character state → many observations| 1:∞	       | observation.state_id → character_state.state_id		|
| One source → many observations	 | 1:∞	       | observation.source_id → source.source_id 			|
| One source → many taxon assignments	 | 1:∞	       | taxon_assignment.source._id --> source.source_is		|
| Many specimens ↔ many taxa		 | ∞:∞	       | Junction table taxon_assignment with specimen_id --> taxon_id	|





