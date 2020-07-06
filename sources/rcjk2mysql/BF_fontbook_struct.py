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
import copy
import plistlib

from typing import Dict, Union, List, Any, Optional, Iterable, Set, Tuple, Iterator
import BF_author

NONE, CGLYPH, DCOMPONENT, AELEMENT, AELAYER, LAYER, CGLYPH_2_DCOMPONENT, DCOMPONENT_2_AELEMENT = range(8)
XML_CG_DEFAULT = """<?xml version='1.0' encoding='UTF-8'?>
<glyph name="{}" format="2">
  <advance width="1000"/>
  <unicode hex="{}"/>
  <outline>
  </outline>
</glyph>
"""
XML_DEFAULT = """<?xml version='1.0' encoding='UTF-8'?>
<glyph name="{}" format="2">
  <advance width="1000"/>
  <outline>
  </outline>
</glyph>
"""

def name_2_unicode(name: str) -> str:
	"""
	"""
	if not name.startswith("uni"):
		return ""
	try:
		unicode = name[3:]
		int(unicode, 16)
		return unicode
	except:
		return ""

def str_2_bytes(xml: str) -> bytes:
	return bytes(xml.replace("\n",""), encoding='ascii')

class BfFont:
	def __init__(self, name: str, 
					database_name: str="database.json", database_data: str="",
					fontlib_name: str="fontLib.json", fontlib_data: str=""):
		self._name = name
		self._database_name = database_name
		self._database_data = database_data
		self._fontlib_name = fontlib_name
		self._fontlib_data = fontlib_data

		self._changed = True

		self.cglyphs = set() 
		self.dcomponents = set() 
		self.aelements = set()
		self._changed_subitems = False

	@property
	def name(self) -> str:
		return self._name

	# fontlib part
	# ------------------
	@property
	def database_name(self):	
		return self._database_name

	@database_name.setter
	def database_name(self, name: str):
		if self._database_name != name:
			self._database_name = name
			self._changed = True

	@property
	def database_data(self):
		return self._database_data

	@database_data.setter
	def database_data(self, data: str):
		if self._database_data != data:
			self._database_data = data
			self._changed = True

	# fontlib part
	# ------------------
	@property
	def fontlib_name(self):	
		return self._fontlib_name

	@fontlib_name.setter
	def fontlib_name(self, name: str):
		if self._fontlib_name != name:
			self._fontlib_name = name
			self._changed = True

	@property
	def fontlib_data(self):
		return self._fontlib_data

	@fontlib_data.setter
	def fontlib_data(self, data: str):
		if self._fontlib_data != data:
			self._fontlib_data = data
			self._changed = True

	# find a CG etc
	def get_cglyph(self, name: str) -> "BfItem":
		for elem in self.cglyphs:
			if elem.name == name:
				return elem

	def all_cglyphnames(self) -> List[str]:
		return sorted([cg.name for cg in self.cglyphs])

	def all_cglyphnames_changed(self) -> List[str]:
		return sorted([cg.name for cg in self.cglyphs if cg._changed or cg._changed_subitems])
				
	def get_dcomponent(self, name: str) -> "BfItem":
		for elem in self.dcomponents:
			if elem.name == name:
				return elem

	def all_dcomponentnames(self) -> List[str]:
		return sorted([dc.name for dc in self.dcomponents])

	def all_dcomponentnames_changed(self) -> List[str]:
		return sorted([dc.name for dc in self.dcomponents if dc._changed or dc._changed_subitems])

	def get_aelement(self, name: str) -> "BfItem":
		for elem in self.aelements:
			if elem.name == name:
				return elem

	def all_aelementnames(self) -> List[str]:
		return sorted([ae.name for ae in self.aelements])

	def all_aelementnames_changed(self) -> List[str]:
		return sorted([ae.name for ae in self.aelements if ae._changed or ae._changed_subitems])

	def all_aelayernames_changed(self, item_type: int=AELEMENT) -> List[Tuple[str,str]]:
		if item_type == AELEMENT:
			mset = self.aelements
		elif item_type == CGLYPH:
			mset = self.cglyphs
		elif item_type == self.dcomponents:
			mset = self.dcomponents

		return [(item.name, ael.axisname) for item in mset for ael in item.layers if ael._changed]

	def __repr__(self):
		return f"FONT:'{self._name}'- CGlyphs:{self.cglyphs} - DComponents:{self.dcomponents} - AElements:{self.aelements}"

	def remove(self, item: "BfItem") -> Set[str]:
		"""
		remove an item of the font 
		"""
		# which item use it ?
		c_items = set()
		for citem in item._font_contentitems():
			if item in citem._subitems:
				c_items.add(citem.name)
		try:
			items = item._font_items()
			items.remove(item)
		except:
			pass

		return c_items
			
	def _reset_changed(self, val: bool=False):
		self._changed = val
		self._changed_subitems = val

		for cg in self.cglyphs:
			cg._reset_changed(val)

		for dc in self.dcomponents:
			dc._reset_changed(val)

		for ae in self.aelements:
			ae._reset_changed(val)

	def __iter__(self):
		return iter(self.cglyphs)

