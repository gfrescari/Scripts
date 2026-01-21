#!/usr/bin/env python3
import subprocess
import json
import csv
import time
from pathlib import Path

# =========================
# CONFIGURATION
# =========================
ORG_ID = "214139495384"  # replace with your org ID
OUTPUT_FILE = Path("groups_and_members.csv")
PAGE_SIZE = 5           # adjust for faster fetching

# =========================
# UTILITY FUNCTIONS
# =========================
def run_gcloud(args):
    """Run a gcloud command and return parsed JSON"""
    result = subprocess.run(
        ["gcloud"] + args,
        capture_output=True,
        text=True,
        check=True
    )
    return json.loads(result.stdout)

# =========================
# FETCH ALL GROUPS
# =========================
print("Fetching groups...")
groups_raw = run_gcloud([
    "identity", "groups", "search",
    f"--organization={ORG_ID}",
    "--labels=cloudidentity.googleapis.com/groups.discussion_forum",
    f"--format=json",
    f"--page-size={PAGE_SIZE}"
])

# Flatten nested groups arrays
groups_list = []
for item in groups_raw:
    if "groups" in item:
        groups_list.extend(item["groups"])

print(f"Found {len(groups_list)} groups")

# =========================
# WRITE CSV
# =========================
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["group_email", "group_name", "member_id", "member_type", "roles"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for idx, group in enumerate(groups_list, start=1):
        group_email = group.get("groupKey", {}).get("id")
        group_name = group.get("displayName", "")

        if not group_email:
            continue

        print(f"[{idx}/{len(groups_list)}] Processing group: {group_email}")

        # Fetch members
        try:
            members_raw = run_gcloud([
                "identity", "groups", "memberships", "list",
                f"--group-email={group_email}",
                "--format=json"
            ])
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Failed to fetch members for {group_email}: {e}")
            members_raw = []

        if not members_raw:
            # Write a row with empty member fields if group has no members
            writer.writerow({
                "group_email": group_email,
                "group_name": group_name,
                "member_id": "",
                "member_type": "",
                "roles": ""
            })
            continue

        # Write each member as a row
        for m in members_raw:
            member_id = m.get("preferredMemberKey", {}).get("id", "")
            member_type = m.get("preferredMemberKey", {}).get("namespace", "UNKNOWN")
            roles = [r.get("name") for r in m.get("roles", [])]
            roles_str = ",".join(roles)  # join multiple roles into one CSV field

            writer.writerow({
                "group_email": group_email,
                "group_name": group_name,
                "member_id": member_id,
                "member_type": member_type,
                "roles": roles_str
            })
        time.sleep(0.5)

print(f"✅ Wrote CSV with groups and members to {OUTPUT_FILE}")

