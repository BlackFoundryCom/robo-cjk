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
import random
from typing import Tuple, Optional, Union, Any
import copy
import json

import plistlib

import BF_author
import BF_init
import BF_engine_mysql
import BF_fontbook_struct as bfs
import BF_tools as bft


glyphname = '<glyph name="'
len_g = len(glyphname)
unicodename = '<unicode hex="'
len_u = len(unicodename)

# contourname = '<contour>'
# len_c = len(contourname)
# end_contourname = '</contour>'

def find_value(bf_log, string: str, substring: str, 
				len_sub: int, substring_end: str='"') -> str:
	"""
	"""
	try:
		bf_log.debug(f"+++ 0 - '{string}'")
		pos = string.index(substring)
		string = string[pos+len_sub:]
		bf_log.debug(f"+++ 1 - '{string}'")
		pos_end = string.index(substring_end)
		bf_log.debug(f"+++ 2 '{string[:pos_end]}")
		return string[:pos_end]
	except:
		bf_log.warning(f"ERROR on {string} for search {substring}")
		return None

def get_datas_from_file(bf_log, ftype: int, filename: str) -> dict:
	"""
	"""
	with open(filename, "r") as fp:
		xml_datas = fp.read()

	# bf_log.info(f"xml_datas -> {xml_datas}")
	name = find_value(bf_log, xml_datas, xml_datas[0:1], 1, '<outline')

	# dict to store datas
	d = { "name":"", "items":set() ,"axis_layer":dict()}

	# name is for each item
	try:
		d["name"] = find_value(bf_log, name, glyphname, len_g)
	except:
		pass
	
	byte_datas = bfs.str_2_bytes(xml_datas)
	# CGLYPH datas 
	if ftype == bfs.CGLYPH:
		d["unicode"] = ""
		try: 
			d["unicode"] = find_value(bf_log, name, unicodename, len_u)
			d["items"] = bfs.BfCGlyph._get_subitems_from_xml(byte_datas)
			d["axis_layer"] = bfs.BfCGlyph._get_layers_from_xml_as_dict(byte_datas)
		except:
			bf_log.warning(f"CG:'{filename}'' read data Ko")

	# DCOMP datas 
	elif ftype == bfs.DCOMPONENT:
		try:
			d["items"] = bfs.BfDComponent._get_subitems_from_xml(byte_datas)
			d["axis_layer"] = bfs.BfDComponent._get_layers_from_xml_as_dict(byte_datas)
		except:
			bf_log.warning(f"DC:'{filename}'' read data Ko")

	# AELEM datas 
	elif ftype == bfs.AELEMENT:
		try:
			d["axis_layer"] = bfs.BfAElement._get_layers_from_xml_as_dict(byte_datas)
		except:
			bf_log.warning(f"AE:'{filename}'' read data Ko")

	# AELAYER nothing to search

	return d, xml_datas 

