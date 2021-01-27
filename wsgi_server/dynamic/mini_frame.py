# @Time    : 2021/1/27
# @Author  : sunyingqiang
# @Email   : 344670075@qq.com
import re

URL_DICT = dict()

def route(url):
    def set_func(func):
        URL_DICT[url] = func
        def wapper(*arg, **kwargs):
            return func(*arg, **kwargs)
        return wapper
    return set_func

@route('/index.html')
def index():
    return '这是主页'

@route('/login.html')
def login():
    with open('./templates/qunee_test.html') as f:
        conetent = f.read()
    return conetent

@route(r'/add/\d+\.html')
def add():
    return 'add ok .....'

def application(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/html; charset=UTF-8')])
    file_name = env['PATH_INFO']
    try:
        for url, func in URL_DICT.items():
            ret = re.match(url, file_name)
            if ret:
                return func()
        # func = URL_DICT[file_name]
        # return func()
    except:
        return '404 NOT FOUND'