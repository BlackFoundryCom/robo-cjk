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
            # Get system font list
            manager = Cocoa.NSFontManager.sharedFontManager()
            cls._fonts = list(manager.availableFontFamilies())
        return cls._fonts

    @classmethod
    def reload(cls):
        cls._fonts = None
