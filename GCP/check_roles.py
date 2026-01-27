#!/usr/bin/env python3
import argparse
import subprocess
import json
import re
from datetime import datetime, timezone

BQ_CMD = "bq"
GCLOUD_CMD = "gcloud"

def run_cmd(cmd):
    """Run shell command and return JSON parsed output"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(cmd)}")
        print(e.stderr)
        return {}
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON from command: {' '.join(cmd)}")
        return {}
def run_cmd_debug(cmd):
    """Run shell command, return parsed JSON or {} on failure, with debug"""
    try:
        print(f"Running command: {' '.join(cmd)}")  # debug
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Command stdout:\n{result.stdout}")  # debug
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(cmd)}")
        print(f"Return code: {e.returncode}")
        print(f"stdout:\n{e.stdout}")
        print(f"stderr:\n{e.stderr}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON from command: {' '.join(cmd)}")
        print(f"JSON error: {e}")
        return {}

def get_project_roles(project_id, member_lower):
    policy = run_cmd([GCLOUD_CMD, "projects", "get-iam-policy", project_id, "--format=json"])
    roles = []
    for binding in policy.get("bindings", []):
        for m in binding.get("members", []):
            if m.lower() == member_lower:
                roles.append(binding["role"])
    return roles

def get_dataset_roles(project_id, dataset_id, email_lower):
    """Get dataset roles from .access (no allowlist needed)"""
    roles = []
    dataset_json = run_cmd([BQ_CMD, "--format=json", "show", f"{project_id}:{dataset_id}"])
    for entry in dataset_json.get("access", []):
        # Check group email
        if entry.get("groupByEmail", "").lower() == email_lower:
            role = entry.get("role")
            mapped = {"READER": "Viewer", "WRITER": "Editor", "OWNER": "Owner"}.get(role, role)
            roles.append(f"{mapped} (dataset ACL)")
        # Check user email (for service accounts)
        if entry.get("userByEmail", "").lower() == email_lower:
            role = entry.get("role")
            mapped = {"READER": "Viewer", "WRITER": "Editor", "OWNER": "Owner"}.get(role, role)
            roles.append(f"{mapped} (dataset ACL)")
        # Check special groups (like allAuthenticatedUsers)
        if "specialGroup" in entry and entry["specialGroup"].lower() == email_lower:
            role = entry.get("role")
            mapped = {"READER": "Viewer", "WRITER": "Editor", "OWNER": "Owner"}.get(role, role)
            roles.append(f"{mapped} (dataset special group)")
    return roles

def get_table_roles(project_id, table_full, member_lower):
    """Get table IAM roles (tables do not have legacy ACLs)"""
    table_policy = run_cmd([BQ_CMD, "--format=json", "get-iam-policy", "--table", f"{project_id}:{table_full}"])
    roles = []
    for binding in table_policy.get("bindings", []):
        for m in binding.get("members", []):
            if m.lower() == member_lower:
                roles.append(binding["role"])
    return roles

def main():
    parser = argparse.ArgumentParser(description="Check GCP IAM roles for groups or service accounts (case-insensitive)")
    parser.add_argument("--group", help="Group email")
    parser.add_argument("--sa", help="Service account email")
    parser.add_argument("project", help="Project ID")
    parser.add_argument("tables", nargs="+", help="Tables in dataset.table format")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if args.group:
        account_type = "group"
        email = args.group
    elif args.sa:
        account_type = "serviceAccount"
        email = args.sa
    else:
        parser.error("Must specify --group or --sa")

    member = f"{account_type}:{email}"
    member_lower = member.lower()  # normalize for case-insensitive comparison
    email_lower = email.lower()    # for dataset ACL matching

    project = args.project
    tables = args.tables
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    results = []

    print(f"Checking roles for {account_type}: {email}")
    print(f"Project: {project}\n")

    # Project-level roles
    project_roles = get_project_roles(project, member_lower)

    # Table loop
    for full_table in tables:
        dataset = full_table.split(".")[0]

        table_roles = get_table_roles(project, full_table, member_lower)
        dataset_roles = get_dataset_roles(project, dataset, email_lower)

        found = table_roles or dataset_roles

        print(f"Table: {full_table}")
        if table_roles:
            print("  Table-level roles:")
            for r in table_roles:
                print(f"    - {r}")
        if dataset_roles:
            print("  Dataset-level roles:")
            for r in dataset_roles:
                print(f"    - {r}")
        if not found:
            print("  No table or dataset level grants found.")
        print("--------------------------")

        results.append({
            "table": full_table,
            "roles": {
                "table": table_roles,
                "dataset": dataset_roles
            }
        })

    # Project-level output
    print("\nProject-level roles:")
    if project_roles:
        for r in project_roles:
            print(f"  - {r}")
    else:
        print("  No project-level grants found.")

    # JSON output
    if args.json:
        output = {
            "account_type": account_type,
            "account_email": email,
            "project": project,
            "checked_at": timestamp,
            "tables": results,
            "project_roles": project_roles
        }
        json_file = f"role_checked_{re.sub(r'[@.]','_', email)}_{project}_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nJSON output written to: {json_file}")

if __name__ == "__main__":
    main()

