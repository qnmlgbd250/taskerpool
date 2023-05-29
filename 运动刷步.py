# -*- coding: utf-8 -*-
import random
import requests
import os

from dotenv import load_dotenv
import base64
import hashlib
load_dotenv()
import send_msg
import time
import datetime





class YunDong(object):
    def __init__(self):
        self.headers = {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'referer': os.getenv('WEBREFER'),
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.44'
        }
        self.url = os.getenv('YUNDONG_WEBSITE')
        self.notice = send_msg.send_dingding

    def init_dict(self):
        phone_list_str = os.environ.get('PHONE_NUMBER')
        password_list_str = os.environ.get('PASSWORD')
        phone_list = phone_list_str.split(',')
        password_list = password_list_str.split(',')
        ppdict = dict(zip(phone_list, password_list))
        return ppdict

    def make_step(self,):
        steps = 0
        if self.isDuringThatTime("18:00", "19:00"):
            steps = random.randint(7001, 9999)
        elif self.isDuringThatTime("22:30", "22:50"):
            steps = random.randint(17987, 22000)
        if steps == 0:
            print('不执行当前时间段任务')
            pass
        else:
            for _ in range(3):
                try:
                    ppdict = self.init_dict()
                    massage = ''
                    for phone, password in ppdict.items():
                        for i in range(4):
                            tim1 = str(int(time.time()))
                            step1 = str(int(steps) + random.randint(1, 200))
                            data1 = self.get_md5data(phone=phone, password=password, tim=tim1, step=step1)
                            rep = requests.post(self.url, headers=self.headers, data=data1).json()
                            print(f"返回信息>> {rep['msg']} ")
                            if rep['msg'] == "同步成功":
                                massage += f'用户{phone}修改步数{step1}成功,重试次数{i}.\n时间{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))} \n\n'
                                break
                            else:
                                print(f'第{i + 1}次修改步数失败,重试')
                                continue
                    print(massage)
                    self.notice(massage)
                    break
                except Exception as e:
                    print(e)
                    continue

    def get_md5data(self, step, tim, phone, password):
        data_str = f'{phone}1{password}2{step}xjdsb{tim}'
        bt = base64.b64encode(data_str.encode('utf-8')).decode("utf-8")
        md5_val = hashlib.md5(bt.encode('utf8')).hexdigest()
        data = f'time={tim}&phone={phone}&password={password}&step={step}&key={md5_val}'
        return data

    def isDuringThatTime(self,startTime, endTime):
        start_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + startTime, '%Y-%m-%d%H:%M')
        end_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + endTime, '%Y-%m-%d%H:%M')
        now_time = datetime.datetime.now()
        if start_time < now_time < end_time:
            return True
        return False


if __name__ == '__main__':
    YunDong().make_step()
