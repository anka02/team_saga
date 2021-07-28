#!/bin/bash

THIS_DIR=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)

IMAGE_PREFIX=${IMAGE_PREFIX:-saga}
IMAGE_TAG=${IMAGE_TAG:-latest}
IMAGE_NAME=${IMAGE_PREFIX}:${IMAGE_TAG}

cd "$THIS_DIR"
ARGS=()

set -xe
docker run "${ARGS[@]}" \
       -p 5002:5002 \
       --name="$IMAGE_PREFIX" \
       --rm -ti "${IMAGE_NAME}" "$@"
