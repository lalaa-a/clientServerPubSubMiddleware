# server.py
import socket
import sys

def start_server(port):
 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:

        server_socket.bind(('', port))
        server_socket.listen(1)  
        print(f"[SERVER] Listening on port {port}...")
        
        client_socket, client_address = server_socket.accept()
        print(f"[SERVER] Connected to client: {client_address}")
        
        # Communication loop
        while True:
            # Receive message from client
            message = client_socket.recv(1024).decode('utf-8')
            
            if not message:
                print("[SERVER] Client disconnected.")
                break
            
            print(f"[CLIENT SAYS]: {message}")
            
            # Check for terminate keyword
            if message.strip().lower() == "terminate":
                print("[SERVER] Termination command received. 'Api Wawamu Rata Nagamu' closing connection.")
                break
        
        # Clean up
        client_socket.close()
        
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
    except Exception as e:
        print(f"[SERVER ERROR]: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python server.py <PORT>")
        print("Example: python server.py 5000")
        sys.exit(1)
    
    print("Welcome to 'Api Wawamu Rata Nagamu' Chat Application - Server Side")

    try:
        port = int(sys.argv[1])
        if not (1024 <= port <= 65535):
            print("Port must be between 1024 and 65535")
            sys.exit(1)
        
        start_server(port)
    except ValueError:
        print("Port must be a valid integer")
        sys.exit(1)