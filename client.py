import argparse
import socket
import time

def start_client(ip, port, timeout):

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

            #Retry sending message if no acknowledgment is received
            while retries < 5 and not acknowledgement_received: 
                
                #Send message to server
                client_socket.sendto(message.encode(), (ip, port))
                print(f"Sent message: {message} to {ip}:{port}")

                #Wait for acknowledgement
                try: 
                    data, server_address = client_socket.recvfrom(1024)
                    print(f"Recieved acknowledgment: {data.decode()} from {server_address}")
                    acknowledgement_received = True

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
