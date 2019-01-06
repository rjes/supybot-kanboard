###
# Copyright (c) 2019, Robert Soderlund
# All rights reserved.
#
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import base64
import json
import time
import datetime
import supybot.ircmsgs as ircmsgs

from credentials import *

def kb_fetch(method, **kwargs):
    credentials = base64.b64encode('{}:{}'.format(
        kb_user,
        kb_pass).encode())
    auth_header_prefix = 'Basic '
    headers = {
            'Authorization': auth_header_prefix + credentials.decode(),
            'Content-Type': 'application/json',
            }
    payload = {
            'jsonrpc': '2.0',
            'method': method,
            'id': time.time(),
            'params': kwargs
            }
    result = utils.web.getUrl(kb_url, size=None, timeout=None, headers=headers,
            data=json.dumps(payload))
    return json.loads(result, encoding="utf-8")["result"]


class Kanboard(callbacks.Plugin):
    """Add the help for "@plugin help Kanboard" here
    This should describe *how* to use this plugin."""
    pass
    def todo(self, irc, msg, args):
        self.kanboard(irc, msg, args)
    def kanboard(self, irc, msg, args):
        """Some good help text
            Returns kanboard tasks
        """
        if len(args) == 1:
            if args[0] == "list":
                channel = msg.args[0]
                column_names = {}
                column_names_len = 0
                column_order = {}
                tasks = []
                columns = []

                tasks = kb_fetch("getAllTasks", project_id=18)
                columns = kb_fetch("getColumns", project_id=18)
                for column in columns:
                    column_names[column['id'].encode('utf-8')] = column['title'].encode('utf-8')
                    if len(column['title'].encode('utf-8')) > column_names_len:
                        column_names_len = len(column['title'])
                irc.queueMsg(ircmsgs.privmsg(channel,"| {0:3} | {2:>24} | {1:>{column_names_len}} | {3} ".format(
                    "ID",
                    "Status",
                    "Last updated",
                    "Descr",
                    column_names_len=column_names_len
                    )
                ))
                for task in tasks:
                    print(task)
                    irc.queueMsg(ircmsgs.privmsg(channel,"| {0} | {2} | {1:>{column_names_len}} | {3} ".format(
                        task['id'],
                        column_names[task['column_id'].encode('utf-8')],
                        datetime.datetime.fromtimestamp(float(task['date_modification'])).strftime('%c'),
                        task['title'].encode('utf-8'),
                        column_names_len=column_names_len
                        )
                    ))
            else:
                irc.reply("Unknown action")
        else:
            irc.reply("Argument error")

Class = Kanboard


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