def read_font_from_disk(bf_log, curpath: str, fontname: str) -> bfs.BfFont:
	""" 
	Read a cjk Font from disk and create a BfFont 
	"""

	# Folder and contents
	font_base_folders = (
						(bfs.AELEMENT, "atomicElement", True),
						(bfs.DCOMPONENT, "deepComponent", True), 
						(bfs.CGLYPH, "characterGlyph", True), 
						)

	
	# BfFont object 
	font = bfs.BfFont(fontname)

	# and json file
	for curfile in os.listdir(curpath):
		if curfile == font.database_name:
			bf_log.info(f"'{curfile}' loading in font")
			with open(os.path.join(curpath, font.database_name), "r") as fp:
				font.database_data = fp.read().replace("\\u","\\\\u")
			# with open(os.path.join(curpath, font.database_name), encoding='utf-8') as fp:
			# 	data = json.load(fp)
			# 	font.database_data = data

		elif curfile == font.fontlib_name:
			bf_log.info(f"'{curfile}' loading in font")
			with open(os.path.join(curpath, font.fontlib_name), encoding='utf-8') as fp:
				font.fontlib_data = fp.read()

	# all content
	bf_log.info(f"folder of {fontname} -> {curpath}")
	for ftype, folder, subfolder in font_base_folders:
		wfolder = os.path.join(curpath, folder)
		bf_log.info(f"Working in '{wfolder}'")

		# subfolder for AELAYER of AELEMENT
		if subfolder:
			layerfolder = []

		# read file before directory (with teh sorted and key on isfile, so file first)
		for file in sorted(os.listdir(wfolder), key=os.path.isfile):

			# read only .glih
			if file.endswith(".glif"):				

				# get datas and append the BfFont Object
				datas, xml_datas = get_datas_from_file(bf_log, ftype, os.path.join(wfolder, file))

				#add BfCGlyph 
				if ftype == bfs.CGLYPH:
					bf_log.info(f"{' CGLYPH ':-^60}")
					c = bfs.BfCGlyph(font, datas["name"], datas["unicode"], xml_datas)
					try:
						c.set_dcomponents(datas["items"])
					except:
						bf_log.error(str(e))
						bf_log.error(datas)
						bf_log.error(c)
					for layername, axis in datas['axis_layer'].items():
						# bfs.BfAELayer(font, ae, axis, layername)
						bfs.BfLayer(c, axis, layername)

				#add BfDComponent 
				elif ftype == bfs.DCOMPONENT:
					bf_log.info(f"{' DCOMPONENT ':-^60}")
					d = bfs.BfDComponent(font, datas["name"], xml_datas)
					try:
						d.set_aelements(datas["items"])
					except Exception as e:
						bf_log.error(str(e))
						bf_log.error(datas)
						bf_log.error(d)

				#add BfAElement 
				elif ftype == bfs.AELEMENT:
					bf_log.info(f"{' AELEMENT ':-^60}")
					ae = bfs.BfAElement(font, datas["name"], xml_datas)
					bf_log.info(f"axis_layer -> {datas['axis_layer']}") 
					for layername, axis in datas['axis_layer'].items():
						# bfs.BfAELayer(font, ae, axis, layername)
						bfs.BfLayer(ae, axis, layername)
					# bf_log.debug(x.xml[:100])
				bf_log.debug(f"open file '{file}'")
			else:
				if subfolder:
					dir_path = os.path.join(wfolder, file)
					if not file.startswith(".") and os.path.isdir(dir_path):
						layerfolder.append(dir_path)

		#add AELAYER of AELEMENT 
		if subfolder:
			for layer_file in layerfolder:
				print(layer_file)
				for filename in os.listdir(layer_file):
					if not filename.startswith(".") and filename.endswith(".glif"):
						# parse each aelement of layer folder
						layername = os.path.basename(layer_file)
						datas, xml_datas = get_datas_from_file(bf_log, bfs.AELAYER, os.path.join(layer_file, filename))
						bf_log.info(f"{' AELAYER ':-^60}")
						bf_log.info(f"open file '{filename}' from '{layername}'")
						# bf_log.info(xml_datas)
						try:
							if ftype == bfs.CGLYPH:
								item = font.get_cglyph(datas["name"])
							elif ftype == bfs.AELEMENT:
								item = font.get_aelement(datas["name"])
							elif ftype == bfs.DCOMPONENT:
								item = font.get_dcomponent(datas["name"])

							layer = item.get_layer_name(layername)
							layer.set_xml(xml_datas)
						except:
							pass
	return font

