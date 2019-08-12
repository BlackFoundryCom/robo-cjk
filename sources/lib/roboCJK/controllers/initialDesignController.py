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
import os
from mojo.roboFont import *
from views import initialDesignView
from utils import files
reload(initialDesignView)
reload(files)

class InitialDesignController(object):
    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.interface = None
        self.characterSet = None
        self.fontsList = []

    def launchInitialDesignInterface(self):
        self.characterSet = self.RCJKI.characterSets[self.RCJKI.project.script]['Basic']
        self.interface = initialDesignView.InitialDesignWindow(self)
        self.loadProjectFonts()

    def loadProjectFonts(self):
        self.fontsList = []
        self.RCJKI.allFonts = []
        for name, file in self.RCJKI.project.masterFontsPaths.items():
            path = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Masters', file)
            initialDesignSavepath = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Temp', 'InitialDesign', file)
            if not os.path.isdir(initialDesignSavepath):
                files.makepath(initialDesignSavepath)
                f = OpenFont(path, showInterface=False)
                nf = NewFont(familyName=f.info.familyName, styleName=f.info.styleName, showInterface=False)
                for c in self.characterSet:
                    glyphName = 'uni' + files.normalizeUnicode(hex(ord(c))[2:].upper())
                    if glyphName in f:
                        nf.insertGlyph(f[glyphName])
                f.close()
                nf.save(initialDesignSavepath)
                self.RCJKI.allFonts.append({name:nf})
                self.fontsList.append(name)
            else:
                f = OpenFont(initialDesignSavepath, showInterface=False)
                self.RCJKI.allFonts.append({name:f})
                self.fontsList.append(name)

        if self.interface:
            self.interface.w.fontsList.set(self.fontsList)

    def updateGlyphSetList(self):
        l = []
        if self.RCJKI.currentFont is not None:
            for c in self.characterSet:
                name = 'uni' + files.normalizeUnicode(hex(ord(c))[2:].upper())
                code = c
                l.append(({'#':'', 'Char':code, 'Name':name, 'MarkColor':''}))
        self.interface.w.glyphSetList.set(l)
