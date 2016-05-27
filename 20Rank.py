#!/usr/bin/env python
# coding=utf-8
# code by 92ez.com

import sqlite3
import sys

def get20Rank():
    try:
        cx = sqlite3.connect(sys.path[0]+"/wooyun.db")
        cu = cx.cursor()
        cu.execute("select * from record where rank = 20 order by publishtime desc")
        for row in cu.fetchall():
            print '-'*60
            print 'url: '+row[1]
            print 'title: '+row[2]
            print 'company: '+row[3]
            print 'status: '+row[4]
            print 'author: '+row[5]
            print 'type: '+row[6]
            print 'rank: '+row[7]
            print 'commit: '+row[8]
            print 'publish: '+row[9]

        cu.close()
        cx.close()
    except Exception, e:
        print e

if __name__ == '__main__':
    get20Rank()