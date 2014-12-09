#!/usr/bin/env python
#-*- encoding=utf-8 -*-
import sqlite3

class DBTools:
    def __init__(self):
        self.con = None
        self.cur = None
        #self.create_db(dbname)

    #创建数据库
    def create_db(self, dbname):
        try:
            self.con = sqlite3.connect(dbname)
            self.cur = self.con.cursor()
        except:
            print "database %s create failed!" %dbname
            self.close_db()
    
    #打开数据库
    def open_db(self, dbname):
        try:
            self.con = sqlite3.connect(dbname)
            self.cur = self.con.cursor()
        except:
            print "database %s open failed!" %dbname
            self.close_db()
    
    #创建表或更新一条数据
    def update_table(self, sql):
        try:
            self.cur.execute(sql)
            #self.con.commit()
        except:
            print "update table failed!"
            self.close_db()
    
    #创建多条数据
    def update_table_many(self, sql, row_list):
        try:
            self.cur.executemany(sql, row_list)
        except Exception,ex:
            print ex
            print "update table many failed!"
            self.close_db()

    #查询数据表
    def query_table(self, sql):
        self.cur.execute(sql)
        return self.cur.fetchall()

    #关闭数据库
    def close_db(self):
        self.con.commit()
        self.cur.close()
        self.con.close()
