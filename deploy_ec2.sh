#!/bin/bash

# Main script for deploying AWS resources using Pulumi

set -euo pipefail

CLI_ARG1="${1:-}"
SWARM_ENABLED=false
shift || true # Shift to allow for additional arguments

parse_flags() {
	local flags=()
	while [[ $# -gt 0 ]]; do
		case "$1" in
		--swarm)
			flags+=("--swarm")
			SWARM_ENABLED=true
			shift
			;;
		*)
			flags+=("$1")
			shift
			;;
		esac
	done
	echo "${flags[@]}"
}

swarm_mode() {
	if [[ -f ./swarm/deploy_swarm.sh ]]; then
		echo "[INFO ] Swarm mode is enabled, deploying swarm stack..."
		./swarm/deploy_swarm.sh
	else
		echo "[ERROR] No swarm deployment script found at ./swarm/deploy_swarm.sh"
		exit 1
	fi
}

FLAGS=$(parse_flags "$@")

# ========== Main Logic ==========
case "$CLI_ARG1" in
help)
	echo "Usage : pulumaws.sh [help|<action>] [flags]"
	echo ""
	echo "  help : Show this help message"
	echo "  <action> : deploy | destroy | preview"
	echo "            deploy : Deploy the stack"
	echo "            destroy : Destroy the stack"
	echo "            preview : Preview the stack changes"
	echo ""
	echo "  --swarm : Optional flag to deploy swarm"
	;;
deploy)
	# parse flags
	if [[ -n "$FLAGS" ]]; then
		for flag in $FLAGS; do
			case "$flag" in
			--swarm)
				swarm_mode
				;;
			*)
				echo "[ERROR] Unknown flag: $flag"
				echo "[INFO ] See 'pulumaws.sh help' for usage."
				exit 1
				;;
			esac
		done
	else
		echo "[INFO ] Deploying simple mode..."
		pulumi up --yes --skip-preview
	fi
	;;
destroy)
	echo "[INFO ] Destroying the stack..."
	# Check if swarm mode is enabled
	if [[ $SWARM_ENABLED ]]; then
		if [[ -f ./swarm/destroy_swarm.sh ]]; then
			echo "[INFO ] Destroying swarm stack..."
			./swarm/destroy_swarm.sh
		else
			echo "[ERROR] No swarm destroy script found at ./swarm/destroy_swarm.sh"
			exit 1
		fi
	fi
	pulumi destroy --yes --skip-preview
	;;
preview)
	echo "[INFO ] Previewing the stack changes..."
	# Add your preview logic here
	pulumi preview
	;;
*)
	# default
	if [[ -z "$CLI_ARG1" ]]; then
		echo "[ERROR] No argument provided. Please provide an argument."
		exit 1
	fi
	echo "[ERROR] Unknown argument: $CLI_ARG1"
	echo "[INFO ] See 'pulumaws.sh help' for usage."
	exit 1
	;;
esac
