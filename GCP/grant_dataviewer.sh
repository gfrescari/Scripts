#!/bin/bash

# Validate member type flag
if [[ "$1" != "--group" && "$1" != "--sa" ]]; then
  echo "Usage:"
  echo "  $0 --group group-email dataset.table [dataset.table ...]"
  echo "  $0 --sa service-account-email dataset.table [dataset.table ...]"
  exit 1
fi

MEMBER_TYPE="$1"
MEMBER_VALUE="$2"
shift 2

if [ "$MEMBER_TYPE" = "--group" ]; then
  MEMBER="group:${MEMBER_VALUE}"
  MEMBER_LABEL="Group"
else
  MEMBER="serviceAccount:${MEMBER_VALUE}"
  MEMBER_LABEL="Service Account"
fi

PROJECT=$(gcloud info --format="value(config.project)")
TIMESTAMP=$(date +'%Y%m%d_%H%M%S')
LOG_FILE="dataviewer-${PROJECT}_${TIMESTAMP}.txt"

echo "Logging to ${LOG_FILE}"
echo "Project: ${PROJECT}" > "$LOG_FILE"
echo "Timestamp: ${TIMESTAMP}" >> "$LOG_FILE"
echo "${MEMBER_LABEL}: ${MEMBER}" >> "$LOG_FILE"
echo "----------------------------------------" >> "$LOG_FILE"

INDEX=1
for TABLE in "$@"; do
  CMD="bq add-iam-policy-binding --member=${MEMBER} --role=roles/bigquery.dataViewer --table=true ${TABLE}"

  echo "${INDEX}: Granting roles/bigquery.dataViewer to ${MEMBER} on ${TABLE}"
  echo "$CMD" >> "$LOG_FILE"

  $CMD >> "$LOG_FILE" 2>&1 && sleep 1
  INDEX=INDEX+1
done

echo "----------------------------------------" >> "$LOG_FILE"

echo
echo "==== SUCCESS SUMMARY ===="
grep "Success" "$LOG_FILE" | nl -w1 -s': ' || echo "No successful bindings found."

echo
echo "Full log saved to: $LOG_FILE"
