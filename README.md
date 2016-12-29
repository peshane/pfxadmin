pfxadmin
========

_pfxadmin_ is a command-line interface used to manage mailboxes if you use a postgresql database.

It's using the same scheme as [postfixadmin](http://postfixadmin.sourceforge.net) except the addition of a "comment" column in the "alias" table because i like comments. 

Required
--------
- python 3 (only tested with python 3.5)
- a postgresql database for manage your mails (see postfixadmin) + a "comment" column in the "alias" table
- required the following non standard python libraries:
  - psycopg2
  - passlib
  - colorama
  - tabulate
  - cmd2
  - appdirs

### Creating database
For PostgreSQL:
  CREATE USER postfix WITH PASSWORD 'whatever';
  CREATE DATABASE postfix OWNER postfix ENCODING 'unicode';

then play the create_postfix_db.sql in the created database (eg: _postfix_ as suggested)

then create at least one domain manualy:
  INSERT INTO DOMAIN (domain, transport) VALUES ('domain.tld', 'virtual');

What you can/can't do with (for now)
------------------------------
- mailbox
  - list
  - adding/deleting
  - update comment, password, full name
  - can't
     - enable/disable
- alias
  - list
  - adding/deleting
  - disable/enable
  - update target, comment
- domains
  - select the working domain at launch
  - can't
     - do anything else

And most important, you can't do a lot of things!

So let me now if you want some stuff.

Usage
-----
```
pfxadmin (domain.tld)> help mailbox
for mailbox stuffs
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


pfxadmin (domain.tld)> help alias
for alias stuffs
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


pfxadmin (domain.tld)> mailbox list
 username        name         quota        created             modified         active          comment
----------  --------------  -------  -------------------  -------------------  --------  ---------------------
  buying                          0  04/08/2014 19:42:12  04/08/2014 19:42:12    True        mostly amazon
    me                            0  01/08/2014 14:28:26  01/08/2014 14:28:26    True        that's me !!!
 socials                          0  08/08/2014 11:29:02  08/08/2014 11:29:02    True      socials networks
  spams                           0  08/10/2014 11:29:45  15/04/2015 16:32:27    True      
  works       Mr Peshane          0  03/01/2014 11:29:02  08/08/2014 11:29:02    True    really serious stuffs


pfxadmin (domain.tld)> alias list
  alias       target        comment             created             modified         active
----------  ----------  ----------------  -------------------  -------------------  --------
  abuse     postmaster    don't touch     01/08/2014 12:12:17  21/12/2016 18:39:12    True
   buy        buying                      30/09/2015 19:44:23  30/09/2015 19:44:23    True
hostmaster  postmaster    don't touch     01/08/2014 12:12:17  21/12/2016 18:39:20    True
  http      postmaster                    22/08/2014 13:03:55  22/08/2014 13:03:55    True
postmaster      me                        01/08/2014 12:12:17  01/08/2014 18:50:25    True
  spam        spams     i dislike spams   14/05/2015 17:38:59  14/05/2015 17:38:59    True
webmaster   postmaster    don't touch     01/08/2014 12:12:17  21/12/2016 18:39:44    True

```

ToDo
----
- documentation
  - have a better doc
- pfxadmin functions
  - playing with virtuals domains
  - supporting vacation/out-of-the office (well, i don't use it so... may be one day)
  - playing with quota (the same)
- pfxadmin usability
  - pip installation would be great
  - auto creationg database schema or just add missing stuffs if already there
  - be more logical with commands calls
  - better english

Let me know what you want.

License
-------
_pfxadmin_ is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License version 3 as published by the Free Software Foundation
