#!/usr/bin/env python

import psycopg2
import datetime
import locale
import configparser
from random import randint
from passlib.hash import md5_crypt
from colorama import init, Fore, Back, Style
from tabulate import tabulate
from passlib import pwd
from cmd2 import Cmd  # , make_option, options
from appdirs import *


tabfmt = "simple"  # keep it simple stupid
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
    print('[DATABASE]\nhost = db_host\nname = db_name\n' + \
          'user = db_user\npassword = db_password')
    quit(1)


db_name = config['DATABASE']['name']
db_user = config['DATABASE']['user']
db_pass = config['DATABASE']['password']
db_host = config['DATABASE']['host']


#
# tools
#
def showMess(mess=None, style='info'):
    if style == 'info':
        prefix = Fore.GREEN + '[info]' + Style.RESET_ALL
    elif style == 'warn':
        prefix = Fore.YELLOW + '[warn]' + Style.RESET_ALL
    elif style == 'error':
        prefix = Fore.RED + '[error]' + Style.RESET_ALL
    suffix = Style.RESET_ALL
    print(' {} {}{}'.format(prefix, mess, suffix))


def ask(mess=None, style='optional'):
    if style == 'optional':
        prefix = Fore.GREEN + '(optional)' + Style.RESET_ALL
    elif style == 'required':
        prefix = Fore.YELLOW + '(required)' + Style.RESET_ALL
    suffix = Style.RESET_ALL
    return input(' {} {}{}'.format(prefix, mess, suffix))


def doesAddressExist(address, is_a="alias"):
    """check if an alias or a mailbox exist
    : address is name@domain
    : is_a is "alias" or "mailbox"
    return True or False"""
    if is_a == "alias":
        row_name = "address"
    elif is_a == "mailbox":
        row_name = "username"
    query = "select * from {} where {}=(%s)".format(is_a, row_name)
    data = (address, )
    cur.execute(query, data)
    if cur.rowcount == 0:
        return False
    elif cur.rowcount == 1:
        return True
    else:
        showMess("many {} {}es ?!".format(address, is_a), "error")
        return False


def disconnectBDD():
    cur.close()
    conn.close()


def parseCLIargs(args):
    """convert args passed to CLI command to tuple"""
    return tuple(args.split())


