# -*- coding:utf-8 -*-
import httpie
from http.server import BaseHTTPRequestHandler, HTTPServer

class RequestHandler(BaseHTTPRequestHandler):
    """处理请求并返回页面"""
    # 页面模板
    Page = """\
    <html>
    <body>
    <p>Hello,web!</p>
    </body>
    </html>
    """
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-length", str(len(self.Page)))  #字符串类型
        self.end_headers()
        self.wfile.write(self.Page.encode())

if __name__ == '__main__':
    print("server start...")
    serverAddr = ('', 8080)
    server = HTTPServer(serverAddr, RequestHandler)
    server.serve_forever()

