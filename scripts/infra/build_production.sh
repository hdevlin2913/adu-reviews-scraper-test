#!/bin/bash

# arguments
ADU_ENV=${ADU_ENV:-"dev"}
TARGET=$1
REGISTRY_URL=${REGISTRY_URL:-"registry.digitalocean.com/adu-stack"}
SCRIPT_DIR=$(dirname ${BASH_SOURCE[0]})

DOCKER_FILE="${SCRIPT_DIR}/../../docker/Dockerfile.production"
# This manual workflow requires login first
IMAGE_TAG=$(git rev-parse HEAD)
IMAGE_URL=${REGISTRY_URL}/${ADU_ENV}/${TARGET}:${IMAGE_TAG}

echo "Building ${TARGET}, env=${ADU_ENV} image URL=$IMAGE_URL"

docker build --platform linux/amd64 -f $DOCKER_FILE -t ${IMAGE_URL} --target ${TARGET} "${SCRIPT_DIR}/../../"
