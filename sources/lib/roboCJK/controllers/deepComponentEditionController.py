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
from imp import reload
from views import deepComponentEditionView
import os
from utils import files
from utils import git
from mojo.roboFont import *
from mojo.UI import PostBannerNotification
from resources import deepCompoMasters_AGB1_FULL

reload(deepComponentEditionView)
reload(deepCompoMasters_AGB1_FULL)

class DeepComponentEditionController(object):

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.interface = None
        self.characterSet = None
        self.fontsList = []

        """
        MASTER FONTS
        MASTER DEEP COMPONENTS FONTS (with all dc keys)

        MINI UNICODE DEEP COMPONENTS FONTS (with unicode characters from locker list, and associated extrems versions) -> KeyAndExtremeCharacters
        MINI DEEP COMPONENTS FONTS (with DCNamed glyphs from locker list) -> DeepComponentsGlyphs -> only these glyphs will be injected back

        """

    def launchDeepComponentEditionInterface(self):
        self.setCharacterSet()
        if not self.interface:
            self.interface = deepComponentEditionView.DeepComponentEditionWindow(self)
            self.loadProjectFonts()

    def setCharacterSet(self):
        self.characterSet = "".join([self.RCJKI.characterSets[key]['DeepComponentKeys'] for key in self.RCJKI.project.script])
        self.characterSet += "".join([k for key in self.RCJKI.project.script for k in self.RCJKI.characterSets[key]['Basic'] if k not in self.characterSet])
        # print(self.characterSet, deepCompoMasters_AGB1_FULL.Hanzi)

    def updateGlyphSetList(self):
        l = []
        if self.RCJKI.currentFont is not None:
            later = []
            for c in self.characterSet:
                name = files.unicodeName(c)
                code = c
                if name in self.RCJKI.collab._userLocker(self.RCJKI.user).glyphs['_deepComponentsEdition_glyphs']:
                    l.append(({'#':'', 'Char':code, 'Name':name, 'MarkColor':''}))
                else:
                    later.append(({'#':'', 'Char':code, 'Name':name, 'MarkColor':''}))
            l += later
        self.interface.w.glyphSetList.set(l)

    def updateDeepComponentsSetList(self, glyphName):
        l = []
        if self.RCJKI.currentFont is not None:
            dcset = list(filter(lambda x: glyphName[3:] in x, list(self.RCJKI.currentFont.keys())))
            for name in sorted(dcset):
                _, gname, index = name.split("_")
                code = deepCompoMasters_AGB1_FULL.deepCompoMasters["Hanzi"][chr(int(gname,16))][int(index)][0]
                l.append(({'#':'', 'Char':code, 'Name':name, 'MarkColor':''}))
        self.interface.w.deepComponentsSetList.set(l)

    def saveSubsetFonts(self):
        for f in self.RCJKI.fonts2DCFonts.values():
            f.save()
        PostBannerNotification("Fonts saved", "")

    def injectGlyphsBack(self, glyphs, user):
        self.RCJKI.injectGlyphsBack(glyphs, user)
        self.RCJKI.saveProjectFonts()

    def loadProjectFonts(self):
        self.fontsList = []
        self.RCJKI.allFonts = []
        self.RCJKI.fonts2DCFonts = {}

        for name, file in self.RCJKI.project.masterFontsPaths.items():

            path = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Masters', file)

            deepComponentGlyphsKeyAndXtremSavepath = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Temp', 'DeepComponents', 'Edition', "".join(self.RCJKI.project.script), "KeyAndExtremeCharacters", file)
            deepComponentGlyphsSubsetSavepath = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Temp', 'DeepComponents', 'Edition', "".join(self.RCJKI.project.script), "DeepComponentsGlyphs", file)
            deepComponentGlyphsMasterSavepath = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'DeepComponents', "".join(self.RCJKI.project.script), file)

            f = OpenFont(path, showInterface=False)

            #### MASTER DEEP COMPONENTS FONT -> DeepComponents/*script*/*.ufo
            if not os.path.isdir(deepComponentGlyphsMasterSavepath):
                files.makepath(deepComponentGlyphsMasterSavepath)

                masterDeepComponentsGlyphs = NewFont(familyName=f.info.familyName, styleName=f.info.styleName, showInterface=False)

                masterDCFonts = "".join([self.RCJKI.characterSets[key]['DeepComponentKeys'] for key in self.RCJKI.project.script])
                for masterDCFont in masterDCFonts:
                    glyphName = "DC_"+files.normalizeUnicode(hex(ord(masterDCFont))[2:].upper())

                    for script in self.RCJKI.project.script:
                        if masterDCFont in deepCompoMasters_AGB1_FULL.deepCompoMasters[script]:
                            for i in range(len(deepCompoMasters_AGB1_FULL.deepCompoMasters[script][masterDCFont])):
                                masterDeepComponentsGlyphs.newGlyph(glyphName + "_%s"%str(i).zfill(2))

                masterDeepComponentsGlyphs.save(deepComponentGlyphsMasterSavepath)
            else:
                masterDeepComponentsGlyphs = OpenFont(deepComponentGlyphsMasterSavepath, showInterface = False)

            #### KEYS AND EXTREMES CHARACTERS -> Temp/DeepComponents/Edition/*script*/KeyAndExtremeCharacters/*.ufo
            if not os.path.isdir(deepComponentGlyphsKeyAndXtremSavepath):
                files.makepath(deepComponentGlyphsKeyAndXtremSavepath)
                
                keyAndXtremChars = NewFont(familyName=f.info.familyName, styleName=f.info.styleName, showInterface=False)
                
                for c in self.characterSet:
                    glyphName = files.unicodeName(c)
                    if glyphName in f:
                        keyAndXtremChars.insertGlyph(f[glyphName])

                keyAndXtremChars.save(deepComponentGlyphsKeyAndXtremSavepath)
            else:
                keyAndXtremChars = OpenFont(deepComponentGlyphsKeyAndXtremSavepath, showInterface=False)
                
                glyph0rder = []
                for c in self.characterSet:
                    glyphName = files.unicodeName(c)
                    glyph0rder.append(glyphName)
                keyAndXtremChars.glyphOrder = glyph0rder
                keyAndXtremChars.save()

            self.RCJKI.allFonts.append({name:keyAndXtremChars})
            self.fontsList.append(name)

            #### DEEP COMPONENTS GLYPHS -> Temp/DeepComponents/Edition/*script*/DeepComponentsGlyphs/*.ufo
            if not os.path.isdir(deepComponentGlyphsSubsetSavepath):
                files.makepath(deepComponentGlyphsSubsetSavepath)

                deepComponentsGlyphs = NewFont(familyName=f.info.familyName, styleName=f.info.styleName, showInterface=False)

                for layer in masterDeepComponentsGlyphs.layers:
                    deepComponentsGlyphs.newLayer(layer.name)

                DCGlyphsSet = []
                lockerGlyphs = self.RCJKI.collab._userLocker(self.RCJKI.user).glyphs["_deepComponentsEdition_glyphs"]
                for glyphName in lockerGlyphs:
                    DCGlyphsSet.extend(list(filter(lambda x: glyphName[3:] in x, list(masterDeepComponentsGlyphs.keys()))))

                for glyphName in DCGlyphsSet:
                    for layer in masterDeepComponentsGlyphs.layers:
                        deepComponentsGlyphs.getLayer(layer.name).insertGlyph(masterDeepComponentsGlyphs[glyphName].getLayer(layer.name))
                
                deepComponentsGlyphs.save(deepComponentGlyphsSubsetSavepath)
            else:
                deepComponentsGlyphs = OpenFont(deepComponentGlyphsSubsetSavepath, showInterface=False)

            self.RCJKI.fonts2DCFonts[keyAndXtremChars] = deepComponentsGlyphs

            f.close()
            masterDeepComponentsGlyphs.close()

        if self.interface:
            self.interface.w.fontsList.set(self.fontsList)



