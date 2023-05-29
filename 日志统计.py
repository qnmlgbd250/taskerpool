# -*- coding: utf-8 -*-
import re
import datetime
import send_msg


notice = send_msg.send_dingding

def parse_log_file(file_path, start_time, end_time):
    # 正则表达式，匹配日志中的时间戳
    timestamp_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
    # 正则表达式，匹配类似 '2023-05-03 11:55:56 | 127.0.0.1 | {'text': '为什么取名', 'id': 'chatcmpl-7Bxl57h1cvFuC25VhC05mW3ggfHa4'}' 的内容
    content_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) \| \{\'text\': \'.*?\', \'id\': \'.*?\'\}"

    counter = 1  # 计数器
    output = ""  # 输出的字符串

    with open(file_path, 'r') as file:
        for line in file:
            match = re.search(content_pattern, line)
            if match:
                timestamp = datetime.datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
                if start_time <= timestamp <= end_time:
                    # 提取 'text' 的内容和 IP 地址
                    ip = match.group(2)
                    content = re.search(r"\'text\': \'(.*?)\'", match.group(0)).group(1)
                    output += f"{counter}. 请求IP: {ip} 内容: {content}\n"
                    counter += 1  # 计数器加一

    # 打印拼接后的字符串
    print(output)
    notice(output)

# 获取当前日期和时间
now = datetime.datetime.now()
# 设置开始时间为当前日期的 00:00:00
start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
# 设置结束时间为第二天的 00:00:00
end_time = start_time + datetime.timedelta(days=1)

parse_log_file('app.log', start_time, end_time)  # 替换为你的日志文件路径






