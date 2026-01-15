#!/usr/bin/env bash
set -uo pipefail

usage() {
    echo "Usage:"
    echo "  $0 --group <group-email> <project-id> <dataset.table> [dataset.table ...] [--json]"
    echo "  $0 --sa    <sa-email>    <project-id> <dataset.table> [dataset.table ...] [--json]"
    exit 1
}

# ---- JSON FLAG ----
JSON_OUTPUT=false
for arg in "$@"; do
    [[ "$arg" == "--json" ]] && JSON_OUTPUT=true
done

ARGS=()
for arg in "$@"; do
    [[ "$arg" != "--json" ]] && ARGS+=("$arg")
done
set -- "${ARGS[@]}"

[[ $# -lt 4 ]] && usage

case "$1" in
    --group)
        ACCOUNT_TYPE="group"
        ACCOUNT_EMAIL="$2"
        ;;
    --sa)
        ACCOUNT_TYPE="serviceAccount"
        ACCOUNT_EMAIL="$2"
        ;;
    *)
        usage
        ;;
esac

PROJECT="$3"
shift 3
TABLES=("$@")

MEMBER="${ACCOUNT_TYPE}:${ACCOUNT_EMAIL}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
SAFE_ACCOUNT="$(echo "$ACCOUNT_EMAIL" | sed 's/@/_/g; s/\./_/g')"
JSON_FILE="role_checked_${SAFE_ACCOUNT}_${PROJECT}_${TIMESTAMP}.json"

echo "Checking IAM roles for ${ACCOUNT_TYPE}: ${ACCOUNT_EMAIL}"
echo "Project: ${PROJECT}"
echo

$JSON_OUTPUT && JSON_RESULTS="[]"

# ---- PROJECT-LEVEL ROLES (ONCE) ----
PROJECT_ROLES=$(
    gcloud projects get-iam-policy "$PROJECT" --format=json \
    | jq -r --arg MEMBER "$MEMBER" '
        .bindings[]? | select(.members[]? == $MEMBER) | .role
    ' || true
)

# ---- TABLE LOOP ----
for FULL_TABLE in "${TABLES[@]}"; do
    echo "Table: ${FULL_TABLE}"
    DATASET="${FULL_TABLE%%.*}"
    FOUND=false

    TABLE_ROLES=$(
        bq --format=prettyjson get-iam-policy --table "${PROJECT}:${FULL_TABLE}" 2>/dev/null \
        | grep -v "^[A-Za-z]" \
        | jq -r --arg MEMBER "$MEMBER" '
            .bindings[]? | select(.members[]? == $MEMBER) | .role
        ' || true
    )

    DATASET_ROLES=$(
        bq --format=prettyjson get-iam-policy --dataset "${PROJECT}:${DATASET}" 2>/dev/null \
        | grep -v "^[A-Za-z]" \
        | jq -r --arg MEMBER "$MEMBER" '
            .bindings[]? | select(.members[]? == $MEMBER) | .role
        ' || true
    )

    if [[ -n "$TABLE_ROLES" ]]; then
        echo "  Table-level roles:"
        echo "$TABLE_ROLES" | sed 's/^/    - /'
        FOUND=true
    fi

    if [[ -n "$DATASET_ROLES" ]]; then
        echo "  Dataset-level roles:"
        echo "$DATASET_ROLES" | sed 's/^/    - /'
        FOUND=true
    fi

    if ! $FOUND; then
        echo "  No table or dataset level grants found."
    fi

    echo "--------------------------"

    if $JSON_OUTPUT; then
        JSON_RESULTS=$(jq -c \
            --arg table "$FULL_TABLE" \
            --argjson table_roles "$(printf '%s\n' "$TABLE_ROLES" | jq -R . | jq -s .)" \
            --argjson dataset_roles "$(printf '%s\n' "$DATASET_ROLES" | jq -R . | jq -s .)" \
            '. + [{
                table: $table,
                roles: {
                    table: $table_roles,
                    dataset: $dataset_roles
                }
            }]' <<< "$JSON_RESULTS")
    fi
done

# ---- PROJECT-LEVEL OUTPUT (ONCE) ----
echo
echo "Project-level roles:"
if [[ -n "$PROJECT_ROLES" ]]; then
    echo "$PROJECT_ROLES" | sed 's/^/  - /'
else
    echo "  No project-level grants found."
fi

# ---- JSON WRITE ----
if $JSON_OUTPUT; then
    jq -n \
        --arg account_type "$ACCOUNT_TYPE" \
        --arg account_email "$ACCOUNT_EMAIL" \
        --arg project "$PROJECT" \
        --arg timestamp "$TIMESTAMP" \
        --argjson table_results "$JSON_RESULTS" \
        --argjson project_roles "$(printf '%s\n' "$PROJECT_ROLES" | jq -R . | jq -s .)" \
        '{
            account_type: $account_type,
            account_email: $account_email,
            project: $project,
            checked_at: $timestamp,
            tables: $table_results,
            project_roles: $project_roles
        }' > "$JSON_FILE"

    echo
    echo "JSON output written to: $JSON_FILE"
fi

