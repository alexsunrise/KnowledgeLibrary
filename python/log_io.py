#!/usr/bin/env python
#-*- coding: utf-8 -*-

import threading
import re
import time


class LogReader():
    def __init__(self, path):
        self.condition = threading.Condition()
        self.log_container = LogContainer(self.condition)
        self.log_productor = LogProductor(path,self.log_container)
        self.log_productor.start()
        #time.sleep(1)
        self.lines = []
        self.line_no = 0
        self.line = None

    def read_lines(self):
        self.lines += self.log_container.pop()

    def read_line(self):
        try:
            self.line = self.lines.pop(0)
            self.line_no += 1
        except Exception, ex:
            #print "exception: ", ex
            if len(self.lines) == 0:
                self.read_lines()
            self.line = self.lines.pop(0)
            self.line_no += 1
        finally:
            if self.line == None:
                self.line_no = -1
            return (self.line_no, self.line)

    def skip(self,match_str = '', num = 0):
        if match_str == '' and num != 0:
            for i in range(num):
                if self.line == None:
                    return False
                self.read_line()
            return True
        if match_str != '' and num == 0:
            while True:
                self.read_line()
                if self.line == None:
                    return False
                if None!=re.search(match_str, self.line):
                    return True
        if match_str != '' and num != 0:
            for i in range(num):
                self.read_line()
                if self.line == None:
                    return False
                if None!=re.search(match_str, self.line):
                    return True
            return False
        if match_str == '' and num == 0:
            self.read_line()
            if self.line == None:
                return False
            return True

#都日志文件类，用一个线程来负责读日志
#并将都到的文件块放入container中。
class LogProductor(threading.Thread):
    def __init__(self, path, container, group=None, target=None, name=None, args=(), kwargs={}):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self.path = path
        self.container = container
        self.buf = int(10e6)

    def run(self):
        logfile = open(self.path)
        try:
            while True:
                lines = logfile.readlines(self.buf)
                if not lines:
                    self.container.is_finished = True
                    self.container.push([None])
                    break
                self.container.push(lines)
        finally:
            logfile.close()

#文件存储类，将大文件按照块存储，
#此为生产者消费者模型，存放文件块
class LogContainer(object):
    def __init__(self, condition, size=10):
        self.size = size
        self.container = []
        self.condition = condition
        self.is_finished = False

    def isEmpty(self):
        self.condition.acquire()
        size = len(self.container)
        self.condition.release()
        return size <= 0

    def isFull(self):
        self.condition.acquire()
        size = len(self.container)
        self.condition.release()
        return size >= self.size

    def push(self, buf):
        self.condition.acquire()
        while self.isFull():
            self.condition.wait()
        self.container.append(list(buf))
        self.condition.notifyAll()
        self.condition.release()

    def pop(self):
        self.condition.acquire()
        while self.isEmpty():
            if self.is_finished == True:
                self.push([None])
                break
            self.condition.wait()
        buf = self.container.pop(0)
        self.condition.notifyAll()
        self.condition.release()
        return buf
