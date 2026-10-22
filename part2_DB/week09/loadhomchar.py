"""
load.py — populate the Hominin Character State database from
mod_homchar_db.csv.

I used a modified version of mod_homchar_db.csv. I also had to assess how character states are stored
in a single cell. I needed the loader to split the cells in the .csv into state rows.

"""

import csv
import re
import sys
import psycopg2
import psycopg2.extras
from config import DSN

CSV_FILE = "mod_homchar_db.csv"

# ── Code translations: CSV abbreviations → schema vocabulary ─────────────────

REGION = {
    "CR":  "Cranial",
    "CF":  "Craniofacial",
    "DEN": "Dental",
    "PC":  "Postcranial",
}

ORDERED = {"OM": 1, "UM": 0}   # ordered / unordered multistate

# One state = label text followed by "(digit)". The label may itself contain
# commas or semicolons (e.g. "Monomorphic; small canines (3)").
STATE_PATTERN = re.compile(r"\s*;?\s*([^()]+?)\s*\((\d)\)")


# ── Small helpers ────────────────────────────────────────────────────────────

def clean(row, col):
    """Return the stripped cell value, or None if missing/empty."""
    value = (row.get(col) or "").strip()
    return value or None


def parse_states(cell):
    """'Absent (0); Present (1)' → [(0, 'Absent'), (1, 'Present')]."""
    if not cell:
        return []
    return [(int(code), label.strip())
            for label, code in STATE_PATTERN.findall(cell)]


def character_type(csv_type, n_states):
    """CSV uses C/D. Discrete characters with >2 states become 'multistate'."""
    if csv_type == "C":
        return "continuous"
    if csv_type == "D":
        return "multistate" if n_states > 2 else "discrete"
    return None   # blank → NOT NULL violation → row reported and skipped


def read_records(path):
    """
    Read the CSV, merging broken continuation rows into the record above.

    A few cells in the file wrapped onto extra lines (e.g. 'I1 lingual
    crenulations'); those lines have an empty 'character' column. Their
    text is appended to the previous record instead of being lost.
    """
    records = []
    # utf-8-sig strips the byte-order mark Excel adds before 'character'
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for line_no, row in enumerate(csv.DictReader(fh), start=2):
            if clean(row, "character"):
                row["_line"] = line_no
                records.append(row)
            elif records:
                prev = records[-1]
                for col in ("description", "state_code"):
                    extra = clean(row, col)
                    if extra:
                        prev[col] = f"{(prev[col] or '').strip()} {extra}"
    return records


# ── Foreign-key resolution: SELECT first, INSERT only if not found ───────────

def get_or_create_source(cur, citation):
    cur.execute(
        "SELECT source_id FROM sources WHERE citation = %s AND doi IS NULL",
        (citation,)
    )
    found = cur.fetchone()
    if found:
        return found["source_id"], False

    cur.execute(
        """INSERT INTO sources (citation, pub_year, doi)
           VALUES (%s, %s, %s)
           RETURNING source_id""",
        (citation, None, None)
    )
    return cur.fetchone()["source_id"], True


def get_or_create_character(cur, source_id, name, ctype, is_ordered,
                            region, protocol):
    cur.execute(
        """SELECT character_id FROM characters
           WHERE source_id = %s AND character_description = %s""",
        (source_id, name)
    )
    found = cur.fetchone()
    if found:
        return found["character_id"], False

    cur.execute(
        """INSERT INTO characters
               (character_description, character_type, is_ordered,
                anatomical_region, units, measurement_protocol, source_id)
           VALUES (%s, %s, %s, %s, %s, %s, %s)
           RETURNING character_id""",
        (name, ctype, is_ordered, region, None, protocol, source_id)
    )
    return cur.fetchone()["character_id"], True


def insert_state(cur, character_id, state_code, state_description):
    cur.execute(
        """INSERT INTO character_states
               (character_id, state_code, state_description)
           VALUES (%s, %s, %s)
           ON CONFLICT (character_id, state_code) DO NOTHING""",
        (character_id, state_code, state_description)
    )
    return cur.rowcount == 1


# ── Main loader ──────────────────────────────────────────────────────────────

def load(path):
    conn = psycopg2.connect(DSN, cursor_factory=psycopg2.extras.RealDictCursor)
    cur = conn.cursor()

    counts = {"sources": 0, "characters": 0, "character_states": 0, "errors": 0}

    for row in read_records(path):
        line_no = row["_line"]
        name = clean(row, "character")
        try:
            states = parse_states(clean(row, "state_code"))
            ctype = character_type(clean(row, "character_type"), len(states))

            # is_ordered is only allowed on multistate characters (schema CHECK)
            is_ordered = (ORDERED.get(clean(row, "multistate_type"))
                          if ctype == "multistate" else None)

            region_code = clean(row, "anatomical_region")
            region = REGION.get(region_code) if region_code else None
            if region_code and region is None:
                raise ValueError(f"unknown anatomical_region {region_code!r}")

            # Data-quality warnings (row still loads)
            declared = clean(row, "number_of_states")
            if declared and states and int(declared) != len(states):
                print(f"Line {line_no} warning: '{name}' declares {declared} "
                      f"states but {len(states)} were parsed",
                      file=sys.stderr)

            # ── Sources ──────────────────────────────────────────────────
            source_id, new = get_or_create_source(cur, clean(row, "source"))
            counts["sources"] += new

            # ── Characters ───────────────────────────────────────────────
            character_id, new = get_or_create_character(
                cur, source_id, name, ctype, is_ordered,
                region, clean(row, "description"),
            )
            counts["characters"] += new

            # ── Character states ─────────────────────────────────────────
            for code, label in states:
                counts["character_states"] += insert_state(
                    cur, character_id, code, label)

            # Commit per character so a later failure can't undo this one.
            conn.commit()

        except (psycopg2.Error, ValueError) as e:
            conn.rollback()
            counts["errors"] += 1
            msg = getattr(e, "pgerror", None) or str(e)
            print(f"Line {line_no} skipped ('{name}'): {msg.strip()}",
                  file=sys.stderr)
            continue

    cur.close()
    conn.close()

    print(f"Done. Inserted {counts['sources']} sources, "
          f"{counts['characters']} characters, "
          f"{counts['character_states']} character states "
          f"({counts['errors']} rows skipped).")


if __name__ == "__main__":
    load(sys.argv[1] if len(sys.argv) > 1 else CSV_FILE)