"""Dump log to a JSON file located in ../logs/
"""

import os
import json
from pathlib import Path

def write_log_json(infos, filename : str):
    """Write log to a JSON file located in ../logs/
    """
    path = Path(__file__).parent.parent / "logs"
    
    os.makedirs(path, exist_ok=True)
    filepath = path / filename
    with open(filepath, "w") as f:
        json.dump(infos, f, indent=4)
    print(f"Logs written to {filepath}")
    return infos


if __name__ == "__main__":
    
    # test and debug :
    write_log_json(
        {
            "INSTANCE_TYPE": os.getenv("INSTANCE_TYPE", "t2.micro"),
            "INSTANCE_BASE_NAME": os.getenv("INSTANCE_BASE_NAME", "pulumaws"),
            "INSTANCE_NUMBER": os.getenv("INSTANCE_NUMBER", 1),
            "INSTANCE_OS": os.getenv("INSTANCE_OS", "ubun"),
        },
        filename="instance.json"
    )