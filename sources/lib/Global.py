"""
Copyright 2019 Black Foundry.

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
import os, Cocoa
from mojo.roboFont import CurrentGlyph

cwd = os.getcwd()
rdir = os.path.abspath(os.path.join(cwd, os.pardir))

class CharactersSets:
    _charactersSets_Dict = None
    _characterSet_list = None

    @classmethod
    def get(cls):
        if cls._charactersSets_Dict is None or cls._characterSet_list is None:
            charactersSetsFolder_path = os.path.join(rdir, "resources/CharactersSets")
            charsetListDir = list(filter(lambda x: x.endswith(".txt"), os.listdir(charactersSetsFolder_path)))
            cls._charactersSets_Dict = {charset[:-4]: open("%s/%s"%(charactersSetsFolder_path, charset), "r", encoding = "UTF-8").read() for charset in charsetListDir}
            cls._characterSet_list = [dict(Get = 0, CharactersSets = charset, Glyphs = len(cls._charactersSets_Dict[charset])) for charset in sorted(cls._charactersSets_Dict.keys())]
            
        return cls._charactersSets_Dict, cls._characterSet_list

class fontsList:
    _fonts = None

    @classmethod
    def get(cls):
        if cls._fonts is None:
            manager = Cocoa.NSFontManager.sharedFontManager()
            cls._fonts = list(manager.availableFontFamilies())
        return cls._fonts

    @classmethod
    def reload(cls):
        cls._fonts = None
