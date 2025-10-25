#!/usr/bin/env python3
"""
Simple local development server with clean URL support
Mimics Netlify's URL rewriting behavior for local testing

Usage: python serve.py
Then visit: http://localhost:8000
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 8000

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Handle clean URLs (e.g., /about -> /about.html)
        if not os.path.splitext(self.path)[1]:
            # No file extension, try adding .html
            html_path = self.path.rstrip('/') + '.html'
            if os.path.isfile('.' + html_path):
                self.path = html_path
        
        # Default behavior
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"🚀 Server running at http://localhost:{PORT}/")
        print(f"📁 Serving files from: {os.getcwd()}")
        print(f"\n✨ Clean URLs enabled:")
        print(f"   http://localhost:{PORT}/about")
        print(f"   http://localhost:{PORT}/about.html")
        print(f"\n Press Ctrl+C to stop\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped")

