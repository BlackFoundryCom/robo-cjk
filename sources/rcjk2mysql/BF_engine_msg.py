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
import threading
import time
import datetime
import logging

# import redis
import paho.mqtt.client as mqtt

from typing import Callable, Tuple, Any, Dict


import BF_author
import BF_init

bf_log = logging.getLogger(__name__)

"""--------------------------------------------------------------"""

class CeeMsgManager(threading.Thread):
	""" abstract base class of communication manager 
	"""
	__slots__ = "topics", "stop", "id_msg", "d_msgs", "delay_timeout"
	REDIS_COM, POSTGRES_COM, MOSQUITTO_COM = range(3)
	BROADCAST_INFO, BROADCAST_ASK, BROADCAST_RESP=range(3)
	# BROADCAST_INFO, BROADCAST_ASK, BROADCAST_RESP=("BROADCAST_INFO", 
	# 												"BROADCAST_ASK", 
	# 												"BROADCAST_RESP")
	HEADER_DATA_SEP='#'
	HEADER_SEP = '-'
	HEADER_STR = "HEADER=[{{:08}}{0}{{}}{0}{{:08}}{0}{{}}]".format(HEADER_SEP)
	FORMAT_STR = "{}{}DATA=[{{}}]".format(HEADER_STR, HEADER_DATA_SEP)

	GROUPBY=5
	def __init__(self, myname: str, type: int, topics: Tuple, 
					bf_log: logging.Logger, callback_func=None):
		self.topics = topics
		self.stop = False
		self.id_msg = 1
		self.d_msgs = {}
		self.callback_func = callback_func
		self.delay_timeout = 2.0
		self.lock_send = threading.Lock()
		self.msg_send = []
		self.groupby_send = CeeMsgManager.GROUPBY
		self.bf_log = bf_log
		super().__init__(target=self.recv_msg, name=myname)

	def format_msg(self, msg: str, type_of_msg: int, id_from: int=0) -> str:
		""" Format the lessage as: one HEADER and one DATA part 
			HEADER is: 
				id_message, 
				type of message, 
				id_from message if this is a response message
				end delay timestamp to respond
			DATA is free
		"""
		timestamp_limit = int(datetime.datetime.now().timestamp() + self.delay_timeout)
		m = CeeMsgManager.FORMAT_STR.format(self.id_msg, type_of_msg, id_from, 
												timestamp_limit, msg)
		return m

	def recv_msg(self) -> (str, str):
		raise NotImplementedError("Have to redefine 'recv_msg")

	def decode_header_msg(self, header: str) -> (int, int, int, int):
		""" decode header for HEADER=[etc...] """
		header = header.split('=')[1][1:-1]
		return tuple(map(int, header.split(CeeMsgManager.HEADER_SEP))) + (header,)

	def decode_data_msg(self, data: str) -> (str):
		""" decode DATA for DATA=[etc...] """
		return data.split('=')[1][1:-1]

	def process_msg(self, topic: str,  header: str, data: str):
		self.bf_log.debug(f"{header} 'AND' {data}")
		data = self.decode_data_msg(data)
		_, type_of_msg, id_ask, timestamp, _ = self.decode_header_msg(header)
		if type_of_msg == CeeMsgManager.BROADCAST_RESP:
			self.bf_log.debug("BROADCAST RESP")
			if timestamp >= int(datetime.datetime.now().timestamp()):
				self.bf_log.debug("TimeStamp OK")
				older_msg = self.d_msgs[id_ask][0]
				callfunc = self.d_msgs[id_ask][1]
				extraparams = self.d_msgs[id_ask][-1]
				self.bf_log.debug(f"CALLFUNC IS {callfunc.__name__}")
				if callfunc:
					self.bf_log.debug("++ OLDER is {}".format(older_msg))
					self.last_response = data
					self.bf_log.debug("++ DATA is {}".format(data))
					callfunc(topic, self.decode_data_msg(older_msg.split("#")[1]), data, *extraparams)
			else:
				self.bf_log.debug("Delay to receive a response is over .... {}".format(data))
		elif type_of_msg == CeeMsgManager.BROADCAST_INFO:
			if self.callback_func:
				self.callback_func(topic, data)

	def append_msg(self, topic: str, msg: str):
		self.msg_send.append((topic, msg))
		self.id_msg += 1

	def _send_msg(self, topic: str, msg: str):		
		raise NotImplementedError("Have to redefine '_send_msg")

	def send_appended_msg(self):
		""" """
		#no message so, wh can sent msg
		while self.msg_send and self.groupby_send:
			self.groupby_send -= 1
			with self.lock_send:
				ch, msg = self.msg_send.pop(0)
				self._send_msg(ch, msg)
		else:
			self.groupby_send = CeeMsgManager.GROUPBY

	def send_msg(self, topic: str, msg: str):
		self.append_msg(topic, self.format_msg(msg, CeeMsgManager.BROADCAST_INFO))

	def send_msg_ask(self, topic: str, msg: str, callback: Callable=None, *args: Tuple) -> int:
		""" return id of message """
		id = self.id_msg
		smsg = self.format_msg(msg, CeeMsgManager.BROADCAST_ASK)
		self.append_msg(topic, smsg)

		# store msg via id 
		self.d_msgs[id] = (smsg, callback, args)
		return id  

	def send_msg_resp(self, id_from: int, topic: str, msg: str):
		self.append_msg(topic, self.format_msg(msg,CeeMsgManager.BROADCAST_RESP, id_from))

	def terminate(self):
		self.bf_log.info("Manager '{}' stopping .....".format(self.name))
		self.stop = True

