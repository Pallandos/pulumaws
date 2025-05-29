#!/bin/bash
# ====== Swarm Docker logic ======

echo "=== Starting Docker Swarm setup ==="
# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    apt-get install -y docker.io
    systemctl enable docker
    systemctl start docker
else
    echo "Docker is already installed"
fi

# add current user to the docker group
usermod -aG docker "$(whoami)"

# Join Docker Swarm as a worker node
echo "Joining Docker Swarm as a worker node..."
docker swarm join {SWARM_JOIN_OPTS}

# Check if the join was successful
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to join Docker Swarm"
    exit 1
fi
echo "Successfully joined Docker Swarm as a worker node"