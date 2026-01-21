# server.py
import socket
import sys
import threading

class ClientHandler:
    def __init__(self, client_socket, client_address, role, topic):
        self.socket = client_socket
        self.address = client_address
        self.role = role
        self.topic = topic

    def send_message(self, message):
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

    def broadcast_to_subscribers(self, message, sender):
        """Send message ONLY to subscribers of SAME topic"""
        with self.lock:
            for client in self.clients:
                if (
                    client.role == "SUBSCRIBER"
                    and client.topic == sender.topic
                    and client.address != sender.address
                ):
                    try:
                        client.send_message(
                            f"[TOPIC {sender.topic}] "
                            f"[FROM {sender.role} {sender.address[0]}:{sender.address[1]}]: "
                            f"{message}"
                        )
                    except:
                        self.remove_client(client)

    def remove_client(self, client_handler):
        with self.lock:
            if client_handler in self.clients:
                self.clients.remove(client_handler)
                print(f"[SERVER] Removed client: {client_handler.address} "
                      f"({client_handler.role}, {client_handler.topic})")
                print(f"[SERVER] Active Clients: {len(self.clients)}")

    def handle_client(self, client_socket, client_address):
        client_handler = None

        try:
            # Expect: ROLE TOPIC
            init_message = client_socket.recv(1024).decode('utf-8').strip()
            if not init_message:
                client_socket.close()
                return

            parts = init_message.split()

            if len(parts) != 2:
                client_socket.sendall(
                    "ERROR: Use format -> <ROLE> <TOPIC>".encode('utf-8')
                )
                client_socket.close()
                return

            role, topic = parts[0].upper(), parts[1].upper()

            if role not in ["PUBLISHER", "SUBSCRIBER"]:
                client_socket.sendall(
                    "ERROR: Role must be PUBLISHER or SUBSCRIBER".encode('utf-8')
                )
                client_socket.close()
                return

            client_handler = ClientHandler(
                client_socket, client_address, role, topic
            )

            with self.lock:
                self.clients.append(client_handler)

            print(f"[SERVER] Client {client_address} connected as "
                  f"{role} on topic {topic}")
            print(f"[SERVER] Active Clients: {len(self.clients)}")

            client_socket.sendall(
                f"Connected as {role} on topic {topic}".encode('utf-8')
            )

            while True:
                message = client_socket.recv(1024).decode('utf-8')

                if not message:
                    break

                print(f"[{role} {topic} {client_address[0]}:{client_address[1]}]: {message}")

                if message.strip().lower() == "terminate":
                    print(f"[SERVER] Terminate from {client_address}")
                    break

                if role == "PUBLISHER":
                    self.broadcast_to_subscribers(message, client_handler)
                    client_socket.sendall(
                        "Message published to subscribers.".encode('utf-8')
                    )
                else:
                    client_socket.sendall(
                        f"Subscribed to topic {topic}. Waiting for messages..."
                        .encode('utf-8')
                    )

        except ConnectionResetError:
            print(f"[SERVER] Client {client_address} forcibly disconnected")
        except Exception as e:
            print(f"[SERVER ERROR] {e}")
        finally:
            if client_handler:
                self.remove_client(client_handler)
            client_socket.close()

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind(('', self.port))
            self.server_socket.listen(5)
            print(f"[SERVER] Listening on port {self.port}...")
            print("[SERVER] Waiting for clients...")

            while True:
                client_socket, client_address = self.server_socket.accept()
                threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                ).start()

        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down...")
        finally:
            self.server_socket.close()
            print("[SERVER] Server closed.")


def start_server(port):
    server = Server(port)
    server.start()


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python server.py <PORT>")
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