import http.server
import ssl
import socketserver

class HTTPSServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Hello, secure world!")

port = 4443
httpd = socketserver.TCPServer(('localhost', port), HTTPSServer)

# Setup SSL context to secure the server
httpd.socket = ssl.wrap_socket(httpd.socket, keyfile="./certs/key.pem", certfile='./certs/cert.pem', server_side=True)

print(f"Serving HTTPS on localhost port {port}")
httpd.serve_forever()
