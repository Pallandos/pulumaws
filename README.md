# Pulumaws

By Pallandos

This project is a test project for using aws EC2 and Pulumi

## Installation

You first need to have Pulumi installed on your machine, and ready to start for AWS : see [Pulumi getting started for AWS](https://www.pulumi.com/docs/iac/get-started/aws/). Make sure you can access to your AWS account with Pulumi.

Then you can follow the next steps :

1. Clone the project or download the ZIP file
2. Set up your Python environment :
   1. Create a virtual env (recommended) **named `.venv`** (see [troubleshooting](#troubleshooting))
   2. Install requirements using `pip install -r requirements.txt`
3. Grant execution rights to `./deploy-ec2.sh`
4. Configure your `.env` file (see [configuration](#configuration))


## Configuration

To configure, you should only interact with the `.env` file. 

Here is an example of a configuration file with full descriptions : 

```.env

# configuration file

# === instances options ===

INSTANCE_TYPE = t2.micro
# instance type of the AWS EC2 to be created

INSTANCE_NUMBER = 1
# amount of instances of the above type to be created

INSTANCE_BASE_NAME = pulumaws
# base name : instances will be named for example pulumaws-1, pulumaws-2 etc

INSTANCE_OS = ubuntu 
# supported OS : ubuntu or amazon-linux-2


# === network options ===
# ATTENTION : this options will allow an IP to connect directly to the instances. It is not recommanded to # use this option because of difficulties to define the owner IP. Instead, use Tailscale 

PUB_KEY_PATH = lib/keys/key-hello-aws.pub
PUB_KEY_NAME = key-hello-aws.pub
SSH_IP_TO_ALLOW = None
# if 0.0.0.0/0 is entered, the IP of the user will be choosed 
# if None is entered, no IP will be allowed

# === Tailscale options ===
TAILSCALE_AUTH_KEY_PATH = lib/keys/tailscale-key
# your Tailscale auth key path to connect the instances to your VPN

TAILSCALE_ENABLED = True
# True or False if you want to join your VPN

```

## Troubleshooting

Make sure your virtual environment is named as in `Pulumi.yaml` in the `runtime/options/virtualenv` parameter.