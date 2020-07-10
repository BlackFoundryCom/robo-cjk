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
import logging

from contextlib import contextmanager


from typing import Tuple, List, Dict
# from CollabEExml import cee_persit_sys
import pymysql

import BF_author
import BF_init

import BF_topic_msg as bftop 
import pymysql
import pymysql.err

MY_IP = BF_init._MY_IP
MAX_CHARS = 512

class MySqlConnexionBroken(pymysql.err.InterfaceError):
	pass

class MysqlPersit(object):
	def __init__(self, dict_params: Dict):
		self.params = dict_params
		self._connect()

	def _connect(self):
		""" real connexion to pg server 
			call on __init__ and after a broken connexion """
		# print(self.params)
		self.conn = pymysql.connect(**self.params)
		self.curs = self.conn.cursor()

	def _ping(self):
		return self.conn.ping()

FIRST_LINE, FIRST_COLUMN = 0, 0
DADAISME=True

head_listen = {"create", "drop", "login", "logout", "lock", "unlock", "start"}
item_listen = ("cglyph", "dcomponent", "aelement", "transaction")
head_todo = {"insert", "update", "delete", "rename"}
item_todo = ("font", "cglyph", "dcomponent", "aelement", "layer")

# position of column in each tuple 
MYSQL_FONT_NAME, MYSQL_FONT_DBNAME, MYSQL_FONT_DBDATA,\
					MYSQL_FONT_FLIBNAME, MYSQL_FONT_FLIBDATA= range(1, 6)
MYSQL_CG_NAME, MYSQL_CG_XML, MYSQL_CG_COLOR, MYSQL_CG_UNICODE=range(2, 6)
MYSQL_DCAE_NAME, MYSQL_DCAE_XML, MYSQL_DCAE_COLOR=range(2, 5)
MYSQL_LAY_GLYPHNAME, MYSQL_LAY_AXISNAME, MYSQL_LAY_LAYERNAME, MYSQL_LAY_XML=range(2, 6)

def hex2uni(val: str):
	return  f"\\\\u{val}"

def	hex2uni_v(val: str):
	return f"{chr(int(val, 16))}"

