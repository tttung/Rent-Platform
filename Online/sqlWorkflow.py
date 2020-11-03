#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import json
import pymysql
import _pickle as cPickle
from urllib import parse
from urllib import request
from datetime import datetime
from urllib.request import urlopen
#from userProfile import userProfile  #内存消耗560M

class Workflow(object):
    def __init__(self):
        self.root = '/Users/tung/Documents/Git/Rent-Platform/OnLine/'
        self.conn = pymysql.connect(host = '106.12.83.14', user = 'ping', passwd = 'mima123456', port=3306,
                                    charset='utf8', autocommit=True) #打开数据库连接，utf-8编码，否则中文有可能会出现乱码。
        self.cursor = self.conn.cursor()                             #创建一个游标,用来给数据库发送sql语句
    
    '每天更新新闻到数据库'
    def updateNewsDatabase(self):
        #获取新闻，添加入数据库13类*40个 = 520条新闻
        channel = ['头条','财经','体育','娱乐','军事','教育','科技','NBA','股票','星座','女性','健康','育儿']
        data = {}
        data["appkey"] = "1358c9524b37b9ba"
        data["channel"] = "头条"  #新闻频道(头条,财经,体育,娱乐,军事,教育,科技,NBA,股票,星座,女性,健康,育儿)
        data["start"] = "0"
        data["num"] = "40"
        url_values = parse.urlencode(data)
        url = "https://api.jisuapi.com/news/get" + "?" + url_values
        print(url)
        
        request_list = request.Request(url)
        result = urlopen(request_list)
        jsonarr = json.loads(result.read())

        if jsonarr["status"] != u"0":
            print( jsonarr["msg"])
        #     exit()
        result = jsonarr["result"]
        print(result["channel"],result["num"])

        self.conn.ping(reconnect=True)
        self.conn.select_db('test1')
        #数据库内增加新数据
        for val in result["list"]:
            sql= "insert into news(title,time,src,cat,pic,content,url,weburl) values (%s, %s, %s, %s, %s, %s, %s, %s)" #插入数据库
            #     content = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+".encode('utf-8').decode('utf-8'), "".encode('utf-8').decode('utf-8'), val["content"])
            #     content = re.sub("[A-Za-z0-9\!\%\[\]\,\。]", "", content)
            self.cursor.execute(sql,(val["title"],val["time"],val["src"],val["category"],val["pic"], val["content"], val["url"],val["weburl"]))
            print("标题:{0}时间:{1}".format(val["title"],val["time"]))

        self.conn.close()#关闭数据库

    '获取推荐候选集'
    def getNewsCandidate(self):
        self.conn.ping(reconnect=True)
        self.conn.select_db('test1')
        
        #最新的520*3天=1560条新闻
        # sql="select * from news where 1=1 limit 650"  #前13*50条
        sql="select * from news order by id desc limit 0,1560" #后13*80条
        try:
            self.cursor.execute(sql)
            candidate = self.cursor.fetchall() #获取全部结果集。 fetchone 查询第一条数据，返回tuple类型。
            if not candidate: #判断是否为空。
                print("数据为空！")
            else:
                for row in candidate:
                    ID = row[0]
                    title = row[1]
                    time = row[2]
                    src = row[3]
                    cat = row[4]
                    pic = row[5]
                    content = row[6]
                    url = row[7]
                    weburl = row[8]