def insert_newfont_to_mysql(bf_log, bfont:bfs.BfFont, my_sql:BF_engine_mysql.Rcjk2MysqlObject):
	"""
	"""
	try:
		# FONT part 
		bf_log.info("------------------- FONT with JSON files --------------------------")
		try:
			ret = my_sql.insert_font(bfont.name, bfont.database_name, bfont.database_data,
								bfont.fontlib_name, bfont.fontlib_data)
			if not ret:
				bf_log.error(f"Font already exists ...")
				return
		except Exception as e:
			bf_log.error(f"Create a font error -> {type(e)} on {str(e)}")
			return 
		else:	
			bf_log.debug(f"Insert font '{bfont.name}'")

		bf_log.info("--------------------------- AE -----------------------------------")
		# AELEMENT part 
		for ae in bfont.aelements:
			my_sql.insert_aelement(bfont.name, ae.name, ae.xml, ae.old_name)
			# ADD AELAYER
			for ael in ae.layers:
				# bf_log.info(f"aelname: {ael.axisname}, lib: {ael.xml[:100]}")
				my_sql.insert_ae_layer(bfont.name, ael.axisname, ae.name, ael.layername, ael.xml)

		# DC part
		bf_log.info("-------------------------- DC ------------------------------------")
		for dc in bfont.dcomponents:
			# LINK BETWEEN DCOMPONENT AND AELEMENT*
			my_sql.insert_dcomponent(bfont.name, dc.name, dc.xml, dc.old_name)
			for ael in dc.layers:
				my_sql.insert_dc_layer(bfont.name, ael.axisname, dc.name, ael.layername, ael.xml)

			# for ae in dc:
			# 	my_sql.set_dcomponent_aelement(bfont.name, dc.name, ae.name)

		# CGLYPH part
		bf_log.info("-------------------------- CG -----------------------------------")
		for cg in bfont.cglyphs:
			# LINK BETWEEN CGLYPH AND DCOMPONENT
			my_sql.insert_cglyph(bfont.name, cg.name, cg.xml, cg.unicode, cg.old_name)
			bf_log.info("-------------------------- CG LAYERS -----------------------------------")
			for ael in cg.layers:
				bf_log.info(f"{ ael.axisname:-^80s}")
				my_sql.insert_cg_layer(bfont.name, ael.axisname, cg.name, ael.layername, ael.xml)
			# for dc in cg:
			# 	my_sql.set_cglyph_dcomponent(bfont.name, cg.name, dc.name)

	except Exception as e:
		bf_log.warning(e)
	else:
		bfont._reset_changed(False)
		

def list_locked_from_mysql(bf_log, fontname: str, my_sql:BF_engine_mysql.Rcjk2MysqlObject) -> [tuple, tuple, tuple]:
	"""
	Return list of locked CG, locked DC and locked AE
	"""
	return ("CG", my_sql.select_locked_cglyphs(fontname)),\
				("DC", my_sql.select_locked_dcomponents(fontname)),\
				("AE", my_sql.select_locked_aelements(fontname))

def delete_font_from_mysql(bf_log, fontname: str, my_sql:BF_engine_mysql.Rcjk2MysqlObject):
	"""
	"""
	try:
		# login 
		my_sql.delete_font(fontname)
	except:
		pass


def update_font_to_mysql(bf_log, bfont: bfs.BfFont, my_sql:BF_engine_mysql.Rcjk2MysqlObject, filtering = bft.ALL):
	"""
	"""
	bft._update_filtering(filtering)
	bf_log.debug(f"WRITE TO MYSQL -> Filtering is {filtering}")
	try:
		# login 
		bf_log.info("---------------------------------------------------------------")
		insert_update = (
				  (my_sql.update_cglyph, bfs.CGLYPH, " UPDATE CGLYPHS", my_sql.update_cg_layer), 
				  (my_sql.update_dcomponent, bfs.DCOMPONENT, " UPDATE DCOMPONENTS ", my_sql.update_dc_layer), 
				  (my_sql.update_aelement, bfs.AELEMENT, " UPDATE AELEMENTS ", my_sql.update_ae_layer), 
				#   (my_sql.set_cglyph_dcomponent, bfs.CGLYPH_2_DCOMPONENT, " UPDATE CGLYPH_2_DCOMPONENTS ", my_sql.unset_cglyph_alls), 
				#   (my_sql.set_dcomponent_aelement, bfs.DCOMPONENT_2_AELEMENT, " UPDATE DCOMPONENTS_2_AELEMENTS ", my_sql.unset_dcomponent_alls), 
				  )

		bf_log.info(f"{' FONT UPDATE ':-^40s}")
		my_sql.update_font(bfont.name)

		for func, ftype, msg, layer_func in insert_update:
			if ftype in filtering:
				bf_log.info(f"{msg:-^60s}")
				if ftype == bfs.CGLYPH:
					for cg in bfont.cglyphs:
						if cg._changed:
							bf_log.info(f"CG {cg.name} changed ....")
							res = func(bfont.name, cg.name, cg.xml, cg.unicode, cg.old_name)
							bf_log.info(res)
							for ael in cg.layers:
								if ael._changed:
									bf_log.info(f"AEL {ael.axisname} changed ....")
									res = layer_func(bfont.name, ael.axisname, cg.name, ael.layername, ael.xml)
									bf_log.info(res)

				elif ftype == bfs.DCOMPONENT:
					for dc in bfont.dcomponents:
						if dc._changed:
							bf_log.info(f"DC {dc.name} changed ....")
							res = func(bfont.name, dc.name, dc.xml, dc.old_name)
							bf_log.info(res)
							for ael in dc.layers:
								if ael._changed:
									bf_log.info(f"AEL {ael.axisname} changed ....")
									res = layer_func(bfont.name, ael.axisname, dc.name, ael.layername, ael.xml)
									bf_log.info(res)

				elif ftype == bfs.AELEMENT:
					for ae in bfont.aelements:
						if ae._changed:
							bf_log.info(f"AE {ae.name} changed ....")
							res = func(bfont.name, ae.name, ae.xml, ae.old_name)
							bf_log.info(res)
							for ael in ae.layers:
								if ael._changed:
									bf_log.info(f"AEL {ael.axisname} changed ....")
									res = layer_func(bfont.name, ael.axisname, ae.name, ael.layername, ael.xml)
									bf_log.info(res)

				# elif ftype == bfs.CGLYPH_2_DCOMPONENT:
				# 	for cg in bfont.cglyphs:
				# 		if cg._changed_subitems:
				# 			bf_log.info(f"CG {cg.name} subitem changed ....")
				# 			if init_func:
				# 				init_func(bfont.name, cg.name)
				# 			for dc in cg:
				# 				res = func(bfont.name, cg.name, dc.name) 
				# 				bf_log.info(res)

				# elif ftype == bfs.DCOMPONENT_2_AELEMENT:
				# 	for dc in bfont.dcomponents:
				# 		if dc._changed_subitems:
				# 			bf_log.info(f"DC {dc.name} subitem changed ....")
				# 			if init_func:
				# 				init_func(bfont.name, dc.name)
				# 			for ae in dc:
				# 				res = func(bfont.name, dc.name, ae.name)
				# 				bf_log.info(res)
			else:
				bf_log.info(f"{msg:-^60s} EXCLUDED")
		
		# rest all changes
		bfont._reset_changed(False)

	except Exception as e:
		bf_log.warning(e)

