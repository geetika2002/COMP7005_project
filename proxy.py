import argparse
import socket
import random
import time
import json
import threading
import os

proxy_settings = {}
settings_lock = threading.Lock()

def write_initial_settings_to_file(file_path, settings):
    with open(file_path, 'w') as f:
        json.dump(settings, f, indent=4)
    print(f"Initial settings written to {file_path}")

def load_settings_from_file(file_path):
    try:
        with open(file_path, 'r') as f:
            updated_settings = json.load(f)
        detect_changes(proxy_settings, updated_settings)
        with settings_lock:
            proxy_settings.update(updated_settings)
            print("Settings reloaded successfully.")    
    except Exception as e:
        print(f"Failed to reload settings: {e}")

def detect_changes(old_settings, new_settings):
    changes = {}
    for key, value in new_settings.items():
        old_value = old_settings.get(key)
        if old_value != value:
            changes[key] = {"Previous value":old_value, "New value": value}
    if changes:
        print("Detected changes in settings:")
        for key, value in changes.items():
            print(f"{key}: {value['Previous value']} -> {value['New value']}")

def watch_setting_file(file_path):
    last_modified_time = None
    while True:
        try:
            current_modified_time = os.path.getmtime(file_path)
            if current_modified_time != last_modified_time:
                last_modified_time = current_modified_time
                print(f"Reloading settings due to change in {file_path}")
                load_settings_from_file(file_path)
        except FileNotFoundError:
            print(f"Settings file {file_path} not found. Waiting for it to be created...")
        except Exception as e:
            print(f"Error while watching settings file: {e}")
        time.sleep(3)

def simulate_packet_loss(drop_chance):
    return random.random() < drop_chance

def simulate_packet_delay(delay_chance, delay_time):
    if random.random() < delay_chance: 
        delay = random.uniform(*delay_time) if isinstance(delay_time, tuple) else delay_time
        time.sleep(delay/1000) #Convert delay to seconds 
        return True
    return False 

def start_proxy(listen_ip, listen_port, target_ip, target_port, client_drop, server_drop, client_delay, server_delay, client_delay_time, server_delay_time):
    #Create UDP socket for proxy 
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    proxy_socket.bind((listen_ip, listen_port))
    print(f"Proxy server listening on {listen_ip}:{listen_port}")

    while True: 
        try: 
            #Receive data from client 
            data, client_address = proxy_socket.recvfrom(1024)
            print(f"Received packet from client {client_address}")

            #Simulate packet loss for client-to-server direction
            if simulate_packet_loss(client_drop):
                print("Packet dropped (client to server).")
            else: 
                #Simulate delay for client-to-server direction
                if simulate_packet_delay(client_delay, client_delay_time):
                    print(f"Packet delayed (client to server).")

                #Forward the packet to the server
                proxy_socket.sendto(data, (target_ip, target_port))
                print(f"Forwarded packet to server {target_ip}:{target_port}")

            #Receieve data from server
            data, server_address = proxy_socket.recvfrom(1024)
            print(f"Forwarded packet from server {server_address}")

            #Simulate packet loss for server-to-client direction 
            if simulate_packet_loss(server_drop): 
                print("Packet dropped (server to client)")

            else:
                #Simulate delay for server-to-client direction
                if simulate_packet_delay(server_delay, server_delay_time):
                    print(f"Packet delayed (server to client)")
                
                #Forward the packet back to the client
                proxy_socket.sendto(data, client_address)
                print(f"Forwarded packet to client {client_address}")
        
        except KeyboardInterrupt: 
         print("Proxy server shutting down...")
         break
    
# Parse command-line arguments for the proxy server
parser = argparse.ArgumentParser(description="UDP Proxy Server")
parser.add_argument("--listen-ip", type=str, required=True, help="IP address to bind the proxy server.")
parser.add_argument("--listen-port", type=int, required=True, help="Port number to listen on for client packets.")
parser.add_argument("--target-ip", type=str, required=True, help="IP address of the server to forward packets to.")
parser.add_argument("--target-port", type=int, required=True, help="Port number of the server.")
parser.add_argument("--client-drop", type=float, required=True, help="Drop chance (0% - 100%) for packets from the client.")
parser.add_argument("--server-drop", type=float, required=True, help="Drop chance (0% - 100%) for packets from the server.")
parser.add_argument("--client-delay", type=float, required=True, help="Delay chance (0% - 100%) for packets from the client.")
parser.add_argument("--server-delay", type=float, required=True, help="Delay chance (0% - 100%) for packets from the server.")
parser.add_argument("--client-delay-time", type=str, required=True, help="Delay time in milliseconds (fixed or range).")
parser.add_argument("--server-delay-time", type=str, required=True, help="Delay time in milliseconds (fixed or range).")
args = parser.parse_args()

#Convert delay times to proper format
client_delay_time = [int(x) for x in args.client_delay_time.split('-')] if '-' in args.client_delay_time else float(args.client_delay_time)
server_delay_time = [int(x) for x in args.server_delay_time.split('-')] if '-' in args.server_delay_time else float(args.server_delay_time)


proxy_settings = {
    "listen_ip": args.listen_ip,
    "listen_port": args.listen_port,
    "target_ip": args.target_ip,
    "target_port": args.target_port,
    "client_drop": args.client_drop / 100,
    "server_drop": args.server_drop / 100,
    "client_delay": args.client_delay / 100,
    "server_delay": args.server_delay / 100,
    "client_delay_time": client_delay_time,
    "server_delay_time": server_delay_time
}

write_initial_settings_to_file("proxy_settings.json", proxy_settings)

# Start a thread to watch the settings file for updates
watch_thread = threading.Thread(target=watch_setting_file, args=("proxy_settings.json",), daemon=True)
watch_thread.start()

#Start the proxy server
start_proxy(args.listen_ip, args.listen_port, args.target_ip, args.target_port, 
            args.client_drop / 100, args.server_drop / 100, 
            args.client_delay / 100, args.server_delay / 100, 
            client_delay_time, server_delay_time)