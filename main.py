#/usr/bin/python
# encoding:utf-8
# __Author__ = Slwhy

from selenium import webdriver
from config import User
from lxml import etree
import re
import time
import requests
import demjson

key_list = []

class Give_like:
    def __init__(self):
        self.username = User.username
        self.password = User.password

    def login(self):
        url = 'https://i.qq.com/'
        browser = webdriver.Chrome("/code/python/chorme/chromedriver")
        browser.get(url)
        browser.switch_to_frame('login_frame')
        browser.find_element_by_id('switcher_plogin').click()
        time.sleep(3)
        browser.find_element_by_id('u').send_keys(self.username)
        browser.find_element_by_id('p').send_keys(self.password)
        browser.find_element_by_id('login_button').click()
        time.sleep(5)
        browser.get(url + '{}'.format(self.username))
        # cookie 这有些坑，每个分号后面还得跟一个空格，最后面那个分号后面不带空格
        cookies = browser.get_cookies()
        cookie = ''
        for eleme in cookies:
            cookie += eleme['name'] + '=' + eleme['value'] + '; '
        cookie = cookie[:-1]
        User.cookies = cookie
        User.headers['cookie'] = cookie
        # 获取qzonetoken,但 qzonetoken 会发生变化
        html = browser.page_source
        html = etree.HTML(html)
        js_qzone_func = html.xpath('/html/body/script[7]/text()')
        js_qzone = js_qzone_func[0]
        js_qzone = re.search(u'qzonetoken.+?}',js_qzone).group(0)
        js_qzone = re.search(u'".+?"',js_qzone).group(0)
        qzone = js_qzone.split('\"')[1]
        User.qzone = qzone

    def get_g_tk(self):
        p_skey = User.cookies[User.cookies.find('p_skey=') + 7: User.cookies.find(';', User.cookies.find('p_skey='))]
        h = 5381
        for i in p_skey:
            h += (h << 5) + ord(i)
        print('g_tk', h & 2147483647)
        User.g_tk = h & 2147483647

    def get_dynamics(self):
        url = 'https://user.qzone.qq.com/proxy/domain/ic2.qzone.qq.com/cgi-bin/feeds/feeds3_html_more?uin=[uin]&scope=0&view=1&daylist=&uinlist=&gid=&flag=1&filter=all&applist=all&refresh=0&aisortEndTime=0&aisortOffset=0&getAisort=0&aisortBeginTime=0&pagenum=1&externparam=&firstGetGroup=0&icServerTime=0&mixnocache=0&scene=0&begintime=0&count=10&dayspac=0&sidomain=qzonestyle.gtimg.cn&useutf8=1&outputhtmlfeed=1&getob=1&g_tk=[g_tk]&qzonetoken=[qzonetoken]&g_tk=[g_tk]'
        url = url.replace('[qzonetoken]',User.qzone)
        url = url.replace('[g_tk]',str(User.g_tk))
        url = url.replace('[uin]',User.username)
        r = requests.get(url,headers = User.headers)
        content = r.text
        data = re.search('data.*]',content).group(0)
        data = data.split('data:')[1]
        # 将非标准的 json 数据解析为Python的数据类型
        data = demjson.decode(data)
        return data

    def parser_data(self,data):
        for dynamic in data:
            dynamic_dict = {}
            try:
                dynamic_dict['key'] = dynamic['key']
                dynamic_dict['appid'] = dynamic['appid']
                dynamic_dict['typeid'] = dynamic['typeid']
                dynamic_dict['uin'] = dynamic['uin']
                if dynamic['key'] not in key_list:
                    self.give_like(dynamic_dict)
                    key_list.append(dynamic['key'])
            except:
                print('未找到说说中的 key appid 等值')


    def give_like(self,dynamic_dict):
        # 很多参数都是在说说中的，直接提取出来就可以了
        # 构造点赞 url
        url = 'https://user.qzone.qq.com/proxy/domain/w.qzone.qq.com/cgi-bin/likes/internal_dolike_app?g_tk=[g_tk]&qzonetoken=[qzonetoken]'
        url = url.replace('[qzonetoken]',str(User.qzone))
        url = url.replace('[g_tk]',str(User.g_tk))
        # 构造点赞的参数
        unikey = 'http://user.qzone.qq.com/[qq]/mood/[fid]'
        unikey = unikey.replace('[qq]',str(dynamic_dict['uin']))
        unikey = unikey.replace('[fid]',str(dynamic_dict['key']))
        data = {
            'qzreferrer': 'https://user.qzone.qq.com/'+str(User.username),
            'opuin': str(User.username),
            'unikey': unikey,
            'curkey': unikey,
            'from': ' 1',
            'appid': str(dynamic_dict['appid']),
            'typeid': str(dynamic_dict['typeid']),
            'abstime': str(int(time.time())),
            'fid': str(dynamic_dict['key']),
            'active': 0,
            'fupdate': 1
        }
        r = requests.post(url,data=data,headers = User.headers)


def init():
    User.username = input("请输入自己的 qq 号：")
    User.password = input("请输入 qq 登录密码：")
    print('正在进行登录......')
    give = Give_like()
    give.login()
    give.get_g_tk()
    return give

def relogin(give): # 重新登录获取新的 cookie 等信息
    give.login()
    give.get_g_tk()

def continues_give_like(give):
    print('已经登录成功，将持续为您的空间进行点赞直到您退出程序为止')
    count = 0
    while(True):
        if count >= 1000:
            count = 0
            relogin(give)
        data = give.get_dynamics()
        give.parser_data(data)
        time.sleep(100)
        count = count + 1

if __name__ == '__main__':
    give = init()
    continues_give_like(give)


