#!/bin/sh
set -eu
set -x

JOB_NAME="country-popularity"
JOB_FILE="/jobs/weekly_country_popularity.py"
FLINK_BIN="/opt/flink/bin/flink"
JOBMANAGER="flink-jobmanager:8081"

flink_list() {
  if command -v timeout >/dev/null 2>&1; then
    timeout 10 "$FLINK_BIN" list -m "$JOBMANAGER"
  else
    "$FLINK_BIN" list -m "$JOBMANAGER"
  fi
}

tries=0
while [ "$tries" -lt 30 ]; do
  if list_output=$(flink_list 2>&1); then
    break
  fi
  echo "Flink list failed (attempt $tries):"
  echo "$list_output"
  tries=$((tries + 1))
  sleep 3
done

if ! flink_list >/dev/null 2>&1; then
  echo "Flink JobManager not reachable at $JOBMANAGER"
  exit 1
fi

list_output=$(flink_list 2>/dev/null || true)
existing_id=$(printf "%s\n" "$list_output" | awk -v name="$JOB_NAME" '
  $0 ~ name {print $1; exit}
  / : / && $0 ~ name {split($0, a, " : "); print a[1]; exit}
')

if [ -n "${existing_id:-}" ]; then
  echo "Flink job '$JOB_NAME' already running. Canceling $existing_id."
  $FLINK_BIN cancel -m "$JOBMANAGER" "$existing_id" || true
  sleep 3
fi

exec $FLINK_BIN run -m "$JOBMANAGER" -D "pipeline.name=$JOB_NAME" -py "$JOB_FILE"
