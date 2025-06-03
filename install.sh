#!/bin/bash

set -euo pipefail

# this script install Pulumaws

# ==== Variables ====
COLOR_RED="\033[0;31m"
COLOR_GREEN="\033[0;32m"
COLOR_RESET="\033[0m"

# ==== Functions ====
print_error() {
    echo -e "${COLOR_RED}[ERROR]${COLOR_RESET} $1"
}

print_warning() {
    echo -e "${COLOR_YELLOW}[WARNING]${COLOR_RESET} $1"
}

print_info() {
    echo -e "[INFO ] $1"
}

check_requirements() {
    print_info "Checking system requirements..."

    if ! command -v pulumi &> /dev/null; then
        print_error "Pulumi is not installed. Please install Pulumi first."
        exit 1
    fi

    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install AWS CLI first."
        exit 1
    fi

    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v tailscale &> /dev/null; then
        print_error "Tailscale is not installed. Please install Tailscale first."
        exit 1
    fi

    if ! command -v pip &> /dev/null; then
        print_error "Python pip is not installed. Please install pip first."
        exit 1
    fi

    print_info "All requirements are met."
}

configure_venv() {
    print_info "Configuring Python virtual environment..."
    
    if ! python3 -m venv .venv; then
        print_error "Failed to create virtual environment."
        exit 1
    fi

    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

    print_info "Virtual environment configured successfully."
}

grant_executions_rights() {
    print_info "Granting execution rights to scripts..."

    chmod +x ./swarm/deploy_swarm.sh
    chmod +x ./swarm/destroy_swarm.sh

    chmod +x ./deploy_ec2.sh

    print_info "Execution rights granted."
}

# ==== Main Script ====

echo -e "${COLOR_GREEN}[START]${COLOR_RESET} Installing Pulumaws..."
check_requirements
configure_venv
grant_executions_rights
echo -e "${COLOR_GREEN}[SUCCESS]${COLOR_RESET} Pulumaws installation completed successfully."
./deploy_ec2.sh help