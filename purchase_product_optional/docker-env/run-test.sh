#!/usr/bin/env bash
# run-test.sh — wrapper for every G1/Step 9 Docker test run (from migration-tool
# templates/run-test.sh.template, as adapted by project optional_field_save 19->20).
#
# Why this exists:
# 1. `--test-tags /purchase_product_optional` gets mangled by MSYS/Git Bash on Windows into a Windows
#    path -> empty tag filter -> "0 failed, 0 error(s) of 0 tests" false pass. MSYS_NO_PATHCONV=1 is
#    forced here.
# 2. Re-running `-i` on a DB where the module is already installed silently skips install + tests
#    (same false-pass signature). This wrapper always `docker compose down -v` first.
# Sanity check: fails (exit 2) when no "Starting <Class>.<method>" line appears in the log.
#
# Usage (from docker-env/): ./run-test.sh <db_name> [extra_tags] [extra_modules]
#   extra_modules (comma list) are installed alongside and switch the addons path to include
#   Enterprise 20.0 (/opt/enterprise), e.g. ./run-test.sh ppo_ent "" account_budget_purchase
set -euo pipefail

DB_NAME="${1:-purchase_product_optional_20_test}"
EXTRA_TAGS="${2:-}"
EXTRA_MODULES="${3:-}"
MODULE_NAME="purchase_product_optional"
TAGS="/${MODULE_NAME}${EXTRA_TAGS}"
LOGFILE="./logs/run-test-$(date +%Y%m%d-%H%M%S).log"
ADDONS_PATH="/opt/odoo/addons,/opt/odoo/odoo/addons,/mnt/extra-addons"
INSTALL="${MODULE_NAME}"
if [ -n "${EXTRA_MODULES}" ]; then
  ADDONS_PATH="/opt/odoo/addons,/opt/odoo/odoo/addons,/opt/enterprise,/mnt/extra-addons"
  INSTALL="${MODULE_NAME},${EXTRA_MODULES}"
fi

echo "=== db=${DB_NAME} tags=${TAGS} log=${LOGFILE} ==="
docker compose down -v 2>&1 | tail -5

MSYS_NO_PATHCONV=1 docker compose run --rm odoo \
  -d "${DB_NAME}" -i "${INSTALL}" \
  --addons-path="${ADDONS_PATH}" \
  --test-enable --test-tags "${TAGS}" --stop-after-init 2>&1 | tee "${LOGFILE}"

STARTED_COUNT=$(grep -c "Starting " "${LOGFILE}" || true)
SUMMARY_LINE=$(grep -E "[0-9]+ failed, [0-9]+ error\(s\) of [0-9]+ tests" "${LOGFILE}" | tail -1 || true)
echo ""
echo "Started test methods: ${STARTED_COUNT}"
echo "Odoo summary: ${SUMMARY_LINE:-'(not found)'}"

docker compose down -v 2>&1 | tail -5

if [ "${STARTED_COUNT}" -eq 0 ]; then
  echo "FAILED — 0 tests started (false-pass pattern). Inspect ${LOGFILE}."
  exit 2
fi
