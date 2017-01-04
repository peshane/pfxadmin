#!/usr/bin/env python

from psql import launchQuery
from tools import printTabular, doesAddressExist, showMess
import datetime
# import re


class Alias(object):
    def __init__(self, cur, domain):
        self.cur = cur
        self.domain = domain

    def show(self):
        query = "select * from alias where domain=(%s) order by address"
        rows = launchQuery(self.cur, query, (self.domain,))
        # print("\naliases for {}:".format(domain[0]))
        headers = ["alias", "target", "comment",
                   "created", "modified", "active"]
        data = []
        for row in rows:
            a_name = row[0].split('@')[0]
            # a_dest = re.sub(',', '\n', row[1].split('@')[0])
            a_dest = ""
            l_dest = row[1].split(',')
            for i in range(0, len(l_dest)):
                if l_dest[i].split('@')[1] == self.domain:
                    a_dest += l_dest[i].split('@')[0]
                else:
                    a_dest += l_dest[i]
                if i < len(l_dest) - 1:
                    a_dest += ', '
            # print("{}: {}".format(a_name, a_dest))
            # a_domain = row[2]
            a_created = datetime.datetime.strftime(row[3], "%x %X")
            a_modified = datetime.datetime.strftime(row[4], "%x %X")
            a_active = row[5]
            if row[6] is None:
                a_comment = ""
            else:
                a_comment = row[6]
            if row[0] != row[1]:
                if len(a_dest.split(',')) > 1:
                    a_dest = a_dest.split(',')
                    data.append([a_name, a_dest[0], a_comment,
                                 a_created, a_modified, a_active])
                    a_name = "⁝"
                    # a_name = "⎣"
                    # a_name = "⎿"
                    # a_name = "⌊"
                    # a_name = "⸠"
                    a_comment = ""
                    a_created = ""
                    a_modified = ""
                    a_active = ""
                    for i in range(1, len(a_dest)):
                        data.append([a_name, a_dest[i], a_comment,
                                     a_created, a_modified, a_active])
                else:
                    data.append([a_name, a_dest, a_comment,
                                 a_created, a_modified, a_active])
        printTabular(headers, data)
    def pre_toggle(self, domain=None, args=None):
        """enable or disable an alias"""
        if args[0] == "enable":
            state = True
        elif args[0] == "disable":
            state = False
        else:
            showMess("this is a message which not should displayed",
                     style='error')
            return False
        try:
            address = args[1]
        except:
            showMess("problem with your arguments", style='error')
        else:
            self.toggle(domain=domain, address=address, active=state)

    def toggle(self, domain=None, address=None, active=None):
        """for enable or disable an alias"""
        address = "{}@{}".format(address, domain)
        # check is alias exist
        if not doesAddressExist(address, "alias", cur=self.cur):
            showMess("alias {} does not exist".format(address), "warn")
            return False
        # check if already in targeted state
        query = "select * from alias where address=(%s) and active=(%s)"
        data = (address, active)
        # cur.execute(query, data)
        rows = launchQuery(self.cur, query, data)
        if len(rows) > 0:
            if active:
                showMess(mess="alias {} is already enabled".format(address),
                         style='warn')
            else:
                showMess(mess="alias {} is already disabled".format(address),
                         style='warn')
            return False
        # do the toggle state
        query = "update alias set (active, modified)=(%s, %s) " + \
                "where address=(%s)"
        now = datetime.datetime.now()
        data = (active, now, address)
        try:
            launchQuery(self.cur, query, data, commit=True)
            if active:
                showMess(mess="alias {} is now enabled".format(address))
            else:
                showMess(mess="alias {} is now disabled".format(address))
        except Exception as msg:
            showMess(mess="This problem occured:\n{}".format(msg),
                     style='error')

    def pre_add(self, domain=None, args=None):
        try:
            address = args[1]
            goto = args[2]
            if len(args) > 2:
                comment = " ".join(args[3:])
            else:
                comment = None
        except:
            showMess(mess="problem with your arguments", style='error')
        else:
            self.add(domain=domain, address=address, goto=goto,
                     comment=comment)

    def add(self, domain=None, address=None, goto=None, comment=None):
        address = "{}@{}".format(address, domain)
        raw_goto = goto
        goto = ""
        if len(raw_goto.split(',')) > 1:
            l_goto = raw_goto.split(',')
            # showMess(str(l_goto), 'debug')
            for i in range(0, len(l_goto)):
                if len(l_goto[i].split('@')) == 1:
                    l_goto[i] = "{}@{}".format(l_goto[i], domain)
                goto += l_goto[i]
                if i < len(l_goto) - 1:
                    goto += ','
        else:
            if len(raw_goto.split('@')) == 1:
                goto = "{}@{}".format(raw_goto, domain)
            else:
                goto = raw_goto
        # showMess(goto, 'debug')
        # return True
        # check if goto exist
        # if not doesAddressExist(goto, "alias", cur=self.cur):
        #     showMess("target {} does not exist".format(goto), "warn")
        #     return False
        # check if alias exist
        if doesAddressExist(address, "alias", cur=self.cur):
            showMess("alias {} exist already".format(address), "warn")
            return False
        query = """insert into alias (address, goto, domain, comment)
                values (%s, %s, %s, %s)"""
        data = (address, goto, domain, comment)
        launchQuery(self.cur, query, data, commit=True)
        showMess(mess='alias {} is now availble.'.format(address))

    def remove(self, domain=None, address=None):  # TO FINISH WITH CHECKS
        address = "{}@{}".format(address, domain)
        query = "delete from alias where address=(%s)"
        data = (address, )
        launchQuery(self.cur, query, data, commit=True)
        showMess(mess="alias {} is gone".format(address))

    def pre_update(self, domain=None, args=None):
        if args[2] == "comment":
            try:
                address = args[1]
            except:
                showMess("you have to provide an alias", "warn")
                return False
            try:
                if len(args) > 2:
                    new_comment = " ".join(args[3:])
                else:
                    new_comment = None
            except:
                showMess("", "error")
            else:
                if len(new_comment) > 50:  # abritrary limit
                    showMess("{:n} characters is really too much, limit is 50"
                             .format(len(new_comment)), "warn")
                    return False
                self.update(domain=domain, address=address,
                            comment=True, new_comment=new_comment)

        elif args[2] == "target":
            try:
                address = args[1]
            except:
                showMess("you have to provide an alias", "warn")
                return False
            try:
                new_goto = args[3]
            except:
                showMess("you have to provide a new target", "warn")
                return False
            self.update(domain=domain, address=address,
                        target=True, new_target=new_goto)

    def update(self, domain=None, address=None,
               comment=False, target=False, **kargs):
        """updating comment or target for an alias"""
        address = "{}@{}".format(address, domain)
        # check if alias exist
        if not doesAddressExist(address, "alias", cur=self.cur):
            showMess("alias {} does not exist".format(address), "warn")
            return False
        if comment:
            query = """update alias set (comment, modified)=(%s,%s)
                    where address=(%s)"""
            now = datetime.datetime.now()
            data = (kargs["new_comment"], now, address)
            try:
                launchQuery(self.cur, query, data, commit=True)
                showMess("{}'s comment is updated".format(address))
            except Exception as msg:
                showMess("This problem occured:\n{}".format(msg), "error")
                return False
            else:
                return True
        elif target:
            # new_target = "{}@{}".format(kargs["new_target"], domain)
            raw_goto = kargs["new_target"]
            new_target = ""
            if len(raw_goto.split(',')) > 1:
                l_goto = raw_goto.split(',')
                # showMess(str(l_goto), 'debug')
                for i in range(0, len(l_goto)):
                    if len(l_goto[i].split('@')) == 1:
                        l_goto[i] = "{}@{}".format(l_goto[i], domain)
                    new_target += l_goto[i]
                    if i < len(l_goto) - 1:
                        new_target += ','
            else:
                if len(raw_goto.split('@')) == 1:
                    new_target = "{}@{}".format(raw_goto, domain)
                else:
                    new_target = raw_goto
            # check if new target exist
            # if not doesAddressExist(new_target, "alias", cur=self.cur):
            #     showMess("the new target {} do not exist".format(new_target),
            #              "warn")
            #     return False
            query = """update alias set (goto, modified)=(%s,%s)
                where address=(%s)"""
            now = datetime.datetime.now()
            # data = (kargs["new_target"], now, address)
            data = (new_target, now, address)
            try:
                launchQuery(self.cur, query, data, commit=True)
                showMess("{}'s target is updated".format(address))
            except Exception as msg:
                showMess("This problem occured:\n{}".format(msg), "error")
