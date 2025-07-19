#!/usr/bin/env python3
"""
Minimal Railway test - simplest possible Python server
"""

import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        if self.path == '/health':
            response = '{"status": "healthy", "message": "Railway Python test working"}'
        else:
            response = '{"message": "Railway Python deployment test", "status": "working"}'
        
        self.wfile.write(response.encode())

def main():
    port = int(os.getenv("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    print(f"🚀 Test server starting on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    main()