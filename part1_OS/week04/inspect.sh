!#/usr/bin/env bash



FILEPATH="$1"

FILENAME=$(baseman "$FILEPATH")
ROW_COUNT=$(tail -n +2 "$FILEPATH" | wc -l)
COL_COUNT=$(head -1 "F$ILEPATH" | tr '\t' '\n' | wc -l)
DATACOUNT=$((ROW_COUNT * COL_COUNT))

echo "======================="
echo "File: 	$FILEPATH"
echo "Rows:		$ROW_COUNT (excluding header)"
echo "Columns:	$COL_COUNT"
echo "Datacount: $DATACOUNT"
