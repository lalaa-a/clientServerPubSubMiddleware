# server.py
import socket
import sys
import threading

class ClientHandler:
    def __init__(self, client_socket, client_address, role):
        self.socket = client_socket
        self.address = client_address
        self.role = role

    def send_message(self,message):
        try:
            self.socket.sendall(message.encode('utf-8'))
        except:
            pass

class Server:
    def __init__(self, port):
        self.port = port
        self.server_socket = None
        self.clients = []
        self.lock = threading.Lock()

    def broadcast_to_subscribers(self,message,sender_address,sender_role):
        """Send message to all sunbcriber clients"""
        with self.lock:
            for client in self.clients:
                if client.role == "SUBSCRIBER" and client.address != sender_address:
                    try:
                        client.send_message(f"[FROM {sender_role} {sender_address[0]}:{sender_address[1]}]: {message}")
                    except:
                        self.remove_client(client)
    
    def remove_client(self,client_handler):
        """remove client from list"""
        with self.lock:
            if client_handler in self.clients:
                self.clients.remove(client_handler)
                print(f"[SERVER] Removed client: {client_handler.address} ({client_handler.role}) disconnected.")
                print(f"[SERVER] Active Clients: {len(self.clients)}") 

    def handle_client(self,client_socket,client_address):
        """Handle individual client connection"""
        client_handler = None

        try:
            # First message from client should be its role
            role_message = client_socket.recv(1024).decode('utf-8')
            if not role_message:
                client_socket.close()
                return
            
            role = role_message.strip().upper()
            
            if role not in ["PUBLISHER", "SUBSCRIBER"]:
                client_socket.sendall("ERROR: Invalid role. Use PUBLISHER or SUBSCRIBER".encode('utf-8'))
                client_socket.close()
                return
            
            client_handler = ClientHandler(client_socket, client_address, role)
            
            with self.lock:
                self.clients.append(client_handler)
            
            print(f"[SERVER] Client {client_address} connected as {role}.")
            print(f"[SERVER] Active Clients: {len(self.clients)}")

            client_socket.sendall(f"Connected to server as {role}.".encode('utf-8'))
            
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                
                if not message:
                    print(f"[SERVER] Client {client_address} disconnected.")
                    break
                
                print(f"[{role} {client_address[0]}:{client_address[1]} SAYS]: {message}")
                
                if message.strip().lower() == "terminate":
                    print(f"[SERVER] Termination command received from {client_address}. 'Api Wawamu Rata Nagamu' closing connection.")
                    break
                
                if role == "PUBLISHER":
                    self.broadcast_to_subscribers(message, client_address, role)
                    client_socket.sendall("Message published successfully...".encode('utf-8'))
                elif role == "SUBSCRIBER":
                    client_socket.sendall(f"You are a subscriber for this Publisher.Listening for messages...".encode('utf-8'))

        except ConnectionResetError:
            print(f"[SERVER] Client {client_address} forcibly closed the connection")    
        except Exception as e:
            print(f"[SERVER ERROR] with client {client_address}: {e}")
        finally:
            self.remove_client(client_handler)
            client_socket.close()

    def start(self):
        """Start the multi client server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind(('', self.port))
            self.server_socket.listen(5) #danat clients la 5kt connect wenna puluwan
            print(f"[SERVER] Listening on port {self.port}...")
            print("[SERVER] Waiting for clients (PUBLISHER/SUBSCRIBER)...")
            
            while True:
                client_socket, client_address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                )
                client_thread.start()

        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down...")
        except Exception as e:
            print(f"[SERVER ERROR]: {e}")
        finally:
            self.server_socket.close()
            print("[SERVER] Server closed.")

def start_server(port):
    server = Server(port)
    server.start()
        

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