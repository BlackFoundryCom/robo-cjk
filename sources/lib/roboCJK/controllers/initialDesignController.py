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
from utils import git
reload(initialDesignView)
reload(files)
reload(git)

class InitialDesignController(object):
    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.interface = None
        self.characterSet = None
        self.fontsList = []

    def launchInitialDesignInterface(self):
        self.characterSet = self.RCJKI.characterSets[self.RCJKI.project.script]['Basic']
        if not self.interface:
            self.interface = initialDesignView.InitialDesignWindow(self)
            self.loadProjectFonts()

    def loadProjectFonts(self):
        self.fontsList = []
        self.RCJKI.allFonts = []
        for name, file in self.RCJKI.project.masterFontsPaths.items():
            path = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Masters', file)
            initialDesignSavepath = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Temp', 'InitialDesign', self.RCJKI.project.script, file)
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

    def refreshCollabFromFile(self):
        head, tail = os.path.split(self.RCJKI.projectFileLocalPath)
        title, ext = tail.split('.')
        tail = title + '.roboCJKCollab'
        collabFilePath = os.path.join(head, tail)
        collabFile = open(collabFilePath, 'r')
        d = json.load(collabFile)
        for lck in d['lockers']:
            self.RCJKI.collab._addLocker(lck['user'])
        for lck in d['lockers']:
            locker = self.RCJKI.collab._userLocker(lck['user'])
            locker._addGlyphs(lck['glyphs'])

    def updateGlyphSetList(self):
        l = []
        if self.RCJKI.currentFont is not None:
            later = []
            for c in self.characterSet:
                name = 'uni' + files.normalizeUnicode(hex(ord(c))[2:].upper())
                code = c
                if name in self.RCJKI.collab._userLocker(self.RCJKI.user).glyphs:
                    l.append(({'#':'', 'Char':code, 'Name':name, 'MarkColor':''}))
                else:
                    later.append(({'#':'', 'Char':code, 'Name':name, 'MarkColor':''}))
            l += later
        self.interface.w.glyphSetList.set(l)

    def saveSubsetFonts(self):
        for d in self.RCJKI.allFonts:
            for name, f in d.items():
                f.save()

    def injectGlyphsBack(self, glyphs, user):
        self.RCJKI.injectGlyphsBack(glyphs, user)
        self.RCJKI.saveProjectFonts()

    def pullMastersGlyphs(self):
        glyphs = []
        for c in self.characterSet:
            glyphName = 'uni' + files.normalizeUnicode(hex(ord(c))[2:].upper())
            if glyphName not in self.RCJKI.reservedGlyphs:
                glyphs.append(glyphName)

        self.RCJKI.pullMastersGlyphs(glyphs)

