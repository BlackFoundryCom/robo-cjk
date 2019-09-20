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
from mojo.UI import PostBannerNotification
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
        self.designStep = "_initialDesign_glyphs"

    def launchInitialDesignInterface(self):
        self.setCharacterSet()
        if not self.interface:
            self.RCJKI.resetController()
            self.interface = initialDesignView.InitialDesignWindow(self)
            self.loadProjectFonts()

    def setCharacterSet(self):
        self.characterSet = "".join([self.RCJKI.characterSets[key]['Basic'] for key in self.RCJKI.project.script])

    def loadProjectFonts(self):
        self.fontsList = []
        self.RCJKI.allFonts = []
        for name, file in self.RCJKI.project.masterFontsPaths.items():
            path = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Masters', file)
            initialDesignSavepath = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Temp', 'InitialDesign', "".join(self.RCJKI.project.script), file)
            if not os.path.isdir(initialDesignSavepath):
                files.makepath(initialDesignSavepath)
                f = OpenFont(path, showInterface=False)
                nf = NewFont(familyName=f.info.familyName, styleName=f.info.styleName, showInterface=False)
                for c in self.characterSet:
                    glyphName = files.unicodeName(c)
                    if glyphName in f:
                        nf.insertGlyph(f[glyphName])
                f.close()
                nf.save(initialDesignSavepath)
                self.RCJKI.allFonts.append({name:nf})
                self.fontsList.append(name)
            else:
                f = OpenFont(initialDesignSavepath, showInterface=False)
                
                glyph0rder = []
                for c in self.characterSet:
                    glyphName = files.unicodeName(c)
                    glyph0rder.append(glyphName)
                f.glyphOrder = glyph0rder
                f.save()

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
            self.RCJKI.collab._addLocker(lck['user'], self.designStep)
        for lck in d['lockers']:
            locker = self.RCJKI.collab._userLocker(lck['user'])
            locker._addGlyphs(lck['glyphs'])

    def updateGlyphSetList(self):
        self.interface.w.glyphSetList.set(self.RCJKI.getGlyphSetList(self.characterSet, self.designStep))

    def injectGlyphsBack(self, glyphs, user):
        self.RCJKI.injectGlyphsBack(glyphs, user, self.designStep)
        self.RCJKI.saveProjectFonts()

    def pullMastersGlyphs(self):
        glyphs = []
        for c in self.characterSet:
            glyphName = files.unicodeName(c)
            if glyphName not in self.RCJKI.reservedGlyphs[self.designStep]:
                glyphs.append(glyphName)

        self.RCJKI.pullMastersGlyphs(glyphs, self.designStep)

