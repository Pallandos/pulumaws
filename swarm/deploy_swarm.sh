#!/bin/bash

# Script for deploying a Docker Swarm stack using Pulumi

set -euo pipefail

# === variables ====
ENV_FILE=".env"
SWARM_JOIN_TOKEN=""
SWARM_MANAGER_IP="${SWARM_MANAGER_IP:-$(hostname -I | awk '{print $1}')}" # Default to the first IP address of the host

COLOR_RED="\033[0;31m"
COLOR_GREEN="\033[0;32m"
COLOR_RESET="\033[0m"

# load environment variables from .env file
if [[ -f .env ]]; then
    export "$(grep -v '^#' .env | xargs)"
else
    echo "[ERROR] .env file not found"
    exit 1
fi

# === functions ====
reload_env() {
    if [[ -f .env ]]; then
        set -a
        # shellcheck disable=SC1091
        source .env
        set +a
        echo "[INFO ] Environment variables reloaded"
    fi
}

set_or_replace_key() {
    local key="$1"
    local value="$2"

    # If $ENV_FILE doesn’t exist yet, just create an empty one
    if [ ! -f "$ENV_FILE" ]; then
        touch "$ENV_FILE"
    fi

    # Check if the line exists (exact match at the start of the line)
    if grep -q "^${key}=" "$ENV_FILE"; then
        # Replace the existing line
        sed -i "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
    else
        # Append to the file
        echo "${key}=${value}" >>"$ENV_FILE"
    fi
}

init_manager() {
    echo "[INFO ] Initializing Docker Swarm manager..."
    SWARM_OUTPUT=$(docker swarm init --advertise-addr "${SWARM_MANAGER_IP}")
    if [[ $? -ne 0 ]]; then
        echo "[ERROR] Failed to initialize Docker Swarm manager"
        exit 1
    fi
    echo "[INFO ] Docker Swarm manager initialized successfully"
    SWARM_JOIN_TOKEN=$(echo "$SWARM_OUTPUT" | grep 'docker swarm join --token' | awk '{print $5}')
}

leave_swarm_if_exists() {
    if docker info | grep -q 'Swarm: active'; then
        echo "[INFO ] Leaving current Docker Swarm..."
        docker swarm leave --force >/dev/null 2>&1 || true
        echo "[INFO ] Successfully left current Docker Swarm"
    fi
}

launch_stack() {
    echo "[INFO ] Launching Docker Swarm stack..."
    sleep 5 # Wait for a few seconds to ensure the swarm is ready
    docker stack deploy -c ./swarm/docker-compose.yaml "$SWARM_STACK_NAME"
    if [[ $? -ne 0 ]]; then
        echo -e "${COLOR_RED}[ERROR]${RESET_COLOR} Failed to deploy Docker Swarm stack"
        exit 1
    fi
    echo -e "${COLOR_GREEN}[INFO ]${COLOR_RESET} Docker Swarm stack deployed successfully"
}


# ========= Main Logic ==========
leave_swarm_if_exists
init_manager
set_or_replace_key "SWARM_JOIN_TOKEN" "$SWARM_JOIN_TOKEN"
reload_env
pulumi up --yes --skip-preview
launch_stack