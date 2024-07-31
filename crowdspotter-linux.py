#!/usr/bin/env python3
# API credentials (replace with actual values)
CLIENT_ID = "INSERT API CLIENT ID HERE"
CLIENT_SECRET = "INSERT API CLIENT SECRET HERE"

# Edit this if this file isn't there 
SOUND_FILE = "/usr/share/sounds/oxygen/stereo/message-new-email.ogg"

# Change this, value is in seconds
REFRESH_RATE = 30

TITLE_ART = r"""
_________                               .___  _________                  __     __                   
\_   ___ \ _______   ____  __  _  __  __| _/ /   _____/______    ____  _/  |_ _/  |_   ____  _______ 
/    \  \/ \_  __ \ /  _ \ \ \/ \/ / / __ |  \_____  \ \____ \  /  _ \ \   __\\   __\_/ __ \ \_  __ \
\     \____ |  | \/(  <_> ) \     / / /_/ |  /        \|  |_> >(  <_> ) |  |   |  |  \  ___/  |  | \/
 \______  / |__|    \____/   \/\_/  \____ | /_______  /|   __/  \____/  |__|   |__|   \___  > |__|   
        \/                               \/         \/ |__|                               \/         
"""
VERSION = "2024.07.30-linux"

'''
CrowdSpotter: CrowdStrike Online Host Monitor (Linux Version)

Author: @pixelnull@infosec.exchange

This script monitors the online status of specified hosts using the CrowdStrike Falcon API.
It periodically checks the status of the hosts and alerts the user when a host comes online
or goes offline. It will link online hosts to the the Host Managment page in the CrowdStrike
Web Console. This script is designed to run on Linux systems.

Before running the script:
1. Replace the placeholder values for CLIENT_ID and CLIENT_SECRET above with your actual API credentials.

To run the script:
1. Ensure you have Python installed on your Linux system.
2. Install the required packages:
   pip install crowdstrike-falconpy
3. Run the script with one or more AIDs as arguments:
   python crowdspotter.py aid1 aid2 aid3 ...

The script will:
- Check host statuses at specified interval. Defualt is 30 seconds.
- Print an alert message when a new host comes online.
- Play a sound alert if the system is capable.
- Display updates in the console window.
- Continue running until you press Ctrl+C to stop it.

License:  CrowdSpotter © 2024 by @pixelnull@infosec.exchange is licensed under Creative
Commons Attribution-ShareAlike 4.0 International. To view a copy of this license,
visit https://creativecommons.org/licenses/by-sa/4.0/
'''

import os
from falconpy import Hosts
import argparse
import time
import sys
import signal
import subprocess

# Global flag to maintain the running state of the script
keep_running = True

# Dictionary to store host information
host_info = {}

def check_python_packages():
    """Check if required Python packages are installed."""
    try:
        import falconpy
        return True
    except ImportError:
        print("Error: Required package 'crowdstrike-falconpy' is not installed.")
        print("To install, run: pip install crowdstrike-falconpy")
        return False

def check_python_version():
    """Check if the Python version is 3.6 or higher."""
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required.")
        print("Please upgrade your Python installation.")
        return False
    return True

def check_api_credentials():
    """Check if API credentials are set."""
    if CLIENT_ID == "TALK TO INFOSEC FOR API" or CLIENT_SECRET == "TALK TO INFOSEC FOR API":
        print("Error: API credentials not set.")
        print("Please update the CLIENT_ID and CLIENT_SECRET variables with the correct API credentials.")
        print("Contact your InfoSec team to obtain the necessary API credentials.")
        return False
    return True

def clear_screen():
    """Clear the console screen for fresh output."""
    os.system('clear')  # Use 'cls' for Windows systems

def get_hostname(hosts, aid):
    """Retrieve the hostname for a given AID using the Falcon API."""
    if aid not in host_info:
        try:
            response = hosts.GetDeviceDetailsV2(ids=[aid])
            if response['status_code'] == 200:
                hostname = response['body']['resources'][0].get('hostname')
                if hostname:
                    host_info[aid] = {
                        'hostname': hostname,
                        'seen_count': 0,
                        'status': 'offline',
                        'url': generate_host_url(aid)
                    }
                else:
                    print(f"Error: Hostname not found for AID {aid}")
                    sys.exit(1)
            else:
                print(f"Error: Failed to retrieve details: {response['errors']}")
                sys.exit(1)
        except Exception as e:
            print(f"Error getting hostname for AID {aid}: {e}")
            sys.exit(1)
    
    return host_info[aid]['hostname']

