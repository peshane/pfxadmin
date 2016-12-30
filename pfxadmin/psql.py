#!/usr/bin/env python

import psycopg2


def connectBDD(dbname, user, password, host, port=5432):
    with psycopg2.connect(dbname=dbname,
                          user=user,
                          password=password,
                          host=host,
                          port=port) as conn:
        cur = conn.cursor()
        return conn, cur


def disconnectBDD(cur, conn):
    cur.close()
    conn.close()


def launchQuery(cur, query, data=None, commit=False):
    if data is None:
        cur.execute(query)
    else:
        cur.execute(query, data)
    
    if commit:
        cur.execute("commit")
    else:
        return cur.fetchall()
