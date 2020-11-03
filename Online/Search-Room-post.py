#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json

# api路径
url="http://0.0.0.0:7777/Search-Room"
#url="http://106.12.83.14:7777/Search-Room"

# 传入参数
parms = {
    'query':'经济',
    'location':'金鱼',
    'rental_min':'0',
    'rental_max':'5000',
    'direction':'朝南',
    'sort':'rental asc'
#    'location':'',
#    'rental_min':'',
#    'rental_max':'',
#    'direction':'',
#    'sort':''
}

headers = {
    'User-agent': 'none/ofyourbusiness',
    'password': 'Eggs'
}

res = requests.post(url, data=parms,headers=headers)  # 发送请求

text = res.text
print(json.loads(text))

