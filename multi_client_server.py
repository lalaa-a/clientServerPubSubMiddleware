#!/usr/bin/env python3
"""
Multi-Client Publisher-Subscriber Server
Handles multiple concurrent client connections using threading
Supports PUBLISHER and SUBSCRIBER roles
"""

import socket
import sys
import threading

class ClientHandler:
    """Represents a connected client with its socket, address, and role"""
    
    def __init__(self, client_socket, client_address, role):
        self.socket = client_socket
        self.address = client_address
        self.role = role
        self.active = True

    def send_message(self, message):
        """Send message to this client"""
        try:
            self.socket.sendall(message.encode('utf-8'))
            return True
        except Exception as e:
            print(f"[ERROR] Failed to send to {self.address}: {e}")
            self.active = False
            return False


class PubSubServer:
    """Publisher-Subscriber Server with multi-client support"""
    
    def __init__(self, port):
        self.port = port
        self.server_socket = None
        self.publishers = []  # List of publisher clients
        self.subscribers = []  # List of subscriber clients
        self.lock = threading.Lock()  # Thread-safe operations

    def add_client(self, client_handler):
        """Add client to appropriate list based on role"""
        with self.lock:
            if client_handler.role == "PUBLISHER":
                self.publishers.append(client_handler)
                print(f"[SERVER] Added PUBLISHER: {client_handler.address}")
            elif client_handler.role == "SUBSCRIBER":
                self.subscribers.append(client_handler)
                print(f"[SERVER] Added SUBSCRIBER: {client_handler.address}")
            
            print(f"[SERVER] Active - Publishers: {len(self.publishers)}, Subscribers: {len(self.subscribers)}")

    def remove_client(self, client_handler):
        """Remove client from appropriate list"""
        with self.lock:
            if client_handler.role == "PUBLISHER" and client_handler in self.publishers:
                self.publishers.remove(client_handler)
                print(f"[SERVER] Removed PUBLISHER: {client_handler.address}")
            elif client_handler.role == "SUBSCRIBER" and client_handler in self.subscribers:
                self.subscribers.remove(client_handler)
                print(f"[SERVER] Removed SUBSCRIBER: {client_handler.address}")
            
            print(f"[SERVER] Active - Publishers: {len(self.publishers)}, Subscribers: {len(self.subscribers)}")

    def broadcast_to_subscribers(self, message, sender_address, sender_role):
        """
        Forward message from publisher to ALL subscriber clients
        Publishers should NOT receive these messages
        """
        with self.lock:
            subscribers_copy = self.subscribers.copy()
        
        formatted_message = f"[FROM {sender_role} {sender_address[0]}:{sender_address[1]}]: {message}"
        
        for subscriber in subscribers_copy:
            if subscriber.active:
                success = subscriber.send_message(formatted_message)
                if not success:
                    self.remove_client(subscriber)
        
        print(f"[BROADCAST] Sent to {len(subscribers_copy)} subscriber(s)")

    def handle_client(self, client_socket, client_address):
        """Handle individual client connection"""
        client_handler = None

        try:
            # First message from client should be its role
            role_message = client_socket.recv(1024).decode('utf-8')
            if not role_message:
                client_socket.close()
                return
            
            role = role_message.strip().upper()
            
            # Validate role
            if role not in ["PUBLISHER", "SUBSCRIBER"]:
                error_msg = "ERROR: Invalid role. Use PUBLISHER or SUBSCRIBER"
                client_socket.sendall(error_msg.encode('utf-8'))
                client_socket.close()
                print(f"[SERVER] Rejected connection from {client_address} - Invalid role: {role}")
                return
            
            # Create client handler and add to appropriate list
            client_handler = ClientHandler(client_socket, client_address, role)
            self.add_client(client_handler)
            
            # Send confirmation to client
            confirmation = f"Connected to server as {role}"
            client_socket.sendall(confirmation.encode('utf-8'))
            
            # Message handling loop
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                
                if not message:
                    print(f"[SERVER] Client {client_address} ({role}) disconnected")
                    break
                
                # Display message on server terminal
                print(f"[{role} {client_address[0]}:{client_address[1]}]: {message}")
                
                # Check for termination command
                if message.strip().lower() == "terminate":
                    print(f"[SERVER] Termination command from {client_address} ({role})")
                    client_socket.sendall("Goodbye!".encode('utf-8'))
                    break
                
                # Handle based on client role
                if role == "PUBLISHER":
                    # Broadcast to all subscribers (NOT to other publishers)
                    self.broadcast_to_subscribers(message, client_address, role)
                    client_socket.sendall("Message published to subscribers".encode('utf-8'))
                
                elif role == "SUBSCRIBER":
                    # Subscribers don't publish, just acknowledge
                    client_socket.sendall("You are a subscriber. Listening for messages...".encode('utf-8'))

        except ConnectionResetError:
            print(f"[SERVER] Client {client_address} forcibly closed the connection")
        except Exception as e:
            print(f"[SERVER ERROR] with client {client_address}: {e}")
        finally:
            if client_handler:
                self.remove_client(client_handler)
            client_socket.close()

    def start(self):
        """Start the multi-client server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            # Bind to all interfaces on specified port
            self.server_socket.bind(('', self.port))
            self.server_socket.listen(10)  # Allow up to 10 queued connections
            
            print(f"{'='*60}")
            print(f"  Multi-Client Publisher-Subscriber Server")
            print(f"{'='*60}")
            print(f"[SERVER] Listening on port {self.port}")
            print(f"[SERVER] Waiting for PUBLISHER/SUBSCRIBER clients...")
            print(f"[SERVER] Press Ctrl+C to stop")
            print(f"{'='*60}\n")
            
            # Accept clients in infinite loop
            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f"\n[SERVER] New connection from {client_address}")
                
                # Create new thread for each client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                )
                client_thread.start()

        except KeyboardInterrupt:
            print("\n\n[SERVER] Shutting down...")
        except Exception as e:
            print(f"[SERVER ERROR]: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
            print("[SERVER] Server closed")


def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python multi_client_server.py <PORT>")
        print("Example: python multi_client_server.py 5000")
        sys.exit(1)

    try:
        port = int(sys.argv[1])
        if not (1024 <= port <= 65535):
            print("Error: Port must be between 1024 and 65535")
            sys.exit(1)
        
        server = PubSubServer(port)
        server.start()
        
    except ValueError:
        print("Error: Port must be a valid integer")
        sys.exit(1)


if __name__ == "__main__":
    main()
