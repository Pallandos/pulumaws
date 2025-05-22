import pulumi
import pulumi_aws as aws
import requests


def create_ssh_security_group(ip_to_allow: str) -> aws.ec2.SecurityGroup:
    """Create a security group for SSH access.

    Args:
        ip_to_allow (str): The IP address or CIDR block to allow SSH access from.

    Returns:
        aws.ec2.SecurityGroup: The created security group object.
    """
    
    if ip_to_allow == "0.0.0.0/0":
        # determine the IP address of the current machine
        try:
            response = requests.get("https://checkip.amazonaws.com/", timeout=5)
            public_ip = response.text.strip() + "/32"
        except Exception:
            public_ip = "127.0.1/32"  # Fallback to localhost if the request fails
        print(f"Detected IP address for SSH: {public_ip}")
    else:
        public_ip = ip_to_allow
        
    ssh_security_group = aws.ec2.SecurityGroup("ssh_security_group",
        name="ssh_security_group",
        description="Allow SSH access",
        vpc_id=aws.ec2.get_vpc(default=True).id,
        tags={
            "Name": "ssh_security_group",
            "Project": "Pulumaws",
        }
    )

    ssh_ingress_rule = aws.vpc.SecurityGroupIngressRule("ssh_ingress_rule",
        security_group_id=ssh_security_group.id,
        cidr_ipv4=public_ip,
        ip_protocol="tcp",
        from_port=22,
        to_port=22,
        description="Allow SSH access from specific IP",
    )

    ssh_egress_rule = aws.vpc.SecurityGroupEgressRule("ssh_egress_rule",
        security_group_id=ssh_security_group.id,
        cidr_ipv4="0.0.0.0/0",
        ip_protocol="-1",
        from_port=0,
        to_port=0,
        description="Allow all outbound traffic",
    )
    
    return ssh_security_group