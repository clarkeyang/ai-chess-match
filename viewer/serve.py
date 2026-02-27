#!/usr/bin/env python3
"""체스 관전 뷰어 HTTP 서버 (포트 8080)"""
import http.server
import os

PORT = 8080
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print(f"체스 관전 뷰어: http://localhost:{PORT}")
print("Ctrl+C로 종료")

handler = http.server.SimpleHTTPRequestHandler
handler.extensions_map.update({".json": "application/json"})

with http.server.HTTPServer(("", PORT), handler) as httpd:
    httpd.serve_forever()
