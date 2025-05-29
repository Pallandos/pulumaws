"""
Create the user data script for the EC2 worker instance.
"""

import os
import pulumi
import pulumi_aws as aws

def _load_script_template(path: str) -> str:
    """
    Load a script template from the specified file path.
    
    Args:
        path (str): Path to the script template file
    
    Returns:
        str: Content of the script template
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Script template not found: {path}")
    
    with open(path, 'r') as f:
        return f.read()

def generate_userdata(
    tailscale_key_path: str,
    hostname: str ,
    docker_swarm_join_token: str = None,
    docker_swarm_manager_ip: str = None,
    tags: list = None,
    accept_routes: bool = True,
    accept_dns: bool = True,
    enable_ssh: bool = True
) -> str:
    """
    Generate user data script for EC2 instance with Tailscale installation.
    
    Args:
        tailscale_key_path (str): Path to the Tailscale auth key file
        hostname (str, optional): Custom hostname for the instance in Tailscale
        tags (list, optional): List of Tailscale tags (e.g., ["tag:aws", "tag:pulumi"])
        accept_routes (bool): Accept routes from other Tailscale nodes
        accept_dns (bool): Use Tailscale DNS
        enable_ssh (bool): Enable SSH over Tailscale
    
    Returns:
        str: User data script for EC2 instance
    """
    
    # Read Tailscale auth key
    try:
        if not os.path.exists(tailscale_key_path):
            raise FileNotFoundError(f"Tailscale key file not found: {tailscale_key_path}")
        
        with open(tailscale_key_path, 'r') as f:
            auth_key = f.read().strip()
        
        if not auth_key:
            raise ValueError("Tailscale auth key is empty")
            
    except Exception as e:
        raise RuntimeError(f"Failed to read Tailscale auth key: {str(e)}")
    
    # ====  Build Tailscale up command options ====
    tailscale_options = ["--authkey=" + auth_key]
    
    if hostname:
        tailscale_options.append(f"--hostname={hostname}")
    
    if tags:
        # Convert tags list to comma-separated string
        tags_str = ",".join(tags)
        tailscale_options.append(f"--advertise-tags={tags_str}")
    
    if accept_routes:
        tailscale_options.append("--accept-routes")
    
    if accept_dns:
        tailscale_options.append("--accept-dns")
    
    if enable_ssh:
        tailscale_options.append("--ssh")
    
    # Join all options
    tailscale_cmd_options = " ".join(tailscale_options)
    
    # ==== Build Swarm join command options ====
    if docker_swarm_join_token and docker_swarm_manager_ip:
        swarm_join_opts = f"--token {docker_swarm_join_token} {docker_swarm_manager_ip}:2377"
    else:
        swarm_join_opts = ""
    
    # Generate the user data script
    template_script_tailscale = _load_script_template("ec2_worker/user_data/template_user_data.sh")
    template_script_swarm = _load_script_template("ec2_worker/user_data/swarm_join_template.sh")
    
    tailscale_script = template_script_tailscale.format(
        HOSTNAME = hostname,
        TAILSCALE_CMD_OPTIONS=tailscale_cmd_options,
    )
    swarm_script = template_script_swarm.format(
        SWARM_JOIN_OPTS=swarm_join_opts
    )
    
    
    if swarm_join_opts:
        script =  tailscale_script + "\n" + swarm_script
    else:
        script = tailscale_script
    
    return script
    


def generate_simple_userdata(tails_opts,swarm_opts="") -> str:
    """
    Generate a simple user data script with custom content.
    
    Args:
        script_content (str): Custom bash script content
    
    Returns:
        str: User data script for EC2 instance
    """
    
    template_tailscale = _load_script_template("ec2_worker/user_data/template_user_data.sh")
    template_swarm = _load_script_template("ec2_worker/user_data/swarm_join_template.sh")
    
    tailscale_script = template_tailscale.format(
        TAILSCALE_CMD_OPTIONS=tails_opts
    )
    
    if not swarm_opts:
        swarm_opts = ""
    swarm_script = template_swarm.format(
        SWARM_JOIN_OPTS=swarm_opts
    )
    script = tailscale_script + "\n" + swarm_script if swarm_opts else tailscale_script
    return script

if __name__ == "__main__":
    # Example usage
    userdata = generate_simple_userdata("TESTTTT","token")
    
    print(userdata)

