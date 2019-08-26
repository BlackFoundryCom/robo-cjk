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

from mojo.events import addObserver, removeObserver, extractNSEvent
from mojo.roboFont import *
from mojo.UI import PostBannerNotification, OpenGlyphWindow, CurrentGlyphWindow
from AppKit import NSColor
from views import roboCJKView
from views.drawers import currentGlyphViewDrawer
from views import textCenterView
from controllers import projectEditorController
from controllers import initialDesignController
from controllers import toolsBoxController
from controllers import textCenterController
from tools import powerRuler
from resources import characterSets
from utils import git

reload(roboCJKView)
reload(currentGlyphViewDrawer)
reload(textCenterView)
reload(projectEditorController)
reload(initialDesignController)
reload(toolsBoxController)
reload(textCenterController)
reload(characterSets)
reload(git)
reload(powerRuler)


class RoboCJKController(object):
    def __init__(self):
        self.observers = False
        self.project = None
        self.projectFileLocalPath = None
        self.collab = None
        self.projectFonts = {}
        self.scriptsList = ['Hanzi', 'Hangul', 'Kana']
        self.characterSets = characterSets.sets
        self.currentFont = None
        self.currentGlyph = None
        self.allFonts = []
        self.lockedGlyphs = []
        self.reservedGlyphs = []
        self.user = git.GitEngine(None).user()
        self.settings = {
            'showDesignFrame':True,
            'designFrame':{'showMainFrames': True,
                            'showSecondLines': True,
                            'showCustomsFrames': True,
                            'showproximityPoints': True,
                            'translate_secondLine_X': 0,
                            'translate_secondLine_Y': 0,
                            'drawPreview': False,
                            },

            'stackMasters': True,
            'stackMastersColor': NSColor.colorWithCalibratedRed_green_blue_alpha_(0, .3, 1, .3),
            'waterFall': False,
            'waterFallColor': NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1),

            'interpolaviour':{'onOff': False,
                            'showPoints': False,
                            'showStartPoints': False,
                            'showInterpolation': True,
                            'interpolationValue': .5,
                            'interpolationColor': NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 1, 1),
                            },
            'referenceViewer' : {
                            'onOff': True,
                            'drawPreview': False,
                            }
        }
        self.projectEditorController = projectEditorController.ProjectEditorController(self)
        self.initialDesignController = initialDesignController.InitialDesignController(self)
        self.toolsBoxController = toolsBoxController.toolsBoxController(self)
        self.textCenterController = textCenterController.textCenterController(self)
        

        self.textCenterInterface = None

    def toggleObservers(self, forceKill=False):
        if self.observers or forceKill:
            removeObserver(self, "draw")
            removeObserver(self, "drawPreview")
            removeObserver(self, "drawInactive")
            removeObserver(self, "keyDown")
            # removeObserver(self, "viewWillChangeGlyph")
        else:
            addObserver(self, "drawInGlyphWindow", "draw")
            addObserver(self, "drawInGlyphWindow", "drawPreview")
            addObserver(self, "drawInGlyphWindow", "drawInactive")
            addObserver(self, "keyDownInGlyphWindow", "keyDown")
            # addObserver(self, "viewWillChangeGlyph", "viewWillChangeGlyph")

        self.observers = not self.observers

    # def viewWillChangeGlyph(self, info):
    #     print(info)

    def launchInterface(self):
        self.interface = roboCJKView.RoboCJKWindow(self)
        self.powerRuler = powerRuler.Ruler(self)
        self.updateUI()

    def updateUI(self):
        self.interface.w.initialDesignEditorButton.enable(self.project!=None)
        self.interface.w.textCenterButton.enable(self.project!=None)
        self.interface.w.deepComponentEditorButton.enable(self.project!=None)
        self.interface.w.toolsBoxButton.enable(self.project!=None)

    def launchTextCenterInterface(self):
        if self.textCenterInterface is None:
            self.textCenterInterface = textCenterView.TextCenterWindow(self)

    def drawInGlyphWindow(self, info):
        if self.currentGlyph is None: return
        currentGlyphViewDrawer.CurrentGlyphViewDrawer(self).draw(info)

    def keyDownInGlyphWindow(self, info):
        if self.currentGlyph is None: return

        modifier = extractNSEvent(info)
        commandDown = modifier['commandDown']

        character = info["event"].characters()

        if commandDown and character == "s":
            self.initialDesignController.saveSubsetFonts()
            

    def injectGlyphsBack(self, glyphs, user):
        for d in self.allFonts:
            for name, subsetFont in d.items():
                if name in self.projectFonts:
                    f = self.projectFonts[name]
                    for glyphName in glyphs:
                        if glyphName in self.reservedGlyphs:
                            f.insertGlyph(subsetFont[glyphName].naked())
                    f.save()

    def pullMastersGlyphs(self, glyphs):
        self.projectEditorController.loadProject([self.projectFileLocalPath])
        for d in self.allFonts:
            for name, subsetFont in d.items():
                if name in self.projectFonts:
                    f = self.projectFonts[name]
                    for glyphName in glyphs: 
                        if glyphName not in self.reservedGlyphs:
                            subsetFont[glyphName] = RGlyph(f[glyphName])
                    subsetFont.save()

    def saveProjectFonts(self):
        rootfolder = os.path.split(self.projectFileLocalPath)[0]
        gitEngine = git.GitEngine(rootfolder)
        gitEngine.pull()
        for name in self.projectFonts:
            f = self.projectFonts[name]
            f.save()
        stamp = "Masters Fonts Saved"
        gitEngine.commit(stamp)
        gitEngine.push()
        PostBannerNotification('Git Push', stamp)

    def openGlyphWindow(self, glyph):
        self.currentGlyphWindow = CurrentGlyphWindow()
        if self.currentGlyphWindow is not None:
            self.currentGlyphWindow.setGlyph(glyph)
            self.currentGlyphWindow.w.getNSWindow().makeKeyAndOrderFront_(self)
        else:
            self.currentGlyphWindow = OpenGlyphWindow(glyph)
            self.currentGlyphWindow.w.bind("became main", self.glyphWindowBecameMain)
            self.currentGlyphWindow.w.bind("close", self.glyphWindowCloses)

    def glyphWindowBecameMain(self, sender):
        # print(self.currentGlyph)
        self.currentGlyph = self.currentFont[self.currentGlyphWindow.getGlyph().name]
        # print(self.currentGlyph)
        self.toolsBoxController.updateViews()

    def glyphWindowCloses(self, sender):
        self.currentGlyphWindow = None

