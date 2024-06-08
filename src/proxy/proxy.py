import socket
import logging
import select

def handle_client_and_server(client_socket, server_socket):
    # Open log files for requests and responses
    with open('request.log', 'wb') as request_log, open('response.log', 'wb') as response_log:
        sockets_list = [client_socket, server_socket]
        try:
            while True:
                # Non-blocking sockets with select
                read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
                for notified_socket in read_sockets:
                    data = notified_socket.recv(4096)
                    if data:
                        if notified_socket == client_socket:
                            print("Received from client and sending to server")
                            server_socket.sendall(data)
                            request_log.write(data)
                            request_log.flush()  # Ensure data is written to disk
                        else:
                            print("Received from server and sending to client")
                            client_socket.sendall(data)
                            response_log.write(data)
                            response_log.flush()  # Ensure data is written to disk
                    else:
                        print("Connection closed by the other side")
                        return
        except Exception as e:
            logging.error(f"Error during data handling: {e}")
        finally:
            client_socket.close()
            server_socket.close()
            print("Both connections closed.")

def setup_connection(listen_port, forward_host, forward_port):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('localhost', listen_port))
    listener.listen(1)
    print(f"Proxy listening on localhost:{listen_port}")

    while True:
        client_socket, client_address = listener.accept()
        print(f"Accepted connection from {client_address}")

        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((forward_host, forward_port))
            print(f"Connected to server at {forward_host}:{forward_port}")

            handle_client_and_server(client_socket, server_socket)
        except Exception as e:
            print(f"Failed to connect or forward data to {forward_host}:{forward_port}: {e}")
            client_socket.close()

# Configure the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Specify the local listening port and the destination host and port
local_port = 65432
destination_host = 'localhost'
destination_port = 4443
setup_connection(local_port, destination_host, destination_port)
