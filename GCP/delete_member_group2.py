import csv
import datetime
import os
import sys
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ==========================================
# CONFIGURATION
# ==========================================
CSV_FILE_PATH = "removals.csv"
HAS_HEADER = False

# Set to True if you want to test without actually deleting anything in GCP
DRY_RUN = False

# Cache dictionary for resolved Group IDs
group_id_cache = {}


def initialize_cloud_identity_service():
    try:
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-identity.groups"]
        )
        return build("cloudidentity", "v1", credentials=credentials)
    except Exception as e:
        sys.exit(f"❌ Authentication error: Could not initialize API client. Details: {e}")


def load_pairs_from_csv(file_path, has_header=False):
    if not os.path.exists(file_path):
        sys.exit(f"❌ File Error: The file '{file_path}' was not found.")

    pairs = []
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        if has_header:
            next(reader, None)

        for line_num, row in enumerate(reader, start=1):
            if not row or len(row) < 2:
                continue

            user_email = row[0].strip().lower()
            group_email = row[1].strip().lower()

            if user_email.startswith("#"):
                continue

            if user_email and group_email:
                pairs.append((user_email, group_email))

    return pairs


def get_group_name(service, group_email):
    """Looks up and caches the internal GCP Resource Name (groups/ID)."""
    group_email = group_email.lower()
    
    if group_email in group_id_cache:
        return group_id_cache[group_email]

    try:
        response = service.groups().lookup(groupKey_id=group_email).execute()
        group_name = response.get("name")
        group_id_cache[group_email] = group_name
        return group_name
    except HttpError as e:
        if e.resp.status == 404:
            return ("ERROR_404", f"Group '{group_email}' does not exist.")
        else:
            return ("ERROR_API", f"API error looking up group '{group_email}': {e}")
    except Exception as e:
        return ("ERROR_UNKNOWN", f"Unexpected error looking up group '{group_email}': {e}")


def get_membership_name(service, group_name, member_email):
    """Looks up Membership Resource Name with pagination support."""
    member_email = member_email.lower()
    page_token = None

    try:
        while True:
            response = service.groups().memberships().list(
                parent=group_name, 
                pageToken=page_token
            ).execute()
            
            memberships = response.get("memberships", [])

            for m in memberships:
                member_key = m.get("preferredMemberKey", {}).get("id")
                if member_key and member_key.lower() == member_email:
                    return m.get("name")

            page_token = response.get("nextPageToken")
            if not page_token:
                break

        return None
    except Exception as e:
        return None


def main():
    service = initialize_cloud_identity_service()
    removal_pairs = load_pairs_from_csv(CSV_FILE_PATH, has_header=HAS_HEADER)

    if not removal_pairs:
        sys.exit(f"⚠️ No valid user-group pairs found in '{CSV_FILE_PATH}'. Exiting.")

    # Setup audit log file with timestamp
    now = datetime.datetime.now()
    timestamp_str = now.strftime("%Y%m%d_%H%M%S")
    audit_filename = f"audit_log_{timestamp_str}.txt"

    success_count = 0
    skip_count = 0
    fail_count = 0

    log_entries = []
    removed_records = []

    print(f"🚀 Loaded {len(removal_pairs)} membership pair(s) from '{CSV_FILE_PATH}'.")
    if DRY_RUN:
        print("🧪 RUNNING IN DRY-RUN MODE (No actual deletions will occur)\n")

    for user_email, group_email in removal_pairs:
        action_msg = f"Processing: [{user_email}] ➔ [{group_email}]"
        print(action_msg)

        # Step 1: Resolve Group ID
        group_result = get_group_name(service, group_email)
        
        if isinstance(group_result, tuple):
            _, err_detail = group_result
            msg = f"  ⚠️ SKIPPED: {err_detail}"
            print(f"{msg}\n")
            log_entries.append(f"[SKIPPED] {user_email} from {group_email} - Cause: {err_detail}")
            skip_count += 1
            continue

        group_name = group_result

        # Step 2: Resolve Membership ID
        membership_name = get_membership_name(service, group_name, user_email)
        if not membership_name:
            msg = f"User '{user_email}' is not a member of '{group_email}'."
            print(f"  ⚠️ SKIPPED: {msg}\n")
            log_entries.append(f"[SKIPPED] {user_email} from {group_email} - Cause: Not a member")
            skip_count += 1
            continue

        # Step 3: Trigger API Delete Request or Dry-Run Simulation
        if DRY_RUN:
            print(f"  🧪 [DRY-RUN] Would remove [{user_email}] from [{group_email}].\n")
            log_entries.append(f"[DRY-RUN] {user_email} from {group_email}")
            removed_records.append((user_email, group_email))
            success_count += 1
        else:
            try:
                service.groups().memberships().delete(name=membership_name).execute()
                print(f"  ✅ Successfully removed [{user_email}] from [{group_email}].\n")
                log_entries.append(f"[SUCCESS] Removed {user_email} from {group_email}")
                removed_records.append((user_email, group_email))
                success_count += 1
            except Exception as e:
                print(f"  ❌ Deletion failed for [{user_email}]: {e}\n")
                log_entries.append(f"[FAILED] {user_email} from {group_email} - Error: {e}")
                fail_count += 1

    # Write Audit File
    with open(audit_filename, mode="w", encoding="utf-8") as log_file:
        log_file.write("=" * 60 + "\n")
        log_file.write("GCP CLOUD IDENTITY GROUP REMOVAL AUDIT LOG\n")
        log_file.write("=" * 60 + "\n")
        log_file.write(f"Timestamp      : {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Mode           : {'DRY-RUN (Simulated)' if DRY_RUN else 'LIVE EXECUTION'}\n")
        log_file.write(f"Total Targets  : {len(removal_pairs)}\n")
        log_file.write(f"Successful     : {success_count}\n")
        log_file.write(f"Skipped        : {skip_count}\n")
        log_file.write(f"Failed         : {fail_count}\n")
        log_file.write("=" * 60 + "\n\n")

        log_file.write("LIST OF SUCCESSFULLY REMOVED MEMBERS:\n")
        log_file.write("-" * 60 + "\n")
        if removed_records:
            for user, group in removed_records:
                log_file.write(f" - Member: {user:<30} | Group: {group}\n")
        else:
            log_file.write(" None\n")

        log_file.write("\n\nDETAILED EXECUTION LOG:\n")
        log_file.write("-" * 60 + "\n")
        for entry in log_entries:
            log_file.write(f"{entry}\n")

    print("=" * 40)
    print("📊 EXECUTION SUMMARY")
    print(f"  - Removed : {success_count}")
    print(f"  - Skipped : {skip_count}")
    print(f"  - Failed  : {fail_count}")
    print(f"📝 Audit log written to: {audit_filename}")
    print("=" * 40)


if __name__ == "__main__":
    main()
