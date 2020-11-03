#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from sqlWorkflow import Workflow
sys.path.append("..")       #导入平级目录模块
from OffLine.semanticSearch import search
from flask import Flask, g
from flask_restful import reqparse, Api, Resource

# Flask相关变量声明
app = Flask(__name__)
api = Api(app)

# RESTfulAPI的参数解析 -- put / post参数解析
parser_put = reqparse.RequestParser()
parser_put.add_argument("query", type=str, required=True, help="need user data")
parser_put.add_argument("location", type=str, required=True, help="need user data")
parser_put.add_argument("rental_min", type=str, required=True, help="need user data")
parser_put.add_argument("rental_max", type=str, required=True, help="need user data")
parser_put.add_argument("gender", type=str, required=True, help="need user data")
parser_put.add_argument("sort", type=str, required=True, help="need user data")
#parser_put.add_argument("pwd", type=str, required=True, help="need pwd data")

# 功能方法
def Search_Post(query, location, rental_min, rental_max, gender, sort):
    result = []
    workflow = Workflow()
    postId = workflow.sqlFilter_postId(location, rental_min, rental_max, gender, sort)   #获取post id
    if not postId:
        return "数据为空！"
    
    sear = search()
    sear.get_postRecall(postId)         #召回向量
    temp = sear.post_FlatL2(query)      #query排序TopK

    for post_id, ctr in temp:
        middle = workflow.sqlSearch_post(post_id)
        middle.setdefault('ctr', round(ctr,4))
        result.append(middle)
    return result

# 操作（post / get）资源列表
class TodoList(Resource):
    
    def post(self):
        args = parser_put.parse_args()

        # 构建新参数
        query = args['query']
        location = args['location']
        rental_min = args['rental_min']
        rental_max = args['rental_max']
        gender = args['gender']
        sort = args['sort']
#        pwd = args['pwd']

        print('input query:%s' % query)
        # 调用方法semantic_search
        info = Search_Post(query, location, rental_min, rental_max, gender, sort)
    
        # 资源添加成功，返回201
        return info, 201

# 设置路由，即路由地址为http://106.12.83.14:6666/Search-Post
api.add_resource(TodoList, "/Search-Post")

if __name__ == "__main__":
    app.run(host='0.0.0.0',#任何ip都可以访问
            port=6666,#端口
            debug=True)
