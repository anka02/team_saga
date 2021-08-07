#!/usr/bin/env bash

set -eo pipefail;

THIS_DIR=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)

. /usr/src/app/venv/bin/activate

set -x
rasa x --no-prompt &
P1=$!
rasa run actions &
P2=$!
trap 'kill $P1 $P2' EXIT
set +x

# Wait until API server is started
while ! curl --silent "$RASA_BASE_URL/api/auth"; do
    echo "Waiting for the start of the RASA server ..."
    sleep 1;
done;

set -x
# Create guest URL
rasa_create_guest_url.py

# Wait until all processes are finished
wait $P1 $P2
