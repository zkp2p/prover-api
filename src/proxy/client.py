import socket
import ssl

def run_client_through_proxy(proxy_host, proxy_port, target_host, target_port):
    context = ssl.create_default_context()  
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE  # Disable certificate verification because self signed

    # Connect to the proxy
    with socket.create_connection((proxy_host, proxy_port)) as sock:
        with context.wrap_socket(sock, server_hostname=target_host) as ssock:
            request = "GET / HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n".format(target_host)
            print(f'Sending request: {request}')
            ssock.sendall(request.encode('utf-8'))

            # Receive the complete response
            response = b""
            try:
                while True:
                    data = ssock.recv(4096)
                    if not data:
                        break
                    response += data
            except ssl.SSLError as e:
                print("SSL error:", e)
            except Exception as e:
                print("Error receiving data:", e)

            print("Received response:", response.decode('utf-8'))

if __name__ == "__main__":
    # Proxy details
    proxy_host = 'localhost'
    proxy_port = 65432  # Port where your proxy is listening

    # Target server details
    target_host = 'localhost'
    target_port = 4443  # Port where your TLS server is listening

    run_client_through_proxy(proxy_host, proxy_port, target_host, target_port)
