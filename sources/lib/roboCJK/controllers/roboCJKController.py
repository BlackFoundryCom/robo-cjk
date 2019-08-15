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

from mojo.events import addObserver, removeObserver
from views import roboCJKView
from views import currentGlyphViewDrawer
from controllers import projectEditorController
from controllers import initialDesignController
from resources import characterSets
from utils import git

reload(projectEditorController)
reload(initialDesignController)
reload(roboCJKView)
reload(characterSets)
reload(git)


class RoboCJKController(object):
    def __init__(self):
        self.observers = False
        self.project = None
        self.projectFileLocalPath = None
        self.collab = None
        self.projectFonts = {}
        self.scriptsList = ['Hanzi', 'Hangul']
        self.characterSets = characterSets.sets
        self.currentFont = None
        self.currentGlyph = None
        self.allFonts = []
        self.lockedGlyphs = []
        self.reservedGlyphs = []
        self.user = git.GitEngine(None).user()
        self.settings = {
            'designFrame':{'showMainFrames': True,
                            'showSecondLines': True,
                            'showCustomsFrames': True,
                            'showproximityPoints': True,
                            'translate_secondLine_X': True,
                            'translate_secondLine_Y': True
                            },
            'stackMasters': True
        }
        self.projectEditorController = projectEditorController.ProjectEditorController(self)
        self.initialDesignController = initialDesignController.InitialDesignController(self)
    
    def toggleObservers(self, forceKill=False):
        if self.observers or forceKill:
            removeObserver(self, "draw")
            removeObserver(self, "drawPreview")
            removeObserver(self, "drawInactive")
        else:
            addObserver(self, "drawInGlyphWindow", "draw")
            addObserver(self, "drawInGlyphWindow", "drawPreview")
            addObserver(self, "drawInGlyphWindow", "drawInactive")
        self.observers = not self.observers

    def launchInterface(self):
        self.interface = roboCJKView.RoboCJKWindow(self)

    def drawInGlyphWindow(self, info):
        if self.currentGlyph is None: return
        currentGlyphViewDrawer.CurrentGlyphViewDrawer(self).draw(info)