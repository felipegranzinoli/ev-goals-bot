import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot EV+ rodando!")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

    def log_message(self, format, *args):
        pass

def rodar_servidor():
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    server.serve_forever()

if __name__ == "__main__":
    # Inicia o bot em thread separada
    from main import main
    bot_thread = threading.Thread(target=main, daemon=True)
    bot_thread.start()
    print("[servidor] Bot iniciado em background")

    # Servidor web no thread principal
    print("[servidor] Servidor web na porta 8080")
    rodar_servidor()