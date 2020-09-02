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

class glyphsTypes:

    atomicElement = 'aelements'
    deepComponent = 'dcomponents'
    characterGlyph = 'cglyphs'

    @classmethod
    def mysql(cls, type):
        return getattr(cls, type)

    @classmethod
    def bfs(cls, type):
        if type == 'atomicElement':
            return bfs.AELEMENT
        if type == 'deepComponent':
            return bfs.DCOMPONENT
        if type == 'characterGlyph':
            return bfs.CGLYPH

    @classmethod
    def robocjk(cls, type):
        for x in vars(cls):
            if getattr(cls, x) == type:
                return x 

class Font():


    # def __init__(self, fontPath, gitUserName, gitPassword, gitHostLocker, gitHostLockerPassword, privateLocker):
    #     pass
    def __init__(self):
        self.mysqlFont = False
        self.mysql = False
        self._glyphs = {}
        self._RFont = {}
        self.dataBase = {}

        self._atomicElementSet = []
        self._deepComponentSet = []
        self._characterGlyphSet = []

    def _init_for_git(self, fontPath, gitUserName, gitPassword, gitHostLocker, gitHostLockerPassword, privateLocker):
        # import time
        # start = time.time()
        self.fontPath = fontPath
        
        self.locker = locker.Locker(fontPath, gitUserName, gitPassword, gitHostLocker, gitHostLockerPassword, privateLocker)
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

        if 'fontLib.json' in os.listdir(self.fontPath):
            libPath = os.path.join(self.fontPath, 'fontLib.json')
            with open(libPath, 'r') as file:
                self.fontLib = json.load(file)
            self._initFontLib(self.fontLib)
            # for k, v in self.fontLib.items():
            #     self._RFont.lib[k] = v
        self.fontVariations = self.fontLib.get('robocjk.fontVariations', [])

        self.defaultGlyphWidth = self._RFont.lib.get("rorocjk.defaultGlyphWidth", 1000)

        # getStart = time.time()
        # def getGlyphs(glyphset, type):
        #     for name in glyphset:
        #         self.getGlyph(name, type = type, font = self._fullRFont)

        staticCharacterGlyphSet = list(self.staticCharacterGlyphSet())
        thirdl = len(staticCharacterGlyphSet)//3
        l1 = staticCharacterGlyphSet[0:thirdl]
        l2 = staticCharacterGlyphSet[thirdl:thirdl*2]
        l3 = staticCharacterGlyphSet[thirdl*2:]
        print(len(staticCharacterGlyphSet), len(l1), len(l2), len(l3), len(l1)+len(l2)+len(l3))
        # l4 = staticCharacterGlyphSet[thirdl*3:thirdl*4]
        # l5 = staticCharacterGlyphSet[thirdl*4:thirdl*5]
        # l6 = staticCharacterGlyphSet[thirdl*5:]
        self.queue = queue.Queue()
        threading.Thread(target=self.queueGetGlyphs, args = (self.queue, "atomicElement"), daemon=True).start()
        self.queue.put(self.staticAtomicElementSet())

        self.queue2 = queue.Queue()
        threading.Thread(target=self.queueGetGlyphs, args = (self.queue2, "deepComponent"), daemon=True).start()
        self.queue2.put(self.staticDeepComponentSet())

        self.queue3 = queue.Queue()
        threading.Thread(target=self.queueGetGlyphs, args = (self.queue3, "characterGlyph"), daemon=True).start()
        self.queue3.put(l1)

        self.queue4 = queue.Queue()
        threading.Thread(target=self.queueGetGlyphs, args = (self.queue4, "characterGlyph"), daemon=True).start()
        self.queue4.put(l2)

        self.queue5 = queue.Queue()
        threading.Thread(target=self.queueGetGlyphs, args = (self.queue5, "characterGlyph"), daemon=True).start()
        self.queue5.put(l3)

        # self.queue6 = queue.Queue()
        # threading.Thread(target=self.queueGetGlyphs, args = (self.queue6, "characterGlyph"), daemon=True).start()
        # self.queue6.put(l4)

        # self.queue7 = queue.Queue()
        # threading.Thread(target=self.queueGetGlyphs, args = (self.queue7, "characterGlyph"), daemon=True).start()
        # self.queue7.put(l5)

        # self.queue8 = queue.Queue()
        # threading.Thread(target=self.queueGetGlyphs, args = (self.queue8, "characterGlyph"), daemon=True).start()
        # self.queue8.put(l6)
        # getGlyphs(self.staticCharacterGlyphSet(), 'characterGlyph')
        # getStop = time.time()
        # print(getStop-getStart, 'get glyphs')
        # for glyphset in [self.staticAtomicElementSet(), self.staticDeepComponentSet(), self.staticCharacterGlyphSet()]:
            # for name in glyphset:
            #     startGlyph = time.time()
            #     self.getGlyph(name, font = self._fullRFont)
            #     stopGlyph = time.time()
            #     print(stopGlyph-startGlyph, "per glyph")
        self.createLayersFromVariationAxis()
        # createLayerStop = time.time()
        # print(createLayerStop-getStop, "createLayersFromVariationAxis")
        # stop = time.time()
        # print((stop - start)/60, "minutes to load the project")

    def queueGetGlyphs(self, queue, item_type):
        glyphset = queue.get()
        for name in glyphset:
            self.getGlyph(name, type = item_type, font = self._fullRFont)
        queue.task_done()

    def _init_for_mysql(self, bf_log, fontName, mysql, mysqlUserName, mysqlPassword, fontpath = None):
        self.mysqlFont = True
        self._BFont = BF_mysql2rcjk.read_font_from_mysql(bf_log, fontName, mysql)
        # print("----")
        # for x in self._BFont.cglyphs:
        #     print(x.xml)
        #     break
        # print(self._BFont.cglyphs[0].xml)
        self._RFont = NewFont(
            familyName=fontName, 
            styleName='Regular', 
            showUI = False,
            )
        self.fontPath = fontPath
        if fontpath is not None:
            files.makepath(os.path.join(fontpath, "%s.ufo"%fontName))
            self._RFont.save(os.path.join(fontpath, "%s.ufo"%fontName))

        print("fontpath")
        print(os.path.join(fontpath, "%s.ufo"%fontName))
        self._fullRFont = NewFont(
            familyName="%s-full"%fontName, 
            styleName='Regular', 
            showUI = False
            )
        self._fullGlyphs = {}
        self.fontName = fontName
        self.mysql = mysql
        self.mysqlUserName = mysqlUserName
        self.mysqlPassword = mysqlPassword
        self.bf_log = bf_log

        fontlib = self._BFont.fontlib_data
        print(fontlib)
        if fontlib is None:
            fontlib = '{}'
        # self.fontLib = eval(fontlib)
        self.fontLib = json.loads(fontlib)#.decode()
        self._initFontLib(self.fontLib)

        self.fontVariations = self.fontLib.get('robocjk.fontVariations', [])

        database = self._BFont.database_data
        if database is None:
            database = '{}'
        self.dataBase = json.loads(database)
        # print(self.dataBase)
        self.defaultGlyphWidth = self.fontLib.get("robocjk.defaultGlyphWidth", 1000)
        start = time.time()
        for glyphset in [self.atomicElementSet, self.deepComponentSet, self.characterGlyphSet]:
            for name in glyphset:
                self.getmySQLGlyph(name, font = self._fullRFont)
        stop = time.time()
        print("full font need:", stop-start)
    #     self.insertFullRFont()

    def clearRFont(self):
        self._RFont = NewFont(
                familyName=self.fontName, 
                styleName='Regular', 
                showUI = False,
                )
        if self.mysqlFont:
            if self.fontpath is not None:
                fontFilePath = files.makepath(os.path.join(self.fontpath, "%s.ufo"%fontName))
        else:
            fontFilePath = '{}.ufo'.format(os.path.join(self.fontPath, self.fontName))
        self._RFont.save(fontFilePath)
        self._initFontLib(self.fontLib, self._RFont)

    def loadTeam(self):
        return self.fontLib.get('teamManager', {})

    def saveTeam(self, teamDict):
        self.fontLib['teamManager'] = teamDict
        print("save team", teamDict)
        if self.mysqlFont:
            self.mysql.update_font_fontlib_data(self.fontName, json.dumps(self.fontLib))
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
        if not self.mysqlFont:
            char = chr(int(key, 16))
            return "".join(self.dataBase[char])
        else:
            return self.mysql.select_font_database_key(self.fontName, key)

    def updateDatabaseKey(self, key, values):
        if not self.mysqlFont:
            char = chr(int(key, 16))
            self.dataBase[char] = values
        else:
            data = tuple([hex(ord(x))[2:] for x in values])
            self.mysql.update_font_database_key(self.fontName, key, data)
            self.loadMysqlDataBase()

    def get(self, name, font = None):
        if font is None:
            font = self._fullRFont
        return self._glyphs[font[name]]
        # if self.mysqlFont:
        #     return self._glyphs[self._fullRFont[name]]
        # else:
        #     return self[name]

    def loadMysqlDataBase(self):
        self.dataBase = json.loads(self._BFont.database_data)

    def saveFontlib(self):
        pass

    def saveDatabase(self):
        pass

    def lockGlyph(self, glyph):
        if not self.mysqlFont:
            locked, alreadyLocked = self.locker.lock(glyph)
            return locked, alreadyLocked
        else:
            glyphName = glyph.name
            glyphType = self._findGlyphType(glyphName)
            if glyphType == "cglyphs":
                lock = self.mysql.lock_cglyph(self.fontName, glyphName)
                return lock in [self.mysqlUserName], None
            elif glyphType == "dcomponents":
                lock = self.mysql.lock_dcomponent(self.fontName, glyphName)
                return lock in [self.mysqlUserName], None
            elif glyphType == "aelements":
                lock = self.mysql.lock_aelement(self.fontName, glyphName)
                return lock in [self.mysqlUserName], None
            

    def unlockGlyph(self, glyph):
        if not self.mysqlFont:
            return self.locker.batchUnlock([glyph])
        else:
            glyphName = glyph.name
            glyphType = self._findGlyphType(glyphName)
            if glyphType == "cglyphs":
                return self.mysql.unlock_cglyph(self.fontName, glyphName)
            elif glyphType == "dcomponents":
                return self.mysql.unlock_dcomponent(self.fontName, glyphName)
            elif glyphType == "aelements":
                return self.mysql.unlock_aelement(self.fontName, glyphName)

    def batchLockGlyphs(self, glyphs:list = []):
        if not self.mysqlFont:
            return self.locker.batchLock(glyphs)
        else:
            for glyph in glyphs:
                self.lockGlyph(glyph)
            return True

    def exportDataBase(self):
        if not self.mysqlFont:
            with open(os.path.join(self.fontPath, "database.json"), 'w', encoding="utf-8") as file:
                file.write(json.dumps(self.dataBase))
        else:
            self._BFont.database_data = json.dumps(self.dataBase)
            # print(self._BFont.database_data)
            self.mysql.update_font_database_data(self.fontName, json.dumps(self.dataBase))
            # BF_rcjk2mysql.update_font_to_mysql(self.bf_log, self._BFont, self.mysql)
            # print(self._BFont.database_data)

    def batchUnlockGlyphs(self, glyphs:list = []):
        if not self.mysqlFont:
            return self.locker.batchUnlock(glyphs)
        else:
            for glyph in glyphs:
                self.unlockGlyph(glyph)
            return True

    def glyphLockedBy(self, glyph):
        if not self.mysqlFont:
            return self.locker.potentiallyOutdatedLockingUser(glyph)
        else:
            glyphName = glyph.name
            glyphType = self._findGlyphType(glyphName)
            if glyphType == "cglyphs":
                return self.mysql.who_locked_cglyph(self.fontName, glyphName)
            elif glyphType == "dcomponents":
                return self.mysql.who_locked_dcomponent(self.fontName, glyphName)
            elif glyphType == "aelements":
                return self.mysql.who_locked_aelement(self.fontName, glyphName)

    def currentUserLockedGlyphs(self):
        if not self.mysqlFont:
            return self.locker.myLockedGlyphs
        else:
            cglyphs = [x[0] for x in self.mysql.select_locked_cglyphs(self.fontName) if x[1] == self.mysqlUserName]
            dcomponents = [x[0] for x in self.mysql.select_locked_dcomponents(self.fontName) if x[1] == self.mysqlUserName]
            aelements = [x[0] for x in self.mysql.select_locked_aelements(self.fontName) if x[1] == self.mysqlUserName]
            return cglyphs + dcomponents + aelements

    def removeLockerFiles(self, glyphsnames:list = []):
        if not self.mysqlFont:
            if not isinstance(glyphsnames, list):
                glyphsnames = list(glyphsnames)
            self.locker.removeFiles(glyphsnames)

    def loadCharacterGlyph(self, glyphName):
        bfitem = self._BFont.get_cglyph(glyphName)
        BF_mysql2rcjk.read_item_from_mysql(self.bf_log, bfitem, self.mysql)

    @property
    def lockerUserName(self):
        if not self.mysqlFont:
            return self.locker._username
        else:
            return self.mysqlUserName

    def _findGlyphType(self, glyphname):
        if glyphname in self.characterGlyphSet:
            return "cglyphs"

        elif glyphname in self.atomicElementSet:
            return "aelements"

        elif glyphname in self.deepComponentSet:
            return "dcomponents"

    def __iter__(self):
        for name in self._RFont.keys():
            yield self[name]

    def __getitem__(self, name):
        if not isinstance(name, str):
            name = name["name"]
        try:
            if not set([name]) - set(self._RFont.keys()):
                return self._glyphs[self._RFont[name]]
            else:
                if self.mysqlFont:
                    self.getmySQLGlyph(name)
                else:
                    self.getGlyph(name, font = self._fullRFont)
                    self.getGlyph(name)
                return self._glyphs[self._RFont[name]]
        except:
            if isinstance(name, dict):
                name = name["name"]
            if self.mysqlFont:
                self.getmySQLGlyph(name)
            else:
                self.getGlyph(name, font = self._fullRFont)
                self.getGlyph(name)

            return self._glyphs[self._RFont[name]]
        return self._glyphs[self._RFont[name]]

    def __getitem2__(self, name):
        if isinstance(name, dict):
            name = name["name"]
        try:
            # if set([name]) & set(self._RFont.keys()):
            return self._glyphs[self._RFont[name]]
        except:
            if self.mysqlFont:
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
        if font is None:
            font = self._RFont

        BGlyph = None
        if not isinstance(name, str):
            name = name["name"]
        if name in self.atomicElementSet:
            glyph = atomicElement.AtomicElement(name)
            BGlyph = self._BFont.get_aelement(name)
        elif name in self.deepComponentSet:
            glyph = deepComponent.DeepComponent(name)
            BGlyph = self._BFont.get_dcomponent(name)
        elif name in self.characterGlyphSet:
            glyph = characterGlyph.CharacterGlyph(name)
            BGlyph = self._BFont.get_cglyph(name)

        if BGlyph is None: return
        xml = BGlyph.xml
        self.insertGlyph(glyph, xml, 'foreground', font)

        for layer in BGlyph.layers:
            layerName = layer.layername
            
            if name in self.atomicElementSet:
                glyph = atomicElement.AtomicElement(name)
            elif name in self.deepComponentSet:
                glyph = deepComponent.DeepComponent(name)
            elif name in self.characterGlyphSet:
                glyph = characterGlyph.CharacterGlyph(name)

            xml = layer.xml

            font.newLayer(layerName)
            self.insertGlyph(glyph, xml, layerName, font)

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
            layerNames = glyph._glyphVariations.layerNames
            # path = os.path.join(self.fontPath, type)
            # for layerPath in [f.path for f in os.scandir(path) if f.is_dir()]:
            #     layerName = os.path.split(layerPath)[1]
            for layerName in layerNames:
                layerPath = os.path.join(self.fontPath, type, layerName)
                if not os.path.exists(layerPath): continue
                # print(set(["%s.glif"%files.userNameToFileName(name)]))
                # print(set(os.listdir(layerPath)))
                if set(["%s.glif"%files.userNameToFileName(name)]) & set(os.listdir(layerPath)): 
                # if "%s.glif"%files.userNameToFileName(name) not in os.listdir(layerPath): continue
                    if layerName not in font.layers:
                        font.newLayer(layerName)

                    # for glifFile in filter(lambda x: x.endswith(".glif"), os.listdir(layerPath)):
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

    # def getGlyphs(self, font = None):
    #     if font is None:
    #         font = self._RFont
    #     for glyphName in self.deepComponentSet:
    #         fileName = files.userNameToFileName(glyphName)
    #         self.addGlyph(
    #             deepComponent.DeepComponent(glyphName), 
    #             fileName, 
    #             "foreground",
    #             font = font
    #             )

    #     for glyphName in self.characterGlyphSet:
    #         fileName = files.userNameToFileName(glyphName)
    #         self.addGlyph(
    #             characterGlyph.CharacterGlyph(glyphName), 
    #             fileName, 
    #             "foreground",
    #             font = font
    #             )

    #     for glyphName in self.atomicElementSet:
    #         fileName = files.userNameToFileName(glyphName)
    #         self.addGlyph(
    #             atomicElement.AtomicElement(glyphName), 
    #             fileName, 
    #             "foreground",
    #             font = font
    #             )
    #     glyphtypes = ["atomicElement", "characterGlyph"]
    #     for glyphtype in glyphtypes:
    #         path = os.path.join(self.fontPath, glyphtype)
    #         for layerPath in [f.path for f in os.scandir(path) if f.is_dir()]:
    #             layerName = os.path.split(layerPath)[1]
    #             if layerName not in font.layers:
    #                 font.newLayer(layerName)

    #             for glifFile in filter(lambda x: x.endswith(".glif"), os.listdir(layerPath)):
    #                 layerfileName = glifFile.split('.glif')[0]
    #                 if glyphtype == "atomicElement":
    #                     self.addGlyph(
    #                         atomicElement.AtomicElement(glyphName), 
    #                         layerfileName, 
    #                         layerName,
    #                         font = font
    #                         )
    #                 else:
    #                     self.addGlyph(
    #                         characterGlyph.CharacterGlyph(glyphName), 
    #                         layerfileName, 
    #                         layerName,
    #                         font = font
    #                         )

    def newGLIF(self, glyphType, glyphName):
        if glyphType == 'atomicElement':
            emptyGlyph = atomicElement.AtomicElement(glyphName)

        elif glyphType == 'deepComponent':
            emptyGlyph = deepComponent.DeepComponent(glyphName)
            
        elif glyphType == 'characterGlyph':
            emptyGlyph = characterGlyph.CharacterGlyph(glyphName)
        
        emptyGlyph.name = glyphName
        txt = emptyGlyph.dumpToGLIF()
        fileName = files.userNameToFileName(glyphName)
        path = os.path.join(self.fontPath, glyphType, "%s.glif"%fileName)
        files.makepath(path)
        with open(path, "w", encoding = "utf-8") as file:
            file.write(txt)
        return (emptyGlyph, fileName)

    def duplicateGLIF(self, glyphName, glyphNamePath, newGlyphName, newGlyphNamePath):
        fileName = files.userNameToFileName(glyphName)
        tree = copy.deepcopy(ET.parse(glyphNamePath))
        root = tree.getroot()
        root.set("name", newGlyphName)
        string = ET.tostring(root).decode("utf-8")
        newFileName = files.userNameToFileName(newGlyphName)
        tree.write(open(newGlyphNamePath, "w"), encoding = 'unicode')

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
        glyph._initWithLib()

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
        if not self.mysqlFont:
            return self._returnGlyphsList('atomicElement')
        else:
            return self._BFont.all_aelementnames()

    @property
    def deepComponentSet(self):
        if not self.mysqlFont:
            return self._returnGlyphsList('deepComponent')
        else:
            return self._BFont.all_dcomponentnames()

    @property
    def characterGlyphSet(self):
        if not self.mysqlFont:
            return self._returnGlyphsList('characterGlyph')
        else:
            return self._BFont.all_cglyphnames()

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
        if not self.mysqlFont:
            glif = self.newGLIF(glyphType, glyphName)
            self.addGlyph(*glif, "foreground", font = self._fullRFont)
            self.addGlyph(*glif, "foreground")
            
            self.batchLockGlyphs([self[glyphName]])
            self.updateStaticSet(glyphType)
        else:
            self._RFont.newGlyph(glyphName)
            glyphType = glyphsTypes.bfs(glyphType)
            BF_rcjk2mysql.new_item_to_mysql(self.bf_log, item_type = glyphType, bfont = self._BFont, new_name = glyphName, my_sql = self.mysql)
            self.getmySQLGlyph(glyphName)
            self.saveGlyph(self[glyphName])

    @gitCoverage(msg = 'duplicate Glyph')
    def duplicateGlyph(self, glyphName:str, newGlyphName:str):
        if not self.mysqlFont:
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

            for _, layers, _ in os.walk(os.path.join(self.fontPath, glyphType)):
                for layer in layers:
                    layerDirectory = os.path.join(self.fontPath, glyphType, layer)
                    if "%s.glif"%filename in os.listdir(layerDirectory) and "%s.glif"%newFileName not in os.listdir(layerDirectory):
                        layerGlyphPath = os.path.join(layerDirectory, "%s.glif"%filename)
                        newLayerGlyphPath = os.path.join(layerDirectory, "%s.glif"%newFileName)

                        self.duplicateGLIF(glyphName, layerGlyphPath, newGlyphName, newLayerGlyphPath)
                        self.addGlyph(new_glyph, newFileName, layer)
                        self.addGlyph(new_glyph, newFileName, layer, font = self._fullRFont)

            self.getGlyph(self[newGlyphName])
            self.getGlyph(self[newGlyphName], font = self._fullRFont)
            self.updateStaticSet(glyphType)
        else:
            # glyphType = self._findGlyphType(glyphName)
            # if glyphType == "cglyphs":
            #     bfitem = self._BFont.get_cglyph(glyphName)
            # elif glyphType == "dcomponents":
            #     bfitem = self._BFont.get_dcomponent(glyphName)
            # elif glyphType == "aelements":
            #     bfitem = self._BFont.get_aelement(glyphName)
            bfitem = self._getBFItem(glyphName)
            t = BF_rcjk2mysql.duplicate_item_to_mysql(self.bf_log, bfitem, newGlyphName, self.mysql)
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

            self._RFont.removeGlyph(glyphName)
            self._fullRFont.removeGlyph(glyphName)
            for layer in self._RFont.layers:
                if glyphName in layer.keys():
                    layer.removeGlyph(glyphName) 
            self.locker.removeFiles([glyphName])  
            self.updateStaticSet(glyphType) 
        else:
            bfitem = self._getBFItem(glyphName)
            BF_rcjk2mysql.remove_item_to_mysql(self.bf_log, bfitem, self.mysql)
            
            self._RFont.removeGlyph(glyphName)
            for layer in self._RFont.layers:
                if glyphName in layer.keys():
                    layer.removeGlyph(glyphName) 

    def _getBFItem(self, glyphName):
        glyphType = self._findGlyphType(glyphName)
        if glyphType == "cglyphs":
            return self._BFont.get_cglyph(glyphName)
        elif glyphType == "dcomponents":
            return self._BFont.get_dcomponent(glyphName)
        elif glyphType == "aelements":
            return self._BFont.get_aelement(glyphName)

    def saveGlyph(self, glyph):
        if glyph is None: return  

        self.mysql.login(self.mysqlUserName, self.mysqlPassword)

        name = glyph.name

        glyph.save()
        rglyph = glyph._RGlyph
        rglyph.lib.update(glyph.lib)
        xml = rglyph.dumpToGLIF()

        # glyphtype = self._findGlyphType(name)
        # if glyphtype == "cglyphs":
        #     bglyph = self._BFont.get_cglyph(name)
        # elif glyphtype == "dcomponents":
        #     bglyph = self._BFont.get_dcomponent(name)
        # elif glyphtype == "aelements":
        #     bglyph = self._BFont.get_aelement(name)
        bglyph = self._getBFItem(name)
            
        for layer in self._RFont.layers:
            if layer.name == "foreground": continue
            f = self._RFont.getLayer(layer.name)
            if not set([name])-set(f.keys()):
                variations = glyph._glyphVariations
                layerGlyph = f[name]
                layerxml = layerGlyph.dumpToGLIF()
                blayerGlyph = bglyph.get_layer_name(layer.name)

                if blayerGlyph:
                    blayerGlyph.set_xml(layerxml)
                else:
                    axisname = ""
                    for k, v in variations.items():
                        if isinstance(v, str) and layer.name == v:
                            axisname = k
                            break
                        elif layer.name in v.layerName:
                            axisname = k
                            break
                    if not axisname: continue

                    l = bfs.BfLayer(
                        bglyph, 
                        axisname, 
                        layer.name, 
                        layerxml
                        )
                    l._changed = True

        bglyph.rename(name)
        bglyph.set_xml(xml)

        BF_rcjk2mysql.update_item_to_mysql(self.bf_log, bglyph, self.mysql)

        self.getmySQLGlyph(glyph.name, font = self._fullRFont)
        self.getmySQLGlyph(glyph.name)

    @gitCoverage(msg = 'font save')
    def save(self):
        if not self.mysql:
            self._fullRFont.save()
        
            libPath = os.path.join(self.fontPath, 'fontLib.json')
            with open(libPath, "w") as file:
                lib = self._fullRFont.lib.asDict()
                del lib["public.glyphOrder"]
                file.write(json.dumps(lib,
                    indent=4, separators=(',', ': ')))

            for rglyph in self._RFont.getLayer('foreground'):
                if not self.locker.userHasLock(rglyph): continue
                glyph = self[rglyph.name]
                glyph.save()
                glyphType = glyph.type
                rglyph = glyph._RGlyph
                rglyph.lib.update(glyph.lib)
                txt = rglyph.dumpToGLIF()
                fileName = "%s.glif"%files.userNameToFileName(glyph.name)
                path = os.path.join(self.fontPath, glyphType, fileName)

                with open(path, "w", encoding = "utf-8") as file:
                    file.write(txt)

                for layerName in self._fontLayers:
                    f = self._RFont.getLayer(layerName)
                    if glyph.name in f:
                        layerglyph = f[glyph.name]
                        txt = layerglyph.dumpToGLIF()
                        fileName = "%s.glif"%files.userNameToFileName(layerglyph.name)
                        path = os.path.join(self.fontPath, glyphType, layerName, fileName)
                        files.makepath(path)
                        with open(path, "w", encoding = "utf-8") as file:
                            file.write(txt)

            self._hanziExportUFO()
        else:
            return
            # userGlyphs = self.currentUserLockedGlyphs()
            # for n in userGlyphs:
            #     self.saveGlyph(self.get(n))
            # for name in [x[0] for x in self.mysql.select_locked_aelements(self.fontName) if x[1] == self.mysqlUserName]:
            #     glyph = self[name]
            #     glyph.save()
            #     rglyph = glyph._RGlyph
            #     rglyph.lib.update(glyph.lib)
            #     xml = rglyph.dumpToGLIF()
            #     aelement = self._BFont.get_aelement(name)

            #     aelement.set_xml(xml)

            # for name in [x[0] for x in self.mysql.select_locked_dcomponents(self.fontName) if x[1] == self.mysqlUserName]:
            #     glyph = self[name]
            #     glyph.save()
            #     rglyph = glyph._RGlyph
            #     rglyph.lib.update(glyph.lib)
            #     xml = rglyph.dumpToGLIF()
            #     self._BFont.get_dcomponent(name).set_xml(xml)

            # for name in self.characterGlyphSet:
            #     glyph = self[name]
            #     glyph.save()
            #     rglyph = glyph._RGlyph
            #     rglyph.lib.update(glyph.lib)
            #     xml = rglyph.dumpToGLIF()
            #     self._BFont.get_dcomponent(name).set_xml(xml)

            # BF_rcjk2mysql.update_font_to_mysql(self.bf_log, self._BFont, self.mysql)

    def _hanziExportUFO(self):
        return
        font = NewFont(familyName = "hanzi", styleName = "Regular", showUI = False)
        for rglyph in self._RFont.getLayer('foreground'):
            glyph = self[rglyph.name]
            glyph.save()
            glyphType = glyph.type
            rglyph = glyph._RGlyph
            rglyph.lib.update(glyph.lib)
            font.insertGlyph(rglyph)

            for layerName in self._fontLayers:
                f = self._RFont.getLayer(layerName)
                font.newLayer(layerName)
                if glyph.name in f:
                    layerglyph = f[glyph.name]
                    layer = font.getLayer(layerName)
                    layer.insertGlyph(f[glyph.name])

        font.save(os.path.join(self.fontPath, "hanziUFO.ufo"))

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
            if not self.locker.userHasLock(self[oldName]): return False
            self.save()
            f = self._RFont.getLayer('foreground')
            if newName in f.keys(): return False
            self[oldName].name = newName
            f[oldName].name = newName
            glyph = f[newName]
            txt = glyph.dumpToGLIF()
            fileName = "%s.glif"%files.userNameToFileName(glyph.name)
            oldFileName = "%s.glif"%files.userNameToFileName(oldName)
            glyphType = self[glyph.name].type
            newPath = os.path.join(self.fontPath, glyphType, fileName)
            oldPath = os.path.join(self.fontPath, glyphType, oldFileName)

            if glyphType == "atomicElement":
                for n in self.deepComponentSet:
                    dcg = self[n]
                    for ae in dcg._deepComponents:
                        if ae.name == oldName:
                            ae.name = newName
                
            elif glyphType == "deepComponent":
                for n in self.characterGlyphSet:
                    dcg = self[n]
                    for ae in dcg._deepComponents:
                        if ae.name == oldName:
                            ae.name = newName
     
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
            # if glyphType == "atomicElement":
            #     self.staticAtomicElementSet(update = True)
            # elif glyphType == "deepComponent":
            #     self.staticDeepComponentSet(update = True)
            # elif glyphType == "characterGlyph":
            #     self.staticCharacterGlyphSet(update = True)

            self.locker.changeLockName(oldName, newName)
            return True
        else:
            # glyphType = self._findGlyphType(oldName)
            # if glyphType == "cglyphs":
            #     bfitem = self._BFont.get_cglyph(oldName)
            # elif glyphType == "dcomponents":
            #     bfitem = self._BFont.get_dcomponent(oldName)
            # elif glyphType == "aelements":
            #     bfitem = self._BFont.get_aelement(oldName)
            bfitem = self._getBFItem(oldName)
            BF_rcjk2mysql.rename_item_to_mysql(self.bf_log, item = bfitem, new_name = newName, my_sql = self.mysql)
            self[oldName].name = newName
            self._RFont.renameGlyph(oldName, newName)
            self.saveGlyph(self[newName])
            return True
