import subprocess
import json
import sys

if len(sys.argv) < 4:
    print("Usage: python script.py <PROJECT_ID> <MEMBER> <ROLE1> [ROLE2 ROLE3 ...]")
    print("Example:")
    print("  python script.py my-project group:team@example.com roles/viewer roles/editor")
    sys.exit(1)

project_id = sys.argv[1]
member = sys.argv[2]
input_roles = sys.argv[3:]  # multiple roles

# Get IAM policy
cmd = [
    "gcloud", "projects", "get-iam-policy", project_id,
    "--format=json"
]

result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode != 0:
    print("Error running gcloud command:")
    print(result.stderr)
    sys.exit(1)

policy = json.loads(result.stdout)

# Extract roles for the member
assigned_roles = set()
for binding in policy.get("bindings", []):
    if member in binding.get("members", []):
        assigned_roles.add(binding["role"])

# Compare roles
print(f"Project: {project_id}")
print(f"Roles assigned to {member}:")
for role in sorted(assigned_roles):
    print(f"  {role}")

print("\nRole check results:")
for role in input_roles:
    if role in assigned_roles:
        print(f"  ✅ {role} EXISTS")
    else:
        print(f"  ❌ {role} NOT FOUND")
