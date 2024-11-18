import argparse
import socket
import random
import time

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

#Start the proxy server
start_proxy(args.listen_ip, args.listen_port, args.target_ip, args.target_port, 
            args.client_drop / 100, args.server_drop / 100, 
            args.client_delay / 100, args.server_delay / 100, 
            client_delay_time, server_delay_time)