#                    print("id:{0}标题:{1}时间:{2}来源:{3}标签:{4}图片:{5}内容:{6}url:{7}weburl:{8}".format(ID,title,time,src,cat,pic,content,url,weburl))

        except Exception as e:
            self.conn.rollback()  #如果出错就会滚数据库并且输出错误信息
            print("Error:{0}".format(e))
        finally:
            self.conn.close()#关闭数据库

        print( '获取候选新闻的数据量为：', len(candidate))
        cPickle.dump( candidate, open(self.root + 'candidate.pkl', 'wb')) #tuple对象持久化

    '用户冷启动'
    def userColdStart(self, user_id):
        #生成用户静态画像
        user_profile_vec = userProfile.staticProfile(user_id)
        #在新闻向量中搜索
        return
    
    '新闻冷启动'
    def newsColdStart(self, news_id):
    #生成新闻向量
    #在用户静态画像中搜索
        return
    
    '从本地读入，准备召回'
    def recall(self):
        #[1]标题、[2]时间、[4]分类、[6]内容
        candidate = cPickle.load( open(self.root + 'candidate.pkl','rb') ) #读入数据
        print('候选新闻样本：', candidate[20])
    
    #########################################################################################
    '动态多条件location rental gender 过滤求租贴id，后sort'
    def sqlFilter_postId(self, location="", rental_min="", rental_max="", gender="", sort=""):
        self.conn.ping(reconnect=True)
        self.conn.select_db('rent')
        
        filter_post = 'select * from post where (location like "%%{0}%%" or "{0}"="") and (rental between "{1}" and "{2}"  or "{1}"="" or "{2}"="") and (gender_requirement ="{3}" or "{3}"="")'.format(location, rental_min, rental_max, gender)
        if sort != "":
            filter_post = filter_post + "order by %s" %(sort)

        postId = []
        res = {}
        try:
            self.cursor.execute(filter_post)
            row = self.cursor.fetchall() #fetchone 查询第一条数据，返回tuple类型
            if not row: #判断是否为空。
                print("数据为空！")
            else:
                for i in row:
#                    print(i)
                    postId.append(i[0])     #多个postId拼接
                res.setdefault('postId', postId)
        
        except Exception as e:
            self.conn.rollback()       #如果出错就会关数据库并且输出错误信息
            print("Error:{0}".format(e))
        finally:
            self.conn.close()          #关闭数据库
        return res

    '按id搜索房源(house_resource + picture + room_configuration)'
    def sqlSearch_room(self, search_id):
        self.conn.ping(reconnect=True)
        self.conn.select_db('rent')

        sql_house="select * from house_resource where id=" + str(search_id)  #按id查找

        res = {}
        try:
            self.cursor.execute(sql_house)
            row = self.cursor.fetchone() #fetchone 查询第一条数据，返回tuple类型
            if not row: #判断是否为空。
                print("数据为空！")
            else:
                res.setdefault('id', row[0])
                res.setdefault('lease_type', row[1])
                res.setdefault('area', row[2])
                res.setdefault('house_layout', row[3])
                res.setdefault('direction', row[4])
                res.setdefault('floor', row[5])
                res.setdefault('elevator', row[6])
                res.setdefault('detail_address', row[7])
                res.setdefault('metro', row[8])
                res.setdefault('rental', row[9])
                res.setdefault('usable_time', row[10])
                res.setdefault('user_id', row[11])
            
            picture_url = ""
            sql_picture="select * from picture where house_resource_id="+str(res['id']) #按house_id查找图片
            self.cursor.execute(sql_picture)
            row = self.cursor.fetchall() #fetchone 查询第一条数据，返回tuple类型
            if not row: #判断是否为空。
                print("数据为空！")
            else:
                for i in row:
                    picture_url += " "+i[1]     #多张图片的url拼接
                res.setdefault('picture_url', picture_url)

            sql_config="select * from room_configuration where house_id="+str(res['id']) #按house_id查找房间配置
            self.cursor.execute(sql_config)
            row = self.cursor.fetchone() #fetchone 查询第一条数据，返回tuple类型
            if not row: #判断是否为空。
                print("数据为空！")
            else:
                res.setdefault('television', row[2])
                res.setdefault('washing_machine', row[3])
                res.setdefault('refrigerator', row[4])
                res.setdefault('bed', row[5])
                res.setdefault('wi_fi', row[6])
                res.setdefault('air_conditioner', row[7])
                res.setdefault('soft', row[8])
                res.setdefault('calorifier', row[9])
                res.setdefault('heating', row[10])
                res.setdefault('gas', row[11])

        except Exception as e:
            self.conn.rollback()       #如果出错就会关数据库并且输出错误信息
            print("Error:{0}".format(e))
        finally:
            self.conn.close()          #关闭数据库
        return res
    
    '动态多条件location rental direction 过滤房源贴id，后sort'
    def sqlFilter_roomId(self, location="", rental_min="", rental_max="", direction="", sort=""):
        self.conn.ping(reconnect=True)
        self.conn.select_db('rent')
        
        filter_room = 'select * from house_resource where (detail_address like "%%{0}%%" or "{0}"="") and (rental between "{1}" and "{2}"  or "{1}"="" or "{2}"="") and (direction ="{3}" or "{3}"="")'.format(location, rental_min, rental_max, direction)
        if sort != "":
            filter_room = filter_room + "order by %s" %(sort)
    
        roomId = []
        res = {}
        try:
            self.cursor.execute(filter_room)
            row = self.cursor.fetchall() #fetchone 查询第一条数据，返回tuple类型
            if not row: #判断是否为空。
                print("数据为空！")
            else:
                for i in row:
