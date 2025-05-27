import pulumi
import pulumi_aws as aws
from typing import Optional

def grab_ami(os_name: str, provider: Optional[aws.Provider] = None):
    """
    Grabs the latest AMI ID for a given OS name.

    Args:
        os_name (str): The name of the OS for which to grab the AMI ID.
                       Supported values are "ubuntu" and "amazon-linux-2".
        provider (Optional[aws.Provider]): The AWS provider to use for fetching the AMI.
                                         If None, uses the default provider.
    
    Returns:
        str: The AMI ID for the specified OS.
    """
    if os_name.lower() == "ubuntu":
        filters = [
            aws.ec2.GetAmiFilterArgs(
                name="name",
                values=["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"],
            ),
            aws.ec2.GetAmiFilterArgs(
                name="virtualization-type",
                values=["hvm"],
            ),
        ]
        owners = ["099720109477"]  # Canonical
    elif os_name.lower() == "amazon-linux-2":
        filters = [
            aws.ec2.GetAmiFilterArgs(
                name="name",
                values=["amzn2-ami-hvm-*-x86_64-gp2"],
            ),
            aws.ec2.GetAmiFilterArgs(
                name="virtualization-type",
                values=["hvm"],
            ),
        ]
        owners = ["amazon"]
    else:
        raise ValueError(f"Unsupported OS: {os_name}. Supported OS are: ubuntu, amazon-linux-2")

    # Utiliser InvokeOptions avec le provider si fourni
    invoke_opts = None
    if provider:
        invoke_opts = pulumi.InvokeOptions(provider=provider)

    ami = aws.ec2.get_ami(
        most_recent=True,
        owners=owners,
        filters=filters,
        opts=invoke_opts
    )
    
    return ami.id