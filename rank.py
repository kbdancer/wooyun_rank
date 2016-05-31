#!/usr/bin/env python
# coding=utf-8
# code by 92ez.com

import threading
import subprocess
import requests
import sqlite3
import Queue
import sys
import re

reload(sys)
sys.setdefaultencoding('utf8')

#
def bThread(urllist):
    
    threadl = []
    queue = Queue.Queue()
    for aimlink in urllist:
        queue.put(aimlink)

    for x in xrange(0, 10):
        threadl.append(tThread(queue))
        
    for t in threadl:
        t.start()
    for t in threadl:
        t.join() 

#create thread
class tThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        
        while not self.queue.empty(): 
            aimlink = self.queue.get()
            try:
                getVulInfo(aimlink)
            except:
                continue

def getVulInfo(url):
    header = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"}
    try:
        req = requests.get(url = url,headers = header,timeout = 10)
        result = req.content.replace('\r\n','')

        title = re.findall(r"漏洞标题：(.+?)<",result)[0]
        title = ''.join(title.split())
        title = unicode(title)

        status = re.findall(r"漏洞状态：(.+?)<",result)[0]
        status = ''.join(status.split())
        status = unicode(status)

        if '忽略' in status:
            rank = '0'
        else:
            rank = re.findall(r"漏洞Rank：(.+?)<",result)[0]
            rank = ''.join(rank.split())

        vultype = re.findall(r"漏洞类型：(.+?)<",result)[0]
        vultype = ''.join(vultype.split())
        vultype = unicode(vultype)

        sumittime = re.findall(r"提交时间：(.+?)<",result)[0]
        sumittime = sumittime.replace('\t','')

        publishtime = re.findall(r"公开时间：(.+?)<",result)[0]
        publishtime = publishtime.replace('\t','')

        author = re.findall(r"漏洞作者：(.+?)</h3>",result)[0]
        author = re.findall(r'>(.+?)<',author)[0]
        author = ''.join(author.split()) 
        author = unicode(author)

        company = re.findall(r"相关厂商：(.+?)</h3>",result)[0]
        company = re.findall(r'>(.+?)<',company)[0]
        company = ''.join(company.split()) 
        company = unicode(company)

        try:
            cx = sqlite3.connect(sys.path[0]+"/wooyun.db")
            cu = cx.cursor()
            cu.execute("select * from record where url = '"+ url +"'")
            if not cu.fetchone():
                cu.execute("insert into record (title,url,company,status,author,vultype,rank,sumittime,publishtime) values (?,?,?,?,?,?,?,?,?)", (title,url,company,status,author,vultype,rank,sumittime,publishtime))
                cx.commit()
                print '[+] Insert '+url+' into database successly.'
            else:
                print '[-] Found '+url+' in database, skipped.'
            cu.close()
            cx.close()
        except Exception, e:
            print e
    except Exception,e:
        print e
        pass

def getPageCount(url):
    url = url+'1'
    header = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"}
    wooyunUrlList = []
    try:
        req = requests.get(url = url,headers = header,timeout = 5)
        htmlcode = req.content.replace('\r\n','')

        pageCount = int(re.findall(r'录, (.+?) 页',htmlcode)[0])
        return pageCount

    except Exception,e:
        sys.exit('[e] Error, exception is %s' % e)

def getUrllist(sp,pc,url):
    pageUrl = []
    wooyunUrlList = []

    for p in range(sp,pc+1):
        pageUrl.append(url+str(p))

    for g in pageUrl:
        url = g
        header = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"}
        try:
            req = requests.get(url = url,headers = header,timeout = 5)
            htmlcode = req.content.replace('\r\n','')

            trs = re.findall(r'<tr>(.+?)</tr>',htmlcode)

            for tr in trs:
                if '漏洞标题' not in tr:
                    tds = re.findall(r'<td>(.+?)</td>',tr)
                    thisUrl = "http://www.wooyun.org/bugs/"+re.findall(r'bugs/(.+?)">',tds[0])[0]
                    wooyunUrlList.append(thisUrl)

            print url+' checked.'
        except Exception,e:
            sys.exit('[e] Error, exception is %s' % e)

    return wooyunUrlList

if __name__ == '__main__':
    print '[*] Start...'
    url_public = 'http://wooyun.org/bugs/new_public/page/'
    url_confirm = 'http://wooyun.org/bugs/new_confirm/page/'

    # get public page count
    public_Count = getPageCount(url_public)
    print '[*] Public page count is '+str(public_Count)
    # get confirm page count
    confirm_Count = getPageCount(url_confirm)
    print '[*] Confirm page count is '+str(confirm_Count)
    # get confirm url list
    confirm_urllist = getUrllist(1,confirm_Count,url_confirm)
    print '[*] Confirm vul count is '+str(len(confirm_urllist))
    # get public url list
    public_urllist = getUrllist(1,public_Count,url_public)
    print '[*] Public vul count is '+str(len(public_urllist))
    
    ifstart = raw_input('[*] Public and confirm is '+str(len(public_urllist)+len(confirm_urllist))+'! Start now?(y/n):')
    if ifstart == 'y':
        bThread(checkList)
    else:
        sys.exit('[-] Exit!')