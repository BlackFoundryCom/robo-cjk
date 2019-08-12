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

from views import initialDesignView
from utils import files
reload(initialDesignView)
reload(files)

class InitialDesignController(object):
    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.interface = None
        self.characterSet = None

    def launchInitialDesignInterface(self):
        self.characterSet = self.RCJKI.characterSets[self.RCJKI.project.script]['Basic']
        self.interface = initialDesignView.InitialDesignWindow(self)

    def updateGlyphSetList(self):
        l = []
        if self.RCJKI.currentFont:
            for c in self.characterSet:
                name = 'uni' + files.normalizeUnicode(hex(ord(c))[2:].upper())
                code = c
                l.append(({'#':'', 'Char':code, 'Name':name}))
        self.interface.w.glyphSetList.set(l)
