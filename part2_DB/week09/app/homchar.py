# app/homchar.py — Flask app for the Hominin Character State Database

import psycopg2
import psycopg2.extras
from psycopg2 import errors as pg_errors
from flask import Flask, render_template, request, redirect, url_for

from config import DSN

app = Flask(__name__)

# Controlled vocabularies (must match the CHECK constraints in schema.sql)
CHARACTER_TYPES = ['discrete', 'multistate', 'continuous']
REGIONS         = ['Cranial', 'Craniofacial', 'Dental', 'Postcranial']
UNITS           = ['mm', 'degrees']

# Friendly messages for each CHECK constraint, keyed by the name
# PostgreSQL gives the constraint.
CHECK_MESSAGES = {
    'sources_pub_year_check':
        "Publication year must be between 1800 and 2100.",
    'characters_is_ordered_check':
        "Ordered must be 0 (unordered) or 1 (ordered).",
    'characters_character_type_check':
        "Character type must be discrete, multistate, or continuous.",
    'characters_anatomical_region_check':
        "Anatomical region must be Cranial, Craniofacial, Dental, or Postcranial.",
    'characters_units_check':
        "Units must be mm or degrees.",
    'characters_check':
        "Only multistate characters can be marked ordered or unordered.",
    'characters_check1':
        "Only continuous characters can have units.",
    'character_states_state_code_check':
        "State code must be a whole number from 0 to 9.",
}


def check_message(e):
    """Turn a CheckViolation into a readable message."""
    return CHECK_MESSAGES.get(e.diag.constraint_name,
                              "A value broke one of the database rules.")


# ── Database helper ──────────────────────────────────────────────────────────

def get_db():
    return psycopg2.connect(DSN,
        cursor_factory=psycopg2.extras.RealDictCursor)


def blank_to_none(field):
    """Read an optional form field; empty strings become None (SQL NULL)."""
    value = request.form.get(field, '').strip()
    return value or None


# ── Index ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT COUNT(*) AS n FROM sources")
    n_sources = cur.fetchone()['n']
    cur.execute("SELECT COUNT(*) AS n FROM characters")
    n_characters = cur.fetchone()['n']
    cur.execute("SELECT COUNT(*) AS n FROM character_states")
    n_states = cur.fetchone()['n']
    cur.execute("""
        SELECT anatomical_region, COUNT(*) AS n
        FROM   characters
        GROUP  BY anatomical_region
        ORDER  BY anatomical_region
    """)
    by_region = cur.fetchall()
    conn.close()
    return render_template('index.html',
        n_sources=n_sources, n_characters=n_characters,
        n_states=n_states, by_region=by_region)


# ── Sources ──────────────────────────────────────────────────────────────────

@app.route('/sources')
def list_sources():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        SELECT s.source_id, s.citation, s.pub_year, s.doi,
               COUNT(c.character_id) AS n_characters
        FROM   sources s
        LEFT JOIN characters c ON c.source_id = s.source_id
        GROUP  BY s.source_id
        ORDER  BY s.citation
    """)
    rows = cur.fetchall()
    conn.close()
    return render_template('sources_list.html', rows=rows)


@app.route('/sources/new', methods=['GET', 'POST'])
def new_source():
    error = None
    if request.method == 'POST':
        citation = request.form.get('citation', '').strip()
        pub_year = blank_to_none('pub_year')
        doi      = blank_to_none('doi')
        conn = get_db()
        cur  = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO sources (citation, pub_year, doi)"
                " VALUES (%s, %s, %s)",
                (citation or None, pub_year, doi)
            )
            conn.commit()
            return redirect(url_for('list_sources'))
        except pg_errors.NotNullViolation:
            conn.rollback()
            error = "Citation is required."
        except pg_errors.UniqueViolation:
            conn.rollback()
            error = "A source with that DOI already exists."
        except pg_errors.CheckViolation as e:
            conn.rollback()
            error = check_message(e)
        except pg_errors.InvalidTextRepresentation:
            conn.rollback()
            error = "Publication year must be a whole number."
        finally:
            conn.close()
    return render_template('sources_form.html', error=error, form=request.form)


# ── Characters ───────────────────────────────────────────────────────────────

@app.route('/characters')
def list_characters():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        SELECT c.character_id, c.character_description, c.character_type,
               c.is_ordered, c.anatomical_region, c.units,
               s.citation,
               COUNT(cs.state_id) AS n_states
        FROM   characters c
        JOIN   sources s ON s.source_id = c.source_id
        LEFT JOIN character_states cs ON cs.character_id = c.character_id
        GROUP  BY c.character_id, s.citation
        ORDER  BY c.character_id
    """)
    rows = cur.fetchall()
    conn.close()
    return render_template('characters_list.html', rows=rows)


