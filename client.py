import argparse
import socket
import time
import struct


def start_client(ip, port, timeout):

    message_id = 0

    #Create UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
    client_socket.settimeout(timeout)
    
    print("UDP client started. Type your message(s) below! (type 'exit' to quit)")

    try: 
        while True: 
            #Get user input for the message
            message = input("Enter message: ")

            #Exit the loop if user types exit
            if message.lower() == "exit":
                print("Exiting client...")
                break

            retries = 0 
            acknowledgement_received = False 
            message_id += 1

            #Retry sending message if no acknowledgment is received
            while retries < 5 and not acknowledgement_received: 
                
                #Protocol: Version (1 byte), Content size (2 bytes), Message content (variable size)
                version = 1
                content = message.encode()
                content_size = len(content)

                #Pack the message (Version + Content size + Message content)
                message_to_send = struct.pack('!B I H ', version, message_id, content_size) + content
                client_socket.sendto(message_to_send, (ip, port))
                print(f"Sent message: {message} to {ip}:{port}")

                #Wait for acknowledgement
                try: 
                    data, server_address = client_socket.recvfrom(1024)
                    ack_message = data.decode() #Decode the received acknowledgment 

                    # Unpack the received acknowledgment (Message ID + ACK string)
                    ack_message_id, ack_status = struct.unpack('!I 3s', data[:7])  # Assuming ACK is 3 bytes
                    ack_status = ack_status.decode()  # Decode acknowledgment string

                    if ack_status == "ACK" and ack_message_id == message_id:
                        print(f"Received acknowledgment for Message ID {ack_message_id} from {server_address}")
                        acknowledgement_received = True
                    else:
                        print(f"Unexpected acknowledgment: {ack_status} for Message ID {ack_message_id}")


                except socket.timeout: 
                    print(f"No acknowledgement received within {timeout} seconds. Retrying attempt {retries + 1} of 5")
                    retries += 1 #Increment retry count 
                    time.sleep(timeout)

            #If the acknowledgment is not received after 5 attempts
            if not acknowledgement_received: 
                print(f"Failed to recieve acknowledgment after 5 retries. Giving up...")

    except KeyboardInterrupt: 
        print("\nClient shutting down...")
    finally: 
        client_socket.close()

#Parse command-line arguments
parser = argparse.ArgumentParser(description="UDP Client")
parser.add_argument("--target-ip", type=str, required=True, help="IP address of the server")
parser.add_argument("--target-port", type=int, required=True, help="Port number of the server")
parser.add_argument("--timeout", type=int, required=True, help="Timeout for waiting for acknowledgments")
args = parser.parse_args()

#Start the client 
start_client(args.target_ip, args.target_port, args.timeout)
