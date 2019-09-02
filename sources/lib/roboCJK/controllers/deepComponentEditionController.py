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

    def loadProjectFonts(self):
        self.fontsList = []
        self.RCJKI.allFonts = []
        for name, file in self.RCJKI.project.masterFontsPaths.items():

            path = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Masters', file)

            deepComponentGlyphsEditionSavepath = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Temp', 'DeepComponents', 'Edition', "".join(self.RCJKI.project.script), "KeyAndExtremeCharacters", file)
            deepComponentGlyphsKeysSavepath = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'DeepComponents', "".join(self.RCJKI.project.script), file)

            f = OpenFont(path, showInterface=False)

            if not os.path.isdir(deepComponentGlyphsKeysSavepath):
                files.makepath(deepComponentGlyphsKeysSavepath)

                dcf = NewFont(familyName=f.info.familyName, styleName=f.info.styleName, showInterface=False)

                dcKeys = "".join([self.RCJKI.characterSets[key]['DeepComponentKeys'] for key in self.RCJKI.project.script])
                for dcKey in dcKeys:
                    glyphName = "DC_"+files.normalizeUnicode(hex(ord(dcKey))[2:].upper())

                    if dcKey in deepCompoMasters_AGB1_FULL.deepCompoMasters[self.RCJKI.project.script[0]]:
                        for i in range(len(deepCompoMasters_AGB1_FULL.deepCompoMasters[self.RCJKI.project.script[0]][dcKey])):
                            dcf.newGlyph(glyphName + "_%s"%str(i).zfill(2))

                dcf.save(deepComponentGlyphsKeysSavepath)

            if not os.path.isdir(deepComponentGlyphsEditionSavepath):
                files.makepath(deepComponentGlyphsEditionSavepath)
                
                nf = NewFont(familyName=f.info.familyName, styleName=f.info.styleName, showInterface=False)
                
                for c in self.characterSet:
                    glyphName = files.unicodeName(c)
                    if glyphName in f:
                        nf.insertGlyph(f[glyphName])

                nf.save(deepComponentGlyphsEditionSavepath)

                self.RCJKI.allFonts.append({name:nf})
                self.fontsList.append(name)

            else:
                nf = OpenFont(deepComponentGlyphsEditionSavepath, showInterface=False)
                
                glyph0rder = []
                for c in self.characterSet:
                    glyphName = files.unicodeName(c)
                    glyph0rder.append(glyphName)
                nf.glyphOrder = glyph0rder
                nf.save()

                self.RCJKI.allFonts.append({name:nf})
                self.fontsList.append(name)

            f.close()

        if self.interface:
            self.interface.w.fontsList.set(self.fontsList)



