from dotenv import find_dotenv, load_dotenv
import os


# Load environment variables from .env file

path = find_dotenv()

if path:
    print(f"Loading environment variables from {path}")
    load_dotenv(path, override=True)
else:
    raise FileNotFoundError("Could not find .env file")
    
# ==== instances options ====
INSTANCE_TYPE = os.getenv("INSTANCE_TYPE", "t2.micro")
INSTANCE_BASE_NAME = os.getenv("INSTANCE_BASE_NAME", "pulumaws")
INSTANCE_NUMBER = os.getenv("INSTANCE_NUMBER", 1)
INSTANCE_OS = os.getenv("INSTANCE_OS", "ubuntu")