import http.server
import socketserver
import json
import sqlite3
import os

PORT = 8080
DIRECTORY = "webapp"
DB_PATH = "orders.db"

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve from webapp directory directly
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path == '/api/products':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            # Enable CORS for Telegram inside browser environments
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
            self.end_headers()
            
            try:
                # Direct read from dynamic database
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT product_id, product_name, cost, sell FROM inventory")
                rows = cursor.fetchall()
                
                products = []
                for r in rows:
                    p_id = r["product_id"]
                    # Extract number from product ID for podium image mapping
                    num = "".join(filter(str.isdigit, p_id))
                    img_path = f"assets/podium_{num}.png" if num else "assets/logo.png"
                    
                    products.append({
                        "id": p_id,
                        "name": r["product_name"],
                        "price": r["sell"],
                        "cost": r["cost"],
                        "img": img_path
                    })
                conn.close()
                self.wfile.write(json.dumps(products).encode('utf-8'))
            except Exception as e:
                print(f"Error in server products list: {e}")
                self.wfile.write(json.dumps([]).encode('utf-8'))
        else:
            # Standard static file serving
            super().do_GET()

    def do_OPTIONS(self):
        # Support dynamic pre-flight CORS requests
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        self.end_headers()

if __name__ == "__main__":
    # Ensure working directory is resolved correctly
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    
    # TCPServer allows reusing address to prevent "address already in use" errors
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"Serving premium dynamic webapp on port {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