class BfType:
	def __init__(self, type_id, name_id):
		self.type_id = type_id
		self.name_id = name_id

DBFTYPES = (
			BfType(CGLYPH, "CGlyph"), 
			BfType(DCOMPONENT, "DComponent") , 
			BfType(AELEMENT,"AElement"), 
			BfType(AELAYER, "AELayer"),
			BfType(LAYER, "Layer" )
			)

class BfBaseObj:
	# CONST attrs of class 
	VAL_DTYPES = { t.type_id:t.name_id for t in DBFTYPES }
	STR_DTYPES = { v:k for k, v in VAL_DTYPES.items() }

	__slots__ = ("font", "_name", "_old_name", "_item_type", "_xml", "_changed" ,"_borned", "_erased")
	def __init__(self, font: BfFont, name: str, item_type=None, xml: str=None):
		# base attr
		self.font = font
		self._item_type = item_type
		if self._item_type not in BfItem.VAL_DTYPES: 
			raise ValueError(f"item_init must be  in {BfItem.VAL_DTYPES.values()}")

		# name 
		self._name = name 
		self._old_name = self._name

		# xml 
		self._xml = xml

		# change flags
		self._borned  = True
		self._changed = False
		self._erased = False

	# property of 
	# -------------------------
	@property
	def name(self) -> str:
		return self._name 

	@name.setter
	def name(self, new_name):
		self.rename(new_name)

	@property
	def xml(self) -> str:
		return self._xml 

	@xml.setter
	def xml(self, new_xml):
		self.set_xml(new_xml)

	@property
	def old_name(self) -> str:
		return self._old_name

	@property
	def item_type(self) -> int:
		return self._item_type

	# changed data xml and name
	# -------------------------
	def rename(self, new_name: str):
		# if new_name in self.font:
		# 	pass
		if new_name != self._name:
			self._name = new_name
			self.update_xml(new_name)
			self._changed = True

	def update_xml(self, new_name:str):
		"""
		"""
		self.xml = self.xml.replace(self.name, new_name, 1)


	def set_xml(self, xml: str):
		if xml != self._xml:
			self._xml = xml
			self._changed = True

	# internal changed datas flag 
	# ----------------------------
	def _just_inserted(self):
		self._borned = False

	def _just_updated(self):
		self._changed = False

	def _just_erased(self):
		self._erased = False

	def _reset_changed(self, val: bool=False):
		if not val:
			self._old_name = self._name

		self._changed = val
		self._borned = False
		self._erased = False

	# str representation
	# -------------------
	def __repr__(self) -> str:
		return f"{self.start_repr()}{BfItem.VAL_DTYPES[self._item_type]}:'{self._name}'"

	def __str__(self) -> str:
		return f"<({self.font.name})>" + self.__repr__() 

	def start_repr(self) -> str:
		return "<"

	def end_repr(self) -> str:
		return ">"

		