#                    print(i)
                    roomId.append(i[0])     #多个postId拼接
                res.setdefault('roomId', roomId)

        except Exception as e:
            self.conn.rollback()       #如果出错就会关数据库并且输出错误信息
            print("Error:{0}".format(e))
        finally:
            self.conn.close()          #关闭数据库
        return res

    '按id搜索求租贴(post + picture)'
    def sqlSearch_post(self, search_id):
        self.conn.ping(reconnect=True)
        #选择需要的数据库
        self.conn.select_db('rent')
        # 对于数据库实现增删改查操作
        sql_post="select * from post where id =" + str(search_id)  #按id查找
        
        res = {}
        try:
            self.cursor.execute(sql_post)
            row = self.cursor.fetchone() #fetchone 查询第一条数据，返回tuple类型
            if not row: #判断是否为空。
                print("数据为空！")
            else:
                res.setdefault('id', row[0])
                res.setdefault('t_user_id', row[1])
                res.setdefault('soliciting_type', row[2])
                res.setdefault('title', row[3])
                res.setdefault('update_time', str(row[4]))
                res.setdefault('rental', row[5])
                res.setdefault('gender_requirement', row[6])
                res.setdefault('location', row[7])
                res.setdefault('post_content', row[8])

            picture_url = ""
            sql_picture="select * from picture where post_id="+str(res['id']) #按post_id查找图片
            self.cursor.execute(sql_picture)
            row = self.cursor.fetchall() #fetchone 查询第一条数据，返回tuple类型
            if not row: #判断是否为空。
                    print("数据为空！")
            else:
                for i in row:
                    picture_url += " "+i[1]     #多张图片的url拼接
                res.setdefault('picture_url', picture_url)

        except Exception as e:
            self.conn.rollback()       #如果出错就会关数据库并且输出错误信息
            print("Error:{0}".format(e))
        finally:
            self.conn.close()          #关闭数据库
        return res

if __name__ == '__main__':
    start = datetime.now()

    test = Workflow()
#    test.updateNewsDatabase()
#    test.getNewsCandidate()
#    test.recall()
#    res = test.sqlSearch_room('100656815')
#    res = test.sqlSearch_post('100624617')
    res = test.sqlFilter_postId(location="海淀", rental_min="0",rental_max="5000", gender="限女生", sort="rental desc")
#    res = test.sqlFilter_roomId(location="金鱼", rental_min="0",rental_max="5000", direction="朝南", sort="rental asc")
#    res = test.sqlFilter_postId()
#    res = test.sqlFilter_roomId()

    print(res)
#    print(type(res['postId'][0]))    #postID 是int类型

    print("This took ", datetime.now() - start)
