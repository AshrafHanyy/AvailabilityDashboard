import os
import subprocess
from app import app, socketio

def create_hotspot():
    # Configure hotspot settings (Windows example)
    hotspot_name = "TeamDashboard"
    hotspot_password = "team12345"
    
    try:
        # For Windows:
        # Create hotspot
        subprocess.run(['netsh', 'wlan', 'set', 'hostednetwork', 'mode=allow', f'ssid={hotspot_name}', f'key={hotspot_password}'], check=True)
        # Start hotspot
        subprocess.run(['netsh', 'wlan', 'start', 'hostednetwork'], check=True)
        
        print(f"Hotspot created successfully!\nSSID: {hotspot_name}\nPassword: {hotspot_password}")
        print(f"Users can connect to this hotspot and access the app at: http://{get_local_ip()}:5000")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create hotspot. Error: {e}")
        print("You may need to run this as Administrator")

def get_local_ip():
    """Get the local IP address of the hotspot interface"""
    try:
        # For Windows
        result = subprocess.run(['ipconfig'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if 'IPv4 Address' in line and '192.168' in line:
                return line.split(':')[-1].strip()
        return '192.168.137.1'  # Default Windows hotspot IP
    except:
        return '192.168.137.1'  # Fallback IP

if __name__ == '__main__':
    # Create the hotspot
    create_hotspot()
    
    # Get the local IP address
    local_ip = get_local_ip()
    
    # Run the Flask app on the hotspot IP
    print("\nStarting the Team Dashboard application...")
    socketio.run(app, host=local_ip, port=5000, debug=True)