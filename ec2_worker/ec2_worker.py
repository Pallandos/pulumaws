import pulumi
import pulumi_aws as aws

class Ec2worker(pulumi.ComponentResource):
    """
    A class to create and manage EC2 instances using Pulumi and AWS,
    as a Pulumi ComponentResource.
    """
    def __init__(self, 
                 name: str, 
                 ami_id: pulumi.Input[str], 
                 instance_type: pulumi.Input[str], 
                 tags: pulumi.Input[dict] = None,
                 vpc_security_group_ids: pulumi.Input[list] = None,
                 key_name: pulumi.Input[str] = None,
                 user_data: pulumi.Input[str] = None,
                 provider: aws.Provider = None,
                 opts: pulumi.ResourceOptions = None):
        """
        Initializes an EC2 instance component.

        Args:
            name (str): The logical name of the component resource.
            ami_id (pulumi.Input[str]): The ID of the AMI to use for the instance.
            instance_type (pulumi.Input[str]): The type of instance to launch (e.g., "t2.micro").
            tags (pulumi.Input[dict], optional): A dictionary of tags to apply to the instance. 
                                                 The 'Name' tag will be automatically set to the resource name.
                                                 Defaults to None.
            opts (pulumi.ResourceOptions, optional): Options for the component resource. Defaults to None.
        """
        super().__init__("pkg:index:Ec2worker", name, {}, opts)

        # Prepare tags
        # It's common to merge provided tags with default tags or resource name-based tags.
        # Here, we ensure the 'Name' tag is set based on the Pulumi resource name.
        # pulumi.Output.all is used to combine potentially Input values for tags.
        
        effective_tags = pulumi.Output.all(tags, name).apply(
            lambda args: {**(args[0] or {}), "Name": args[1]}
        )

        # options for Provider
        opts_ = pulumi.ResourceOptions(parent=self)
        if provider:
            opts_ = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(provider=provider))
        
        self.instance = aws.ec2.Instance(f"{name}",
            instance_type=instance_type,
            ami=ami_id,
            vpc_security_group_ids=vpc_security_group_ids,
            key_name=key_name,
            user_data=user_data,
            tags=effective_tags,
            opts=opts_
        )

        # Register outputs for the component
        self.register_outputs({
            "instance_id": self.instance.id,
            "public_ip": self.instance.public_ip,
            "public_dns": self.instance.public_dns,
            "arn": self.instance.arn,
            "region": self.instance.availability_zone
        })
