#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import math
import faiss
import jieba
import logging
import numpy as np
import _pickle as cPickle
from datetime import datetime
from jieba import analyse
from gensim.models import word2vec

jieba.setLogLevel(logging.INFO)

class search(object):
    def __init__(self):
        self.dim = 128         # 向量维度
        self.k = 5             # 排序TopK
        self.root='/Users/tung/Documents/Git/Rent-Platform/OffLine/'
        
        '加载word2vec模型'
        self.word_model = word2vec.Word2Vec.load('/Users/tung/Documents/Git/Rent-Platform/wordEmbedding/sougouCS_wordVec')
        self.vocab = self.word_model.wv.vocab.keys()
 
        self.post_recall_id = []               # 召回求租贴id
        self.post_recall_vec = []              # 召回求租贴向量
        self.room_recall_id = []               # 召回房源帖id
        self.room_recall_vec = []              # 召回房源帖向量

    "得到任意text的vector"
    def get_vector(self, word_list):
        # 建立一个全是0的array
        res =np.zeros([128])
        count = 0
        for word in word_list:
            if word in self.vocab:
                res += self.word_model[word]
                count += 1
        return res/count if count >0 else res
        
    "动态条件召回的求租帖向量"
    def get_postRecall(self, postId):
        self.post_recall_id = postId['postId']
        word_news_feature = cPickle.load( open(self.root + 'persistence/multi_news_word.pkl','rb') )   # 全量新闻词嵌入
        temp = []
        for i in self.post_recall_id:
            temp.append(word_news_feature[str(i)])  #int转一下str
        self.post_recall_vec = np.array(temp).astype('float32')

    def post_FlatL2(self, query):
        # Query分词
        tags = analyse.extract_tags(query,3)
        
        queryVec = self.get_vector(tags)
        queryVec = queryVec.reshape(1,128).astype('float32')
        
        #相似度检索
        index = faiss.IndexFlatL2(self.dim)         # L2距离，欧式距离（越小越好）
        index.add(self.post_recall_vec)             # 添加训练时的样本
        D, I = index.search(queryVec, self.k)       # 寻找相似向量， I表示相似向量ID矩阵， D表示距离矩阵

        res = []
        for idx, i in enumerate(I[0]):
            post_id = self.post_recall_id[i]
            similarity = 1/math.log(1+D[0][idx])     #距离转相似度
            res.append((post_id, similarity))        #返回相似度
        return res

    "动态条件召回的房源帖向量"
    def get_roomRecall(self, roomId):
        self.room_recall_id = roomId['roomId']
        word_news_feature = cPickle.load( open(self.root + 'persistence/multi_news_word.pkl','rb') )   # 全量新闻词嵌入
        temp = []
        for i in self.room_recall_id:
            temp.append(word_news_feature[str(i)])  #int转一下str
            self.room_recall_vec = np.array(temp).astype('float32')
    
    def room_FlatL2(self, query):
        # Query分词
        tags = analyse.extract_tags(query,3)
        
        queryVec = self.get_vector(tags)
        queryVec = queryVec.reshape(1,128).astype('float32')
        
        #相似度检索
        index = faiss.IndexFlatL2(self.dim)         # L2距离，欧式距离（越小越好）
        index.add(self.room_recall_vec)             # 添加训练时的样本
        D, I = index.search(queryVec, self.k)       # 寻找相似向量， I表示相似向量ID矩阵， D表示距离矩阵
        
        res = []
        for idx, i in enumerate(I[0]):
            room_id = self.room_recall_id[i]
            similarity = 1/math.log(1+D[0][idx])     #距离转相似度
            res.append((room_id, similarity))        #返回相似度
        return res
    
    "其它检索方法"
    def IVFFlat(self, query):
        # Query分词
        tags = analyse.extract_tags(query,3)
        
        queryVec = self.get_vector(tags)
        queryVec = queryVec.reshape(1,128).astype('float32')
        
        #相似度检索
        nlist = 100       #聚类中心的个数
        quantizer = faiss.IndexFlatL2(self.dim)         # 定义量化器
        index = faiss.IndexIVFFlat(quantizer, self.dim, nlist, faiss.METRIC_L2)
        index.nprobe = 10                          #查找聚类中心的个数，默认为1个，若nprobe=nlist则等同于精确查找
        assert not index.is_trained
        index.train(self.word_news_feature_vec)    #需要训练
        assert index.is_trained
        index.add(self.word_news_feature_vec)      #添加训练时的样本
        D, I = index.search(queryVec, self.k)           #寻找相似向量， I表示相似用户ID矩阵， D表示距离矩阵
        
        res = []
        for idx, i in enumerate(I[0]):
            news_id = self.word_news_feature_id[i]
            #     res.append((news_id, newsSet[news_id]))    #返回title
            similarity = 1/math.log(1+D[0][idx])     #距离转相似度
            res.append((news_id, similarity))        #返回相似度
        
        return res
    
    def factory(self, query):
        # Query分词
        tags = analyse.extract_tags(query,3)
        
        queryVec = self.get_vector(tags)
        queryVec = queryVec.reshape(1,128).astype('float32')
        
        #相似度检索
        index = faiss.index_factory(self.dim, "PCAR32,IVF100,SQ8") #PCA降到32位；搜索空间100；SQ8,scalar标量化，每个向量编码为8bit(1字节)
        assert not index.is_trained
        index.train(self.word_news_feature_vec)    #需要训练
        assert index.is_trained
        index.add(self.word_news_feature_vec)      #添加训练时的样本
        D, I = index.search(queryVec, self.k)           #寻找相似向量， I表示相似用户ID矩阵， D表示距离矩阵
        
        res = []
        for idx, i in enumerate(I[0]):
            news_id = self.word_news_feature_id[i]
            #     res.append((news_id, newsSet[news_id]))    #返回title
            similarity = 1/math.log(1+D[0][idx])     #距离转相似度
            res.append((news_id, similarity))        #返回相似度
        
        return res

if __name__ == '__main__':
    start = datetime.now()
    test = search()
    
    postId = {'postId': [100624617, 100649885, 100654809, 100655161, 100656239, 100656369, 100656610, 100656815, 100657188, 100657261]}
    test.get_postRecall(postId)
#    query = '经济'
    query = sys.argv[1]

    result = test.post_FlatL2(query)
##    result = test.IVFFlat(query)
##    result = test.factory(query)
#
    print('input query:%s' % query)
    for news_id, ctr in result:
        print('id:%s, ctr:%s' % (news_id, ctr))
    print("This took ", datetime.now() - start)