def duplicate_item_to_mysql(bf_log, item: bfs.BfItem, new_name: str, 
								my_sql: BF_engine_mysql.Rcjk2MysqlObject) -> Optional[bfs.BfItem]:
	"""
	"""
	# duplicate 
	new_item = item.duplicate(new_name) 

	# create a new one 
	if item.item_type == bfs.CGLYPH:
		if my_sql.lock_cglyph(item.font.name, item.name) == my_sql.username:
			ret = my_sql.insert_cglyph(new_item.font.name, new_item.name, new_item.xml, new_item.unicode)
			for ael in new_item.layers:
				my_sql.insert_gc_layer(new_item.font.name, ael.axisname, new_item.name, ael.layername, ael.xml)
	elif item.item_type == bfs.DCOMPONENT:
		if my_sql.lock_dcomponent(item.font.name, item.name) == my_sql.username:
			ret = my_sql.insert_dcomponent(new_item.font.name, new_item.name, new_item.xml)
			for ael in new_item.layers:
				my_sql.insert_dc_layer(new_item.font.name, ael.axisname, new_item.name, ael.layername, ael.xml)
	elif item.item_type == bfs.AELEMENT:
		if my_sql.lock_aelement(item.font.name, item.name) == my_sql.username:
			ret = my_sql.insert_aelement(new_item.font.name, new_item.name, new_item.xml)
			for ael in new_item.layers:
				my_sql.insert_ae_layer(new_item.font.name, ael.axisname, new_item.name, ael.layername, ael.xml)

	# reset internal changed flag 
	if ret:
		new_item._reset_changed(False)
		return new_item

	# Duplicate is down Ko so remove this new_item
	item.font.remove(new_item)

def rename_item_to_mysql(bf_log, item: bfs.BfItem, new_name: str, 
								my_sql: BF_engine_mysql.Rcjk2MysqlObject) -> bfs.BfItem:
	"""
	"""
	# rename item 
	if item.item_type == bfs.CGLYPH:
		if my_sql.lock_cglyph(item.font.name, item.name) == my_sql.username:
			ret = my_sql.rename_cglyph(item.font.name, new_name, item.name)
	elif item.item_type == bfs.DCOMPONENT:
		if my_sql.lock_dcomponent(item.font.name, item.name) == my_sql.username:
			ret = my_sql.rename_dcomponent(item.font.name, new_name, item.name)
	elif item.item_type == bfs.AELEMENT:
		if my_sql.lock_aelement(item.font.name, item.name) == my_sql.username:
			ret = my_sql.rename_aelement(item.font.name, new_name, item.name)

	# reset internal changed flag 
	if ret:
		item.rename(new_name)
		item.update_xml(new_name)
		# item._reset_name()
		item._reset_changed(False)
	
	return item


