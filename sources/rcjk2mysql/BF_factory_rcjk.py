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
from typing import Callable, Tuple

import BF_author
import BF_init
import BF_topic_msg as bftop
import BF_engine_msg as bmsg
import BF_engine_mysql as bmysql

from dataclasses import dataclass

ALL_TOPICS = (bftop.TOPIC_MYSQL_ALL, bftop.TOPIC_APPLICATION_TODO, bftop.TOPIC_APPLICATION_LISTEN)
TYPE_SENDER, TYPE_RECEIVER, TYPE_BOTH = range(3)

@dataclass
class ParamMsg:
    '''Class for keeping track of an item in inventory.'''
    type_msg: int=TYPE_SENDER
    config_mymsg: str=BF_init._REMOTE

@dataclass
class ReceiverParamMsg(ParamMsg):
    '''Class for keeping track of an item in inventory.'''
    topics: Tuple[str, ...]
    callback: Callable[[str, str], None]
    callback_self: bool=False
    type_msg: int=TYPE_RECEIVER
    config_mymsg: str=BF_init._REMOTE

class NewFactoryRCJK:
    SENDER = None
    def __init__(self, config_mysql: str, conf_mymsg: ParamMsg):
        self._curpath = os.path.dirname(__file__)
        self._bf_log = BF_init.init_log(self._curpath)
        dict_mysql_params, dict_mymsg_params = BF_init.init_params(self._bf_log, self._curpath, config_mysql, conf_mymsg.config_mymsg) 
        self._my_sql = bmysql.Rcjk2MysqlObject(dict_mysql_params,self._bf_log)
        if conf_mymsg.type_msg == TYPE_SENDER:
            self._my_msg = bmsg.CeeMosquittoSender(dict_mymsg_params, self._bf_log)
        elif conf_mymsg.type_msg in (TYPE_RECEIVER, TYPE_BOTH):
            # if callback_self set to True, 
            # add self as first paramter as with the callback
            if conf_mymsg.callback_self:
                conf_mymsg.callback = functools.partial(conf_mymsg.callback, self)
            self._my_msg = bmsg.CeeMosquittoManager(FactoryRCJK.ALL_TOPICS, dict_mymsg_params, self._bf_log, conf_mymsg.callback or self.on_receive)
        else:
            raise ValueError("Bad value to type_msg")    
        
        # set a static sender
        if not FactoryRCJK.SENDER:
            FactoryRCJK.SENDER = functools.partialmethod(self.my_msg.send_msg)


class FactoryRCJK:
    SENDER = None
    def __init__(self, config_mysql: str, config_mymsg: str, 
                    type_msg: int=TYPE_SENDER, callback=None, callback_self: bool=None):
        self._curpath = os.path.dirname(__file__)
        self._bf_log = BF_init.init_log(self._curpath)
        dict_mysql_params, dict_mymsg_params = BF_init.init_params(self._bf_log, self._curpath, config_mysql, config_mymsg) 
        self._my_sql = bmysql.Rcjk2MysqlObject(dict_mysql_params,self._bf_log)
        if type_msg == TYPE_SENDER:
            self._my_msg = bmsg.CeeMosquittoSender(dict_mymsg_params, self._bf_log)
        elif type_msg in (TYPE_RECEIVER, TYPE_BOTH):
            # if callback_self set to True, 
            # add self as first paramter as with the callback
            if callback_self:
                callback = functools.partial(callback, self)
            self._my_msg = bmsg.CeeMosquittoManager(FactoryRCJK.ALL_TOPICS, dict_mymsg_params, self._bf_log, callback or self.on_receive)
        else:
            raise ValueError("Bad value to type_msg")    
        
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