class BfItem(BfBaseObj):
	# From BfBaseObj -> "font", "_name", "_old_name", "_item_type", "_xml", "_changed"

	__slots__ = BfBaseObj.__slots__ + ("_subitems", "_subitem_type", "_changed_subitems",\
										"_layers", "_changed_layers")

	_XML_SUBITEM_STRING = "robocjk.deepComponents"
	_XML_LAYER_STRING = "robocjk.glyphVariationGlyphs"

	def __init__(self, font: BfFont, name: str, item_type: int=NONE, xml:str=None):
		# base attr
		super().__init__(font, name, item_type, xml)

		# set of subitem as			
		self._subitems = set()
		self._subitem_type = None

		# set of layer 
		self._layers = set()

		# change flags
		self._changed_subitems = False
		self._changed_layers = False

		# add this item to its own set of font
		self._font_items().add(self)

	@property
	def layers(self):
		return self._layers

	# duplication
	# -----------------
	def _duplicate_sets_from(self, src_bfitem: "BfItem"):
		"""
		"""
		# layers
		for lay in src_bfitem.layers:
			if not lay._erased:
				self._set_layer(BfLayer(self, lay.axisname, lay.layername, lay.xml))

		# subitems
		self._subitems = copy.copy(src_bfitem._subitems)

		return self 

	# pure virtual method 
	# ---------------------
	def _font_items(self) -> Iterable:
		"""
		return the Set where this object will be stored
		in the BfFont object
		So if we are an AE, this is the AE set of font
		"""
		raise NotImplementedError()

	def _font_subitems(self) -> Iterable:
		"""
		return the Set where this subobject will be stored 
		in the BfFont object 
		So if we are a CG, this is the DC set of font 
		"""
		raise NotImplementedError()

	def _font_contentitems(self) -> Iterable:
		"""
		return a Set where this object will be used 
		in the BfFont object
		So if we are an AE, this is the DC set of font
		"""
		raise NotImplementedError()

	# str representation
	# -------------------
	def details(self) -> str:
		if self._subitems:
			return f"{', '.join(str(x) for x in self._subitems)}"
		return ""

	def layerdetails(self) -> str:
		return f"{', '.join(str(x) for x in self.layers if not x._erased)}"

	def __repr__(self) -> str:
		string = super().__repr__() 

		if self.layerdetails():
			string += f"+L({self.layerdetails()})"
		
		if self.details():
			string += f"-[{self.details()}]"
		
		return string + super().end_repr()

	# internal changed datas flag 
	# ----------------------------
	def _reset_changed(self, val: bool=False):
		super()._reset_changed(val)

		self._changed_subitems = val
		self._changed_layers = val

		for layer in self.layers:
			layer._reset_changed(val)


	# changed internal data (name, xml or specific)
	# -------------------------------------------
	@staticmethod		
	def str_2_bytes(xml) -> bytes:
		return bytes(xml.replace("\n",""), encoding='ascii')

	@classmethod
	def _get_subitems_from_xml(cls, xml: bytes) -> Set[str]:
		if xml:
			# get lib part 
			try:
				data = plistlib.loads(xml)
				return {item["name"] for item in data[cls._XML_SUBITEM_STRING]} 
			except Exception as e:
				return set()

	@classmethod
	def _get_layers_from_xml_as_dict(cls, xml: bytes) -> Dict[str,str]:
		if xml:
			# get lib part 
			try:
				data = plistlib.loads(xml)
				# for k in data[cls._XML_LAYER_STRING]:
				# 	print(k, "->", data[cls._XML_LAYER_STRING][k])
				# print()
				return {v["layerName"]:k for k, v in data[cls._XML_LAYER_STRING].items()}
			except Exception as e:
				return dict()

	@classmethod
	def _get_layers_from_xml(cls, xml: bytes) -> Set[str]:
		return set(cls._get_layers_from_xml_as_dict(xml))
		# if xml:
		# 	# get lib part 
		# 	try:
		# 		data = plistlib.loads(xml)
		# 		return {item["layerName"] for item in data[cls._XML_LAYER_STRING].values()} 
		# 	except Exception as e:
		# 		return set()

	def set_xml(self, xml: str, update_subitem=True):
		if xml != self._xml:
			self._xml = xml
			self._changed = True
			if update_subitem:
				# get all subitems from xml
				sub = self._get_subitems_from_xml(self.str_2_bytes(xml))
				# an empty set si possible - do nothing
				if sub:
					# del removed subitems
					self._unset_subitems(self.subitems_names() - sub)
					# add new ones 
					self._set_subitems(sub - self.subitems_names())


	# set of names 
	# -----------------
	def subitems_names(self) -> Set:
		return {item.name for item in self._subitems}

	def layers_names(self) -> Set:
		return {layer.layername for layer in self.layers if not layer._erased}

	def axis_names(self) -> Set:
		return {layer.axisname for layer in self.layers  if not layer._erased}

	# subitem set/unset
	# --------------------
	def __extract_names(self, names: Union[str, Iterable[str]]) -> Tuple[str, ...]:
		# only one subitem name
		if isinstance(names, str):
			names = (names,)
		# Or a collection of subitem name
		elif isinstance(names, Iterable):
			# keep only DC name
			names = tuple(filter(lambda x: isinstance(x, str), names))
		else:
			# another type ...
			raise TypeError(f"{names} is not a str or iterable of str")

		return names 

	def _set_subitems(self, names: Union[str, Iterable[str]], delete_all=False):
		try: 
			# delete all ref
			if delete_all:
				self._changed_subitems = True
				del self._subitems

			# run from an iterable of name
			for name in self.__extract_names(names):
				try:
					self._subitems.add(self._font_subitems_name(name))
					self._changed_subitems = True
				except:
					raise ValueError(f"{BfItem.VAL_DTYPES[self._subitem_type]} {name} does not exist in {self.font.name}")
		except:
			raise

	def _unset_subitems(self, names: Union[str, Iterable[str]]):
		try: 
			# run for a name or an iterable of name
			for name in self.__extract_names(names):
				try:
					self._subitems.remove(self._font_subitems_name(name))
					self._changed_subitems = True
				except:
					raise ValueError(f"{BfItem.VAL_DTYPES[self._subitem_type]} {name} does not exist in {self.font.name}")
		except: 
			raise
 
	def _font_subitems_name(self, name:str) -> "BfItem":
		for item in self._font_subitems():
			if item.name == name:
				return item

		raise ValueError(f"'{name}' not found")

	def get_subitem(self, name:str) -> "BfItem":
		for item in self._subitems:
			if item.name == name:
				return item

		raise ValueError(f"'{name}' not found")

	# layer set/unset
	# --------------- 
	# def _unset_aelayer(self, aelayer: "BfLayer"):
	# 	return self._unset_layer(aelayer)

	def _set_layer(self, layer: "BfLayer"):
		self.layers.add(layer)
		self._changed_layers = True

	def _unset_layer(self, layer: "BfLayer") -> "BfLayer":
		if layer in self.layers:
			self.layers.remove(layer)
			self._changed_layers = True
			layer._erased = True

		del layer

	def get_layer_name(self, name:str) -> "BfLayer":
		for item in self.layers:
			if not item._erased and item.layername == name:
				return item

	def get_layer_axis(self, name:str) -> "BfLayer":
		for item in self.layers:
			if not item._erased and item.axisname == name:
				return item

	def __iter__(self):
		return iter(self._subitems)