class CeeMosquittoManager(CeeMsgManager):
	""" Message manager based on MQTT system"""

	def __init__(self, topics:Tuple, dict_params: Dict, bf_log: logging.Logger, callback_func: Callable=None):
		super().__init__("MosquittoManager", CeeMsgManager.MOSQUITTO_COM, topics, bf_log, callback_func)
		self.client = mqtt.Client(userdata=self)
		self.client.on_connect = CeeMosquittoManager._on_connect
		self.client.on_message = CeeMosquittoManager._on_receive
		if "username" in dict_params and "password" in dict_params:
			dict_params['password'] = BF_init.__decode__(dict_params['password'])
			self.client.username_pw_set(dict_params["username"], dict_params["password"])
		self.client.connect(dict_params["host"], int(dict_params["port"]), 60)
		for topic in self.topics:
			self.client.subscribe(topic)
		self.start()

	@staticmethod
	def _on_connect(client, userdata, flags, rc):
		userdata.bf_log.info("Connected with result code "+str(rc))

	@staticmethod
	def _on_receive(client, userdata, msg):
		message = msg.payload.decode()
		userdata.bf_log.debug("\tMQ GOT: topic:{} - msg:{}".format(msg.topic, message))
		userdata.process_msg(msg.topic, *message.split(CeeMsgManager.HEADER_DATA_SEP))

	def recv_msg(self):
		""" Specific function from mosquitto 
		Here loop method is used """
		self.bf_log.info("\trecv_msg starting ......")
		start = time.time()
		while not self.stop:
			self.client.loop(0.01)	
			if time.time() - start > 1.0:
				self.bf_log.debug("\trecv_msg client loop ......")
				start = time.time()
			time.sleep(0.01)
			self.send_appended_msg()

		self.bf_log.info("Manager '{}' recv ending .....".format(self.name))

	def _send_msg(self, topic: str, msg: str):
		""" specific function from redis subsystem pubsub 
		Here method publish is used 
		"""
		self.bf_log.debug("MQ PUBLISH {}, '{}'".format(topic, msg))
		self.client.publish(topic, msg) # , qos=1)

	def terminate(self):
		self.client.loop_stop()
		super().terminate()

class CeeMosquittoSender(CeeMsgManager):
	""" Message manager based on MQTT system"""

	def __init__(self, dict_params: Dict, bf_log: logging.Logger):
		super().__init__("MosquittoManager", CeeMsgManager.MOSQUITTO_COM, tuple(), bf_log)
		self.client = mqtt.Client(userdata=self)
		if "username" in dict_params and "password" in dict_params:
			dict_params['password'] = BF_init.decode(dict_params['password'])
			self.client.username_pw_set(dict_params["username"], dict_params["password"])
		self.client.connect(dict_params["host"], int(dict_params["port"]), 60)

	def send_msg(self, topic: str, msg: str):
		self._send_msg(topic, self.format_msg(msg, CeeMsgManager.BROADCAST_INFO))

	def _send_msg(self, topic: str, msg: str):
		""" specific function from redis subsystem pubsub 
		Here method publish is used 
		"""
		self.bf_log.debug("MQ PUBLISH {}, '{}'".format(topic, msg))
		self.client.publish(topic, msg) # , qos=1)
