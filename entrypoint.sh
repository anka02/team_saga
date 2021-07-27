#!/usr/bin/env bash

set -xeo pipefail;

THIS_DIR=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)

rasa x --no-prompt &
P1=$!
rasa run actions &
P2=$!
trap 'kill $P1 $P2' EXIT

# Wait until API server is started
while ! curl "$RASA_BASE_URL/api/auth"; do sleep 1; done;

# Create guest URL
rasa_create_guest_url.py

# Wait until all processes are finished
wait $P1 $P2
