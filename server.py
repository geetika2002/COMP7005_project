import socket 
import argparse
import struct

def start_server(ip_address, port): 
#Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip_address, port))
    print(f"Server listening on {ip_address}:{port}")

    while True: 
        try: 
            #Recieve data from client
            data, client_address = server_socket.recvfrom(1024)

            #Unpack the protocol (Version + content size + message content)
            version, message_id, content_size = struct.unpack('!B I H', data[:7]) #Unpack first bytes for version and content size
            content = data[3:] #The remaining bytes are the message content 

            print(f"Received message: {content.decode()} (Version: {version}), (Size: {content_size}) from {client_address}")
            
            #Send acknowledgement to client
            response = struct.pack('!I 3s', message_id, b"ACK")
            server_socket.sendto(response, client_address)
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