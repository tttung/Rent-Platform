#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json

# api路径
#url="http://0.0.0.0:6666/Search-Post"
url="http://106.12.83.14:6666/Search-Post"

# 传入参数
parms = {
    'query': '经济',  # 发送给服务器的内容
#    'address':'一号线 苹果园'，
#    'rental':'2000',
#    'filter':'限女生',
#    'sort':'rental'
}

headers = {
    'User-agent': 'none/ofyourbusiness',
    'password': 'Eggs'
}

res = requests.post(url, data=parms,headers=headers)  # 发送请求

text = res.text
print(json.loads(text))
