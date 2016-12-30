#!/usr/bin/env python

from psql import launchQuery
from tools import printTabular, doesAddressExist, showMess
import datetime


class Domain(object):
    def __init__(self, cur):
        self.cur = cur

    def choose(self):
        query = "select * from domain where domain!='ALL'"
        rows = launchQuery(self.cur, query)
        if len(rows) > 1:
            print('domain selection:')
            i = 0
            for row in rows:
                print('[{}] {}'.format(i, row[0]))
                i += 1
            domain = int(input("which domain ? "))
            return rows[domain][0]
        else:
            showMess(mess="only one domain is available: {}".format(rows[0][0]))
            return rows[0][0]
