#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json

# api路径
#url="http://0.0.0.0:3333/Rec-nearbyRoom"
url="http://106.12.83.14:3333/Rec-nearbyRoom"

# 传入参数
parms = {
    'user_id': '8936831'  # 发送给服务器的内容
}

headers = {
    'User-agent': 'none/ofyourbusiness',
    'password': 'Eggs'
}

res = requests.post(url, data=parms,headers=headers)  # 发送请求

text = res.text
print(json.loads(text))