class BfCGlyph(BfItem):
	__slots__ = BfItem.__slots__ + ("_unicode", "dcomponents")
	_XML_LAYER_STRING = "robocjk.fontVariationGlyphs"
	def __init__(self, font: BfFont, name: str, unicode: str = None, xml: str=None):
		new_xml = xml or XML_CG_DEFAULT.format(name, name_2_unicode(name))
		super().__init__(font, name, CGLYPH, new_xml)
		self._subitem_type = DCOMPONENT
		self._unicode = unicode 

	# Duplicate 
	# -------------------

	def duplicate(self, new_name: str) -> "BfCGlyph":
		"""
		deepcopy of a CG
		"""
		new_unicode = name_2_unicode(new_name)
		new_xml = self.xml.replace(self.name, new_name, 1).replace(self.unicode, new_unicode, 1)
	
		return BfCGlyph(self.font, new_name, new_unicode, new_xml)._duplicate_sets_from(self)

	def update_xml(self, new_name: str):
		"""
		"""
		super().update_xml(new_name)
		new_unicode = name_2_unicode(new_name)
		self.xml = self.xml.replace(self.name, new_name, 1).replace(self.unicode, new_unicode, 1)

	# changed internal data (name, xml or specific)
	# -------------------------------------------
	@property
	def unicode(self) -> str:
		return self._unicode 

	@unicode.setter
	def unicode(self, new_unicode:str):
		self.set_unicode(new_unicode) 

	def set_unicode(self, unicode):
		if self._unicode != unicode:
			self._unicode = unicode
			self._changed = True

	# set / unset subitems
	# ---------------------		
	def set_dcomponents(self, dcompname: Union[str, Iterable[str]]):
		self._set_subitems(dcompname)
	
	def unset_dcomponents(self, dcompname: Union[str, Iterable[str]]):
		self._unset_subitems(dcompname)

	# define subitems sets
	# --------------
	def _font_items(self) -> Iterable:
		return self.font.cglyphs

	def _font_subitems(self) -> Iterable:
		return self.font.dcomponents 

	def _font_contentitems(self) -> Iterable:
		return set()


class BfDComponent(BfItem):
	__slots__ = BfItem.__slots__ + ("aelements", ) 

	def __init__(self, font: BfFont, name: str, xml: str=None):
		new_xml = xml or XML_DEFAULT.format(name)
		super().__init__(font, name, DCOMPONENT, new_xml)
		self._subitem_type = AELEMENT

	# Duplicate 
	# -------------------
	def duplicate(self, new_name: str) -> "BfDComponent":
		"""
		deepcopy of a DC
		"""
		new_xml = self.xml.replace(self.name, new_name, 1)
		return BfDComponent(self.font, new_name, new_xml)._duplicate_sets_from(self) 

	# set / unset subitems
	# ---------------------		
	def set_aelements(self, aelemname: Union[str, Iterable[str]]):
		self._set_subitems(aelemname)
	
	def unset_aelements(self, aelemname: Union[str, Iterable[str]]):
		self._unset_subitems(aelemname)

	# define subitems sets
	# --------------
	def _font_items(self) -> Iterable:
		return self.font.dcomponents 

	def _font_subitems(self) -> Iterable:
		return self.font.aelements 

	def _font_contentitems(self) -> Iterable:
		return self.font.cglyphs

