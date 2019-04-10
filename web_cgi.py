# -*- coding: utf-8 -*-

"""
Created on Thursday

"""
import http.server as hs
import sys, os
import subprocess

class ServerException(Exception):
    """服务器内部错误"""

    pass



class base_case(object):
    """定义基类，用来处理不同的条件类，条件类继承该基类"""
    def handle_file(self, handler, full_path):
        try:
            with open(full_path, 'r', encoding="UTF-8") as file:
                content = file.read()

            handler.send_content(content, 200)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(full_path, msg)

            handler.handle_error(msg)

    # 判断路径是否是目录，且需要判断目录下是否包含index.html页面

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index_html.html')

    def test(self, handler):
        assert False, "Not implemented."

    def act(self, handler):
        assert False, "Not implemented."


# 如果路径不存在
class case_no_path(base_case):
    """ 如果路径不存在 """

    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))


class case_CGI_file(base_case):
    """可执行脚本"""

    def run_cgi(self, handler):

        # 运行cgi脚本并获得格式化的输出，从而显示到浏览器上
        data = subprocess.check_output(["python", handler.full_path], shell=False)

        # self.wfile.write(bytes(fullpath, encoding='UTF-8'))

        handler.send_content(page=str(data, encoding='UTF-8'))

    def test(self, handler):
        print(os.path.isfile(handler.full_path) and handler.full_path.endswith('.py'))
        return os.path.isfile(handler.full_path) and \
            handler.full_path.endswith('.py')


    def act(self, handler):
        self.run_cgi(handler)

# 所有的情况都不符合时的默认处理类
class case_allother_fail(base_case):
    """所有情况都不符合时的默认类"""

    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknown object {0}".format(handler.full_path))

class case_is_file(base_case):
    """输入的路径是一个文件"""

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        self.handle_file(handler, handler.full_path)



class case_index_file(base_case):
    """输入根url时显示index.html"""

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
         os.path.isfile(self.index_path(handler))

    def act(self, handler):
        self.handle_file(handler, self.index_path(handler))

class RequestHandler(hs.BaseHTTPRequestHandler):
    """
    请求路径合法则返回相应处理，
    否则返回错误页面
    """

    full_path = ""

    # 一定要注意条件类的优先顺序不同，对于文件的捕捉能力也不同，越是针对某种特例的条件
    # 越应该放在前面

    Cases = [case_no_path(),
             case_index_file(),
             case_CGI_file(),
             case_is_file(),
             case_allother_fail()]



    def send_content(self, page, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content=Length", str(len(page)))
        self.end_headers()
        self.wfile.write(bytes(page, encoding='UTF-8'))

    def do_GET(self):
        try:
            self.full_path = os.getcwd() + self.path

            for case in self.Cases:
                if case.test(self):
                    case.act(self)
                    break
        except Exception as msg:
            self.handle_error(msg)



    Error_Page = """\
    <html>
    <body>
    <h1>Error accessing {path} </h1>
    <p>{msg}</p>
    </body>
    </html>
    """

    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content, 404)


if __name__ == '__main__':
    print("server start...")
    httpAddress = ('', 8080)
    httpd = hs.HTTPServer(httpAddress, RequestHandler)

    httpd.serve_forever()
