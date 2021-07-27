#!/bin/bash

set -eo pipefail

THIS_DIR=$( (cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P) )

error() {
    echo >&2 "* Error: $*"
}

fatal() {
    error "$@"
    exit 1
}

message() {
    echo "$@"
}

IMAGE_PREFIX=${IMAGE_PREFIX:-saga}
IMAGE_TAG=${IMAGE_TAG:-latest}
IMAGE_NAME=${IMAGE_PREFIX}:${IMAGE_TAG}

usage() {
    echo "Build saga container"
    echo
    echo "$0 [options]"
    echo "options:"
    echo "  -t, --tag=                 Image name and optional tag"
    echo "                             (default: ${IMAGE_NAME})"
    echo "      --no-cache             Disable Docker cache"
    echo "      --help                 Display this help and exit"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -t|--tag)
            IMAGE_NAME="$2"
            shift 2
            ;;
        --tag=*)
            IMAGE_NAME="${1#*=}"
            shift
            ;;
        --no-cache)
            NO_CACHE=--no-cache
            shift
            ;;
        --help)
            usage
            exit
            ;;
        --)
            shift
            break
            ;;
        -*)
            fatal "Unknown option $1"
            ;;
        *)
            break
            ;;
    esac
done

echo "IMAGE_NAME:        $IMAGE_NAME"
echo "NO_CACHE:          $NO_CACHE"

set -x
time docker build $NO_CACHE \
             -t "${IMAGE_NAME}" \
             "$THIS_DIR"
set +x
echo "Successfully built docker image $IMAGE_NAME"
