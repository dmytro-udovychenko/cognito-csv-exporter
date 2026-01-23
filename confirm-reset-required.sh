#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   AWS_PROFILE=shift-dev ./scripts/confirm-reset-required.sh us-east-1_VC87i2BIY
# Or:
#   AWS_PROFILE=shift-dev USER_POOL_ID=us-east-1_VC87i2BIY ./scripts/confirm-reset-required.sh

AWS_PROFILE="${AWS_PROFILE:-shift-dev}"
USER_POOL_ID="${USER_POOL_ID:-${1:-}}"
DRY_RUN="${DRY_RUN:-false}"
TEMP_PASSWORD="${TEMP_PASSWORD:-}"

if [[ -z "${USER_POOL_ID}" ]]; then
  echo "ERROR: user pool id is required."
  echo "Usage: AWS_PROFILE=shift-dev ./scripts/confirm-reset-required.sh us-east-1_VC87i2BIY"
  exit 1
fi

if ! command -v aws >/dev/null 2>&1; then
  echo "ERROR: aws CLI not found."
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq not found."
  exit 1
fi

echo "Using AWS_PROFILE=${AWS_PROFILE}"
echo "User pool: ${USER_POOL_ID}"
echo "Dry run: ${DRY_RUN}"
if [[ -n "${TEMP_PASSWORD}" ]]; then
  echo "Temp password: set via TEMP_PASSWORD"
else
  echo "Temp password: auto-generated per user"
fi

generate_password() {
  if command -v python3 >/dev/null 2>&1; then
    python3 - <<'PY'
import secrets
import string
alphabet = string.ascii_letters + string.digits
special = "!@#$%*_-+=?"
pw = ''.join(secrets.choice(alphabet) for _ in range(12)) + secrets.choice(special) + "Aa1"
print(pw)
PY
    return 0
  fi
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -base64 24 | tr -d '\n' | sed 's/[+/]/A/g' | awk '{print $0 "Aa1!"}'
    return 0
  fi
  echo "TempPassw0rd!Aa1"
}

users_json="$(aws cognito-idp list-users \
  --user-pool-id "${USER_POOL_ID}" \
  --profile "${AWS_PROFILE}" \
  --output json)"

reset_users=()
while IFS= read -r username; do
  reset_users+=("${username}")
done <<<"$(echo "${users_json}" | jq -r '.Users[] | select(.UserStatus=="RESET_REQUIRED") | .Username')"

if [[ "${#reset_users[@]}" -eq 0 ]]; then
  echo "No users with status RESET_REQUIRED found."
  exit 0
fi

echo "Found ${#reset_users[@]} users with status RESET_REQUIRED."

confirmed=0
for username in "${reset_users[@]}"; do
  if [[ "${DRY_RUN}" == "true" ]]; then
    echo "[dry-run] Would confirm: ${username}"
    continue
  fi

  password="${TEMP_PASSWORD}"
  if [[ -z "${password}" ]]; then
    password="$(generate_password)"
  fi

  echo "Setting permanent password (and confirming): ${username}"
  aws cognito-idp admin-set-user-password \
    --user-pool-id "${USER_POOL_ID}" \
    --username "${username}" \
    --password "${password}" \
    --permanent \
    --profile "${AWS_PROFILE}" >/dev/null
  confirmed=$((confirmed + 1))
done

echo "Done. Confirmed ${confirmed} users."
