import requests
import os
from dotenv import load_dotenv
import re
import base64
import cv2
import numpy as np
import encrypt_tools

load_dotenv()

import send_msg
import time

class Feige(object):
    def __init__(self):
        self.requests_ = requests.Session()
        self.https_proxy = f"http://{os.getenv('PROXY_USER')}:{os.getenv('PROXY_PASS')}@{os.getenv('PROXY_HOST')}:{os.getenv('PROXY_PORT')}"
        self.requests_.proxies = {'http': self.https_proxy, 'https': self.https_proxy}
        self.url = os.getenv('FEIGE_WEBSITE')
        self.requests_.get(self.url)
        self.notice = send_msg.send_dingding

    def get_yzm(self):
        json_data = {
            "captchaType": "blockPuzzle",
            "clientUid": "slider-477ad1f5-c470-45e8-ba3a-f997bef1b55c",
            "ts": str(int(time.time() * 1000))
        }
        res_captcha = self.requests_.post(f"{self.url}/captcha/get", json=json_data)
        res_json = res_captcha.json()
        jigsaw_base64 = original_base64 = secret_key = token = ''
        if res_json["success"]:
            rep_data = res_json["repData"]
            token = rep_data["token"]
            secret_key = rep_data["secretKey"]
            jigsaw_base64 = rep_data["jigsawImageBase64"]  # 滑块图片
            original_base64 = rep_data["originalImageBase64"]  # 背景图片
            with open('test.png', 'wb') as f:
                f.write(base64.b64decode(original_base64))
        move_left_distance = self.get_captcha_distance(original_base64, jigsaw_base64)
        distance_msg = '{"x":%s,"y":5}' % move_left_distance
        point_json = self.aes_encrypt(distance_msg, secret_key)
        json_check_captcha = {
            "captchaType": "blockPuzzle",
            "clientUid": "slider-477ad1f5-c470-45e8-ba3a-f997bef1b55c",
            "ts": str(int(time.time() * 1000)),
            "pointJson": point_json,
            "token": token,
        }
        res_check_captcha = self.requests_.post(f"{self.url}/captcha/check", json=json_check_captcha)
        if res_check_captcha.json()["success"]:
            captcha_ver = self.aes_encrypt(token + "---" + distance_msg, secret_key)
            return captcha_ver

    def get_captcha_distance(self, original_base64, jigsaw_base64):
        """调用opencv识别滑块验证码"""
        # cv读取返回的图片数据
        image_cut = self.base64_to_image(jigsaw_base64)
        image_bg = self.base64_to_image(original_base64)
        # 寻找最佳匹配
        res = cv2.matchTemplate(self._tran_canny(image_cut), self._tran_canny(image_bg), cv2.TM_CCOEFF_NORMED)
        # 最小值，最大值，并得到最小值, 最大值的索引
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = max_loc[0]  # 横坐标
        return top_left

    def base64_to_image(self, base64_code):
        # base64解码
        img_data = base64.b64decode(base64_code)
        # 转换为np数组
        img_array = np.frombuffer(img_data, np.uint8)
        # 转换成opencv可用格式
        img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
        return img

    def _tran_canny(self, image):
        """消除噪声"""
        image = cv2.GaussianBlur(image, (3, 3), 0)
        return cv2.Canny(image, 50, 150)

    def aes_encrypt(self, word, key):
        """AES加密"""
        aes_cipher = encrypt_tools.AESCipher(key)
        encrypted = aes_cipher.encrypt(word)
        return encrypted

    def login_(self):
        try:
            post_data = {
                "email": os.environ.get('FEIGE_USER'),
                "password": os.environ.get('FEIGE_NUMBER'),
                "rememberMe": "1",
            }
            rep = self.requests_.post(f'{self.url}/login', data=post_data)
            if rep.status_code != 200:
                self.notice('飞鸽内网穿透登录失败,检查代理是否正常使用,登录返回状态码：' + str(rep.status_code))
            print('飞鸽登录返回信息' + str(rep.text))
        except Exception as e:
            print(e)
            self.notice('飞鸽内网穿透登录失败,检查代理是否正常使用,错误信息：' + str(e))


    def sign_(self):
        self.login_()
        rt = 0
        while True:
            try:
                json_data = {"captchaVerification": self.get_yzm()}
                headers = {
                    'content-type': 'application/json;charset=UTF-8',
                }
                res_sign = self.requests_.post(f"{self.url}/signIn", json=json_data,
                                               headers=headers)
                tunnel_info = self.requests_.get(f"{self.url}/queryTunnels?showAll=false&search=&sort=&order=&limit=10&page=1&offset=0",headers=headers)
                endDate = tunnel_info.json()['rows'][0]['endDate']
                print('飞鸽内网穿透签到返回信息'+ str(res_sign.json()))
                if res_sign.json()['success']:
                    check_in = res_sign.json()["days"]
                    credits = res_sign.json()["points"]
                    msg = '飞鸽内网穿透签到返回信息\n\n' \
                          '今日签到成功' + '\n' \
                          '连续签到天数:' + str(check_in) + '\n' \
                          '积分:' + str(credits) + '\n' \
                          '隧道到期:' + str(endDate[:10]) + '\n' \
                          '重试次数:' + str(rt) + '\n\n' \
                          '时间:' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
                    self.notice(msg)
                    break
                else:
                    dashboard = self.requests_.get(f'{self.url}/dashboard.html')
                    if '今日已签到' in dashboard.text:
                        credits = re.findall(r'<span id="credits">(.*?)</span>',dashboard.text)[0]
                        check_in = re.findall(r'<span id="check-in">(.*?)</span>',dashboard.text)[0]
                        msg = '飞鸽内网穿透签到返回信息\n\n' \
                              '今日已签到' + '\n' \
                              '连续签到天数:'+str(check_in) + '\n'\
                              '积分:' + str(credits) + '\n' \
                              '隧道到期:' + str(endDate[:10]) + '\n' \
                              '重试次数:' + str(rt) + '\n\n'\
                              '时间:' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
                        self.notice(msg)
                        break
                    else:
                        rt += 1
                        print(f'飞鸽内网穿透签到失败:{str(res_sign.json())},重试次数:{str(rt)}')
                        time.sleep(5)
                        continue

            except Exception as e:
                rt += 1
                print(f'飞鸽内网穿透任务执行异常:{str(e)}')
                time.sleep(5)
                continue
if __name__ == '__main__':
    Feige().sign_()