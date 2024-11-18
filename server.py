import socket 
import argparse

def start_server(ip_address, port): 
#Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip_address, port))
    print(f"Server listening on {ip_address}:{port}")

    while True: 
        try: 
            #Recieve data from client
            data, client_address = server_socket.recvfrom(1024)
            print(f"Recieved message: {data.decode()} from {client_address}")

            #Send acknowledgement
            ack_message = "ACK"
            server_socket.sendto(ack_message.encode(), client_address)
            print(f"Sent acknowledgement to {client_address}")
            
        except KeyboardInterrupt:
            print("Server shutting down...")
            break

#Parse command-line arguments
parser=argparse.ArgumentParser(description="UDP Server")
parser.add_argument("--listen-ip", type=str, required=True, help="IP address to bind the server.")
parser.add_argument("--listen-port", type=int, required=True, help="Port to listen on")
args = parser.parse_args()

#Start the server 
start_server(args.listen_ip, args.listen_port)