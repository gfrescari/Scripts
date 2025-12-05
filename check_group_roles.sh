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

    # --- TABLE LEVEL ---
    ROLES=$(bq --format=prettyjson get-iam-policy --table "$PROJECT:$FULL_TABLE" 2>/dev/null \
        | grep -v "^[A-Za-z]" \
        | jq -r --arg GROUP "group:$GROUP" '
            .bindings[]? | select(.members[]? == $GROUP) | .role
        ')

    LEVEL="table"

    # --- DATASET LEVEL ---
    if [[ -z "$ROLES" ]]; then
        ROLES=$(bq --format=prettyjson get-iam-policy --dataset "$PROJECT:$DATASET" 2>/dev/null \
            | grep -v "^[A-Za-z]" \
            | jq -r --arg GROUP "group:$GROUP" '
                .bindings[]? | select(.members[]? == $GROUP) | .role
            ')
        LEVEL="dataset"
    fi

    # --- PROJECT LEVEL ---
    if [[ -z "$ROLES" ]]; then
        ROLES=$(gcloud projects get-iam-policy "$PROJECT" --format=json \
            | jq -r --arg GROUP "group:$GROUP" '
                .bindings[]? | select(.members[]? == $GROUP) | .role
            ')
        LEVEL="project"
    fi

    # --- RESULTS ---
    if [[ -n "$ROLES" ]]; then
        echo "$ROLES" | sed "s/^/  - /"
        echo "  (Role granted at $LEVEL level)"
    else
        echo "  No grants found at table, dataset, or project level."
    fi

    echo "--------------------------"
done

