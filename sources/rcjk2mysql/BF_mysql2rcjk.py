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

from rcjk2mysql import BF_author
from rcjk2mysql import BF_init
from rcjk2mysql import BF_engine_mysql as bmy
from rcjk2mysql import BF_fontbook_struct as bfs
from rcjk2mysql import BF_tools as bft



def write_font_to_disk(bf_log, curpath: str, bfont: bfs.BfFont, debug: bool=False):
	""" 
	Write a cjk Font to disk from a BfFont 
	"""

	# Folder and contents
	font_base_folders = (
						(bfs.AELEMENT, "atomicElement", bfont.aelements, True),
						(bfs.DCOMPONENT, "deepComponent", bfont.dcomponents, True), 
						(bfs.CGLYPH, "characterGlyph", bfont.cglyphs, True), 
						)

	bf_log.info(f"debug is {debug}")
	bf_log.info(f"folder of {bfont.name}")
	bf_log.info(f"folder of {bfont}")
	bf_log.info(f"Path to create is '{curpath}' if not exists")
	if not debug:
		bft.check_folder_or_create_it(bf_log, curpath)
	# font path 
	fontpath = os.path.join(curpath, bfont.name+'.rcjk')
	bf_log.info(f"Path to remove '{fontpath}' if exists and recreate it empty")
	if not debug:
		bft.clearout_folder(bf_log, fontpath)

	# fontLib and database
	for name, data in ((bfont.database_name,bfont.database_data), 
						(bfont.fontlib_name, bfont.fontlib_data)):
		if name:
			bf_log.info(f"write {name} - len of data is {len(data)}")
			with open(os.path.join(fontpath, name), "w+") as fp:
				fp.write(data)

	for _, folder, from_datas, subfolder in font_base_folders:
		# create elem folder
		type_folder = os.path.join(fontpath, folder)
		bf_log.info(f"Folder to create is {type_folder}")
		if not debug:
			bft.check_folder_or_create_it(bf_log, type_folder)

		for elem in from_datas:
			file_to_create = os.path.join(type_folder, elem.name+".glif")
			bf_log.info(f"File created is { elem.name+'.glif'}") # file_to_create}")
			if not debug: 
				with open(file_to_create,"w+") as fp:
					try:
						fp.write(elem.xml) 
					except:
						bf_log.warning(f"Trap on elem -> {elem.xml}")

				if subfolder: #  and ftype == bfs.AELEMENT:
					for item in elem.layers:
						if item.xml:
							# create it if not exists
							subtype_folder = os.path.join(type_folder, item.layername)
							bf_log.info(f"folder to produce layers is {item.layername}")
							if not debug:
								bft.check_folder_or_create_it(bf_log, subtype_folder)

							file_to_create = os.path.join(subtype_folder, elem.name+".glif")  
							bf_log.info(f"File created is {os.path.basename(file_to_create)}")
							if not debug:
								with open(file_to_create,"w+") as fp:
									fp.write(item.xml)

	return True


def read_font_from_mysql(bf_log, fontname: str, my_sql:bmy.Rcjk2MysqlObject, 
						filtering = bft.ALL) -> bfs.BfFont:
	"""
	"""
	bf_log.debug(f"READ TO MYSQL init -> Filtering is {filtering}")
	bft._update_filtering(filtering)
	bf_log.debug(f"READ TO MYSQL -> Filtering is {filtering}")
	try:

		bfont = bfs.BfFont(fontname)
		bf_log.info(f"{' FONT SELECT ':-^40s}")
		try:
			res = my_sql.select_font(bfont.name)
			bfont.database_name = res[0][bmy.MYSQL_FONT_DBNAME]
			bfont.database_data = res[0][bmy.MYSQL_FONT_DBDATA]
			bfont.fontlib_name = res[0][bmy.MYSQL_FONT_FLIBNAME]
			bfont.fontlib_data = res[0][bmy.MYSQL_FONT_FLIBDATA]

		except Exception as e:
			return None

		my_sql.sdebug = True 
		bf_log.info(f"SELECT FONTS {res}")


		bf_log.info(f"{' test ':-^40s}")
		selects = (
				  (my_sql.select_cglyphs, bfs.CGLYPH, " SELECT GLYPHS"), 
				  (my_sql.select_all_cg_layers, bfs.LAYER, " SELECT CG LAYERS "), 
				  (my_sql.select_dcomponents, bfs.DCOMPONENT, " SELECT DCOMPONENTS "), 
				  (my_sql.select_all_dc_layers, bfs.LAYER, " SELECT DC LAYERS "), 
				  (my_sql.select_aelements, bfs.AELEMENT, " SELECT AELEMENTS "), 
				  (my_sql.select_all_ae_layers, bfs.LAYER, " SELECT AE LAYERS "), 
				  )

		for func_select, ftype, msg in selects:
			if ftype in filtering:
				bf_log.info(f"{msg:-^60s}")
				res = func_select(fontname)
				bf_log.info(f"Len de res: {len(res)}")
				
				# for each line frim msysql	
				for elem in res:
					name = elem[bmy.MYSQL_DCAE_NAME]
					xml = elem[bmy.MYSQL_DCAE_XML]
					if ftype == bfs.CGLYPH:
						unicode = elem[bmy.MYSQL_CG_UNICODE]
						# bf_log.info(elem[:4])
						bfs.BfCGlyph(bfont, name, unicode, xml)
					elif ftype == bfs.DCOMPONENT:
						bfs.BfDComponent(bfont, name, xml)
					elif ftype == bfs.AELEMENT:
						bfs.BfAElement(bfont, name, xml)
					elif ftype == bfs.LAYER:
						# bf_log.info(f"{elem[:-1]}")
						axisname = elem[bmy.MYSQL_LAY_AXISNAME]
						layername = elem[bmy.MYSQL_LAY_LAYERNAME]
						xml = elem[bmy.MYSQL_LAY_XML]
						if name in bfont.all_aelementnames():
							bfs.BfLayer(bfont.get_aelement(name), axisname, layername, xml)
						elif name in bfont.all_dcomponentnames():
							bfs.BfLayer(bfont.get_dcomponent(name), axisname, layername, xml)
						elif name in bfont.all_cglyphnames():
							bfs.BfLayer(bfont.get_cglyph(name), axisname, layername, xml)

			else:
				bf_log.info(f"{msg:-^60s} EXCLUDED")

		# font is loaded so all changed flags are set to False
		bfont._reset_changed(False)
		return bfont 

	except Exception as e:
		bf_log.error(e)
		raise 

def read_item_from_mysql(bf_log, item: bfs.BfItem,
							my_sql: bmy.Rcjk2MysqlObject) -> bool:
	"""
	"""
	if item.item_type == bfs.CGLYPH:
		# load cglyph
		ret = my_sql.select_cglyph(item.font.name, item.name) 
		if ret:
			item.set_xml(ret[0][bmy.MYSQL_CG_XML], False)
			# load layers
			layers = my_sql.select_cg_layers(item.font.name, item.name)
			for l in layers:
				if l[bmy.MYSQL_LAY_AXISNAME] not in item.axis_names():
					bfs.BfLayer(item.name, l[bmy.MYSQL_LAY_AXISNAME], 
								l[bmy.MYSQL_LAY_LAYERNAME], l[bmy.MYSQL_LAY_XML]) 

			item._reset_changed(False)
			return True
		
	return False