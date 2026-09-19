#!/usr/bin/env bash
# dataset_report.sh
# Generate a summary report of all TSV files in a directory.
# Usage: ./dataset_report.sh <directory>
#
# Author: Jyhreh Johnson
# Date: 2026-09-15

# ── Argument handling ────────────────────────────────────────────────────────

if [ $# -ne 1 ]; then
    echo "Usage: $0 <directory>"
    echo "Example: $0 ~/Documents/UT/comp_paleo/part1_OS/week03"
    exit 1
fi

DIRPATH="$1"

if [ ! -d "$DIRPATH" ]; then
    echo "Error: not a directory: $DIRPATH"
    exit 1
fi

# ── Initialise counters and log file ─────────────────────────────────────────

TOTAL_FILES=0
TOTAL_ROWS=0
SMALL_FILES=0
OVERALL_ERRORS=0
SMALL_LOG="small_files.log"


> "$SMALL_LOG"

echo "Dataset Report"
echo "Directory: $DIRPATH"
echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

# ── Main loop: process each TSV file ─────────────────────────────────────────

for FILEPATH in "$DIRPATH"/*.tsv; do
    [ -e "$FILEPATH" ] || continue

    FILENAME=$(basename "$FILEPATH")
    ROWS=$(tail -n +2 "$FILEPATH" | wc -l | tr -d ' ')
    COLS=$(head -1 "$FILEPATH" | tr '\t' '\n' | wc -l | tr -d ' ')
    FIELDS=$(head -1 "$FILEPATH" | tr '\t' '\n' | head -3 | paste -sd '|' - | sed 's/|/ | /g')


    BAD_ROWS=$(awk -F'\t' -v cols="$COLS" 'NF != cols {c++} END {print c+0}' "$FILEPATH")
    if [ "$BAD_ROWS" -eq 0 ]; then
        VALIDATION="PASS"
    else
        VALIDATION="FAIL"
        OVERALL_ERRORS=$((OVERALL_ERRORS + 1))
    fi

    echo ""
    echo "File: $FILENAME"
    echo "  Rows:    $ROWS"
    echo "  Columns: $COLS"
    echo "  Fields:  $FIELDS"
    echo "  Validation: $VALIDATION"

    TOTAL_FILES=$((TOTAL_FILES + 1))
    TOTAL_ROWS=$((TOTAL_ROWS + ROWS))

    if [ "$ROWS" -lt 100 ]; then
        SMALL_FILES=$((SMALL_FILES + 1))
        echo "$FILENAME: $ROWS rows" >> "$SMALL_LOG"
    fi
done

# ── Summary ───────────────────────────────────────────────────────────────────

echo ""
echo "============================================================"
echo "Summary"
echo "  Files processed: $TOTAL_FILES"
echo "  Total rows:      $TOTAL_ROWS"
echo "  Small files:     $SMALL_FILES"

if [ "$OVERALL_ERRORS" -eq 0 ]; then
    echo "  Overall result:  PASS"
    exit 0
else
    echo "  Overall result:  FAIL"
    exit 1
fi
