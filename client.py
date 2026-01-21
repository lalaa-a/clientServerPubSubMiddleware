# client.py
import socket
import sys
import threading

def receive_messages(sock):
    """Thread to receive messages from server"""
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            if not message:
                print("[CLIENT] Server disconnected.")
                break
            print(message)
        except:
            break


def start_client(server_ip, port, role, topic):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((server_ip, port))
        print(f"[CLIENT] Connected to server {server_ip}:{port}")

        # Send ROLE and TOPIC to server
        init_message = f"{role} {topic}"
        client_socket.sendall(init_message.encode('utf-8'))

        # Receive server confirmation
        response = client_socket.recv(1024).decode('utf-8')
        print(response)

        # Start receiving thread (important for subscribers)
        receiver_thread = threading.Thread(
            target=receive_messages,
            args=(client_socket,),
            daemon=True
        )
        receiver_thread.start()

        # CLI loop
        while True:
            user_input = input()

            client_socket.sendall(user_input.encode('utf-8'))

            if user_input.strip().lower() == "terminate":
                print("[CLIENT] Terminating connection...")
                break

    except ConnectionRefusedError:
        print("[CLIENT ERROR] Unable to connect to server.")
    except Exception as e:
        print(f"[CLIENT ERROR] {e}")
    finally:
        client_socket.close()
        print("[CLIENT] Connection closed.")


if __name__ == "__main__":

    if len(sys.argv) != 5:
        print("Usage: python client.py <SERVER_IP> <PORT> <ROLE> <TOPIC>")
        print("Example:")
        print("python client.py 127.0.0.1 5000 PUBLISHER TOPIC_A")
        print("python client.py 127.0.0.1 5000 SUBSCRIBER TOPIC_A")
        sys.exit(1)

    server_ip = sys.argv[1]

    try:
        port = int(sys.argv[2])
    except ValueError:
        print("Port must be a valid integer")
        sys.exit(1)

    role = sys.argv[3].upper()
    topic = sys.argv[4].upper()

    if role not in ["PUBLISHER", "SUBSCRIBER"]:
        print("Role must be either PUBLISHER or SUBSCRIBER")
        sys.exit(1)

    print("Welcome to 'Api Wawamu Rata Nagamu' Chat Application - Client Side")
    print(f"Role  : {role}")
    print(f"Topic : {topic}")

    start_client(server_ip, port, role, topic)
