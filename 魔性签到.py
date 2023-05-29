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


class MoXing(object):
    def __init__(self):
        self._url = os.getenv('MOXING_WEBSITE')
        self.headers = {
            'referer': f'{self._url }/home.php',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.50'}
        self.requests_ = requests.session()
        self.https_proxy = f"http://{os.getenv('PROXY_USER')}:{os.getenv('PROXY_PASS')}@{os.getenv('PROXY_HOST')}:{os.getenv('PROXY_PORT')}"
        self.requests_.proxies = {'http': self.https_proxy, 'https': self.https_proxy}
        self.notice = send_msg.send_dingding

    def login_with_cookie(self):
        cookie = 'dyHK_4efa_saltkey=ex6s1p6T; dyHK_4efa_lastvisit=1667098715; _ga=GA1.2.1448995118.1667099014; _gid=GA1.2.1160741905.1667099014; dyHK_4efa_ulastactivity=a30cxqoSE8WFLeTCBBIay7Og2R7tVzgdhuFvDmeiSQF9NGB2GmPU; dyHK_4efa_auth=b0d24L0T%2F%2FBG1phEr%2FhtgGXXlJBkly02WPOiAYyaYD5qeVX6Ia8sCspJhqHOq1bMEoYV0%2Bo4dKbhSAGw53N%2BGlknSdk; dyHK_4efa_lastcheckfeed=142325%7C1667102415; dyHK_4efa_nofavfid=1; dyHK_4efa_atarget=1; dyHK_4efa_smile=1D1; dyHK_4efa_sid=lm900i; dyHK_4efa_home_diymode=1; dyHK_4efa_st_p=142325%7C1667118624%7C6325cea16b7d365071cbb5077e7f3ff5; dyHK_4efa_viewid=tid_371343; dyHK_4efa_visitedfid=61D46D220; dyHK_4efa_st_t=142325%7C1667118744%7C7db0bec8c8cd3271357d4c1aac8ca8d5; dyHK_4efa_forum_lastvisit=D_220_1667102607D_46_1667118665D_61_1667118744; dyHK_4efa_lastact=1667118771%09home.php%09spacecp'
        self.headers.update({'cookie': cookie})
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
                    f'{self._url}/plugin.php?id=k_misign:sign&operation=qiandao&format=global_usernav_extra&formhash={formhash}&inajax=1&ajaxtarget=k_misign_topb',
                    headers = self.headers)
                if '今日已签' in resp.text:
                    status = '今日已签到'
            resp_ = self.requests_.get(f'{self._url}/home.php?mod=spacecp&ac=credit&showcredit=1',
                                       headers = self.headers)
            coin = re.findall(r'<li><em> 软妹币: </em>(\d+) </li>', str(resp_.text))[0]
            massage = f'M论坛签到状态: {status}\n\n' \
                      f'当前积分: {coin} \n\n' \
                      f'时间{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))}'
            print(massage)
            self.notice(massage)

        except Exception as e:
            self.notice('签到出错了' + str(e))


if __name__ == '__main__':
    MoXing().login_with_cookie()