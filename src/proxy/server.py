import http.server
import ssl
import socketserver

class HTTPSServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Hello, secure world!")

def main():
    port = 4443
    httpd = socketserver.TCPServer(('localhost', port), HTTPSServer)

    # Setup SSL context to secure the server
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.maximum_version = ssl.TLSVersion.TLSv1_2
    context.set_ciphers('ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-CHACHA20-POLY1305:DHE-RSA-CHACHA20-POLY1305')

    # Load your certificate and key
    context.load_cert_chain(certfile='./certs/cert.pem', keyfile='./certs/key.pem')

    # Wrap the server's socket with the SSL context
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f"Serving HTTPS on localhost port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    main()
