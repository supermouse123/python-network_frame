# @Time    : 2021/1/27
# @Author  : sunyingqiang
# @Email   : 344670075@qq.com

import threading
import socket
import re
import sys
import json


class WSGIServer:
    """模拟WSGI服务器"""

    def __init__(self, port, app, conf_info):
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_server_socket.bind(('', port))
        self.tcp_server_socket.listen(128)
        self.application = app
        self.conf_info = conf_info

    def service_client(self, new_socket):
        request = new_socket.recv(1024).decode('utf-8')
        request_lines = request.splitlines()
        file_name = ''
        ret = re.match(r'[^/]+(/[^ ]*)', request_lines[0])
        if ret:
            file_name = ret.group(1)
            if file_name == '/':
                file_name = '/index.html'

        if not file_name.endswith('.html'):
            try:
                f = open(self.conf_info['static_path'] + file_name, 'rb')
            except:
                response = 'HTTP/1.1 404 NOT FOUND\r\n'
                response += "\r\n"
                response += '--------file not found------'
                new_socket.send(response.encode('utf-8'))
            else:
                html_content = f.read()
                f.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += '\r\n'
                new_socket.send(response.encode('utf-8'))
                new_socket.send(html_content)
        else:
            env = dict()
            env['PATH_INFO'] = file_name
            body = self.application(env, self.set_response_header)
            header = 'HTTP/1.1 %s\r\n' % self.status
            for temp in self.headers:
                header += '%s:%s\r\n' % (temp[0], temp[1])
            header += '\r\n'
            response = header + body
            new_socket.send(response.encode('utf-8'))
        new_socket.close()

    def set_response_header(self, status, headers):
        self.status = status
        self.headers = headers

    def run_forever(self):
        while True:
            new_socket, client_addr = self.tcp_server_socket.accept()
            p = threading.Thread(target=self.service_client, args=(new_socket,))
            p.start()
            # new_socket.close()

def main():
    if len(sys.argv) == 3:   #sys.argv获取控制台输入的东西
        try:
            port = int(sys.argv[1])
            frame_app_name = sys.argv[2]
        except:
            print('端口输入错误')
            return
    else:
        print('python xxx.py port mini_frame:application')
    ret = re.match(r'([^:]+):(.*)', frame_app_name)
    if ret:
        frame_name = ret.group(1)
        app_name = ret.group(2)
    else:
        print('控制台输入错误')
        return

    with open('web_server.conf', 'r') as f:
        conf_info = json.load(f)
    sys.path.append(conf_info['dynamic_path'])
    frame = __import__(frame_name)    #相当于import 但是import不能使用变量，这个frame_name那么可以是变量,如果使用import相当于导入frame_name模块
    app = getattr(frame, app_name)   #获取这个模块中的某一个方法
    wsgi_server = WSGIServer(port, app, conf_info)
    wsgi_server.run_forever()

if __name__ == '__main__':
    main()