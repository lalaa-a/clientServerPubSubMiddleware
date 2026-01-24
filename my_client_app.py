#!/usr/bin/env python3
"""
Multi-Client Application with Publisher/Subscriber Support
Can connect as either PUBLISHER or SUBSCRIBER role
"""

import socket
import sys
import threading

def receive_messages(client_socket, role):
    """Background thread to receive messages from server"""
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print("\n[CONNECTION CLOSED] Server disconnected")
                break
            
            # Display received message with newline for better formatting
            print(f"\n[SERVER]: {message}")
            
            # Show prompt again for publishers
            if role == "PUBLISHER":
                print(">> ", end="", flush=True)
                
    except Exception as e:
        pass


def start_client(server_ip, server_port, role):
    """Start client with specified role (PUBLISHER or SUBSCRIBER)"""
    
    # Create TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to server
        print(f"[CLIENT] Connecting to {server_ip}:{server_port}...")
        client_socket.connect((server_ip, server_port))
        
        # Send role to server as first message
        client_socket.sendall(role.encode('utf-8'))
        
        print(f"[CLIENT] Connected as {role}")
        print(f"{'='*60}")
        
        # Start background thread to receive messages
        receive_thread = threading.Thread(
            target=receive_messages,
            args=(client_socket, role),
            daemon=True
        )
        receive_thread.start()
        
        # Wait for initial server response
        import time
        time.sleep(0.1)
        
        # Main interaction loop
        if role == "PUBLISHER":
            print("[PUBLISHER MODE] Type messages to publish to all subscribers")
            print("Type 'terminate' to quit\n")
            
            while True:
                message = input(">> ")
                
                if not message:
                    continue
                
                # Send message to server
                client_socket.sendall(message.encode('utf-8'))
                
                # Check for termination
                if message.strip().lower() == "terminate":
                    print("[CLIENT] Disconnecting...")
                    break
        
        else:  # SUBSCRIBER
            print("[SUBSCRIBER MODE] Listening for messages from publishers")
            print("Type 'terminate' to quit\n")
            
            while True:
                command = input()
                
                if command.strip().lower() == "terminate":
                    client_socket.sendall("terminate".encode('utf-8'))
                    print("[CLIENT] Disconnecting...")
                    break
        
    except ConnectionRefusedError:
        print(f"[ERROR] Could not connect to {server_ip}:{server_port}")
        print("Make sure the server is running on the specified address and port")
    except KeyboardInterrupt:
        print("\n[CLIENT] Interrupted by user")
    except Exception as e:
        print(f"[CLIENT ERROR]: {e}")
    finally:
        client_socket.close()
        print("[CLIENT] Connection closed")


def main():
    """Main entry point"""
    if len(sys.argv) != 4:
        print("Usage: python my_client_app.py <SERVER_IP> <SERVER_PORT> <ROLE>")
        print("\nRoles:")
        print("  PUBLISHER  - Send messages to all subscribers")
        print("  SUBSCRIBER - Receive messages from publishers")
        print("\nExamples:")
        # print("ex:  python my_client_app.py 192.168.10.2 5000 PUBLISHER")
        # print("ex:  python my_client_app.py 192.168.10.2 5000 SUBSCRIBER")
        # print("ex:  python my_client_app.py 127.0.0.1 5000 PUBLISHER")
        sys.exit(1)

    try:
        server_ip = sys.argv[1]
        server_port = int(sys.argv[2])
        role = sys.argv[3].upper()

        # Validate role
        if role not in ["PUBLISHER", "SUBSCRIBER"]:
            print("Error: Role must be either 'PUBLISHER' or 'SUBSCRIBER'")
            sys.exit(1)
        
        # Validate port
        if not (1024 <= server_port <= 65535):
            print("Error: Port must be between 1024 and 65535")
            sys.exit(1)
        
        start_client(server_ip, server_port, role)
        
    except ValueError:
        print("Error: Port must be a valid integer")
        sys.exit(1)


if __name__ == "__main__":
    main()
