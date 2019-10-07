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
from views import keysAndExtremesEditionView
from resources import deepCompo2Chars
from resources import deepCompoMasters_AGB1_FULL
from utils import files
from utils import git
reload(keysAndExtremesEditionView)
reload(files)
reload(git)

class KeysAndExtremsEditionController(object):

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.interface = None
        self.characterSet = None
        self.fontsList = []


    def launchkeysAndExtremsEditionInterface(self):
        self.setCharacterSet()
        if not self.interface:
            self.RCJKI.resetController()
            self.RCJKI.designStep = "_keysAndExtrems_glyphs"
            self.interface = keysAndExtremesEditionView.KeysAndExtremsEditionWindow(self)
            self.loadProjectFonts()
            

    def setCharacterSet(self):
        self.characterSet = "".join([self.RCJKI.characterSets[key]['DeepComponentKeys'] for key in self.RCJKI.project.script])

    def loadProjectFonts(self):
        self.fontsList = []
        self.RCJKI.allFonts = []
        for name, file in self.RCJKI.project.masterFontsPaths.items():
            path = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Masters', file)
            initialDesignSavepath = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Temp', 'keysAndExtrems', "".join(self.RCJKI.project.script), file)
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
                
                glyphOrder = []
                for c in self.characterSet:
                    glyphName = files.unicodeName(c)
                    glyphOrder.append(glyphName)
                f.glyphOrder = glyphOrder
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
            self.RCJKI.collab._addLocker(lck['user'], self.RCJKI.designStep)
        for lck in d['lockers']:
            locker = self.RCJKI.collab._userLocker(lck['user'])
            locker._addGlyphs(lck['glyphs'])

    def updateGlyphSetList(self):
        self.interface.w.glyphSetList.set(self.RCJKI.getGlyphSetList(self.characterSet, self.RCJKI.designStep))

    def updateCharactersSetList(self, gname):
        l = []
        later = []
        if self.RCJKI.currentFont is not None:
            char = chr(int(gname[3:],16))
            script = self.RCJKI.collab._userLocker(self.RCJKI.user).script
            if char in deepCompoMasters_AGB1_FULL.deepCompoMasters[script]:
                charsLists = deepCompoMasters_AGB1_FULL.deepCompoMasters[script][char]
                for li in charsLists:
                    for c in li:
                        charname = files.unicodeName(c)
                        if charname in self.RCJKI.collab._userLocker(self.RCJKI.user).glyphs[self.RCJKI.designStep]:
                            l.append(({'#':'', 'Char':c, 'Name':charname, 'MarkColor':''}))
                        else:
                            later.append(({'#':'', 'Char':c, 'Name':charname, 'MarkColor':''}))
            l += later
        self.interface.w.charactersSetList.set(l)
        if len(l):
            self.interface.w.charactersSetList.setSelection([0])

    def injectGlyphsBack(self, glyphs, user):
        self.RCJKI.injectGlyphsBack(glyphs, user, self.RCJKI.designStep)
        self.RCJKI.saveProjectFonts()

    def pullMastersGlyphs(self):
        glyphs = []
        for c in self.characterSet:
            glyphName = files.unicodeName(c)
            if glyphName not in self.RCJKI.reservedGlyphs[self.RCJKI.designStep]:
                glyphs.append(glyphName)

        self.RCJKI.pullMastersGlyphs(glyphs, self.RCJKI.designStep)

