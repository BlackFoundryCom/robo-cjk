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
from fontTools.ufoLib.glifLib import readGlyphFromString
from xml.etree import ElementTree as ET
from mojo.roboFont import *
import json
import os
import copy
import time

from imp import reload
from utils import decorators, files, locker
# reload(decorators)
# reload(locker)
gitCoverage = decorators.gitCoverage
from utils import interpolation
# reload(interpolation)
from models import atomicElement, deepComponent, characterGlyph
# reload(atomicElement)
# reload(deepComponent)
# reload(characterGlyph)

# from rcjk2mysql import BF_mysql2rcjk as BF_mysql2rcjk
# from rcjk2mysql import BF_fontbook_struct as bfs
# from rcjk2mysql import BF_rcjk2mysql
import threading
import queue

from vanilla.dialogs import message
from PyObjCTools.AppHelper import callAfter

# class glyphsTypes:

#     atomicElement = 'aelements'
#     deepComponent = 'dcomponents'
#     characterGlyph = 'cglyphs'

#     @classmethod
#     def mysql(cls, type):
#         return getattr(cls, type)

#     @classmethod
#     def bfs(cls, type):
#         if type == 'atomicElement':
#             return bfs.AELEMENT
#         if type == 'deepComponent':
#             return bfs.DCOMPONENT
#         if type == 'characterGlyph':
#             return bfs.CGLYPH

#     @classmethod
#     def robocjk(cls, type):
#         for x in vars(cls):
#             if getattr(cls, x) == type:
#                 return x 

