"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws
from ec2_worker import Ec2worker, ami_grabber, create_ssh_security_group, generate_userdata
from py.dump_log import write_log_json

from py.config import (
    INSTANCE_TYPE,
    INSTANCE_BASE_NAME,
    INSTANCE_NUMBER,
    INSTANCE_OS,
    PUB_KEY_PATH,
    PUB_KEY_NAME,
    SSH_IP_TO_ALLOW,
    TAILSCALE_AUTH_KEY_PATH,
    TAILSCALE_ENABLED
    )

# ==== get the AMI of the specified OS ====
ami = ami_grabber.grab_ami(INSTANCE_OS)

# ==== create Key Pair ====
with open(PUB_KEY_PATH, "r") as pub_key_file:
    pub_key = pub_key_file.read()

key_pair = aws.ec2.KeyPair("ssh_key_pair",
    key_name=PUB_KEY_NAME,
    public_key=pub_key
)

# ==== create a security group for SSH access ====
ssh_security_group = create_ssh_security_group(
    ip_to_allow=SSH_IP_TO_ALLOW
)


# ==== Create a list of EC2 instances ====
instances = []

for i in range(int(INSTANCE_NUMBER)):
    instance_name = f"{INSTANCE_BASE_NAME}-{i+1}"
    
        # Generate user data script for Tailscale
    if TAILSCALE_ENABLED:
        user_data = generate_userdata(
            tailscale_key_path=TAILSCALE_AUTH_KEY_PATH,
            hostname=instance_name,
            tags=["tag:aws-instances"],
            accept_routes=True,
            accept_dns=True,
            enable_ssh=True
        )
        
    instance = Ec2worker(
        name=instance_name,
        ami_id=ami,
        instance_type=INSTANCE_TYPE,
        vpc_security_group_ids=[ssh_security_group.id],
        key_name=key_pair.key_name,
        user_data=user_data if TAILSCALE_ENABLED else None,      
        tags={
            "Name": instance_name,
            "Environment": "Pulumi",
            "Project": "AWS-Pulumi",
        },
    )
    instances.append(instance)
    
# ==== export data to a JSON file ====
instances_outputs = [
    pulumi.Output.all(
        name = instance.instance._name,
        instance_id = instance.instance.id,
        public_ip = instance.instance.public_ip,
        instance_type = instance.instance.instance_type,
    )
    for instance in instances
]

# dump the log to a JSON file
pulumi.Output.all(*instances_outputs).apply(lambda infos: write_log_json(infos, filename="instances.json"))