class Rcjk2MysqlObject(MysqlPersit):
	def __init__(self, dict_params: dict, bf_log: logging.Logger=None, 
						username: str=None, debug: bool=False):
		dict_params["autocommit"] = True
		if DADAISME:
			dict_params['password'] = BF_init.decode(dict_params['password'])
		super().__init__(dict_params)
		self.username = username
		self.password = None
		self.debug = debug
		self.checkip_login = True
		self.bf_log = bf_log or logging.getLogger(__name__)
		self.callback_func = None

		# waiting for end of dev of JSON MySQL Functions
		self.dev = False

	def set_callback_msg(self, callback_func):
		if callback_func:
			self.bf_log.info(f"Sender callback is '{callback_func.__name__}'")
		self.callback_func = callback_func

	def send_msg(self, topic, msg):
		if self.callback_func:
			self.callback_func(topic, msg)

	def sdebug(self, debug):
		self.debug = debug

	def __call__(self, username: str, password: str):
		# print(f"{' call ':-^60}")
		self.login(username, password)
		return self

	def __enter__(self):
		self.bf_log.debug(f"{' enter ':-^60}")
		return self 

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.bf_log.debug(f"{' exit ':-^60}")
		self.logout(self.username, self.password)

	# login  parts
	# -----------------------------
	@contextmanager
	def cmlogin(self, username: str, password: str) -> str:
		try:
			if self.login(username, password) > 0:
				yield self

		except:
			self.bf_log.info("logout from ko ...")
			self.logout(username, password)
		else:
			self.bf_log.info("logout from ok ...")
			self.logout(username, password)



	def login(self, username: str, password: str) -> str:
		req = "select rcjk_login('{}','{}','{}')".format(username, password, BF_init._MY_IP)
		ret = self.__execute(req)
		self.bf_log.info(f"login {ret}")
		if ret[FIRST_LINE][FIRST_COLUMN] > 0:
			self.username = username
			self.password = password
		return ret[FIRST_LINE][FIRST_COLUMN]

	def logout(self, username: str, password: str) -> str:
		req = "select rcjk_logout('{}','{}','{}')".format(username, password, BF_init._MY_IP)
		ret = self.__execute(req)
		self.bf_log.info(f"logout {ret}")
		if ret[FIRST_LINE][FIRST_COLUMN] == 1:
			self.username = None
			self.password = None 
		return ret[FIRST_LINE][FIRST_COLUMN]

	def who_login(self, username: str) -> str:
		req = "call rcjk_p_select_whologin('{username}')"
		return self.__execute(req)

	# SELECT FONTS AND ITEMS parts
	# -----------------------------
	def select_fonts(self) -> List:
		req = "call rcjk_p_select_fonts('{}')".format(self.username)
		self.bf_log.info(f"\t\t-> SELECT FONTS")
		return self.__execute(req)

	def select_cglyphs(self, fontname: str, with_xml=True) -> List:
		req = "call rcjk_p_select_cglyphs('{}',{},'{}')".format(fontname, int(with_xml), self.username)
		self.bf_log.info(f"\t\t-> SELECT CGs")
		return self.__execute(req)

	def select_all_cg_layers(self, fontname: str) -> List:
		req = "call rcjk_p_select_all_layers('{}',1,'{}')".format(fontname, self.username)
		ret = self.__execute(req)
		return ret

	# def select_cglyphs_dcomponents(self, fontname: str) -> List:
	# 	req = "call ufo_select_cglyphs_dcomponents('{}', '{}')".format(fontname, self.username)
	# 	return self.__execute(req)

	def select_dcomponents(self, fontname: str, with_xml=True) -> List:
		req = "call rcjk_p_select_dcomponents('{}',{},'{}')".format(fontname, int(with_xml), self.username)
		self.bf_log.info(f"\t\t-> SELECT DCs")
		return self.__execute(req)

	def select_all_dc_layers(self, fontname: str) -> List:
		req = "call rcjk_p_select_all_layers('{}',2,'{}')".format(fontname, self.username)
		ret = self.__execute(req)
		return ret
	
	# def select_dcomponents_aelements(self, fontname: str) -> List:
	# 	req = "call ufo_select_dcomponents_aelements('{}', '{}')".format(fontname, self.username)
	# 	return self.__execute(req)

	def select_aelements(self, fontname: str, with_xml=True) -> List:
		req = "call rcjk_p_select_aelements('{}',{},'{}')".format(fontname, int(with_xml), self.username)
		self.bf_log.info(f"\t\t-> SELECT AEs")
		return self.__execute(req)

	def select_all_ae_layers(self, fontname: str) -> List:
		req = "call rcjk_p_select_all_layers('{}',3,'{}')".format(fontname, self.username)
		ret = self.__execute(req)
		return ret

	# ---- Font part -----
	def select_font(self, fontname: str) -> Tuple:
		req = "call rcjk_p_select_font('{}','{}')".format(fontname, self.username)
		print(f"\t\t-> SELECT FONT {fontname} from {req}")
		return self.__execute(req)

	def insert_font(self, fontname: str, 
						database_name: str=None, database_data: str="{}", 
						fontlib_name: str=None, fontlib_data: str="{}") -> str:
		req = "select rcjk_insert_font('{}','{}',{!a},'{}','{}','{}')".format(fontname, 
																			database_name, database_data,
																			fontlib_name, fontlib_data, 
																			self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> INSERT FONT {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def update_font(self, fontname: str, 
						database_name: str=None,
						fontlib_name: str=None) -> str:
		req = "select rcjk_update_font('{}','{}','{}','{}')".format(fontname, 
																	database_name, 
																	fontlib_name, 
																	self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> UPDATE FONT {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def delete_font(self, fontname: str):
		req = "call rcjk_p_delete_font('{}','{}')".format(fontname, self.username)
		self.bf_log.info(f"\t\t-> DELETE FONT {fontname} from '{req}'")
		ret = self.__execute(req)
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def duplicate_font(self, fontname: str, new_fontname: str):
		req = "call rcjk_p_duplicate_font('{}','{}','{}')".format(fontname, new_fontname, self.username)
		self.bf_log.info(f"\t\t-> DUPLICATE FONT from {fontname} to {new_fontname} '{req}'")
		ret = self.__execute(req)
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	# ----------------- Database.json  part ---------------
	def select_font_database_data(self, fontname:str):
		req = "call rcjk_p_select_font_database_data('{}','{}')".format(fontname, self.username)
		self.bf_log.info(f"\t\t->SELECT FONT database '{req}'")
		ret = self.__execute(req)
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def update_font_database_data(self, fontname:str, database_data: str):
		req = "select rcjk_update_font_database_data('{}','{}','{}')".format(fontname, database_data, self.username)
		self.bf_log.info(f"\t\t-> UPDATE FONT database DATA '{req[:300]}'")
		ret = self.__execute(req)
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def select_font_database_key(self, fontname:str, unicode:str) -> List[str]:
		"""
		key of json
		cf https://stackoverflow.com/questions/35735454/mysql-json-extract-path-expression-error/35735594
		"""
		dbkey = f'"{hex2uni(unicode)}"'
		req = "call rcjk_p_select_font_dbjson_key('{}','$.{}','{}')".format(fontname, dbkey, self.username)
		self.bf_log.info(f"\t\t-> SELECT DBJSON KEY from '{req}'")
		ret = self.__execute(req)
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def insert_font_database_key(self, fontname, unicode:str, dbvalues: tuple) -> Tuple[int]:
		dbkey = f'"{hex2uni(unicode)}"'
		db_newvalues = "".join(hex2uni_v(x) for x in dbvalues)
		req = "select rcjk_insert_font_dbjson_key('{}','$.{}','{}','{}')".format(fontname, dbkey, db_newvalues, self.username)
		self.bf_log.info(f"\t\t-> INSERT DBJSON KEY '{req}'")
		ret = self.__execute(req)
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def update_font_database_key(self, fontname, unicode:str, dbvalues: tuple) -> Tuple[int]:
		dbkey = f'"{hex2uni(unicode)}"'
		db_newvalues = "".join(hex2uni_v(x) for x in dbvalues)
		req = "select rcjk_update_font_dbjson_key('{}','$.{}','{}','{}')".format(fontname, dbkey, db_newvalues, self.username)
		self.bf_log.info(f"\t\t-> UPDATE DBJSON KEY'{req}'")
		ret = self.__execute(req)
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def delete_font_database_key(self, fontname:str, unicode:str):
		dbkey = f'"{hex2uni(unicode)}"'
		req = "select rcjk_delete_font_dbjson_key('{}','$.{}','{}')".format(fontname, dbkey, self.username)
		self.bf_log.info(f"\t\t-> DELETE DBJSON KEY '{req}'")
		ret = self.__execute(req)
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	# ----------------- Fontlib.json  part ---------------
	def select_font_fontlib_data(self, fontname:str) -> str:
		req = "call rcjk_p_select_font_fontlib_data('{}','{}')".format(fontname, self.username)
		self.bf_log.info(f"\t\t-> SELECT FONTLIB DATA '{req}'")
		ret = self.__execute(req)
		return ret[FIRST_LINE][FIRST_COLUMN]

	def update_font_fontlib_data(self, fontname:str, fontlib_data: str):
		req = "select rcjk_update_font_fontlib_data('{}','{}','{}')".format(fontname, fontlib_data, self.username)
		self.bf_log.info(f"\t\t-> UPDATE FONTLIB DATA '{req}'")
		ret = self.__execute(req)
		return ret[FIRST_LINE][FIRST_COLUMN]

	# ----------------- CGlyph part ---------------
	def select_cglyph(self, fontname: str, cglyphname: str)  -> Tuple:
		req = "call rcjk_p_select_glyph('{}','{}', 1, '{}')".format(fontname, cglyphname, self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> SELECT CGLYPH {ret}")
		return ret

	def insert_cglyph(self, fontname: str, cglyphname: str, 
										xml: str, colorglyph: str, 
										unicode: str, old_name:str = None):

		# rename part 
		if old_name and old_name != cglyphname:
			ret = self.rename_cglyph(fontname, cglyphname, old_name)

		req = "select rcjk_insert_glyph('{}','{}',1,{!a},'{}','{}','{}')".format(fontname, cglyphname, 
																				xml, colorglyph, 
																				unicode,  self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> INSERT CGLYPH {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN] 

	def update_cglyph(self, fontname: str, cglyphname: str, xml: str, colorglyph: str, 
								unicode: str, old_name:str = None) -> str:
		# rename part 
		if old_name and old_name != cglyphname:
			ret = self.rename_cglyph(fontname, cglyphname, old_name)

		req = "select rcjk_update_glyph('{}','{}',1,{!a},'{}','{}','{}')".format(fontname, cglyphname, 
																				xml, colorglyph,
																				unicode, self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> UPDATE CGLYPH {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	# def set_cglyph_dcomponent(self, fontname: str, 
	# 								cglyphname: str, dcomponentname:str) -> List:
	# 	req = "select rcjk_set_cglyph_dcomponent('{}','{}','{}','{}')".format(fontname, cglyphname, 
	# 																dcomponentname, self.username)
	# 	ret = self.__execute(req)
	# 	self.bf_log.info(f"\t\t-> SET CGLYPH 2 DCOMPONENT {ret}")
	# 	return ret

	# def unset_cglyph_dcomponent(self, fontname: str, 
	# 							cglyphname: str, dcomponentname:str) -> List:
	# 	req = "select rcjk_unset_cglyph_dcomponent('{}','{}','{}','{}')".format(fontname, cglyphname, 
	# 																	dcomponentname, self.username)
	# 	ret = self.__execute(req)
	# 	self.bf_log.info(f"\t\t-> UNSET CGLYPH 2 DCOMPONENT {ret}")
	# 	return ret

	# def unset_cglyph_alls(self, fontname: str, 
	# 							cglyphname: str) -> List:
	# 	req = "select rcjk_unset_cglyph_dcomponent('{}','{}','{}','{}')".format(fontname, cglyphname, 
	# 																				None, self.username)
	# 	ret = self.__execute(req) 
	# 	self.bf_log.info(f"\t\t-> UNSET CGLYPH 2 DCOMPONENT ALL {ret}")
	# 	return ret

	#
	def delete_cglyph(self, fontname: str, name: str):
		req = "call rcjk_p_delete_cglyph('{}','{}', 1, '{}')".format(fontname, name, self.username)
		self.bf_log.info(f"\t\t-> DELETE CGLYPH {fontname}.{name} from '{req}'")
		ret = self.__execute(req)
		return ret and ret[FIRST_LINE][FIRST_COLUMN] 

	# ----------------- DComponent part ---------------
	def select_dcomponent(self, fontname: str, dcomponentname:str) -> List:
		req = "call rcjk_p_select_glyph('{}','{}',2,'{}')".format(fontname, dcomponentname, self.username)
		ret = self.__execute(req)
		return ret

	def insert_dcomponent(self, fontname: str, dcomponentname:str, xml: str, colorglyph: str,
							old_name:str = None) -> List:

		# rename part 
		if old_name and old_name != dcomponentname:
			ret = self.rename_dcomponent(fontname, dcomponentname, old_name)

		req = "select rcjk_insert_glyph('{}','{}',2,{!a},'{}',NULL,'{}')".format(fontname, dcomponentname, 
																			xml, colorglyph,
																			self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> INSERT DCOMPONENT {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def update_dcomponent(self, fontname: str, dcomponentname:str, xml: str, colorglyph: str,
							old_name:str = None) -> List:

		# rename part 
		if old_name and old_name != dcomponentname:
			ret = self.rename_dcomponent(fontname, dcomponentname, old_name)

		req = "select rcjk_update_glyph('{}','{}',2,{!a},'{}',NULL,'{}')".format(fontname, dcomponentname, 
																			xml, colorglyph, 
																			self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> UPDATE DCOMPONENT {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	# def set_dcomponent_aelement(self, fontname: str, 
	# 						dcomponentname:str, aelementname: str) -> List:
	# 	req = "select rcjk_set_dcomponent_aelement('{}','{}','{}','{}')".format(fontname, dcomponentname, 
	# 																		aelementname, self.username)
	# 	ret = self.__execute(req)
	# 	self.bf_log.info(f"\t\t-> SET DCOMPONENT 2 AELEMENT {ret}")
	# 	return ret

	# def unset_dcomponent_aelement(self, fontname: str, 
	# 						dcomponentname:str, aelementname: str) -> List:
	# 	req = "select rcjk_unset_dcomponent_aelement('{}','{}','{}','{}')".format(fontname, dcomponentname, 
	# 																		aelementname, self.username)
	# 	ret = self.__execute(req)
	# 	self.bf_log.info(f"\t\t-> UNSET DCOMPONENT 2 AELEMENT {ret}")
	# 	return ret

	# def unset_dcomponent_alls(self, fontname: str, 
	# 						dcomponentname:str) -> List:
	# 	req = "select rcjk_unset_dcomponent_aelement('{}','{}','{}','{}')".format(fontname, dcomponentname, 
	# 																		None, self.username)
	# 	ret = self.__execute(req)
	# 	self.bf_log.info(f"\t\t-> UNSET DCOMPONENT 2 AELEMENT ALL {ret}")
	# 	return ret

	def delete_dcomponent(self, fontname: str, name: str):
		req = "call rcjk_p_delete_glyph('{}','{}',2,'{}')".format(fontname, name, self.username)
		self.bf_log.info(f"\t\t-> DELETE DCOMPO {fontname}.{name} from '{req}'")
		ret = self.__execute(req)
		return ret and ret[FIRST_LINE][FIRST_COLUMN]
		
	# ----------------- AELEMENT part ---------------
	def select_aelement(self, fontname: str, aelementname:str) -> List:
		req = "call rcjk_p_select_glyph('{}','{}', 3, '{}')".format(fontname, aelementname, self.username)
		ret = self.__execute(req)
		return ret

	def insert_aelement(self, fontname: str, aelementname:str, xml: str, colorglyph: str,
											old_name:str = None) -> int:
		# rename part 
		if old_name and old_name != aelementname:
			ret = self.rename_aelement(fontname, aelementname, old_name)

		req = "select rcjk_insert_glyph('{}','{}',3,{!a},'{}',NULL,'{}')".format(fontname,aelementname, 
																			xml, colorglyph, 
																			self.username)
		ret = self.__execute(req)		
		self.bf_log.info(f"\t\t-> INSERT AELEMENT {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def update_aelement(self, fontname: str, 
							aelementname:str, 
							xml: str,
							colorglyph: str, 
							old_name:str = None
							) -> int:
		# rename part 
		if old_name and old_name != aelementname:
			ret = self.rename_aelement(fontname, aelementname, old_name)

		req = "select rcjk_update_glyph('{}','{}',3, {!a},'{}',NULL,'{}')".format(fontname, aelementname, 
																			xml, colorglyph, 
																			self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> UPDATE AELEMENT {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def delete_aelement(self, fontname: str, name: str):
		req = "call rcjk_p_delete_glyph('{}','{}',3,'{}')".format(fontname, name, self.username)
		self.bf_log.info(f"\t\t-> DELETE AELEMENT AND ITS AELAYERS {fontname}.{name} from '{req}'")
		ret = self.__execute(req)
		return ret and ret[FIRST_LINE][FIRST_COLUMN] 

	# ----------------- AELEMENT part ---------------
	def insert_cg_layer(self, fontname: str, 
							axisname:str, 
							cgname: str,
							layername: str, 
							xml: str
							) -> List:

		req = "select rcjk_insert_layer('{}','{}',1,'{}','{}',{!a},'{}')".format(fontname, cgname,
																			axisname, layername, 
																			xml, self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> INSERT CG LAYER {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def insert_dc_layer(self, fontname: str, 
							axisname:str, 
							dcname: str,
							layername: str, 
							xml: str
							) -> List:

		req = "select rcjk_insert_layer('{}','{}',2,'{}','{}',{!a},'{}')".format(fontname, dcname,
																			axisname, layername, 
																			xml, self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> INSERT DC LAYER {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def insert_ae_layer(self, fontname: str, 
							axisname:str, 
							aename: str,
							layername: str, 
							xml: str
							) -> List:

		req = "select rcjk_insert_layer('{}','{}',3,'{}','{}',{!a},'{}')".format(fontname, aename,
																			axisname, layername, 
																			xml, self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> INSERT AE LAYER {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def update_cg_layer(self, fontname: str, 
							axisname:str, 
							cgname: str,
							layername: str, 
							xml: str) -> List:

		req = "select rcjk_update_layer('{}','{}',1,'{}','{}',{!a},'{}')".format(fontname, cgname, 
																			axisname, layername, 
																			xml, self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> UPDATE CG LAYER {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def update_dc_layer(self, fontname: str, 
							axisname:str, 
							dcname: str,
							layername: str, 
							xml: str) -> List:

		req = "select rcjk_update_layer('{}','{}',2,'{}','{}',{!a},'{}')".format(fontname, dcname, 
																			axisname, layername, 
																			xml, self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> UPDATE DC LAYER {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def update_ae_layer(self, fontname: str, 
							axisname:str, 
							aename: str,
							layername: str, 
							xml: str) -> List:

		req = "select rcjk_update_layer('{}','{}',3,'{}','{}',{!a},'{}')".format(fontname, aename, 
																			axisname, layername, 
																			xml, self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> UPDATE AE LAYER {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def select_cg_layers(self, fontname: str, cgname: str) -> List:
		req = "call rcjk_p_select_layers('{}','{}',1,'{}')".format(fontname, cgname, self.username)
		ret = self.__execute(req)
		return ret

	def select_dc_layers(self, fontname: str, dcname: str) -> List:
		req = "call rcjk_p_select_layers('{}','{}',2,'{}')".format(fontname, dcname, self.username)
		ret = self.__execute(req)
		return ret
	
	def select_ae_layers(self, fontname: str, aename: str) -> List:
		req = "call rcjk_p_select_layers('{}','{}',3,'{}')".format(fontname, aename, self.username)
		ret = self.__execute(req)
		return ret

	# delete part 
	def delete_cg_layers(self, fontname: str, cgname:str) -> List:
		req = "call rcjk_p_delete_layers('{}','{}',1,'{}')".format(fontname, cgname, self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> DELETE ALL LAYERS OF A CG {ret}")
		return ret

	def delete_dc_layers(self, fontname: str, dcname:str) -> List:
		req = "call rcjk_p_delete_layers('{}','{}',2,'{}')".format(fontname, dcname, self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> DELETE ALL LAYERS OF A DC {ret}")
		return ret
	
	def delete_ae_layers(self, fontname: str, aename:str) -> List:
		req = "call rcjk_p_delete_layers('{}','{}',3,'{}')".format(fontname, aename, self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> DELETE ALL LAYERS OF AN AE {ret}")
		return ret

	# ----- LOCK PART -----
	# ---------------------
	# LOCK CGLYPH 	
	# -------------
	def lock_cglyph(self, fontname: str, cglyphname: str) -> str:
		req = "select rcjk_lock_glyph('{}','{}',1,'{}')".format(fontname, cglyphname, 
    								        						 self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> LOCK CGLYPH {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def unlock_cglyph(self, fontname: str, cglyphname: str) -> str:
		req = "select rcjk_unlock_glyph('{}','{}',1,'{}')".format(fontname, 
							        		    				       cglyphname, 
    								        	    				   self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> UNLOCK CGLYPH {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def who_locked_cglyph(self, fontname: str, cglyphname: str) -> str:
		req = "select rcjk_wholocked_glyph('{}','{}',1)".format(fontname, 
							        		    			cglyphname)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> WHO LOCKED CGLYPH {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	# LOCK DCOMPONENT 	
	# -------------
	def lock_dcomponent(self, fontname: str, dcomponentname: str) -> str:
		req = "select rcjk_lock_glyph('{}','{}',2,'{}')".format(fontname, 
							        							dcomponentname, 
    								        					self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> LOCK DCOMPONENT {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def unlock_dcomponent(self, fontname: str, dcomponentname: str) -> str:
		req = "select rcjk_unlock_glyph('{}','{}',2,'{}')".format(fontname, 
							        		    				dcomponentname, 
    								        	    			self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> UNLOCK DCOMPONENT {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def who_locked_dcomponent(self, fontname: str, dcomponentname: str) -> str:
		req = "select rcjk_wholocked_glyph('{}','{}',2)".format(fontname, 
							        		    		         dcomponentname)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> WHO LOCKED DCOMPONENT {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	# LOCK AELEMENT 	
	# -------------
	def lock_aelement(self, fontname: str, aelementname: str) -> str:
		req = "select rcjk_lock_glyph('{}','{}',3,'{}')".format(fontname, 
							        							aelementname, 
    								        					self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> LOCK AELEMENT {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def unlock_aelement(self, fontname: str, aelementname: str) -> str:
		req = "select rcjk_unlock_glyph('{}','{}',3,'{}')".format(fontname, 
							        		    				aelementname, 
    								        	    			self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> UNLOCK AELEMENT {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def who_locked_aelement(self, fontname: str, aelementname: str) -> str:
		req = "select rcjk_wholocked_glyph('{}','{}', 3)".format(fontname, 
							        		    				aelementname)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> WHO LOCKED AELEMENT {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def select_locked_cglyphs(self, fontname: str) -> List:
		req = "call rcjk_p_select_locked_glyphs('{}',1,'{}')".format(fontname, self.username)
		return self.__execute(req)

	def select_locked_dcomponents(self, fontname: str) -> List:
		req = "call rcjk_p_select_locked_glyphs('{}',2,'{}')".format(fontname, self.username)
		return self.__execute(req)

	def select_locked_aelements(self, fontname: str) -> List:
		req = "call rcjk_p_select_locked_glyphs('{}',3,'{}')".format(fontname, self.username)
		return self.__execute(req)

	# ----- RENAME PART -----
	# ---------------------

	def rename_cglyph(self, fontname: str, name: str, old_name:str):
		req = "select rcjk_rename_glyph('{}','{}',1,'{}','{}')".format(fontname, name, old_name, self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> RENAME CG {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def rename_dcomponent(self, fontname: str, name: str, old_name:str):
		req = "select rcjk_rename_glyph('{}','{}',2,'{}','{}')".format(fontname, name, old_name, self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> RENAME DC {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	def rename_aelement(self, fontname: str, name: str, old_name:str):
		req = "select rcjk_rename_glyph('{}','{}',3,'{}','{}')".format(fontname, name, old_name, self.username)
		ret = self.__execute(req)
		self.bf_log.info(f"\t\t-> RENAME AE {ret}")
		return ret and ret[FIRST_LINE][FIRST_COLUMN]

	# def rename_aelayer(self, fontname: str, name: str, old_name:str):
	# 	req = "select rcjk_rename_aelayer('{}','{}','{}','{}')".format(fontname, name, old_name, self.username)
	# 	ret = self.__execute(req)
	# 	self.bf_log.info(f"\t\t-> RENAME AEL {ret}")
	# 	return ret

	# --- other ------
	def select_current_database(self) -> str:
		return self.__execute("select database()")[FIRST_LINE][FIRST_COLUMN]

	def select_current_user(self) -> str:
		return self.__execute("select current_user()")[FIRST_LINE][FIRST_COLUMN]

	@contextmanager
	def on_transaction(self, name: str="trans1"):
		try:
			self.bf_log.info(f"\t\t +++++ START TRANSACTION +++++")
			# self.curs.execute("START TRANSACTION")
			self.conn.begin()
			yield self
		except:
			self.bf_log.info(f"\t\t +++++ ROLLBACK +++++")
			return self.conn.rollback()
		else:
			self.bf_log.info(f"\t\t +++++ COMMIT +++++")
			return self.conn.commit()
		

	def validate(self):
		self.bf_log.info(f"\t\t +++++ VALIDATE (COMMIT) +++++")
		return self.conn.commit()

	def invalidate(self):
		self.bf_log.info(f"\t\t +++++ INVALIDATE (ROLLBACK) +++++")
		return self.conn.rollback()

	def decompose_order_sql(self, req):
		"""
		req is always as "call/select ufo_order_itemtype(value1, value2, *args)
		order in head_listen or head_todo
		itemtype in item_todo
		""" 
		try:
			if "current_user" in req or "start" in req or "database" in req:
				return None, None

			if "(" in req:
				order, params = req[:-1].split("(")
				l = order.split(' ')[1].split('_')
				if 'p' in l:
					l.remove('p')
			
				if len(l) == 1:
					return order.split(' ')
				elif len(l) >= 2 and l[1] in head_listen:
					return l[1], params.split(',') 
				elif len(l) >= 3 and l[1] in head_todo:	
					return l[1], l[2], params.split(',')
				return None, None
			else:
				return order.split(' ')
		except:
			raise ValueError("MySQL command impossible to analyze")

	def prepare_msg_and_send(self, req):
		"""
		"""
		self.send_msg(bftop.TOPIC_MYSQL_ALL, req)
		try:
			order, *args = self.decompose_order_sql(req)
			if order:
				if order in head_listen:
					self.send_msg(bftop.TOPIC_APPLICATION_LISTEN, req)
				elif order in head_todo:
					self.bf_log.debug(f"args[0] is {args[0]}")
					self.bf_log.debug(f"args[1] is {args[1][0]}-{args[1][1]}")
					self.send_msg(bftop.TOPIC_APPLICATION_TODO, f"RELOAD font:{args[1][0]}, {args[0]}:{args[1][1]}")
		except Exception as e:
			self.bf_log.warning(f"{type(e)} - {str(e)}")

	def rename_none_values(self, req):
		rep1 = req.replace("'None'", "NULL")
		return rep1.replace("None", "NULL")
			
	# ---- do the job ------
	def __execute(self, req: str):
		req = self.rename_none_values(req)
		if self.username:
			user = self.username
		else:
			user = "NO LOGIN"
		msg = f"USER:{user:16s} - IP:{BF_init._MY_IP:15s} - MSG:{req[:MAX_CHARS]}"
		self.bf_log.debug(msg)
		try:
			self.prepare_msg_and_send(req[:MAX_CHARS])
		except:
			pass
		if not self.debug:
			try:
				self.curs.execute(req)
				if req.startswith("call") and self.curs.description:
					self.bf_log.debug(f"columns of call are:{[d[0] for d in self.curs.description]}")
			except MySqlConnexionBroken as e:
				self._ping()
				self.curs.execute(req)
			except Exception as e:
				self.bf_log.error(f"type of except {type(e)} -> {str(e)}")
				raise
			finally:				
				return self.curs.fetchall()
		else:
			self.bf_log.debug(f"Req is '{req}'")
			return req
			
	def __execute_4docs(self, req: str):
		if not self.debug:
			try:
				self.curs.execute(req)
				if req.startswith("call"):
					res_col = f"columns of call are:{[d[0] for d in self.curs.description]}"
					self.bf_log.info(res_col)

			except:
				pass