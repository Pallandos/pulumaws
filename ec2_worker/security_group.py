import pulumi
import pulumi_aws as aws

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
    cidr_ipv4="0.0.0.0/0",
    ip_protocol="tcp",
    from_port=22,
    to_port=22,
    description="Allow SSH access from anywhere",
)

ssh_egress_rule = aws.vpc.SecurityGroupEgressRule("ssh_egress_rule",
    security_group_id=ssh_security_group.id,
    cidr_ipv4="0.0.0.0/0",
    ip_protocol="-1",
    from_port=0,
    to_port=0,
    description="Allow all outbound traffic",
)