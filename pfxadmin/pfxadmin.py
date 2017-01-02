#!/usr/bin/env python

# import psycopg2
import psql
from tools import showMess, parseCLIargs
from alias import Alias
from domain import Domain
from mailbox import Mailbox
# import datetime
import locale
import configparser
# from random import randint
# from passlib.hash import md5_crypt
from colorama import init, Back, Style
# from tabulate import tabulate
# from passlib import pwd
from cmd2 import Cmd  # , make_option, options
from appdirs import user_data_dir


locale.setlocale(locale.LC_ALL, locale.getlocale())  # set locale for datetime


appname = "pfxadmin"
appauthor = "peshane"

conf_file = "{}/pfxadmin.ini".format(user_data_dir(appname, appauthor))

# print(conf_file)
# quit()


# colorama initialization (mostly for windows)
init()

try:
    config = configparser.ConfigParser()
    config.read(conf_file)
    if config['DATABASE']['name']:
        pass
except Exception as msg:
    print("the following error occured:\n{}\n".format(msg))
    print("Please create the {} file with the following skeleton:"
          .format(conf_file))
    print('[DATABASE]\nhost = db_host\nname = db_name\n'
          'user = db_user\npassword = db_password')
    quit(1)


db_name = config['DATABASE']['name']
db_user = config['DATABASE']['user']
db_pass = config['DATABASE']['password']
db_host = config['DATABASE']['host']


#
# cli related
#
def setDomain():
    return Domain(cur)


class Shell(Cmd):
    """ Class for the CLI """

    prompt_text = '\npfxadmin ({})> '

    def preloop(self):
        # self.selectedDomain = domainSelect()
        dom = setDomain()
        self.selectedDomain = dom.choose()
        self.set_prompt()

    def set_prompt(self):
        self.prompt = self.prompt_text.format(self.selectedDomain)
        self.alias = Alias(cur, self.selectedDomain)
        self.mbox = Mailbox(cur, self.selectedDomain)

    def do_alias(self, line):
        """for alias stuffs
        you can:
            add     -- add an alias
                       ex: alias add new_alias dest_mailbox[,dest] [comment]
            disable -- disable an alias
                       ex: alias disable alias_name
            enable  -- enable an alias
                       ex: alias enable alias_name
            list    -- list aliases for current domain
            remove  -- remove an alias
                       ex: alias remove alias_name
            update  -- update target or comment
                       ex: alias update alias_name comment [new comment]
                       ex: alias update alias_name target new_dest_mailbox
        """
        sAlias(domain=self.selectedDomain, args=parseCLIargs(line),
               alias=self.alias)

    def complete_alias(self, text, line, begidx, endidx):
        self.goodCommands = ['add', 'disable', 'enable',
                             'list', 'update', 'remove']
        if not text:
            completions = self.goodCommands[:]
        else:
            completions = [c for c in self.goodCommands
                           if c.startswith(text)]
        return completions

    def do_mailbox(self, line, opts=None):
        """for mailbox stuffs
        you can:
            add    -- add a new mailbox
                      ex: mailbox add new_mailbox
            list   -- list all mailbox for current domain
            remove -- remove a mailbox
                      ex: mailbox remove mailbox
            update -- update full name, comment or password
                      ex: mailbox update mailbox_name comment [new comment]
                      ex: mailbox update mailbox_name name [new full name]
                      ex: mailbox update mailbox_name password
        """
        smailbox(domain=self.selectedDomain, args=parseCLIargs(line),
                 mbox=self.mbox)

    def complete_mailbox(self, text, line, begidx, endidx):
        self.goodCommands = ['add', 'list', 'remove', 'update']
        if not text:
            completions = self.goodCommands[:]
        else:
            completions = [c for c in self.goodCommands
                           if c.startswith(text)]
        return completions

    def do_EOF(self, line):
        return True


def sAlias(domain=None, args=None, alias=None):
    if len(args) == 0 or args[0] == "list":
        alias.show()
    elif args[0] == "add":
        alias.pre_add(domain=domain, args=args)
    elif args[0] == "remove":
        try:
            address = args[1]
        except:
            showMess(mess="problem with your arguments", style='error')
        else:
            alias.remove(domain=domain, address=address)
    elif args[0] == "disable" or args[0] == "enable":
        alias.pre_toggle(domain=domain, args=args)
    elif args[0] == "update":
        alias.pre_update(domain=domain, args=args)
    else:
        print("the args: {}".format(args))


def smailbox(domain=None, args=None, password=None, comment=None, mbox=None):
    if len(args) == 0 or args[0] == "list":
        # mailboxPrint(domain)
        mbox.show(domain)
    elif args[0] == "add":
        try:
            address = args[1]
        except:
            showMess("please provide an name for the new mailbox", "warn")
            return False
        # mailboxOptionAdd(domain=domain, address=address)
        mbox.pre_add(domain=domain, address=address)
    elif args[0] == "remove":
        try:
            address = args[1]
        except:
            showMess("please provide an name for the new mailbox", "warn")
            return False
        # mailboxOptionRemove(domain=domain, address=address)
        mbox.remove(domain=domain, address=address)
    elif args[0] == "update":
        try:
            address = args[1]
        except:
            showMess("please provide an name for the new mailbox", "warn")
            return False
        # mailboxOptionUpdate(domain=domain, args=args)
        mbox.pre_update(domain=domain, args=args)
    else:
        print("the args: {}".format(args))


#
# pfxadmin functions
#
def domainSelect():
    d = Domain(cur)
    return d.choose()


if __name__ == '__main__':
    print("\n " + Back.BLUE + Style.BRIGHT +
          "Welcome to PostFix ADMIN" + Style.RESET_ALL + "\n")
    conn, cur = psql.connectBDD(db_name, db_user, db_pass, db_host)
    Shell().cmdloop()