def check_hosts(falcon, aids):
    """Check the online status of the specified hosts and update their information."""
    try:
        id_list = ','.join(aids)
        response = falcon.get_online_state(ids=id_list)
        
        if response['status_code'] == 200:
            print(f"\nAPI calls remaining: {response['headers']['X-Ratelimit-Remaining']}")
            
            for resource in response['body']['resources']:
                aid = resource['id']
                hostname = get_hostname(falcon, aid)
                
                new_status = resource['state']
                if new_status == 'online':
                    host_info[aid]['seen_count'] += 1
                
                host_info[aid]['status'] = new_status
            
        else:
            print(f"Error: Status code {response['status_code']}")
            sys.exit(1)
    
    except Exception as e:
        print(f"An error occurred while checking hosts: {e}")
        sys.exit(1)

def signal_handler(sig, frame):
    """Handle Ctrl+C signal to gracefully terminate the script."""
    global keep_running
    print("\nCtrl+C received. Shutting down...")
    keep_running = False

def countdown(seconds):
    """Display a countdown timer until the next check."""
    for remaining in range(seconds, 0, -1):
        sys.stdout.write(f"\rTime until next check: {remaining:3d} seconds")
        sys.stdout.flush()
        time.sleep(1)
        if not keep_running:
            break
    sys.stdout.write("\r" + " " * 40 + "\r")
    sys.stdout.flush()

def generate_host_url(aid):
    """Generate the CrowdStrike Falcon host management URL for a given AID."""
    return f"https://falcon.crowdstrike.com/hosts/hosts/host/{aid}?filter=device_id%3A%27{aid}%27"

def check_sound_capability():
    """Check if the system is capable of playing sounds for alerts."""
    try:
        subprocess.run(['paplay', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        print("Warning: 'paplay' not found. Sound alerts will be disabled.")
        print("To enable sound alerts, install 'pulseaudio' package.")
        return False
    except subprocess.SubprocessError:
        print("Warning: Unable to run 'paplay'. Sound alerts will be disabled.")
        print("Please ensure 'pulseaudio' is correctly installed and configured.")
        return False

def play_sound():
    """Play a sound to alert the user to significant events."""
    try:
        subprocess.run(['paplay', SOUND_FILE])
    except (FileNotFoundError, subprocess.SubprocessError):
        print("Warning: Unable to play sound.")

def main():
    global keep_running
    
    print(TITLE_ART)
    print(f"Version: {VERSION}")
    
    # Perform environment checks
    if not check_python_version() or not check_python_packages() or not check_api_credentials():
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="CrowdSpotter: CrowdStrike Online Host Monitor")
    parser.add_argument("aids", nargs="+", help="Agent IDs to monitor")
    args = parser.parse_args()

    print("Script starting...")
    
    sound_capable = check_sound_capability()
    if sound_capable:
        print("Sound alerts are enabled.")
    else:
        print("Sound alerts are disabled.")
    
    try:
        falcon = Hosts(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        time.sleep(5)
        clear_screen()
        
        previous_online = set()
        sound_played = False
        
        while keep_running:
            try:
                check_hosts(falcon, args.aids)
                
                current_online = {aid for aid, info in host_info.items() if info['status'] == 'online'}
                
                new_online = current_online - previous_online
                if new_online:
                    print("New hosts online:")
                    for aid in new_online:
                        print(f"Host {host_info[aid]['hostname']} is online. URL: {host_info[aid]['url']}")
                    if sound_capable and not sound_played:
                        play_sound()
                        sound_played = True
                else:
                    sound_played = False
                
                new_offline = previous_online - current_online
                if new_offline:
                    for aid in new_offline:
                        print(f"Host {host_info[aid]['hostname']} is now offline.")
                
                previous_online = current_online
                
                print("\nCurrent host statuses:")
                for aid, info in sorted(host_info.items(), key=lambda x: x[1]['hostname']):
                    status_str = f"Host {info['hostname']} is {info['status']}. Seen online {info['seen_count']} times."
                    if info['status'] == 'online':
                        status_str += f" URL: {info['url']}"
                    print(status_str)

                if keep_running:
                    print("\nWaiting for next check...")
                    countdown(REFRESH_RATE)
                    clear_screen()
            
            except SystemExit:
                print("Exiting due to an error in retrieving host information.")
                break
            except Exception as e:
                print(f"An error occurred during the main loop: {e}")
                time.sleep(REFRESH_RATE)  # Wait before retrying
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    finally:
        keep_running = False
        print("Script terminated.")

if __name__ == "__main__":
    main()