#
# cli related
#
class Shell(Cmd):
    """ Class for the CLI """

    prompt_text = '\npfxadmin ({})> '

    def preloop(self):
        self.selectedDomain = domainSelect()
        self.set_prompt()
        # self.intro = "\n " + Back.BLUE + Style.BRIGHT + \
        #         "Welcome to PostFix ADMIN" + Style.RESET_ALL + "\n"

    def set_prompt(self):
        self.prompt = self.prompt_text.format(self.selectedDomain)

    def do_alias(self, line):
        """for alias stuffs
        you can:
            add     -- add an alias
                       ex: alias add new_alias dest_mailbox [comment]
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
        alias(domain=self.selectedDomain, args=parseCLIargs(line))

    def complete_alias(self, text, line, begidx, endidx):
        self.goodCommands = ['add', 'disable', 'enable',
                             'list', 'update', 'remove']
        if not text:
            completions = self.goodCommands[:]
        else:
            completions = [c for c in self.goodCommands
                           if c.startswith(text)]
        return completions

    def do_mailboxlist(self, line):
        """affiche la liste des boites mails du domaine courant"""
        mailboxPrint(domain=self.selectedDomain)

    # @options([make_option('-p', '--password', action="store",
    #                       help="the password you want, gen pass if empty",
    #                       default=None),
    #           make_option('-c', '--comment', action="store",
    #                       help="add a comment to your new mailbox",
    #                       default=None)])
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
        mailbox(domain=self.selectedDomain, args=parseCLIargs(line))

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


def alias(domain=None, args=None):
    if len(args) == 0 or args[0] == "list":
        aliasPrint(domain)
    elif args[0] == "add":
        aliasOptionAdd(domain=domain, args=args)
    elif args[0] == "remove":
        try:
            address = args[1]
        except:
            showMess(mess="problem with your arguments", style='error')
        else:
            aliasDel(domain=domain, address=address)
    elif args[0] == "disable" or args[0] == "enable":
        aliasOptionsToggle(domain=domain, args=args)
    elif args[0] == "update":
        aliasOptionUpdate(domain=domain, args=args)
    else:
        print("the args: {}".format(args))


def aliasOptionAdd(domain=None, args=None):
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
        aliasAdd(domain=domain, address=address, goto=goto,
                 comment=comment)


def aliasOptionsToggle(domain=None, args=None):
    """enable or disable an alias"""
    if args[0] == "enable":
        state = True
    elif args[0] == "disable":
        state = False
    else:
        showMess("this is a message which not should displayed", style='error')
        return False
    try:
        address = args[1]
    except:
        showMess("problem with your arguments", style='error')
    else:
        aliasToggle(domain=domain, address=address, active=state)


def aliasOptionUpdate(domain=None, args=None):
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
            aliasUpdate(domain=domain, address=address,
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
        aliasUpdate(domain=domain, address=address,
                    target=True, new_target=new_goto)


def mailboxOptionUpdate(domain=None, args=None):
    if args[2] == "comment":
        try:
            address = args[1]
        except:
            showMess("you have to provide a mailbox", "warn")
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
            mailboxUpdate(domain=domain, address=address,
                          comment=True, new_comment=new_comment)
    elif args[2] == "name":
        try:
            address = args[1]
        except:
            showMess("you have to provide a mailbox", "warn")
            return False
        try:
            if len(args) > 2:
                new_name = " ".join(args[3:])
            else:
                new_name = ''
        except:
            showMess("", "error")
        else:
            if len(new_name) > 20:  # abritrary limit
                showMess("{:n} characters is really too much, limit is 20"
                         .format(len(new_name)), "warn")
                return False
            mailboxUpdate(domain=domain, address=address,
                          name=True, new_name=new_name)
    elif args[2] == 'password':
        try:
            address = args[1]
        except:
            showMess("you have to provide a mailbox", "warn")
            return False
        new_password = ask("password (empty for autogenerated): ", "required")
        new_password = new_password.replace(" ", "")  # remove space
        if len(new_password) == 0:
            new_password = pwd.genword(charset="ascii_72",
                                       length=randint(8, 12))
        elif not new_password.isprintable():
            showMess("Only printable characters are allowed", "warn")
            return False
        showMess("the new password for {} will be: {}"
                 .format(address, new_password))
        confirm = ask("Do you confirm ? [y/N] ", "required")
        if confirm == "y" or confirm == "Y":
            mailboxUpdate(domain, address,
                          password=True, new_password=new_password)
        else:
            showMess("you don't want this")
            return True


def mailbox(domain=None, args=None, password=None, comment=None):
    if len(args) == 0 or args[0] == "list":
        mailboxPrint(domain)
    elif args[0] == "add":
        try:
            address = args[1]
        except:
            showMess("please provide an name for the new mailbox", "warn")
            return False
        mailboxOptionAdd(domain=domain, address=address)
    elif args[0] == "remove":
        try:
            address = args[1]
        except:
            showMess("please provide an name for the new mailbox", "warn")
            return False
        mailboxOptionRemove(domain=domain, address=address)
    elif args[0] == "update":
        try:
            address = args[1]
        except:
            showMess("please provide an name for the new mailbox", "warn")
            return False
        mailboxOptionUpdate(domain=domain, args=args)
    else:
        print("the args: {}".format(args))


def printTabular(headers, data, tablefmt=tabfmt, stralign="center"):
    print(tabulate(data, headers=headers, tablefmt=tablefmt,
                   stralign=stralign))
    print()


#
# pfxadmin functions
#
def aliasAdd(domain=None, address=None, goto=None, comment=None):
    address = "{}@{}".format(address, domain)
    goto = "{}@{}".format(goto, domain)
    # check if goto exist
    if not doesAddressExist(goto, "alias"):
        showMess("target {} does not exist".format(goto), "warn")
        return False
    # check if alias exist
    if doesAddressExist(address, "alias"):
        showMess("alias {} exist already".format(address), "warn")
        return False
    query = """insert into alias (address, goto, domain, comment)
            values (%s, %s, %s, %s)"""
    data = (address, goto, domain, comment)
    cur.execute(query, data)
    cur.execute("commit")
    showMess(mess='alias {} is now availble.'.format(address))


def aliasDel(domain=None, address=None):  # TO FINISH WITH CHECKS
    address = "{}@{}".format(address, domain)
    SQL = "delete from alias where address=(%s)"
    data = (address, )
    cur.execute(SQL, data)
    cur.execute("commit")
    showMess(mess="alias {} is gone".format(address))


def aliasPrint(domain=None):
    SQL = "select * from alias where domain=(%s) order by address"
    domain = (domain,)
    cur.execute(SQL, domain)
    rows = cur.fetchall()
    # print("\naliases for {}:".format(domain[0]))
    headers = ["alias", "target", "comment", "created", "modified", "active"]
    data = []
    for row in rows:
        a_name = row[0].split('@')[0]
        a_dest = row[1].split('@')[0]
        # a_domain = row[2]
        a_created = datetime.datetime.strftime(row[3], "%x %X")
        a_modified = datetime.datetime.strftime(row[4], "%x %X")
        a_active = row[5]
        if row[6] is None:
            a_comment = ""
        else:
            a_comment = row[6]
        if row[0] != row[1]:
            data.append([a_name, a_dest, a_comment,
                         a_created, a_modified, a_active])
    printTabular(headers, data)


def aliasToggle(domain=None, address=None, active=None):
    """for enable or disable an alias"""
    address = "{}@{}".format(address, domain)
    # check is alias exist
    if not doesAddressExist(address, "alias"):
        return False
    # check if already in targeted state
    query = "select * from alias where address=(%s) and active=(%s)"
    data = (address, active)
    cur.execute(query, data)
    if cur.rowcount > 0:
        if active:
            showMess(mess="alias {} is already enabled".format(address),
                     style='warn')
        else:
            showMess(mess="alias {} is already disabled".format(address),
                     style='warn')
        return False
    # do the toggle state
    query = "update alias set (active, modified)=(%s, %s) where address=(%s)"
    now = datetime.datetime.now()
    data = (active, now, address)
    try:
        cur.execute(query, data)
        cur.execute("commit")
        if active:
            showMess(mess="alias {} is now enabled".format(address))
        else:
            showMess(mess="alias {} is now disabled".format(address))
    except Exception as msg:
        showMess(mess="This problem occured:\n{}".format(msg),
                 style='error')


def aliasUpdate(domain=None, address=None,
                comment=False, target=False, **kargs):
    """updating comment or target for an alias"""
    address = "{}@{}".format(address, domain)
    # check if alias exist
    if not doesAddressExist(address, "alias"):
        showMess("alias {} does not exist".format(address), "warn")
        return False
    if comment:
        query = """update alias set (comment, modified)=(%s,%s)
                where address=(%s)"""
        now = datetime.datetime.now()
        data = (kargs["new_comment"], now, address)
        try:
            cur.execute(query, data)
            cur.execute("commit")
            showMess("{}'s comment is updated".format(address))
        except Exception as msg:
            showMess("This problem occured:\n{}".format(msg), "error")
            return False
        else:
            return True
    elif target:
        new_target = "{}@{}".format(kargs["new_target"], domain)
        # check if new target exist
        if not doesAddressExist(new_target, "alias"):
            showMess("the new target {} do not exist".format(new_target),
                     "warn")
            return False
        query = """update alias set (goto, modified)=(%s,%s)
               where address=(%s)"""
        now = datetime.datetime.now()
        data = (kargs["new_target"], now, address)
        try:
            cur.execute(query, data)
            cur.execute("commit")
            showMess("{}'s target is updated".format(address))
        except Exception as msg:
            showMess("This problem occured:\n{}".format(msg), "error")


def domainSelect():
    cur.execute("select * from domain where domain!='ALL'")
    rows = cur.fetchall()
    if cur.rowcount > 1:
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


def mailboxUpdate(domain=None, address=None,
                  comment=False, name=False,
                  password=False, **kargs):
    """updating comment or full name for a mailbox"""
    address = "{}@{}".format(address, domain)
    # check if alias exist
    if not doesAddressExist(address, "alias"):
        showMess("mailbox {} does not exist".format(address), "warn")
        return False
    if comment:
        query = """update alias set (comment, modified)=(%s,%s)
                where address=(%s)"""
        now = datetime.datetime.now()
        data = (kargs["new_comment"], now, address)
        try:
            cur.execute(query, data)
            cur.execute("commit")
            showMess("{}'s comment is updated".format(address))
        except Exception as msg:
            showMess("This problem occured:\n{}".format(msg), "error")
            return False
        return True
    elif name:
        new_name = kargs["new_name"]
        query = """update mailbox set (name, modified)=(%s, %s)
                   where username=(%s)"""
        now = datetime.datetime.now()
        data = (new_name, now, address)
        try:
            cur.execute(query, data)
            cur.execute("commit")
            showMess("{}'s full name is updated".format(address))
        except Exception as msg:
            showMess("This problem occured:\n{}".format(msg), "error")
            return False
        else:
            return True
    elif password:
        new_pwd = md5_crypt.hash(kargs["new_password"])
        query = """update mailbox set (password, modified)=(%s, %s)
                   where username=(%s)"""
        now = datetime.datetime.now()
        data = (new_pwd, now, address)
        try:
            cur.execute(query, data)
            cur.execute("commit")
            showMess("{}'s full name is updated".format(address))
        except Exception as msg:
            showMess("This problem occured:\n{}".format(msg), "error")
            return False
        else:
            return True


def mailboxOptionAdd(domain=None, address=None):
    """add a new mailbox"""
    if doesAddressExist(address + "@" + domain):
        showMess("{}@{} already exist".format(address, domain), "warn")
        return False
    password = ask("password (empty for autogenerated): ", "required")
    password = password.replace(" ", "")  # remove space
    if len(password) == 0:
        password = pwd.genword(charset="ascii_72", length=randint(8, 12))
    elif not password.isprintable():
        showMess("Only printable characters are allowed", "warn")
        return False
    # showMess("The password is: {}".format(password))
    name = ask("Full Name: ", "optional")
    comment = ask("comment: ", "optional")
    if len(comment) == 0:
        comment = None
    # print("password:{}".format(password))
    # recap tab
    headers = ["mailbox", "password", "full name", "comment"]
    data = [[address + '@' + domain, password, name, comment]]
    printTabular(headers, data)

    confirm = ask("Do you confirm ? [y/N] ", "required")
    if confirm == "y" or confirm == "Y":
        mailboxAdd(domain, address, password, name, comment)
    else:
        showMess("you don't want this")
        return True


def mailboxOptionRemove(domain=None, address=None):
    """remove a mailbox"""
    username = '{}@{}'.format(address, domain)
    if not doesAddressExist(username):
        showMess("mailbox {} does not exist".format(username), "warn")
        return False
    confirm = ask("Do you really want to remove {}? [y/N] "
                  .format(username), "required")
    if confirm == "y" or confirm == "Y":
        query = "delete from mailbox where username=(%s)"
        data = (username, )
        cur.execute(query, data)
        cur.execute("commit")
        query = "delete from alias where address=(%s)"
        cur.execute(query, data)
        cur.execute("commit")
        showMess("mailbox {} has been removed".format(username))
        showMess("don't forget to remove the vmail directory")
    else:
        showMess("{} deletion canceled".format(username))
        return True


def mailboxAdd(domain=None, address=None, password=None,
               name='', comment=None):
    """execute the query for adding new mailbox"""
    username = "{}@{}".format(address, domain)
    maildir = "{}/".format(username)
    # active = True
    local_part = address
    password = md5_crypt.hash(password)

    query = """insert into mailbox
               (username, password, name, maildir, domain, local_part)
               values (%s, %s, %s, %s, %s, %s)"""
    data = (username, password, name, maildir, domain, local_part)
    cur.execute(query, data)
    cur.execute("commit")
    query = """insert into alias
               (address, goto, domain, comment)
               values (%s, %s, %s, %s)"""
    data = (username, username, domain, comment)
    cur.execute(query, data)
    cur.execute("commit")

    showMess('mailbox {} is now available')


def mailboxPrint(domain=None):
    # SQL = "select * from mailbox where domain=(%s) order by username"
    SQL = """select mailbox.*, alias.comment from mailbox
             inner join alias on mailbox.username = alias.address
             where mailbox.domain=(%s) order by username"""
    domain = (domain, )
    cur.execute(SQL, domain)
    rows = cur.fetchall()
    headers = ["username", "name", "quota", "created", "modified", "active",
               "comment"]
    data = []
    # print("\nmailbox for {}:".format(domain[0]))
    for row in rows:
        m_username = row[0].split('@')[0]
        m_name = row[2]
        m_quota = row[4]
        m_created = datetime.datetime.strftime(row[5], "%x %X")
        m_modified = datetime.datetime.strftime(row[6], "%x %X")
        m_active = row[7]
        m_comment = row[10]
        data.append([m_username, m_name, m_quota,
                     m_created, m_modified, m_active,
                     m_comment])
    printTabular(headers, data)


if __name__ == '__main__':
    print("\n " + Back.BLUE + Style.BRIGHT +
          "Welcome to PostFix ADMIN" + Style.RESET_ALL + "\n")
    with psycopg2.connect(dbname=db_name, user=db_user,
                          password=db_pass, host=db_host) as conn:
        cur = conn.cursor()
        Shell().cmdloop()
        # disconnectBDD()