def new_item_to_mysql(bf_log, item_type: int, # one value from bfs.CGLYPH, bfs.DCOMPONENT, bfs.AELEMENT]
						bfont: bfs.BfFont, 
						new_name: str, 
						my_sql: BF_engine_mysql.Rcjk2MysqlObject) -> Optional[bfs.BfItem]:
	"""
	"""
	# get all items already locked 
	if item_type == bfs.CGLYPH:
		new_item = bfs.BfCGlyph(bfont, new_name)
		ret = my_sql.insert_cglyph(new_item.font.name, new_item.name, new_item.xml, new_item.unicode)
		userlock = my_sql.lock_cglyph(new_item.font.name, new_item.name)

	elif item_type == bfs.DCOMPONENT:
		new_item = bfs.BfDComponent(bfont, new_name)
		ret = my_sql.insert_dcomponent(new_item.font.name, new_item.name, new_item.xml)
		userlock = my_sql.lock_dcomponent(new_item.font.name, new_item.name)

	elif item_type == bfs.AELEMENT:
		new_item = bfs.BfAElement(bfont, new_name)
		ret = my_sql.insert_aelement(new_item.font.name, new_item.name, new_item.xml)
		userlock = my_sql.lock_aelement(new_item.font.name, new_item.name)

	# reset internal changed flag 
	if ret and userlock == my_sql.username:
		new_item._reset_changed(False)
		return new_item 
	
	# New Item is dwon so remove this item
	bfont.remove(new_item)

	return None

def remove_item_to_mysql(bf_log, item: bfs.BfItem,
								my_sql: BF_engine_mysql.Rcjk2MysqlObject) -> Tuple[str]:
	"""
	"""
	if item.item_type == bfs.CGLYPH:
		if my_sql.lock_cglyph(item.font.name, item.name) == my_sql.username:
			my_sql.delete_cglyph(item.bfont.name, item.name) 
	elif item.item_type == bfs.DCOMPONENT:
		if my_sql.lock_dcomponent(item.font.name, item.name) == my_sql.username:
			my_sql.delete_dcomponent(item.font.name, item.name)
	elif item.item_type == bfs.AELEMENT:
		if my_sql.lock_aelement(item.font.name, item.name) == my_sql.username:
			my_sql.delete_aelement(item.font.name, item.name)

	# reset internal changed flag
	content_items = item.font.remove(item)
	del item
	return content_items

INSERT, DELETE=range(2)
def update_item_to_mysql(bf_log, item: bfs.BfItem,
							my_sql: BF_engine_mysql.Rcjk2MysqlObject):
	"""
	"""
	d_update_orders_sql = {
						bfs.CGLYPH: 	(my_sql.insert_cg_layer, my_sql.delete_cg_layers),
						bfs.DCOMPONENT: (my_sql.insert_dc_layer, my_sql.delete_dc_layers),
						bfs.AELEMENT:	(my_sql.insert_ae_layer, my_sql.delete_ae_layers)
					      }
	if item._changed:
		if item.item_type == bfs.CGLYPH:
			my_sql.update_cglyph(item.font.name, item.name, item.xml, item.unicode, item.old_name)			
		elif item.item_type == bfs.DCOMPONENT:
			my_sql.update_dcomponent(item.font.name, item.name, item.xml, item.old_name)
		elif item.item_type == bfs.AELEMENT:
			my_sql.update_aelement(item.font.name, item.name, item.xml, item.old_name)
		
	# all layers of this item
	with my_sql.on_transaction("test"): 
	# if True:
		d_update_orders_sql[item.item_type][DELETE](item.font.name, item.name)
		for layer in item.layers:
			d_update_orders_sql[item.item_type][INSERT](item.font.name, layer.axisname, item.name, layer.layername, layer.xml)

	# reset internal changed flag
	item._reset_changed(False)
