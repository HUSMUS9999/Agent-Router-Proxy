import http.server
import socketserver
import urllib.request
import sys

PORT = 8888
TARGET_URL = "https://agentrouter.org/v1"

API_KEY = "sk---------------"

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Clean up the path
        clean_path = self.path.replace('/v1', '') if self.path.startswith('/v1') else self.path
        target = f"{TARGET_URL}{clean_path}"
        
        print(f"🔄 Forwarding request via Codex Disguise: {clean_path}")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            
            "User-Agent": "codex_cli_rs/0.71.0 (Debian 6.4.0; x86_64) VTE/7006",
            "Originator": "codex_cli_rs",
            "Accept": "text/event-stream"
        }

        req = urllib.request.Request(target, data=post_data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req) as response:
                self.send_response(response.status)
                
                for key, value in response.headers.items():
                    if key.lower() not in ['content-encoding', 'transfer-encoding', 'content-length']:
                        self.send_header(key, value)
                self.end_headers()
                
                while True:
                    chunk = response.read(1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                print("✅ Success! Response forwarded.")
                
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8')
            print(f"❌ Error {e.code}: {error_msg}")
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(error_msg.encode('utf-8'))
        except Exception as e:
            print(f"❌ Connection Failed: {str(e)}")
            self.send_error(500, str(e))

print(f"🚀 Codex Replica Proxy running on http://127.0.0.1:{PORT}")
print("Leave this terminal open!")

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
    httpd.serve_forever()