class BfAElement(BfItem):
	__slots__ = BfItem.__slots__ + ("aelayers", ) 
	_XML_SUBITEM_STRING = None

	def __init__(self, font: BfFont, name: str, xml: str=None):
		new_xml = xml or XML_DEFAULT.format(name)
		super().__init__(font, name, AELEMENT, new_xml)
		self._subitem_type = LAYER

	# Duplicate 
	# -------------------
	def duplicate(self, new_name: str) ->"BfAELement":
		"""
		deepcopy of an element
		"""
		new_xml = self.xml.replace(self.name, new_name, 1)
		return BfAElement(self.font, new_name, new_xml)._duplicate_sets_from(self)

	# str representation
	# -------------------
	def details(self) -> str:
		return ""

	def subitems_names(self) -> Set:
		return {item.layername for item in self._subitems if not self._erased}

	@classmethod
	def _get_subitems_from_xml(cls, xml: bytes) -> Set[str]:
		return 	cls._get_layers_from_xml(xml) 

	# ----- Set news layers from xml
	def set_xml(self, xml: str, check_layer=True):
		if xml != self._xml:
			self._xml = xml
			self._changed = True
			if check_layer:
				"""
				"""
				# get all subitems from xml
				subaxis = self._get_layers_from_xml(self.str_2_bytes(xml))
				# an empty set si possible - do nothing
				return subaxis == self.axis_names()

	# define subitems sets
	# --------------
	def _font_items(self) -> Iterable:
		return self.font.aelements 

	def _font_subitems(self) -> Iterable:
		return set()

	def _font_contentitems(self) -> Iterable:
		return self.font.dcomponents


class BfLayer(BfBaseObj):
	__slots__ = BfBaseObj.__slots__ + ("item", "axisname", "layername")

	def __init__(self, item: Union[BfAElement, BfDComponent, BfCGlyph], axisname: str, 
				layername: str, xml: str=None):
		if item.item_type not in (CGLYPH, DCOMPONENT, AELEMENT):
			raise ValueError(f"'{item}' must be an aelement")
		if item not in item._font_items():
			raise ValueError(f"'{item}' is not an aelement of font '{item.font.name}'")
		super().__init__(item.font, axisname, LAYER, xml)
		self.item = item
		self.axisname = axisname
		self.layername = layername
		self.item._set_layer(self)

	def duplicate(self, item) -> "BfLayer":
		self.item._changed_layers = True
		return BfLayer(item, self.axisname, self.layername, self.xml)

	# changed data xml and name
	# -------------------------
	def rename(self, new_name: str):
		# if new_name in self.font:
		# 	pass
		if new_name != self.axisname:
			self.axisname = new_name
			self._changed = True
			self.item._changed_layers = True

	# str representation
	# -------------------
	def __str__(self):
		return self.axisname

	__repr__ = __str__

	# extra not here - So raise
	# ----------------- 
	def _font_items(self) -> Iterable:
		raise NotImplementedError("'_font_items' Not used in BfLayer")

	def _font_subitems(self) -> Iterable:
		raise NotImplementedError("'_font_subitems' Not used in BfLayer")

	def _font_contentitems(self) -> Iterable:
		raise NotImplementedError("'_font_contentitems' Not used in BfLayer")

	@classmethod
	def _get_subitems_from_xml(cls, xml) -> Set[str]:
		raise NotImplementedError("'_get_subitems_from_xml' Not used in BfLayer")

	@classmethod
	def _get_layers_from_xml(cls, xml) -> Set[str]:
		raise NotImplementedError("'_get_subitems_from_xml' Not used in BfLayer")


# class BfAELayer(BfLayer):
# 	def __init__(self, font: BfFont, aelement: BfAElement, axisname: str, 
# 				layername: str, xml: str=None):
# 		if aelement.item_type != AELEMENT:
# 			raise ValueError(f"'{aelement}' must be an aelement")
# 		super().__init__(aelement, axisname, layername, xml)
# 		self._item_type = AELAYER

# 	def duplicate(self, item) -> "BfAELayer":
# 		return BfAELayer(item.font, item, self.axisname, self.layername, self.xml)
