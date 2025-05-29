"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws
from ec2_worker import Ec2worker, ami_grabber, create_ssh_security_group, generate_userdata
from py.dump_log import write_log_json
from py.regions import load_clean_regions_config, get_region_names

from py.config import (
    INSTANCE_TYPE,
    INSTANCE_BASE_NAME,
    INSTANCE_OS,
    PUB_KEY_PATH,
    PUB_KEY_NAME,
    SSH_IP_TO_ALLOW,
    TAILSCALE_AUTH_KEY_PATH,
    REGIONS_PATH,
    SWARM_JOIN_TOKEN,
    SWARM_MANAGER_IP,
    )

# ==== Load regions configuration ====
regions_config = load_clean_regions_config(REGIONS_PATH)
REGIONS = get_region_names(REGIONS_PATH)

# ==== Creating Providers ====
providers = {}
for region in REGIONS:
    providers[region] = aws.Provider(f"{region}-provider", region=region)

instances = []

# for buildig names
numbers_by_continent = {
    reg.split('-')[0]: 1 for reg in REGIONS
}

# ==== **** Main loop by region **** ====
for region in REGIONS:
    provider = providers[region]

    # get the AMI of the specified OS in specified region
    ami = ami_grabber.grab_ami(INSTANCE_OS, provider=provider)

    # create Key Pair
    with open(PUB_KEY_PATH, "r") as pub_key_file:
        pub_key = pub_key_file.read()

    key_pair = aws.ec2.KeyPair(f"ssh_key_pair-{region}",
        key_name=PUB_KEY_NAME,
        public_key=pub_key,
        opts = pulumi.ResourceOptions(provider=provider)
    )

    # create a security group for SSH access in the specified region
    ssh_security_group = create_ssh_security_group(
        ip_to_allow=SSH_IP_TO_ALLOW,
        name_suffix=f"-{region}",
        provider=provider
    )
    
    # generate the ec2 instances
    instance_number = regions_config[region].get("instances", 1)
    
    for i in range(int(instance_number)):  
        suffix = f"{region.split('-')[0]}-{numbers_by_continent[region.split('-')[0]]}"
        instance_name = f"{INSTANCE_BASE_NAME}-{suffix}"
        
        numbers_by_continent[region.split('-')[0]] += 1
    
        # Generate user data script for Tailscale

        user_data = generate_userdata(
            tailscale_key_path=TAILSCALE_AUTH_KEY_PATH,
            hostname=instance_name,
            tags=["tag:aws-instances"],
            docker_swarm_join_token=SWARM_JOIN_TOKEN,
            docker_swarm_manager_ip=SWARM_MANAGER_IP,
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
            user_data=user_data,  
            provider=provider,    
            tags={
                "Name": instance_name,
                "Environment": "Pulumi",
                "Project": "AWS-Pulumi",
            }
            )
        instances.append(instance)
    
# ==== export data to a JSON file ====
instances_outputs = [
    pulumi.Output.all(
        name = instance.instance._name,
        instance_id = instance.instance.id,
        public_ip = instance.instance.public_ip,
        instance_type = instance.instance.instance_type,
        region = instance.instance.availability_zone, 
    )
    for instance in instances
]

# dump the log to a JSON file
pulumi.Output.all(*instances_outputs).apply(lambda infos: write_log_json(infos, filename="instances.json"))