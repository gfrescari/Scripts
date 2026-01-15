#!/bin/bash

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 project.dataset.table [project.dataset.table ...]"
  exit 1
fi

for INPUT in "$@"; do
  # Split project.dataset.table
  PROJECT="${INPUT%%.*}"
  REST="${INPUT#*.}"
  DATASET="${REST%%.*}"
  TABLE="${REST#*.}"

  # Validate format
  if [ -z "$PROJECT" ] || [ -z "$DATASET" ] || [ -z "$TABLE" ]; then
    echo "$INPUT : INVALID FORMAT (expected project.dataset.table)"
    continue
  fi

  # Convert to BigQuery format
  BQ_TABLE="${PROJECT}:${DATASET}.${TABLE}"

  OUTPUT=$(bq show "$BQ_TABLE" 2>&1)
  STATUS=$?

  if [ $STATUS -eq 0 ]; then
    echo "$INPUT : FOUND"
  elif echo "$OUTPUT" | grep -qi "Not found"; then
    echo "$INPUT : NOT FOUND"
  elif echo "$OUTPUT" | grep -qi "Access Denied"; then
    echo "$INPUT : NO PERMISSION"
  else
    echo "$INPUT : ERROR"
    echo "  $OUTPUT"
  fi
done

