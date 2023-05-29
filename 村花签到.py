import random
import requests
import os
import hashlib
import base64
from dotenv import load_dotenv
import re

load_dotenv()
import send_msg
import time


class SignCunHua(object):
    def __init__(self):
        self._url = os.getenv('CUNHUA_WEBSITE')
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br', 'accept-language': 'zh-CN,zh;q=0.9',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.50'}
        self.requests_ = requests.session()
        self.notice = send_msg.send_dingding

    def login_with_cookie(self):
        cookie = os.getenv('Cookie_CUNHUA')
        self.headers.update({'Cookie': cookie})
        resp = self.requests_.get(self._url, headers = self.headers)
        if 'qazedc1W' in resp.text:
            print('cookie缓存登录成功')
            self.sign_today()
        else:
            print('cookie缓存登录失败')

    def sign_today(self):
        try:
            status = '签到失败'
            resp_ = self.requests_.get(self._url, headers = self.headers)
            if '今日已签' in resp_.text:
                status = '今日已签到'
            else:
                formhash = re.findall(r'name="formhash" value="(\S{8})"', resp_.text)[0]
                resp = self.requests_.get(
                    f'{self._url}/k_misign-sign.html?operation=qiandao&format=global_usernav_extra&formhash={formhash}&inajax=1&ajaxtarget=k_misign_topb',
                    headers = self.headers)
                if '今日已签' in resp.text:
                    status = '今日已签到'
            resp_ = self.requests_.get(f'{self._url}/home.php?mod=spacecp&ac=credit&showcredit=1',
                                       headers = self.headers)
            coin = re.findall(r'<li><em> 金币: </em>(\d+) 个</li>', str(resp_.text))[0]
            massage = f'C论坛签到状态: {status}\n\n' \
                      f'当前积分: {coin} \n\n' \
                      f'时间{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))}'
            print(massage)
            self.notice(massage)

        except Exception as e:
            self.notice('签到出错了' + str(e))


if __name__ == '__main__':
    SignCunHua().login_with_cookie()