import psutil
from flask import Flask, jsonify
import socket
from datetime import datetime

def info_cpu():
    """Get CPU information including number of cores, usage, and frequency.

    Returns:
        dict: number of cores, CPU usage percentage, and current frequency in MHz.
        
        {"cores": int, "usage": float, "frequency": float}
    """
    cores = psutil.cpu_count(logical=True)
    usage = psutil.cpu_percent(interval=0.5)
    freq = round(psutil.cpu_freq().current,2)
    
    response = {
        "cores": cores,
        "usage": usage,
        "frequency": freq
    }
    return response

app = Flask(__name__)

@app.route('/health')
def health():
    """Return system health information"""
    cpu_info = info_cpu()
    
    response = {
        "node": socket.gethostname(),
        "timestamp": datetime.now().isoformat(),
        "cpu": cpu_info
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)