#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json

# api路径
url="http://0.0.0.0:6666/Search-Post"
#url="http://106.12.83.14:6666/Search-Post"

# 传入参数
parms = {
    'query':'经济',
#    'location':'海淀',
#    'rental_min':'0',
#    'rental_max':'5000',
#    'gender':'限女生',
#    'sort':'rental desc'
    'location':'',
    'rental_min':'',
    'rental_max':'',
    'gender':'',
    'sort':''
}

headers = {
    'User-agent': 'none/ofyourbusiness',
    'password': 'Eggs'
}

res = requests.post(url, data=parms,headers=headers)  # 发送请求

text = res.text
print(json.loads(text))
