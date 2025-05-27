import pulumi
import pulumi_aws as aws
import requests
from typing import Optional


def create_ssh_security_group(ip_to_allow: str, 
                            name_suffix: str = "", 
                            provider: Optional[aws.Provider] = None) -> aws.ec2.SecurityGroup:
    """Create a security group for SSH access.

    Args:
        ip_to_allow (str): The IP address or CIDR block to allow SSH access from.
        name_suffix (str): Suffix to add to the security group name (e.g., "-us-east-1").
        provider (Optional[aws.Provider]): The AWS provider to use for creating the security group.
                                         If None, uses the default provider.

    Returns:
        aws.ec2.SecurityGroup: The created security group object.
    """
    if ip_to_allow is None or ip_to_allow.lower() == "none":
        public_ip = None
        print(f"[{provider._name.replace('-provider','')}] No IP address provided for SSH access. SSH will only be allowed by Tailscale.")
    elif ip_to_allow == "0.0.0.0/0":
        # determine the IP address of the current machine
        try:
            response = requests.get("https://checkip.amazonaws.com/", timeout=5)
            public_ip = response.text.strip() + "/32"
        except Exception:
            public_ip = "127.0.0.1/32"  # Fallback to localhost if the request fails
        print(f"Detected IP address for SSH: {public_ip}")
    else:
        public_ip = ip_to_allow

    # Créer les options de ressource avec le provider
    resource_opts = None
    if provider:
        resource_opts = pulumi.ResourceOptions(provider=provider)

    # Générer des noms uniques pour éviter les conflits entre régions
    sg_name = f"ssh_security_group{name_suffix}"
    sg_logical_name = f"ssh_security_group{name_suffix}"
    
    # Obtenir le VPC par défaut dans la région du provider
    invoke_opts = None
    if provider:
        invoke_opts = pulumi.InvokeOptions(provider=provider)
    
    default_vpc = aws.ec2.get_vpc(default=True, opts=invoke_opts)
        
    ssh_security_group = aws.ec2.SecurityGroup(sg_logical_name,
        name=sg_name,
        description=f"Allow SSH access{name_suffix}",
        vpc_id=default_vpc.id,
        tags={
            "Name": sg_name,
            "Project": "Pulumaws",
        },
        opts=resource_opts
    )

    # Add ingress rule for SSH access if a public IP is provided
    if public_ip is not None:
        ssh_ingress_rule = aws.vpc.SecurityGroupIngressRule(f"ssh_ingress_rule{name_suffix}",
            security_group_id=ssh_security_group.id,
            cidr_ipv4=public_ip,
            ip_protocol="tcp",
            from_port=22,
            to_port=22,
            description="Allow SSH access from specific IP",
            opts=resource_opts
        )

    ssh_egress_rule = aws.vpc.SecurityGroupEgressRule(f"ssh_egress_rule{name_suffix}",
        security_group_id=ssh_security_group.id,
        cidr_ipv4="0.0.0.0/0",
        ip_protocol="-1",
        from_port=0,
        to_port=0,
        description="Allow all outbound traffic",
        opts=resource_opts
    )
    
    return ssh_security_group