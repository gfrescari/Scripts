#!/usr/bin/env bash

# Usage:
# ./check_sa_roles.sh PROJECT SERVICE_ACCOUNT DATASET1.TABLE1 DATASET2.TABLE2 ...
PROJECT="$1"
SA="$2"
shift 2
TABLES=("$@")

echo "Checking IAM roles for service account: $SA"
echo "Project: $PROJECT"
echo

for FULL_TABLE in "${TABLES[@]}"; do
    echo "Table: $FULL_TABLE"

    DATASET="${FULL_TABLE%%.*}"
    FOUND=false

    # --- TABLE LEVEL ---
    TABLE_ROLES=$(bq --format=prettyjson get-iam-policy --table "$PROJECT:$FULL_TABLE" 2>/dev/null \
        | grep -v "^[A-Za-z]" \
        | jq -r --arg SA "serviceAccount:$SA" '
            .bindings[]? | select(.members[]? == $SA) | .role
        ')

    if [[ -n "$TABLE_ROLES" ]]; then
        echo "  Table-level roles:"
        echo "$TABLE_ROLES" | sed "s/^/    - /"
        FOUND=true
    fi

    # --- DATASET LEVEL ---
    DATASET_ROLES=$(bq --format=prettyjson get-iam-policy --dataset "$PROJECT:$DATASET" 2>/dev/null \
        | grep -v "^[A-Za-z]" \
        | jq -r --arg SA "serviceAccount:$SA" '
            .bindings[]? | select(.members[]? == $SA) | .role
        ')

    if [[ -n "$DATASET_ROLES" ]]; then
        echo "  Dataset-level roles:"
        echo "$DATASET_ROLES" | sed "s/^/    - /"
        FOUND=true
    fi

    # --- PROJECT LEVEL ---
    PROJECT_ROLES=$(gcloud projects get-iam-policy "$PROJECT" --format=json \
        | jq -r --arg SA "serviceAccount:$SA" '
            .bindings[]? | select(.members[]? == $SA) | .role
        ')

    if [[ -n "$PROJECT_ROLES" ]]; then
        echo "  Project-level roles:"
        echo "$PROJECT_ROLES" | sed "s/^/    - /"
        FOUND=true
    fi

    # --- RESULTS ---
    if [[ "$FOUND" == false ]]; then
        echo "  No grants found at table, dataset, or project level."
    fi

    echo "--------------------------"
done
