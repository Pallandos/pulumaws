#!/bin/bash

# Main script for deploying AWS resources using Pulumi

set -euo pipefail

CLI_ARG1="${1:-}"

case "$CLI_ARG1" in
    help)
        echo "Usage : pulumaws.sh [help|<action>]"
        echo ""
        echo "  help : Show this help message"
        echo "  <action> : deploy | destroy | preview"
        echo "            deploy : Deploy the stack"
        echo "            destroy : Destroy the stack"
        echo "            preview : Preview the stack changes"
        ;; 
	deploy)
		echo "Deploying the stack..."
		# Add your deployment logic here
		pulumi up --yes
		;;
	destroy)
		echo "Destroying the stack..."
		# Add your destroy logic here
		pulumi destroy --yes
		;;
	preview)
		echo "Previewing the stack changes..."
		# Add your preview logic here
		pulumi preview
		;;
    *) 
    # default
        if [[ -z "$CLI_ARG1" ]]; then
            echo "No argument provided. Please provide an argument."
            exit 1
        fi
		echo "Unknown argument: $CLI_ARG1"
		echo "See 'pulumaws.sh help' for usage."
		exit 1
        ;;
esac