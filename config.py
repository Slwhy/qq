#/usr/bin/python 
# encoding:utf-8
# __Author__ = Slwhy


class User:

    qzone = ''
    cookies = ''
    username = ''  # qq 号
    password = ''  # qq 密码
    g_tk = ''

    headers = {
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-length': '0',
        'content-type': 'text/plain',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
    }  # 之前的错误是因为替换的时候，将 user 替换为了ower