@app.route('/characters/new', methods=['GET', 'POST'])
def new_character():
    error = None
    if request.method == 'POST':
        description = request.form.get('character_description', '').strip()
        ctype       = blank_to_none('character_type')
        is_ordered  = blank_to_none('is_ordered')
        region      = blank_to_none('anatomical_region')
        units       = blank_to_none('units')
        protocol    = blank_to_none('measurement_protocol')
        source_id   = blank_to_none('source_id')
        conn = get_db()
        cur  = conn.cursor()
        try:
            cur.execute(
                """INSERT INTO characters
                       (character_description, character_type, is_ordered,
                        anatomical_region, units, measurement_protocol,
                        source_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (description or None, ctype, is_ordered, region, units,
                 protocol, source_id)
            )
            conn.commit()
            return redirect(url_for('list_characters'))
        except pg_errors.NotNullViolation:
            conn.rollback()
            error = "Description, character type, and source are required."
        except pg_errors.CheckViolation as e:
            conn.rollback()
            error = check_message(e)
        except pg_errors.ForeignKeyViolation:
            conn.rollback()
            error = "The selected source no longer exists."
        finally:
            conn.close()

    # Live dropdown for the source_id foreign key
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT source_id, citation FROM sources ORDER BY citation")
    sources = cur.fetchall()
    conn.close()
    return render_template('characters_form.html',
        error=error, form=request.form, sources=sources,
        character_types=CHARACTER_TYPES, regions=REGIONS, units=UNITS)


# ── Character states ─────────────────────────────────────────────────────────

@app.route('/states')
def list_states():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        SELECT cs.state_id, cs.state_code, cs.state_description,
               c.character_id, c.character_description
        FROM   character_states cs
        JOIN   characters c ON c.character_id = cs.character_id
        ORDER  BY c.character_id, cs.state_code
    """)
    rows = cur.fetchall()
    conn.close()
    return render_template('character_states_list.html', rows=rows)


@app.route('/states/new', methods=['GET', 'POST'])
def new_state():
    error = None
    if request.method == 'POST':
        character_id = blank_to_none('character_id')
        state_code   = blank_to_none('state_code')
        description  = blank_to_none('state_description')
        conn = get_db()
        cur  = conn.cursor()
        try:
            cur.execute(
                """INSERT INTO character_states
                       (character_id, state_code, state_description)
                   VALUES (%s, %s, %s)""",
                (character_id, state_code, description)
            )
            conn.commit()
            return redirect(url_for('list_states'))
        except pg_errors.NotNullViolation:
            conn.rollback()
            error = "Character, state code, and state description are required."
        except pg_errors.UniqueViolation:
            conn.rollback()
            error = "That character already has a state with this code."
        except pg_errors.CheckViolation as e:
            conn.rollback()
            error = check_message(e)
        except pg_errors.ForeignKeyViolation:
            conn.rollback()
            error = "The selected character no longer exists."
        except pg_errors.InvalidTextRepresentation:
            conn.rollback()
            error = "State code must be a whole number."
        finally:
            conn.close()

    # Live dropdown for the character_id foreign key
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""SELECT character_id, character_description
                   FROM characters ORDER BY character_description""")
    characters = cur.fetchall()
    conn.close()
    return render_template('character_states_form.html',
        error=error, form=request.form, characters=characters)