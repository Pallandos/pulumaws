"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws
from ec2_worker import Ec2worker, ami_grabber

# 1. Récupérer l'AMI Amazon Linux 2 la plus récente
# Vous pouvez remplacer cela par un ID d'AMI spécifique si vous le souhaitez.
ami = ami_grabber.grab_ami("ubuntu")

# 2. Créer une instance de votre Ec2worker
worker_instance = Ec2worker(name="my-first-worker",
                            ami_id=ami,
                            instance_type="t2.micro", # Choisissez le type d'instance souhaité
                            tags={"Environment": "Development", "Project": "MyProject"})

# 3. Exporter certaines des sorties de l'instance
pulumi.export("worker_instance_id", worker_instance.instance.id)
pulumi.export("worker_public_ip", worker_instance.instance.public_ip)
pulumi.export("worker_public_dns", worker_instance.instance.public_dns)
pulumi.export("worker_arn", worker_instance.instance.arn)