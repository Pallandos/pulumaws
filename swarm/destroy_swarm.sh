#!/bin/bash

# Script for destroying the Docker Swarm
# NOTE : this would probably be run only on the manager node

set -euo pipefail

# === variables ====
ENV_FILE=".env"

RESET_COLOR='\033[0m'
ORANGE='\033[0;33m'
GREEN='\033[0;32m'

# load environment variables from .env file
if [[ -f $ENV_FILE ]]; then
    export "$(grep -v '^#' $ENV_FILE | xargs)"
else
    echo "[ERROR] .env file not found"
    exit 1
fi

# === functions ====
set_or_replace_key() {
    local key="$1"
    local value="$2"

    # If $ENV_FILE doesn't exist yet, just create an empty one
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

check_swarm_status() {
    if docker info 2>/dev/null | grep -q 'Swarm: active'; then
        echo "[INFO ] Docker Swarm is currently active"
        return 0
    else
        echo "[INFO ] No active Docker Swarm found"
        return 1
    fi
}

remove_all_services() {
    echo "[INFO ] Removing all Docker services..."

    # Get list of services
    SERVICES=$(docker service ls --quiet 2>/dev/null || true)

    if [[ -n "$SERVICES" ]]; then
        echo "[INFO ] Found services to remove: $(docker service ls --format "table {{.Name}}" | tail -n +2 | tr '\n' ' ')"
        docker service rm "$SERVICES" >/dev/null 2>&1 || true
        echo "[INFO ] All services removed"
    else
        echo "[INFO ] No services found to remove"
    fi
}

remove_all_networks() {
    echo "[INFO ] Removing custom Docker networks..."

    # Remove custom networks (skip default ones)
    CUSTOM_NETWORKS=$(docker network ls --filter "driver=overlay" --quiet 2>/dev/null || true)

    if [[ -n "$CUSTOM_NETWORKS" ]]; then
        yes | docker network rm --force "$CUSTOM_NETWORKS" >/dev/null 2>&1 || true
        echo "[INFO ] Custom networks removed"
    else
        echo "[INFO ] No custom networks found to remove"
    fi
}

leave_swarm() {
    echo "[INFO ] Leaving Docker Swarm..."

    # Check if this node is a manager
    if docker info 2>/dev/null | grep -q 'Is Manager: true'; then
        echo "[INFO ] This node is a manager, forcing leave..."
        docker swarm leave --force >/dev/null 2>&1 || true
    else
        echo "[INFO ] This node is a worker, leaving gracefully..."
        docker swarm leave >/dev/null 2>&1 || true
    fi

    echo "[INFO ] Successfully left Docker Swarm"
}

cleanup_env_file() {
    echo "[INFO ] Cleaning up environment file..."
    set_or_replace_key "SWARM_JOIN_TOKEN" ""
    echo "[INFO ] Environment file updated"
}

confirm_destruction() {
    echo -e "${ORANGE}[WARN!]${RESET_COLOR} This will destroy the Docker Swarm and remove all services!\033[0m"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "[INFO ] Operation cancelled"
        exit 0
    fi
}

# === Main Logic ===
echo "[INFO ] Starting Docker Swarm destruction process..."

# Ask for confirmation
confirm_destruction

# Check if swarm is active
if check_swarm_status; then
    echo ""

    # Remove services first
    remove_all_services

    # Remove custom networks
    remove_all_networks

    # Leave the swarm
    leave_swarm

    # Clean up environment
    cleanup_env_file
else
    echo "[INFO ] Nothing to destroy"
fi

echo ""
echo -e "${GREEN}[SUCCESS]${RESET_COLOR} Swarm destruction process completed"
