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

from imp import reload
from utils import decorators, files, locker
reload(decorators)
reload(locker)
gitCoverage = decorators.gitCoverage
from utils import interpolation
reload(interpolation)
from models import atomicElement, deepComponent, characterGlyph
reload(atomicElement)
reload(deepComponent)
reload(characterGlyph)


class Font():

    def __init__(self, fontPath, gitUserName, gitPassword):
        self.fontPath = fontPath
        
        self.locker = locker.Locker(fontPath, gitUserName, gitPassword)
        name = os.path.split(fontPath)[1].split('.')[0]
        self._RFont = NewFont(
            familyName=name, 
            styleName='Regular', 
            showUI = False
            )
        fontFilePath = '{}.ufo'.format(os.path.join(fontPath, name))
        self._RFont.save(fontFilePath)
        self._glyphs = {}

        self.getGlyphs()
        if 'fontLib.json' in os.listdir(self.fontPath):
            libPath = os.path.join(self.fontPath, 'fontLib.json')
            with open(libPath, 'r') as file:
                f = json.load(file)
            for k, v in f.items():
                self._RFont.lib[k] = v

    def __iter__(self):
        for name in self._RFont.keys():
            yield self[name]

    def __getitem__(self, name):
        return self._glyphs[self._RFont[name]]

    def __len__(self):
        return len(self._RFont)

    def __contains__(self, name):
        return name in self._RFont

    def keys(self):
        return self._RFont.keys()

    def shallowDocument(self):
        return self._RFont.shallowDocument()

    @property
    def _fontLayers(self):
        return [l.name for l in self._RFont.layers if l.name != 'foreground']

    def getGlyphs(self):
        for glyphName in self.deepComponentSet:
            fileName = files.userNameToFileName(glyphName)
            self.addGlyph(
                deepComponent.DeepComponent(glyphName), 
                fileName, 
                "foreground"
                )

        for glyphName in self.characterGlyphSet:
            fileName = files.userNameToFileName(glyphName)
            self.addGlyph(
                characterGlyph.CharacterGlyph(glyphName), 
                fileName, 
                "foreground"
                )

        for glyphName in self.atomicElementSet:
            fileName = files.userNameToFileName(glyphName)
            self.addGlyph(
                atomicElement.AtomicElement(glyphName), 
                fileName, 
                "foreground"
                )

        path = os.path.join(self.fontPath, 'atomicElement')

        for layerPath in [f.path for f in os.scandir(path) if f.is_dir()]:
            layerName = os.path.split(layerPath)[1]
            if layerName not in self._fontLayers:
                self._RFont.newLayer(layerName)

            for glifFile in filter(lambda x: x.endswith(".glif"), os.listdir(layerPath)):
                layerfileName = glifFile.split('.')[0]
                self.addGlyph(
                    atomicElement.AtomicElement(glyphName), 
                    layerfileName, 
                    layerName
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
        fileName = files.userNameToFileName(glyphName)
        path = os.path.join(self.fontPath, glyphType, "%s.glif"%fileName)
        files.makepath(path)
        with open(path, "w", encoding = "utf-8") as file:
            file.write(txt)
        return (emptyGlyph, fileName)

    def addGlyph(self, glyph, fileName, layerName):
        if layerName == 'foreground':
            glifPath = os.path.join(self.fontPath, glyph.type, "%s.glif"%fileName)
        else:
            glifPath = os.path.join(self.fontPath, glyph.type, layerName, "%s.glif"%fileName)
        tree = ET.parse(glifPath)
        root = tree.getroot()
        self.insertGlyph(glyph, ET.tostring(root), layerName)

    def insertGlyph(self, glyph, string, layerName):  
        if glyph is None: return
        glyph.setParent(self)
        pen = glyph.naked().getPointPen()
        readGlyphFromString(string, glyph.naked(), pen)
        layer = self._RFont.getLayer(layerName)
        layer.insertGlyph(glyph)
        self._glyphs[layer[glyph.name]] = glyph
        glyph._initWithLib()

    @property
    def atomicElementSet(self):
        return self._returnGlyphsList('atomicElement')

    @property
    def deepComponentSet(self):
        return self._returnGlyphsList('deepComponent')

    @property
    def characterGlyphSet(self):
        return self._returnGlyphsList('characterGlyph')

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
        self.addGlyph(*self.newGLIF(glyphType, glyphName), "foreground")

    @gitCoverage('font save')
    def save(self):
        self._RFont.save()

        libPath = os.path.join(self.fontPath, 'fontLib.json')
        with open(libPath, "w") as file:
            file.write(json.dumps(self._RFont.lib.asDict(),
                indent=4, separators=(',', ': ')))

        for rglyph in self._RFont.getLayer('foreground'):
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
                    # layerglyph = self._glyphs[f[glyph.name]]
                    layerglyph = f[glyph.name]
                    # layerglyph.save()
                    txt = layerglyph.dumpToGLIF()
                    fileName = "%s.glif"%files.userNameToFileName(layerglyph.name)
                    path = os.path.join(self.fontPath, glyphType, layerName, fileName)
                    files.makepath(path)
                    with open(path, "w", encoding = "utf-8") as file:
                        file.write(txt)

    def renameGlyph(self, oldName, newName):
        self.save()
        print(oldName,newName )
        f = self._RFont.getLayer('foreground')
        if newName in f.keys(): return
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
                for ae in dcg._atomicElements:
                    if ae["name"] == oldName:
                        ae["name"] = newName
            
        elif glyphType == "deepComponent":
            for n in self.characterGlyphSet:
                dcg = self[n]
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
            newPath = os.path.join(self.fontPath, glyphType, layerName, fileName)
            oldPath = os.path.join(self.fontPath, glyphType, layerName, oldFileName)
            with open(newPath, "w", encoding = "utf-8") as file:
                file.write(txt)
            os.remove(oldPath)

