# client.py
import socket
import sys


def start_client(server_ip, server_port):
  
    #creating TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        #server connection server_ip = localhost nisa 127.0.0.1 , port eka api server side eke run karana port eka danna ona
        client_socket.connect((server_ip, server_port))
        print(f"[CLIENT] Connected to server at {server_ip}:{server_port}")
        print("[CLIENT] Type messages to send to server. Type 'terminate' to quit.")
        
 
        while True:

            message = input("> ")
            
            client_socket.sendall(message.encode('utf-8'))
            
            # Check for terminatie keyword
            if message.strip().lower() == "terminate":
                print("[CLIENT] Termination command sent. 'Api Wawamu Rata Nagamu' Disconnecting...")
                break
        
    except ConnectionRefusedError:
        print(f"[CLIENT ERROR] Could not connect to {server_ip}:{server_port}")
        print("Make sure server is running and port is correct.")
    except KeyboardInterrupt:
        print("\n[CLIENT] Interrupted by user.")
    except Exception as e:
        print(f"[CLIENT ERROR]: {e}")
    finally:
        client_socket.close()
        print("[CLIENT] Connection closed.")

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python client.py <SERVER_IP> <SERVER_PORT>")
        print("Example: if localhost - python client.py 127.0.0.1 5000")
        sys.exit(1)
    
    print("Welcome to 'Api Wawamu Rata Nagamu' Chat Application - Client Side")

    try:
        server_ip = sys.argv[1]
        server_port = int(sys.argv[2])
        
        start_client(server_ip, server_port)
    except ValueError:
        print("Port must be a valid integer")
        sys.exit(1)