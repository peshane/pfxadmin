#!/usr/bin/env python

from colorama import init, Fore, Back, Style
from tabulate import tabulate
from psql import launchQuery

# colorama initialization (mostly for windows)
init()


def showMess(mess=None, style='info'):
    if style == 'info':
        prefix = Fore.GREEN + '[info]' + Style.RESET_ALL
    elif style == 'warn':
        prefix = Fore.YELLOW + '[warn]' + Style.RESET_ALL
    elif style == 'error':
        prefix = Fore.RED + '[error]' + Style.RESET_ALL
    elif style == 'debug':
        prefix = Fore.CYAN + '[debug]' + Style.RESET_ALL
    suffix = Style.RESET_ALL
    print(' {} {}{}'.format(prefix, mess, suffix))


def ask(mess=None, style='optional'):
    if style == 'optional':
        prefix = Fore.GREEN + '(optional)' + Style.RESET_ALL
    elif style == 'required':
        prefix = Fore.YELLOW + '(required)' + Style.RESET_ALL
    suffix = Style.RESET_ALL
    return input(' {} {}{}'.format(prefix, mess, suffix))


def parseCLIargs(args):
    """convert args passed to CLI command to tuple"""
    return tuple(args.split())


def printTabular(headers, data, tablefmt="simple", stralign="center"):
    print(tabulate(data, headers=headers, tablefmt=tablefmt,
                   stralign=stralign))
    print()


def doesAddressExist(address, is_a="alias", cur=None):
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
    # cur.execute(query, data)
    rows = launchQuery(cur, query, data)
    # showMess("doesAddressExist, nb rows: {}".format(len(rows)), "debug")
    if len(rows) == 0:
        return False
    elif len(rows) == 1:
        return True
    else:
        showMess("many {} {}es ?!".format(address, is_a), "error")
        return False
