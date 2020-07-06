"""
Copyright 2020 Black Foundry.

This file is part of Robo-CJK.

Robo-CJK is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Robo-CJK is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Robo-CJK.  If not, see <https://www.gnu.org/licenses/>.
"""
import sys
import os
import functools

import BF_author
import BF_init
import BF_topic_msg as bftop
import BF_engine_msg as bmsg
import BF_engine_mysql as bmysql

# import BF_fontbook_struct as bfs
# import BF_tools as bft


class FactoryRCJK:
    ALL_TOPICS = (bftop.TOPIC_MYSQL_ALL, bftop.TOPIC_APPLICATION_TODO, bftop.TOPIC_APPLICATION_LISTEN)

    TYPE_SENDER, TYPE_RECEIVER, TYPE_BOTH = range(3)
    SENDER = None
    def __init__(self, config_mysql: str, config_mymsg: str, 
                    type_msg: int=TYPE_SENDER, callback=None, callback_self: bool=None):
        self._curpath = os.path.dirname(__file__)
        self._bf_log = BF_init.init_log(self._curpath)
        dict_mysql_params, dict_mymsg_params = BF_init.init_params(self._bf_log, self._curpath, config_mysql, config_mymsg) 
        self._my_sql = bmysql.Rcjk2MysqlObject(dict_mysql_params,self._bf_log)
        if type_msg == FactoryRCJK.TYPE_SENDER:
            self._my_msg = bmsg.CeeMosquittoSender(dict_mymsg_params, self._bf_log)
        else:
            # if callback_self set to True, 
            # add self as first paramter as with the callback
            if callback_self:
                callback = functools.partial(callback, self)
            self._my_msg = bmsg.CeeMosquittoManager(FactoryRCJK.ALL_TOPICS, dict_mymsg_params, self._bf_log, callback or self.on_receive)
        
        # set a static sender
        if not FactoryRCJK.SENDER:
            FactoryRCJK.SENDER = functools.partialmethod(self.my_msg.send_msg)

        # set a callback from mysql msg
        self._my_sql.set_callback_msg(self.my_msg.send_msg)

    @property
    def bf_log(self):
        return self._bf_log

    @property
    def my_sql(self):
        return self._my_sql
    
    @property
    def my_msg(self):
        return self._my_msg

    @staticmethod
    def send_mysql_trace(msg: str):
        if FactoryRCJK.SENDER:
            FactoryRCJK.SENDER(bftop.TOPIC_MYSQL_ALL, msg)
      
    @staticmethod
    def send_application_listen(msg: str):
        if FactoryRCJK.SENDER:
            FactoryRCJK.SENDER(bftop.TOPIC_APPLICATION_LISTEN, msg)

    @staticmethod
    def send_application_todo(msg: str):
        if FactoryRCJK.SENDER:
            FactoryRCJK.SENDER(bftop.TOPIC_APPLICATION_TODO, msg)       

    @staticmethod
    def on_receive(topic: str, data_receive: str):
        pass