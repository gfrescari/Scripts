#!/usr/bin/env bash

# Usage:
# ./check_group_roles.sh PROJECT GROUP_EMAIL DATASET1.TABLE1 DATASET2.TABLE2 ...

PROJECT="$1"
GROUP="$2"
shift 2
TABLES=("$@")

echo "Checking IAM roles for group: $GROUP"
echo "Project: $PROJECT"
echo

for FULL_TABLE in "${TABLES[@]}"; do
    echo "Table: $FULL_TABLE"

    DATASET="${FULL_TABLE%%.*}"
    FOUND_ANY=false

    # --- TABLE LEVEL ---
    TABLE_ROLES=$(bq --format=prettyjson get-iam-policy --table "$PROJECT:$FULL_TABLE" 2>/dev/null \
        | grep -v "^[A-Za-z]" \
        | jq -r --arg GROUP "group:$GROUP" '
            .bindings[]? | select(.members[]? == $GROUP) | .role
        ')

    if [[ -n "$TABLE_ROLES" ]]; then
        echo "  Table-level roles:"
        echo "$TABLE_ROLES" | sed "s/^/    - /"
        FOUND_ANY=true
    fi

    # --- DATASET LEVEL ---
    DATASET_ROLES=$(bq --format=prettyjson get-iam-policy --dataset "$PROJECT:$DATASET" 2>/dev/null \
        | grep -v "^[A-Za-z]" \
        | jq -r --arg GROUP "group:$GROUP" '
            .bindings[]? | select(.members[]? == $GROUP) | .role
        ')

    if [[ -n "$DATASET_ROLES" ]]; then
        echo "  Dataset-level roles:"
        echo "$DATASET_ROLES" | sed "s/^/    - /"
        FOUND_ANY=true
    fi

    # --- PROJECT LEVEL ---
    PROJECT_ROLES=$(gcloud projects get-iam-policy "$PROJECT" --format=json \
        | jq -r --arg GROUP "group:$GROUP" '
            .bindings[]? | select(.members[]? == $GROUP) | .role
        ')

    if [[ -n "$PROJECT_ROLES" ]]; then
        echo "  Project-level roles:"
        echo "$PROJECT_ROLES" | sed "s/^/    - /"
        FOUND_ANY=true
    fi

    # --- RESULTS ---
    if [[ "$FOUND_ANY" = false ]]; then
        echo "  No grants found at table, dataset, or project level."
    fi

    echo "--------------------------"
done
