# -*- coding: UTF-8 -*-
import requests

def run():
    # 添加头部，数据字典类型
    headers = {
        "Host": "www.meizitu.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.5383.400 QQBrowser/10.0.1313.400"
    }
    response = requests.get("http://www.meizitu.com/a/pure_1.html", headers=headers)
    print(response.text)

if __name__ == '__main__':
    run()