#!/usr/bin/env python
# coding=utf-8
# code by 92ez.com

import sqlite3
import sys

def get20Rank():
    try:
        cx = sqlite3.connect(sys.path[0]+"/wooyun.db")
        cu = cx.cursor()
        cu.execute("select count(company) as number,company from record where rank = 20 group by company order by number desc")

        for row in cu.fetchall():
            print 'company: '+row[1]+' ----> 20Rank count: '+str(row[0])

        cu.close()
        cx.close()
    except Exception, e:
        print e

if __name__ == '__main__':
    get20Rank()