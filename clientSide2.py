# client.py
import socket
import sys
import threading

def receive_messages(client_socket):
    """Function to receive messages from server"""
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print("\n[CONNECTION CLOSED] Server disconnected")
                break
            print(f"\n[FROM SERVER]: {message}")
    except:
        pass


def start_client(server_ip, server_port, role):
    """Start client with specific role"""
  
    #creating TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        #server connection server_ip = localhost nisa 127.0.0.1 , port eka api server side eke run karana port eka danna ona
        client_socket.connect((server_ip, server_port))

        #connection ekn passe role eka server ta ywanawa
        client_socket.sendall(role.encode('utf-8'))
        print(f"[CLIENT] Connected as {role} to server at {server_ip}:{server_port}")
        print("[CLIENT] Type messages to send (if publisher).Type 'terminate' to quit.")

        # Start receive thread for ALL roles (both PUBLISHER and SUBSCRIBER)
        receive_thread = threading.Thread(
            target=receive_messages,
            args=(client_socket,),
            daemon=True
        )
        receive_thread.start()
 
        while True:
            if role == "PUBLISHER":
                print("You are in PUBLISHER mode.Type your message to publish.")
                message = input(">> ")
                client_socket.sendall(message.encode('utf-8'))
            
                # Check for terminate keyword
                if message.strip().lower() == "terminate":
                    print("[CLIENT] Termination command sent.'Api Wawamu Rata Nagamu' Publisher Disconnecting...")
                    break
            else:
                # In subscriber mode, just wait for messages
                command = input("Type 'terminate' to quit: ")
                if command.strip().lower() == "terminate":
                    client_socket.sendall("terminate".encode('utf-8'))
                    print("[CLIENT] Termination command sent. Subscriber Disconnecting...")
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

    if len(sys.argv) != 4:
        print("Usage: python client.py <SERVER_IP> <SERVER_PORT> <ROLE>")
        print("Roles: 'PUBLISHER' or 'SUBSCRIBER'")
        print("Example: if localhost - python clientSide2.py 127.0.0.1 5000 PUBLISHER") # port eka change krnna pluwn.ee port ekm server tath dennon hbai
        sys.exit(1)
    
    print("Welcome to 'Api Wawamu Rata Nagamu' Chat Application - Client Side")

    try:
        server_ip = sys.argv[1]
        server_port = int(sys.argv[2])
        role = sys.argv[3].upper()

        if role not in ["PUBLISHER", "SUBSCRIBER"]:
            print("Role must be either 'PUBLISHER' or 'SUBSCRIBER'")
            sys.exit(1)
        
        start_client(server_ip, server_port, role)
    except ValueError:
        print("Port must be a valid integer")
        sys.exit(1)