class Font():


    def __init__(self):
        self.mysql = False
        self.mysql = False
        self._glyphs = {}
        self._RFont = {}
        self.dataBase = {}
        self.deepComponents2Chars = {}

        self._atomicElementSet = []
        self._deepComponentSet = []
        self._characterGlyphSet = []

    def getLocker(self, args):
        self.locker = locker.Locker(*args)

    def _init_for_git(self, fontPath, gitUserName, gitPassword, gitHostLocker, gitHostLockerPassword, privateLocker, robocjkVersion):
        self.admin = False
        if gitHostLockerPassword:
            self.admin = True
        self.fontPath = fontPath


        # self.locker = locker.Locker(fontPath, gitUserName, gitPassword, gitHostLocker, gitHostLockerPassword, privateLocker)
        callAfter(self.getLocker, (fontPath, gitUserName, gitPassword, gitHostLocker, gitHostLockerPassword, privateLocker))
        name = os.path.split(fontPath)[1].split('.')[0]
        self.fontName = name
        self._RFont = NewFont(
            familyName=name, 
            styleName='Regular', 
            showUI = False
            )
        fontFilePath = '{}.ufo'.format(os.path.join(fontPath, name))
        self._RFont.save(fontFilePath)
        fontFilePath = '{}.ufo'.format(os.path.join(fontPath, "%sfull"%name))
        self._fullRFont = NewFont(
            familyName="%s-full"%self.fontName, 
            styleName='Regular', 
            showUI = False
            )
        self._fullRFont.save(fontFilePath)

        self._glyphs = {}
        self._fullGlyphs = {}
        self.fontVariations = []
        if 'fontLib.json' in os.listdir(self.fontPath):
            libPath = os.path.join(self.fontPath, 'fontLib.json')
            with open(libPath, 'r') as file:
                self.fontLib = json.load(file)
            self.fontLib['robocjk.version'] = robocjkVersion
            self._initFontLib(self.fontLib)
            self.fontVariations = self.fontLib.get('robocjk.fontVariations', [])

        self.defaultGlyphWidth = self._RFont.lib.get("rorocjk.defaultGlyphWidth", 1000)

        # staticCharacterGlyphSet = list(self.staticCharacterGlyphSet())
        # thirdl = len(staticCharacterGlyphSet)//3
        # l1 = staticCharacterGlyphSet[0:thirdl]
        # l2 = staticCharacterGlyphSet[thirdl:thirdl*2]
        # l3 = staticCharacterGlyphSet[thirdl*2:]
        # print(len(staticCharacterGlyphSet), len(l1), len(l2), len(l3), len(l1)+len(l2)+len(l3))
        self.queue = queue.Queue()
        threading.Thread(target=self.queueGetGlyphsAEDC, args = (self.queue), daemon=True).start()
        self.queue.put([(self.staticAtomicElementSet(), "atomicElement"), (self.staticDeepComponentSet(), "deepComponent")])
        # self.queue2 = queue.Queue()
        # threading.Thread(target=self.queueGetGlyphsAEDC, args = (self.queue2), daemon=True).start()
        # self.queue2.put((self.staticDeepComponentSet(), "deepComponent"))

        self.queue3 = queue.Queue()
        threading.Thread(target=self.queueGetGlyphs, args = (self.queue3, "characterGlyph"), daemon=True).start()
        self.queue3.put(self.staticCharacterGlyphSet())

        # self.queue4 = queue.Queue()
        # threading.Thread(target=self.queueGetGlyphs, args = (self.queue4, "characterGlyph"), daemon=True).start()
        # self.queue4.put(l2)

        # self.queue5 = queue.Queue()
        # threading.Thread(target=self.queueGetGlyphs, args = (self.queue5, "characterGlyph"), daemon=True).start()
        # self.queue5.put(l3)

        self.createLayersFromVariationAxis()
        # self.save()

    def queueGetGlyphsAEDC(self, queue):
        glyphsets = queue.get()
        for item in glyphsets:
            glyphset, item_type = item
            for name in glyphset:
                self.getGlyph(name, type = item_type, font = self._fullRFont)
        queue.task_done()

    def queueGetGlyphs(self, queue, item_type):
        glyphset = queue.get()
        for name in glyphset:
            self.getGlyph(name, type = item_type, font = self._fullRFont)
        queue.task_done()

    def _init_for_mysql(self, font, client, username, hiddenSavePath):
        self.mysql = True
        self.username = username
        self.client = client
        self.fontName = font["data"]["name"]
        self._RFont = NewFont(
            familyName=self.fontName, 
            styleName='Regular', 
            showUI = False
            )
        savePath = os.path.join(hiddenSavePath, f"{self.fontName}.ufo")
        files.makepath(savePath)
        self._RFont.save(savePath)
        self._mysqlInsertedGlyph = {}
        self.uid = font["data"]["uid"]
        self._fullRFont = self._RFont
        self.fontLib = font["data"]["fontlib"]
        # self.dataBase = font["data"]["glyphs_composition"]
        self.dataBase = self.client.glyphs_composition_get(self.uid)["data"]
        # print(self.dataBase)
        self._initFontLib(self.fontLib, self._RFont)
        self.fontVariations = self.fontLib.get('robocjk.fontVariations', [])
        self.defaultGlyphWidth = self._RFont.lib.get("rorocjk.defaultGlyphWidth", 1000)

    def clearRFont(self):
        # for k, v in copy.deepcopy(self._RFont.lib.asDict()).items():
        #     self.fontLib[k] = v
        self._RFont = NewFont(
                familyName=self.fontName, 
                styleName='Regular', 
                showUI = False,
                )
        if self.mysql:
            pass
            # if self.fontpath is not None:
            #     fontFilePath = files.makepath(os.path.join(self.fontpath, "%s.ufo"%fontName))
        else:
            fontFilePath = '{}.ufo'.format(os.path.join(self.fontPath, self.fontName))
        self._RFont.save(fontFilePath)
        self._initFontLib(self.fontLib, self._RFont)

    def loadTeam(self):
        return self.fontLib.get('teamManager', {})

    def saveTeam(self, teamDict):
        self.fontLib['teamManager'] = teamDict
        print("save team", teamDict)
        if self.mysql:
            pass
            # self.mysql.update_font_fontlib_data(self.fontName, json.dumps(self.fontLib))
        else:
            pass
        
    # def insertFullRFont(self):
    #     print(self.atomicElementSet[1])
    #     print(self.deepComponentSet[1])
    #     print(self.characterGlyphSet[1])

    def _initFontLib(self, lib, font = None):
        for k, v in lib.items():
            if font is None:
                self._RFont.lib[k] = v
                self._fullRFont.lib[k] = v
            else:
                font.lib[k] = v

    def selectDatabaseKey(self, key):
        if not self.mysql:
            char = chr(int(key, 16))
            return "".join(self.dataBase[char])
        else:
            pass
            # return self.mysql.select_font_database_key(self.fontName, key)

    def updateDatabaseKey(self, key, values):
        char = chr(int(key, 16))
        if not self.mysql:
            self.dataBase[char] = values
        else:
            response = self.client.glyphs_composition_get(self.uid)
            if response['status'] == 200:
                self.dataBase = self.client.glyphs_composition_get(self.uid)["data"]
                self.dataBase[char] = values
                self.client.glyphs_composition_update(self.uid, self.dataBase)
            else:
                print(response)

    def get(self, name, font = None):
        if font is None:
            font = self._fullRFont
        try:
            return self._glyphs[font[name]]
        except:
            if self.mysql:
                self.getmySQLGlyph(name)
            else:
                self.getGlyph(name, font = font)
            return self._glyphs[font[name]]
        # if self.mysql:
        #     return self._glyphs[self._fullRFont[name]]
        # else:
        #     return self[name]

    # def loadMysqlDataBase(self):
    #     self.dataBase = json.loads(self._BFont.database_data)

    def saveFontlib(self):
        if self.mysql:
            self.client.font_update(self.uid, fontlib=self.fontLib)

    # def saveDatabase(self):
    #     pass

    def lockGlyph(self, glyph):
        if not self.mysql:
            locked, alreadyLocked = self.locker.lock(glyph)
            return locked, alreadyLocked
        else:
            glyphtype = self._findGlyphTypeFromName(glyph.name)
            if glyphtype == "atomicElement":
                user = self.client.atomic_element_get(self.uid, glyph.name, return_layers=False, return_related=False)["data"]["locked_by_user"]
            elif glyphtype == "deepComponent":
                user = self.client.deep_component_get(self.uid, glyph.name, return_layers=False, return_related=False)["data"]["locked_by_user"]
            else:
                user = self.client.character_glyph_get(self.uid, glyph.name, return_layers=False, return_related=False)["data"]["locked_by_user"]
            if user:
                return user["username"] == self.username, None
            else:
                if glyphtype == "atomicElement":
                    user = self.client.atomic_element_lock(self.uid, glyph.name)
                elif glyphtype == "deepComponent":
                    user = self.client.deep_component_lock(self.uid, glyph.name)
                else:
                    user = self.client.character_glyph_lock(self.uid, glyph.name)
                return 1, None

    def _findGlyphTypeFromName(self, name):
        if name in self.staticAtomicElementSet():
            return "atomicElement"
        elif name in self.staticDeepComponentSet():
            return "deepComponent"
        else:
            return "characterGlyph"

    def batchLockGlyphs(self, glyphs:list = []):
        if not self.mysql:
            return self.locker.batchLock(glyphs)
        else:
            set_glyphs = set(glyphs)
            AE = set_glyphs & self.staticAtomicElementSet()
            DC = set_glyphs & self.staticDeepComponentSet()
            CG = set_glyphs & self.staticCharacterGlyphSet()
            self.client.glif_lock(self.uid, atomic_elements = list(AE), deep_components = list(DC), character_glyphs = list(CG))
            return True


    def batchUnlockGlyphs(self, glyphs:list = []):
        if not self.mysql:
            return self.locker.batchUnlock(glyphs)
        else:
            print("Unlocked glyphs:", " ".join(glyphs))
            set_glyphs = set(glyphs)
            AE = set_glyphs & self.staticAtomicElementSet()
            DC = set_glyphs & self.staticDeepComponentSet()
            CG = set_glyphs & self.staticCharacterGlyphSet()
            self.client.glif_unlock(self.uid, atomic_elements = list(AE), deep_components = list(DC), character_glyphs = list(CG))
            return True

    def glyphLockedBy(self, glyph):
        if not self.mysql:
            return self.locker.potentiallyOutdatedLockingUser(glyph)
        else:
            if glyph.type == "atomicElement":
                user = self.client.atomic_element_get(self.uid, glyph.name, return_layers=False, return_related=False)["data"]["locked_by_user"]
            elif glyph.type == "deepComponent":
                user = self.client.deep_component_get(self.uid, glyph.name, return_layers=False, return_related=False)["data"]["locked_by_user"]
            else:
                user = self.client.character_glyph_get(self.uid, glyph.name, return_layers=False, return_related=False)["data"]["locked_by_user"]
            if user:
                return user["username"]

    def exportDataBase(self):
        if not self.mysql:
            with open(os.path.join(self.fontPath, "database.json"), 'w', encoding="utf-8") as file:
                file.write(json.dumps(self.dataBase))
        else:
            # self.client.font_update(self.uid, glyphs_composition=self.dataBase)
            pass
            self.client.glyphs_composition_update(self.uid, self.dataBase)
            # self.client.glyphs_composition_update(self.uid, self.dataBase)

    def currentUserLockedGlyphs(self):
        if not self.mysql:
            return self.locker.myLockedGlyphs
        else:
            lockedGlyph = []
            for items in self.client.glif_list(self.uid, is_locked_by_current_user=True)["data"].values():
                lockedGlyph.extend([x["name"] for x in items])
            return lockedGlyph
            # cglyphs = [x[0] for x in self.mysql.select_locked_cglyphs(self.fontName) if x[1] == self.mysqlUserName]
            # dcomponents = [x[0] for x in self.mysql.select_locked_dcomponents(self.fontName) if x[1] == self.mysqlUserName]
            # aelements = [x[0] for x in self.mysql.select_locked_aelements(self.fontName) if x[1] == self.mysqlUserName]
            # return cglyphs + dcomponents + aelements

    def removeLockerFiles(self, glyphsnames:list = []):
        if not self.mysql:
            if not isinstance(glyphsnames, list):
                glyphsnames = list(glyphsnames)
            self.locker.removeFiles(glyphsnames)

    # def loadCharacterGlyph(self, glyphName):
    #     bfitem = self._BFont.get_cglyph(glyphName)
    #     BF_mysql2rcjk.read_item_from_mysql(self.bf_log, bfitem, self.mysql)

    @property
    def lockerUserName(self):
        if not self.mysql:
            return self.locker._username
        else:
            return self.username
            # return self.mysqlUserName

    def changeGlyphState(self, state="", glyph=None):
        if not self.mysql: return
        if glyph is None: return
        if not state: return
        if glyph.type == "atomicElement":
            self.client.atomic_element_update_status(self.uid, glyph.name, state)
        elif glyph.type == "deepComponent":
            self.client.deep_component_update_status(self.uid, glyph.name, state)
        else:
            self.client.character_glyph_update_status(self.uid, glyph.name, state)

    def _findGlyphType(self, glyphname):
        if glyphname in self.characterGlyphSet:
            return "cglyphs"

        elif glyphname in self.atomicElementSet:
            return "aelements"

        elif glyphname in self.deepComponentSet:
            return "dcomponents"

    def getGlyphFromLayer(self, name, layerName):
        try:
            return self._glyphs[self._RFont.getLayer(layerName)[name]]
        except:
            if self.mysql:
                pass
                # self.getmySQLGlyph(name)
            else:
                self.getGlyph(name, font = self._fullRFont)
                self.getGlyph(name)
            return self._glyphs[self._RFont.getLayer(layerName)[name]]

    def __iter__(self):
        for name in self._RFont.keys():
            yield self[name]

    def __getitem__(self, name):
        if not isinstance(name, str):
            name = name["name"]
        try:
            return self._glyphs[self._RFont[name]]
        except:
            if self.mysql:
                pass
                self.getmySQLGlyph(name)
            else:
                self.getGlyph(name, font = self._fullRFont)
                self.getGlyph(name)
            return self._glyphs[self._RFont[name]]

    def __len__(self):
        return len(self._RFont.keys())

    def __contains__(self, name):
        return name in self._RFont

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<RCJKFontObject '%s',  path='%s', %s atomicElements, %s deepComponents, %s characterGlyphs>"%(self.fontPath.split("/")[-1], self.fontPath, len(self.atomicElementSet), len(self.deepComponentSet), len(self.characterGlyphSet))

    def keys(self):
        return self._RFont.keys()

    def glyphSet(self):
        return self.atomicElementSet + self.deepComponentSet + self.characterGlyphSet

    def shallowDocument(self):
        return self._RFont.shallowDocument()

    @property
    def _fontLayers(self):
        return [l.name for l in self._RFont.layers if l.name != 'foreground']

    @property
    def currentState(self):
        AE_empty = 0
        AE_maxName = ""
        AE_maxNumber = 0
        AE_averageVariation = []
        for n in self.atomicElementSet:
            glyph = self.get(n)
            if len(glyph._glyphVariations) > AE_maxNumber:
                AE_maxNumber = len(glyph._glyphVariations)
                AE_maxName = n
            if glyph._glyphVariations:
                AE_averageVariation.append(len(glyph._glyphVariations))
            if not len(glyph):
                AE_empty += 1
        DC_empty = 0
        DC_designed = 0
        DC_designedUnique = set()
        DC_designedVariant = 0
        DC_maxName = ""
        DC_maxNumber = 0
        DC_averageVariation = []
        for n in self.deepComponentSet:
            glyph = self.get(n)
            if not glyph._deepComponents:
                DC_empty += 1
            else:
                DC_designedVariant += 1
                DC_designedUnique.add(n.split("_")[1])
            if len(glyph._glyphVariations) > DC_maxNumber:
                DC_maxNumber = len(glyph.glyphVariations)
                DC_maxName = n
            if glyph._glyphVariations:
                DC_averageVariation.append(len(glyph._glyphVariations))

        CG_withDC = 0
        CG_withOutlines = 0
        CG_mixed = 0
        CG_withVariation = 0
        CG_withoutVariation = 0
        CG_withVariationanddeepcomponents = 0
        CG_empty = 0
        for n in self.characterGlyphSet:
            glyph = self.get(n)
            if glyph._deepComponents:
                CG_withDC += 1
            if len(glyph):
                CG_withOutlines += 1
            if glyph._deepComponents and len(glyph):
                CG_mixed += 1
            if glyph._glyphVariations:
                CG_withVariation += 1
            if glyph._glyphVariations and glyph._deepComponents and not len(glyph):
                CG_withVariationanddeepcomponents += 1
            else:
                CG_withoutVariation += 1
            if not glyph._deepComponents and not len(glyph):
                CG_empty += 1
        string = f"""
        Current state of {self.fontName}:\n
          • AtomicElements :
            \t - {AE_empty} are empty,
            \t - maximum of glyph variation: '{AE_maxName}' with {AE_maxNumber} axis,
            \t - average of glyph variation: {round(sum(AE_averageVariation)/len(AE_averageVariation), 2)} axis,
            \t - total: {len(self.atomicElementSet)} atomicElements,\n
          • DeepComponents :
            \t - {len(DC_designedUnique)} unique designed,
            \t - {DC_designedVariant} designed (with variants),
            \t - {DC_empty} are empty,
            \t - maximum of glyph variation: '{DC_maxName}' with {DC_maxNumber} axis,
            \t - average of glyph variation: {round(sum(DC_averageVariation)/len(DC_averageVariation), 2)} axis,
            \t - total: {len(self.deepComponentSet)} deepComponents,\n
          • CharacterGlyphs :
            \t - {CG_withDC} with deep components,
            \t - {CG_withOutlines} with outlines,
            \t - {CG_mixed} are mixed,
            \t - {CG_withVariation} with glyph variation,
            \t - {CG_withVariationanddeepcomponents} with glyph variation and deep components,
            \t - {CG_withoutVariation} without glyph variation,
            \t - {CG_empty} are empty,
            \t - total: {len(self.characterGlyphSet)} characterGlyphs,\n
        """
        return string

    def createLayersFromVariationAxis(self):
        if not self.fontVariations: return
        for variation in self.fontVariations:
            if variation not in [x.name for x in self._RFont.layers]:
                self._RFont.newLayer(variation)

    def getmySQLGlyph(self, name, font = None):      
        prev = self._mysqlInsertedGlyph.get(name, None)
        if prev is not None:
            now = time.time()
            if now - prev < 30:
                return

        if font is None:
            font = self._RFont

        if not isinstance(name, str):
            name = name["name"]

        if name in self.staticAtomicElementSet():
            gtype = "AE"
        elif name in self.staticDeepComponentSet():
            gtype = "DC"
        else:
            gtype = "CG"

        made_of_aes = []
        made_of_dcs = []

        start = time.time()
        if gtype == "AE":
            glyph = atomicElement.AtomicElement(name)
            BGlyph = self.client.atomic_element_get(self.uid, name)["data"]
        elif gtype == "DC":
            glyph = deepComponent.DeepComponent(name)
            BGlyph = self.client.deep_component_get(self.uid, name)["data"]
            made_of_aes = BGlyph["made_of"]
        elif gtype == "CG":
            glyph = characterGlyph.CharacterGlyph(name)
            BGlyph = self.client.character_glyph_get(self.uid, name)["data"]
            made_of_dcs = BGlyph["made_of"]
            made_of_aes = [x for dc in made_of_dcs for x in dc["made_of"]]

        stop = time.time()
        print("download glyphs:", stop-start, 'seconds to download %s'%name)

        start = time.time()
        self.insertmysqlGlyph(glyph, name, BGlyph, font, gtype)
        for ae in made_of_aes:
            # print(ae)
            glyph = atomicElement.AtomicElement(ae["name"])
            self.insertmysqlGlyph(glyph, ae["name"], ae, font, gtype)
        for dc in made_of_dcs:
            glyph = deepComponent.DeepComponent(dc["name"])
            self.insertmysqlGlyph(glyph, dc["name"], dc, font, gtype)
        stop = time.time()
        print("insert glyphs:", stop-start, 'seconds to insert %s'%str(1+len(made_of_aes+made_of_dcs)))

    def insertmysqlGlyph(self, glyph, name, BGlyph, font, gtype):
        if BGlyph is None: return
        xml = BGlyph["data"]
        self.insertGlyph(glyph, xml, 'foreground', font)

        for layer in BGlyph["layers"]:
            layerName = layer["group_name"]

            if gtype == "AE":
                glyph = atomicElement.AtomicElement(name)
            elif gtype == "DC":
                glyph = deepComponent.DeepComponent(name)
            elif gtype == "CG":
                glyph = characterGlyph.CharacterGlyph(name)

            xml = layer["data"]

            # font.newLayer(layerName)
            self.insertGlyph(glyph, xml, layerName, font)

        self._mysqlInsertedGlyph[name] = time.time()

    def getGlyph(self, glyph, type = None, font = None):
        if font is None:
            font = self._RFont
        if isinstance(glyph, str):
            name = glyph
            if type is None:
                if set([name]) & self.staticDeepComponentSet():
                    type = "deepComponent"
                elif set([name]) & self.staticAtomicElementSet():
                    type = "atomicElement"
                else:
                    type = "characterGlyph"
        else:
            name = glyph.name
            type = glyph.type

        fileName = files.userNameToFileName(name)
        if type == "deepComponent":
            self.addGlyph(
                deepComponent.DeepComponent(name), 
                fileName, 
                "foreground",
                font = font
                )
        elif type == "characterGlyph":
            self.addGlyph(
                characterGlyph.CharacterGlyph(name), 
                fileName, 
                "foreground",
                font = font
                )
        elif type == "atomicElement":
            self.addGlyph(
                atomicElement.AtomicElement(name), 
                fileName, 
                "foreground",
                font = font
                )

        if type in ["atomicElement", "characterGlyph"]:
            if isinstance(glyph, str):
                glyph = self.get(glyph)
            layerNames = glyph._glyphVariations.layerNames()
            for layerPath in [ f.path for f in os.scandir(os.path.join(self.fontPath, type)) if f.is_dir() ]:
                layerName = os.path.basename(layerPath)
            # for layerName in layerNames:
                # layerPath = os.path.join(self.fontPath, type, layerName)
                # if not os.path.exists(layerPath): continue
                if set(["%s.glif"%files.userNameToFileName(name)]) & set(os.listdir(layerPath)): 
                    if layerName not in font.layers:
                        font.newLayer(layerName)
                    layerfileName = files.userNameToFileName(name)#glifFile.split('.glif')[0]
                    if type == "atomicElement":
                        self.addGlyph(
                            atomicElement.AtomicElement(name), 
                            layerfileName, 
                            layerName,
                            font = font
                            )
                    else:
                        self.addGlyph(
                            characterGlyph.CharacterGlyph(name), 
                            layerfileName, 
                            layerName,
                            font = font
                            )

    def newGLIF(self, glyphType, glyphName):
        if glyphType == 'atomicElement':
            emptyGlyph = atomicElement.AtomicElement(glyphName)

        elif glyphType == 'deepComponent':
            emptyGlyph = deepComponent.DeepComponent(glyphName)
            
        elif glyphType == 'characterGlyph':
            emptyGlyph = characterGlyph.CharacterGlyph(glyphName)
        
        emptyGlyph.name = glyphName
        txt = emptyGlyph.dumpToGLIF()
        if not self.mysql:
            fileName = files.userNameToFileName(glyphName)
            path = os.path.join(self.fontPath, glyphType, "%s.glif"%fileName)
            files.makepath(path)
            with open(path, "w", encoding = "utf-8") as file:
                file.write(txt)
            return (emptyGlyph, fileName)
        else:
            return txt

    

    def addGlyph(self, glyph, fileName, layerName, font = None):
        if font is None:
            font = self._RFont
        if layerName == 'foreground':
            glifPath = os.path.join(self.fontPath, glyph.type, "%s.glif"%fileName)
        else:
            glifPath = os.path.join(self.fontPath, glyph.type, layerName, "%s.glif"%fileName)
        tree = ET.parse(glifPath)
        root = tree.getroot()
        self.insertGlyph(glyph, ET.tostring(root), layerName, font = font)
        color = glyph.markColor

        name = glyph.name
        if not set([name]) - set(font.keys()): return
        glyph = self._glyphs.get(font[name])
        if glyph is None: return

        glyph.save()
        glyph._RGlyph.lib.clear()
        glyph._RGlyph.lib.update(glyph.lib)

    def insertGlyph(self, glyph, string, layerName, font = None):  
        if glyph is None: return
        if string is None: return
        if font is None:
            font = self._RFont
        glyph.setParent(self)
        pen = glyph.naked().getPointPen()
        readGlyphFromString(string, glyph.naked(), pen)
        font.newLayer(layerName)
        layer = font.getLayer(layerName)
        layer.insertGlyph(glyph)
        glyph._RFont = font
        self._glyphs[layer[glyph.name]] = glyph
        # _initWithLib_start = time.time()
        glyph._initWithLib()
        # _initWithLib_stop = time.time()
        # print("_initWithLib = ", _initWithLib_stop-_initWithLib_start, "seconds for %s"%glyph.name)

    def staticAtomicElementSet(self, update = False):
        if not self._atomicElementSet or update:
            self._atomicElementSet = self.atomicElementSet
        return set(self._atomicElementSet)

    def staticDeepComponentSet(self, update = False):
        if not self._deepComponentSet or update:
            self._deepComponentSet = self.deepComponentSet
        return set(self._deepComponentSet)

    def staticCharacterGlyphSet(self, update = False):
        if not self._characterGlyphSet or update:
            self._characterGlyphSet = self.characterGlyphSet
        return set(self._characterGlyphSet)

    @property
    def atomicElementSet(self):
        if not self.mysql:
            return self._returnGlyphsList('atomicElement')
        else:
            return [x["name"] for x in self.client.atomic_element_list(self.uid)["data"]]

    @property
    def deepComponentSet(self):
        if not self.mysql:
            return self._returnGlyphsList('deepComponent')
        else:
            return [x["name"] for x in self.client.deep_component_list(self.uid)["data"]]

    @property
    def characterGlyphSet(self):
        if not self.mysql:
            return self._returnGlyphsList('characterGlyph')
        else:
            return [x["name"] for x in self.client.character_glyph_list(self.uid)["data"]]

    def _returnGlyphsList(self, glyphType):
        if self.fontPath is None: return []
        l = []
        files.makepath(os.path.join(self.fontPath, glyphType, 'folder.proofer'))
        listDir = os.listdir(os.path.join(self.fontPath, glyphType))
        for glifFile in filter(lambda x: x.endswith(".glif"), listDir):
            glifPath = os.path.join(self.fontPath, glyphType, glifFile)
            tree = ET.parse(glifPath)
            root = tree.getroot()
            glyphName = root.get('name')
            l.append(glyphName)
        return sorted(l)

    def newGlyph(self, glyphType, glyphName = "newGlyph"):
        if not self.mysql:
            glif = self.newGLIF(glyphType, glyphName)
            self.addGlyph(*glif, "foreground", font = self._fullRFont)
            self.addGlyph(*glif, "foreground")
            
            self.batchLockGlyphs([self[glyphName]])
            
        else:
            # pass
            xml = self.newGLIF(glyphType, glyphName)
            if glyphType == "atomicElement":
                self.client.atomic_element_create(self.uid, xml)
                self.staticAtomicElementSet(update = True)
            elif glyphType == "deepComponent":
                self.client.deep_component_create(self.uid, xml)
                self.staticDeepComponentSet(update = True)
            else:
                self.client.character_glyph_create(self.uid, xml)
                self.staticCharacterGlyphSet(update = True)
            self.getmySQLGlyph(glyphName)
        self.updateStaticSet(glyphType)
            # self.saveGlyph(self[glyphName])
        # self.save()

    def duplicateGLIF(self, glyphName, glyphNamePath, newGlyphName, newGlyphNamePath):
        fileName = files.userNameToFileName(glyphName)
        tree = copy.deepcopy(ET.parse(glyphNamePath))
        root = tree.getroot()
        root.set("name", newGlyphName)
        string = ET.tostring(root).decode("utf-8")
        newFileName = files.userNameToFileName(newGlyphName)
        tree.write(open(newGlyphNamePath, "w"), encoding = 'unicode')

    @gitCoverage(msg = 'duplicate Glyph')
    def duplicateGlyph(self, glyphName:str, newGlyphName:str):
        if not self.mysql:
            glyphType = self[glyphName].type

            filename = files.userNameToFileName(glyphName)
            newFileName = files.userNameToFileName(newGlyphName)

            glyphPath = os.path.join(self.fontPath, glyphType, "%s.glif"%filename)
            newGlyphPath = os.path.join(self.fontPath, glyphType, "%s.glif"%newFileName)

            if glyphType == "deepComponent":
                new_glyph = deepComponent.DeepComponent(newGlyphName)
            elif glyphType == "atomicElement":
                new_glyph = atomicElement.AtomicElement(newGlyphName)
            elif glyphType == "characterGlyph":
                new_glyph = characterGlyph.CharacterGlyph(newGlyphName)

            self.duplicateGLIF(glyphName, glyphPath, newGlyphName, newGlyphPath)
            self.addGlyph(new_glyph, newFileName, "foreground")
            self.addGlyph(new_glyph, newFileName, "foreground", font = self._fullRFont)

            for layerPath in [ f.path for f in os.scandir(os.path.join(self.fontPath, glyphType)) if f.is_dir() ]:
                layerName = os.path.basename(layerPath)
                listdir = set(os.listdir(layerPath))
                if set(["%s.glif"%filename])&listdir and not set(["%s.glif"%newFileName])&listdir:
                    layerGlyphPath = os.path.join(layerPath, "%s.glif"%filename)
                    newLayerGlyphPath = os.path.join(layerPath, "%s.glif"%newFileName)

                    self.duplicateGLIF(glyphName, layerGlyphPath, newGlyphName, newLayerGlyphPath)
                    self.addGlyph(new_glyph, newFileName, layerName)
                    self.addGlyph(new_glyph, newFileName, layerName, font = self._fullRFont)

            self.getGlyph(self[newGlyphName])
            self.getGlyph(self[newGlyphName], font = self._fullRFont)
            self.updateStaticSet(glyphType)
        else:
            f = self._RFont.getLayer('foreground')
            # f[glyphName].name = newGlyphName
            glyph = f[glyphName].copy()
            glyph.name = newGlyphName
            xml = glyph.dumpToGLIF()
            glyphType = self[glyphName].type
            if glyphType == "atomicElement":
                self.client.atomic_element_create(self.uid, xml)
            elif glyphType == "deepComponent":
                self.client.deep_component_create(self.uid, xml)
            else:
                self.client.character_glyph_create(self.uid, xml)

            for layerName in self._fontLayers:
                f = self._RFont.getLayer(layerName)
                # f[glyphName].name = newGlyphName
                if glyphName not in f.keys(): continue
                g = f[glyphName].copy()
                g.name = newGlyphName
                xml = g.dumpToGLIF()
                if glyphType == "atomicElement":
                    self.client.atomic_element_layer_create(self.uid, newGlyphName, layerName, xml)
                elif glyphType == "deepComponent":
                    pass
                else:
                    self.client.character_glyph_layer_create(self.uid, newGlyphName, layerName, xml)

            # self.removeGlyph(glyphName)
            self.updateStaticSet(glyphType)
            self.getmySQLGlyph(newGlyphName)
            

    @gitCoverage(msg = 'remove Glyph')
    def removeGlyph(self, glyphName:str): 
        # return
        if not self.mysql:
            fileName = "%s.glif"%files.userNameToFileName(glyphName)
            glyph = self[glyphName]
            glyphType = glyph.type
            if fileName in os.listdir(os.path.join(self.fontPath, glyphType)):
                path = os.path.join(self.fontPath, glyphType, fileName)
                os.remove(path)
                folderPath = os.path.join(self.fontPath, glyphType)
                for _, layers, _ in os.walk(folderPath):
                    for layer in layers:
                        if fileName in os.listdir(os.path.join(folderPath, layer)):
                            layerPath = os.path.join(folderPath, layer, fileName)
                            os.remove(layerPath)

            
            self._fullRFont.removeGlyph(glyphName)
            self.locker.removeFiles([glyphName])

        else:
            glyph = self[glyphName]
            glyphType = glyph.type
            if glyphType == "atomicElement":
                self.client.atomic_element_delete(self.uid, glyphName)
            elif glyphType == "deepComponent":
                self.client.deep_component_delete(self.uid, glyphName)
            else:
                self.client.character_glyph_delete(self.uid, glyphName)

        self._RFont.removeGlyph(glyphName)
        for layer in self._RFont.layers:
            if glyphName in layer.keys():
                layer.removeGlyph(glyphName) 
          
        self.updateStaticSet(glyphType) 

    def _getBFItem(self, glyphName):
        pass
        # glyphType = self._findGlyphType(glyphName)
        # if glyphType == "cglyphs":
        #     return self._BFont.get_cglyph(glyphName)
        # elif glyphType == "dcomponents":
        #     return self._BFont.get_dcomponent(glyphName)
        # elif glyphType == "aelements":
        #     return self._BFont.get_aelement(glyphName)

    def saveGlyph(self, glyph):
        if glyph is None: return  
        if self.glyphLockedBy(glyph) != self.lockerUserName: return
        name = glyph.name
        glyph.save()
        rglyph = glyph._RGlyph
        rglyph.lib.update(glyph.lib)
        xml = rglyph.dumpToGLIF()
        if glyph.type == "atomicElement":
            self.client.atomic_element_update(self.uid, glyph.name, xml)
        elif glyph.type == "deepComponent":
            self.client.deep_component_update(self.uid, glyph.name, xml)
        else:
            self.client.character_glyph_update(self.uid, glyph.name, xml)

        for layerName in self._fontLayers:
            if not layerName: continue
            f = self._RFont.getLayer(layerName)
            if glyph.name in f:
                layerglyph = f[glyph.name]
                xml = layerglyph.dumpToGLIF()
                if glyph.type == "atomicElement":
                    layer_update_response = self.client.atomic_element_layer_update(self.uid, glyph.name, layerName, xml)
                    if layer_update_response['status'] == 404:
                        self.client.atomic_element_layer_create(self.uid, glyph.name, layerName, xml)
                elif glyph.type == "deepComponent":
                    pass
                else:
                    layer_update_response = self.client.character_glyph_layer_update(self.uid, glyph.name, layerName, xml)
                    if layer_update_response['status'] == 404:
                        self.client.character_glyph_layer_create(self.uid, glyph.name, layerName, xml)


    def writeGlif(self, glyph):
        glyph.save()
        glyphType = glyph.type
        rglyph = glyph._RGlyph
        rglyph.lib.clear()
        rglyph.lib.update(glyph.lib)
        txt = rglyph.dumpToGLIF()
        fileName = "%s.glif"%files.userNameToFileName(glyph.name)
        path = os.path.join(self.fontPath, glyphType, fileName)

        with open(path, "w", encoding = "utf-8") as file:
            file.write(txt)

        for layerName in self._fontLayers:
            if not layerName: continue
            f = self._RFont.getLayer(layerName)
            if glyph.name in f:
                layerglyph = f[glyph.name]
                txt = layerglyph.dumpToGLIF()
                fileName = "%s.glif"%files.userNameToFileName(layerglyph.name)
                path = os.path.join(self.fontPath, glyphType, layerName, fileName)
                files.makepath(path)
                with open(path, "w", encoding = "utf-8") as file:
                    file.write(txt)


    @gitCoverage(msg = 'font save')
    def save(self):
        if not self.mysql:
            # self._fullRFont.save()
            
            if self.admin:
                libPath = os.path.join(self.fontPath, 'fontLib.json')
                with open(libPath, "w") as file:
                    lib = self._fullRFont.lib.asDict()
                    if "public.glyphOrder" in lib:
                        del lib["public.glyphOrder"]
                    file.write(json.dumps(lib,
                        indent=4, separators=(',', ': ')))

            for rglyph in self._RFont.getLayer('foreground'):
                if not self.locker.userHasLock(rglyph): continue
                glyph = self[rglyph.name]
                self.writeGlif(glyph)
                self.getGlyph(rglyph.name, type = glyph.type, font = self._fullRFont)

        else:
            pass
            # return

    def updateStaticSet(self, glyphType = ""):
        if glyphType == "atomicElement":
            self.staticAtomicElementSet(update = True)
        elif glyphType == "deepComponent":
            self.staticDeepComponentSet(update = True)
        elif glyphType == "characterGlyph":
            self.staticCharacterGlyphSet(update = True)

    def renameGlyph(self, oldName, newName):
        if not set([newName]) - set(self.atomicElementSet + self.deepComponentSet + self.characterGlyphSet):
            return
        if not self.mysql:
            if not self.locker.userHasLock(self[oldName]): 
                return False
            self.save()
            f = self._RFont.getLayer('foreground')
            if newName in f.keys(): 
                return False
            self.get(oldName).name = newName
            f[oldName].name = newName
            glyph = f[newName]
            txt = glyph.dumpToGLIF()
            fileName = "%s.glif"%files.userNameToFileName(glyph.name)
            oldFileName = "%s.glif"%files.userNameToFileName(oldName)
            glyphType = self[glyph.name].type
            newPath = os.path.join(self.fontPath, glyphType, fileName)
            oldPath = os.path.join(self.fontPath, glyphType, oldFileName)

            if glyphType == "atomicElement":
                for n in self.staticDeepComponentSet():
                    dcg = self.get(n)
                    for ae in dcg._deepComponents:
                        if ae["name"] == oldName:
                            ae["name"] = newName
                
            elif glyphType == "deepComponent":
                for n in self.staticCharacterGlyphSet():
                    dcg = self.get(n)
                    for ae in dcg._deepComponents:
                        if ae["name"] == oldName:
                            ae["name"] = newName
     
            with open(newPath, "w", encoding = "utf-8") as file:
                file.write(txt)
            os.remove(oldPath)
            for layerName in self._fontLayers:
                f = self._RFont.getLayer(layerName)
                if oldName not in f: continue
                f[oldName].name = newName
                glyph = f[newName]
                txt = glyph.dumpToGLIF()
                newPath = os.path.join(self.fontPath, glyphType, layerName, fileName)
                oldPath = os.path.join(self.fontPath, glyphType, layerName, oldFileName)
                with open(newPath, "w", encoding = "utf-8") as file:
                    file.write(txt)
                os.remove(oldPath)

            self.getGlyph(newName, type = glyphType, font = self._fullRFont)
            self.getGlyph(newName, type = glyphType, font = self._RFont)
            self.updateStaticSet(glyphType)

            self.locker.changeLockName(oldName, newName)
            return True
        else:
            f = self._RFont.getLayer('foreground')
            f[oldName].name = newName
            glyph = f[newName]
            xml = glyph.dumpToGLIF()
            glyphType = self[glyph.name].type
            if glyphType == "atomicElement":
                self.client.atomic_element_create(self.uid, xml)
            elif glyphType == "deepComponent":
                self.client.deep_component_create(self.uid, xml)
            else:
                self.client.character_glyph_create(self.uid, xml)

            for layerName in self._fontLayers:
                f = self._RFont.getLayer(layerName)
                f[oldName].name = newName
                g = f[newName]
                xml = g.dumpToGLIF()
                if glyphType == "atomicElement":
                    self.client.atomic_element_layer_create(self.uid, newName, layerName, xml)
                elif glyphType == "deepComponent":
                    pass
                else:
                    self.client.character_glyph_layer_create(self.uid, newName, layerName, xml)

            self.removeGlyph(oldName)
            self.updateStaticSet(glyphType)
            self.getmySQLGlyph(newName)
            
