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
from vanilla import *
from vanilla.dialogs import getFolder, putFile, askYesNo, message
from mojo.canvas import Canvas
from fontParts.ui import AskYesNoCancel, AskString
from mojo.UI import OpenGlyphWindow, AllWindows, CurrentGlyphWindow, UpdateCurrentGlyphView, PostBannerNotification, SetCurrentLayerByName
from defconAppKit.windows.baseWindow import BaseWindowController
from views import canvasGroups
from mojo.canvas import CanvasGroup
import mojo.drawingTools as mjdt
# from lib.doodleDocument import DoodleDocument
from AppKit import NSFont, NumberFormatter, NSColor
from imp import reload
from utils import decorators, files
from lib.cells.colorCell import RFColorCell
from collections import defaultdict
# reload(decorators)
# reload(files)
# reload(canvasGroups)
from models import font
# reload(font)
from views import sheets
# reload(sheets)
from views import PDFProofer

from controllers import teamManager
# reload(PDFProofer)
from views import scriptingWindow
# reload(scriptingWindow)
from views import textCenter
# reload(textCenter)

from mojo.events import addObserver, removeObserver

import os, json, copy, time
import threading
import queue

# import BF_fontbook_struct as bfs
# import BF_rcjk2mysql

gitCoverage = decorators.gitCoverage
lockedProtect = decorators.lockedProtect
refresh = decorators.refresh

from mojo.roboFont import *
from datetime import datetime
import threading
import queue

from utils import colors
INPROGRESS = colors.INPROGRESS
CHECKING1 = colors.CHECKING1
CHECKING2 = colors.CHECKING2
CHECKING3 = colors.CHECKING3
DONE = colors.DONE

EditButtonImagePath = os.path.join(os.getcwd(), "resources", "EditButton.pdf")
removeGlyphImagePath = os.path.join(os.getcwd(), "resources", "removeButton.pdf")
duplicateGlyphImagePath = os.path.join(os.getcwd(), "resources", "duplicateButton.pdf")
localiseGlyphImagePath = os.path.join(os.getcwd(), "resources", "localiseButton.pdf")

class SmartTextBox(TextBox):
    def __init__(self, posSize, text="", alignment="natural", 
        selectable=False, callback=None, sizeStyle=40.0,
        red=0,green=0,blue=0, alpha=1.0):
        super().__init__(posSize, text=text, alignment=alignment, 
            selectable=selectable, sizeStyle=sizeStyle)
        
    def _setSizeStyle(self, sizeStyle):
        value = sizeStyle
        self._nsObject.cell().setControlSize_(value)
        font = NSFont.systemFontOfSize_(value)
        self._nsObject.setFont_(font)

def getRelatedGlyphs(font, glyphName, regenerated = []):
    g = font.get(glyphName)
    if glyphName not in regenerated:
        if not font.mysql:
            q = queue.Queue()
            threading.Thread(target=font.queueGetGlyphs, args = (q, g.type), daemon=True).start()
            q.put([glyphName])
        else:
            font.getmySQLGlyph(glyphName)
        regenerated.append(glyphName)
    if not hasattr(g, "_deepComponents"): return
    for dc in g._deepComponents:
        getRelatedGlyphs(font, dc['name'], regenerated)

# This function is outside of any class
def openGlyphWindowIfLockAcquired(RCJKI, glyph):
    start = time.time()
    font = RCJKI.currentFont
    g = glyph._RGlyph
    # font[glyphName]._initWithLib()
    # locked, alreadyLocked = font.locker.lock(g)
    locked, alreadyLocked = font.lockGlyph(g)
    RCJKI.currentGlyphIsLocked = locked
    if not RCJKI.mysql:
        print(locked, alreadyLocked)
        if not locked: return
        if not alreadyLocked:
            RCJKI.gitEngine.pull()
            # font.getGlyphs()
            getRelatedGlyphs(font, glyph.name)
            # font.getGlyph(font[glyphName])
            # g = font.get(glyphName, font._RFont)._RGlyph
    else:
        # if not locked: return
        getRelatedGlyphs(font, glyph.name)
    if not g.width:
        g.width = font.defaultGlyphWidth
    try:
        CurrentGlyphWindow().close()
    except: pass
    # font.get(glyphName, font._RFont).update()
    glyph = font.get(glyph.name, font._RFont)
    glyph.update()
    g = glyph._RGlyph
    window = OpenGlyphWindow(g)
    window.window().setPosSize(RCJKI.glyphWindowPosSize)
    if not locked:
        message(
            "The couldn't be locked, so changes will not be saved",
            parentWindow=window.window(),
        )
    RCJKI.openedGlyphName = glyph.name
    stop = time.time()
    RCJKI.disabledEditingUIIfValidated()
    print(stop-start, 'to open a %s'%glyph.name)


class RoboCJKView(BaseWindowController):
    
    def __init__(self, RCJKI):
        x = RFColorCell.alloc().init()
        listRFColorCell = RFColorCell.alloc().init()
        statusColumnDescriptions = [
            dict(title="color", key="color", cell=listRFColorCell, width=30),
            dict(title="sourceName", key="sourceName", editable=False, width=80),
            dict(title="status", cell=PopUpButtonListCell(colors.names), binding="selectedValue")
            ]

        self.RCJKI = RCJKI
        self.prevGlyphName = None
        self.w = Window(
            (620, 670), 
            'RoboCJK'
            )

        self.w.loadProjectButton = Button(
            (10, 10, 200, 20), 
            "Login & load projects", 
            callback = self.loadProjectButtonCallback,
            )
        self.w.setDefaultButton(self.w.loadProjectButton)
        self.w.saveProjectButton = Button(
            (210, 10, 200, 20), 
            "Save font", 
            callback = self.saveProjectButtonCallback,
            )
        self.w.saveProjectButton.enable(False)

        self.w.newProjectButton = Button(
            (410, 10, 200, 20), 
            "New font", 
            callback = self.newProjectButtonCallback,
            )
        self.w.newProjectButton.enable(False)

        self.w.fontInfos = Button(
            (210, 40, 200, 20), 
            "Fonts Infos", 
            callback = self.fontInfosCallback,
            )
        self.w.fontInfos.enable(False)

        self.w.pdfProoferButton = Button(
            (410, 40, 200, 20), 
            "PDF Proofer", 
            callback = self.pdfProoferButtonCallback,
            )
        self.w.pdfProoferButton.enable(False)

        self.w.rcjkFiles = PopUpButton(
            (10, 40, 180, 20),
            [],
            callback = self.rcjkFilesSelectionCallback
            )
        self.w.rcjkFiles.enable(False)

        self.w.reloadProject = ImageButton(
            (190, 40, 20, 20),
            imagePath = os.path.join(os.getcwd(), "resources/reloadIcon.pdf"),
            bordered = False,
            callback = self.reloadProjectCallback
            )

        # self.w.generateFontButton = Button(
        #     (10, 70, 200, 20),
        #     "generateFont",
        #     callback = self.generateFontButtonCallback,
        #     )
        # self.w.generateFontButton.enable(False)

        # self.w.teamManagerButton = Button(
        #     (10, 100, 200, 20),
        #     "Team manager",
        #     callback = self.teamManagerButtonCallback,
        #     )
        # self.w.teamManagerButton.enable(False)

        self.RCJKI.textCenterWindows = []
        self.w.textCenterButton = Button(
            (410, 70, 200, 20),
            "Text Center",
            callback = self.textCenterButtonCallback,
            )
        self.w.textCenterButton.enable(False)

        self.w.codeEditorButton = Button(
            (10, 70, 200, 20),
            "Scripting Window",
            callback = self.codeEditorButtonCallback,
            )
        self.w.codeEditorButton.enable(False)

        self.w.lockControllerDCButton = Button(
            (210, 70, 200, 20),
            "Lock controller",
            callback = self.lockControllerDCButtonCallback,
            )
        self.w.lockControllerDCButton.enable(False)

        self.w.lockerInfoTextBox = TextBox(
            (210, 100, 200, 20),
            "",
            alignment='center'
            )

        self.w.firstFilterAtomicElement = PopUpButton(
            (10, 120, 80, 20),
            ["All those", "Locked and"],
            callback = self.filterAtomicElementCallback,
            sizeStyle = "mini"
            )
        self.w.secondFilterAtomicElement = PopUpButton(
            (90, 120, 120, 20),
            [
            "that are in font", 
            "that are not empty", 
            "that are empty", 
            "that have outlines",
            "that are in progress", 
            "that are checking 1", 
            "that are checking 2", 
            "that are checking 3", 
            "that are done"
            ],
            callback = self.filterAtomicElementCallback,
            sizeStyle = "mini"
            )
        self.w.firstFilterAtomicElement.enable(False)
        self.w.secondFilterAtomicElement.enable(False)

        self.w.atomicElementSearchBox = SearchBox(
            (10, 140, 200, 20),
            callback = self.atomicElementSearchBoxCallback
            )
        self.w.atomicElementSearchBox.enable(False)
        self.w.atomicElement = List(
            (10, 160, 200, 190),
            [],
            allowsMultipleSelection = False,
            doubleClickCallback = self.GlyphsListDoubleClickCallback,
            editCallback = self.GlyphsListEditCallback,
            selectionCallback = self.GlyphsListSelectionCallback, 
            )

        self.w.removeAtomicElement = ImageButton(
            (10, 350, 20, 20),
            imagePath = removeGlyphImagePath,
            bordered = False,
            callback = self.removeAtomicElementCallback
            )
        self.w.removeAtomicElement.enable(False)
        self.w.duplicateAtomicElement = ImageButton(
            (190, 350, 20, 20),
            imagePath = duplicateGlyphImagePath,
            bordered = False,
            callback = self.duplicateAtomicElementCallback
            )
        self.w.duplicateAtomicElement.enable(False)
        self.w.localiseAtomicElement = ImageButton(
            (170, 350, 20, 20),
            imagePath = localiseGlyphImagePath,
            bordered = False,
            callback = self.localiseAtomicElementCallback
            )
        self.w.localiseAtomicElement.enable(False)
        self.w.newAtomicElement = Button(
            (30, 350, 140, 20),
            "New AE",
            callback = self.newAtomicElementCallback
            )
        self.w.newAtomicElement.enable(False)
        self.w.atomicElementPreview = canvasGroups.GlyphPreviewCanvas(
            (10, 372, 200, -70),
            self.RCJKI,
            glyphType = "atomicElement")

        self.w.atomicElementStatusList = List((10, -70, 200, -0), [], 
            columnDescriptions=statusColumnDescriptions,
            editCallback = self.glyphStatusListEditCallback,
            showColumnTitles = False
            )
        # self.w.atomicElementDesignStepPopUpButton = PopUpButton(
        #     (10, -20, 100, -0), 
        #     [
        #     "In Progress", 
        #     "Checking 1", 
        #     "Checking 2", 
        #     "Checking 3", 
        #     "Done"
        #     ],
        #     callback = self.atomicElementDesignStepPopUpButtonCallback
        #     )
        # self.w.atomicElementDesignStepPopUpButton.enable(False)

        self.w.firstFilterDeepComponent = PopUpButton(
            (210, 120, 80, 20),
            ["All those", "Locked and"],
            callback = self.filterDeepComponentCallback,
            sizeStyle = "mini"
            )
        self.w.secondFilterDeepComponent = PopUpButton(
            (290, 120, 120, 20),
            [
            "that are in font", 
            "that are not empty", 
            "that are empty", 
            "that have outlines", 
            "that are not locked",
            "that are in progress", 
            "that are checking 1", 
            "that are checking 2", 
            "that are checking 3", 
            "that are done"
            ],
            callback = self.filterDeepComponentCallback,
            sizeStyle = "mini"
            )
        self.w.firstFilterDeepComponent.enable(False)
        self.w.secondFilterDeepComponent.enable(False)

        self.w.deepComponentSearchBox = SearchBox(
            (210, 140, 200, 20),
            callback = self.deepComponentSearchBoxCallback
            )
        self.w.deepComponentSearchBox.enable(False)
        self.w.deepComponent = List(
            (210, 160, 200, 190),
            [],
            allowsMultipleSelection = False,
            doubleClickCallback = self.GlyphsListDoubleClickCallback,
            editCallback = self.GlyphsListEditCallback,
            selectionCallback = self.GlyphsListSelectionCallback, 
            )
        self.w.removeDeepComponent = ImageButton(
            (210, 350, 20, 20),
            imagePath = removeGlyphImagePath,
            bordered = False,
            callback = self.removeDeepComponentCallback
            )
        self.w.removeDeepComponent.enable(False)
        self.w.duplicateDeepComponent = ImageButton(
            (390, 350, 20, 20),
            imagePath = duplicateGlyphImagePath,
            bordered = False,
            callback = self.duplicateDeepComponentCallback
            )
        self.w.duplicateDeepComponent.enable(False)
        self.w.localiseDeepComponent = ImageButton(
            (370, 350, 20, 20),
            imagePath = localiseGlyphImagePath,
            bordered = False,
            callback = self.localiseDeepComponentCallback
            )
        self.w.localiseDeepComponent.enable(False)
        self.w.newDeepComponent = Button(
            (230, 350, 140, 20),
            "New DC",
            callback = self.newDeepComponentCallback
            )
        self.w.newDeepComponent.enable(False)
        self.w.deepComponentPreview = canvasGroups.GlyphPreviewCanvas(
            (210, 372, 200, -70),
            self.RCJKI,
            glyphType = "deepComponent")

        self.w.deepComponentStatusList = List((210, -70, 200, -0), [], 
            columnDescriptions=statusColumnDescriptions,
            editCallback = self.glyphStatusListEditCallback,
            showColumnTitles = False
            )
        # self.w.deepComponentDesignStepPopUpButton = PopUpButton(
        #     (210, -20, 100, -0), 
        #     [
        #     "In Progress", 
        #     "Checking 1", 
        #     "Checking 2", 
        #     "Checking 3", 
        #     "Done"
        #     ],
        #     callback = self.deepComponentDesignStepPopUpButtonCallback
        #     )
        # self.w.deepComponentDesignStepPopUpButton.enable(False)

        self.w.firstFilterCharacterGlyph = PopUpButton(
            (410, 120, 80, 20),
            ["All those", "Locked and"],
            callback = self.filterCharacterGlyphCallback,
            sizeStyle = "mini"
            )
        self.w.secondFilterCharacterGlyph = PopUpButton(
            (490, 120, 120, 20),
            [
            "that are in font", 
            "that can be fully designed", 
            "that are not empty", 
            "that are empty", 
            "that have outlines", 
            "that are not locked",
            "that are in progress", 
            "that are checking 1", 
            "that are checking 2", 
            "that are checking 3", 
            "that are done"
            ],
            callback = self.filterCharacterGlyphCallback,
            sizeStyle = "mini"
            )
        self.w.firstFilterCharacterGlyph.enable(False)
        self.w.secondFilterCharacterGlyph.enable(False)
        self.w.characterGlyphSearchBox = SearchBox(
            (410, 140, 200, 20),
            callback = self.characterGlyphearchBoxCallback
            )
        self.w.characterGlyphSearchBox.enable(False)
        self.w.characterGlyph = List(
            (410, 160, 200, 190),
            [],
            columnDescriptions = [
                {"title":"char", "width":20, "editable":False}, 
                {"title":"name"}
                ],
            drawFocusRing = False,
            showColumnTitles = False,
            allowsMultipleSelection = False,
            doubleClickCallback = self.GlyphsListDoubleClickCallback,
            editCallback = self.GlyphsListEditCallback,
            selectionCallback = self.GlyphsListSelectionCallback, 
            )
        self.w.removeCharacterGlyph = ImageButton(
            (410, 350, 20, 20),
            imagePath = removeGlyphImagePath,
            bordered = False,
            callback = self.removeCharacterGlyphCallback
            )
        self.w.removeCharacterGlyph.enable(False)
        self.w.duplicateCharacterGlyph = ImageButton(
            (590, 350, 20, 20),
            imagePath = duplicateGlyphImagePath,
            bordered = False,
            callback = self.duplicateCharacterGlyphCallback
            )
        self.w.duplicateCharacterGlyph.enable(False)
        self.w.localiseCharacterGlyph = ImageButton(
            (570, 350, 20, 20),
            imagePath = localiseGlyphImagePath,
            bordered = False,
            callback = self.localiseCharacterGlyphCallback
            )
        self.w.localiseCharacterGlyph.enable(False)
        self.w.newCharacterGlyph = Button(
            (430, 350, 140, 20),
            "New CG",
            callback = self.newCharacterGlyphCallback
            )
        self.w.newCharacterGlyph.enable(False)
        self.w.characterGlyphPreview = canvasGroups.GlyphPreviewCanvas(
            (410, 372, 200, -70),
            self.RCJKI,
            glyphType = "characterGlyph")

        self.w.characterGlyphStatusList = List((410, -70, 200, -0), [], 
            columnDescriptions=statusColumnDescriptions,
            editCallback = self.glyphStatusListEditCallback,
            showColumnTitles = False
            )

        # self.w.characterGlyphDesignStepPopUpButton = PopUpButton(
        #     (410, -20, 100, -0), 
        #     [
        #     "In Progress", 
        #     "Checking 1", 
        #     "Checking 2", 
        #     "Checking 3", 
        #     "Done"
        #     ],
        #     callback = self.characterGlyphDesignStepPopUpButtonCallback
        #     )
        # self.w.characterGlyphDesignStepPopUpButton.enable(False)
        
        self.lists = [
            self.w.atomicElement,
            self.w.deepComponent,
            self.w.characterGlyph
        ]
        self.RCJKI.toggleObservers()
        self.w.bind('close', self.windowCloses)
        self.w.open()

    @lockedProtect
    def glyphStatusListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            return
        if self.w.atomicElementStatusList == sender:
            l = self.w.atomicElement
            name = l.get()[l.getSelection()[0]]
        elif self.w.deepComponentStatusList == sender:
            l = self.w.deepComponent
            name = l.get()[l.getSelection()[0]]
        elif self.w.characterGlyphStatusList == sender:
            l = self.w.characterGlyph
            name = l.get()[l.getSelection()[0]]["name"]

        f = self.RCJKI.currentFont
        glyph = self.RCJKI.currentFont[name]
        lock, _ = f.lockGlyph(glyph)
        if not lock: 
            self.setglyphState(glyph, l)
            return

        status = sender.get()[sel[0]]["status"]
        sourceName = sender.get()[sel[0]]["sourceName"]
        colorindex = 0
        for i, color in enumerate(colors.colors):
            if color.name == status:
                colorindex = i
        if sourceName == "default":
            glyph._status = colorindex
        else:
            for v in glyph._glyphVariations:
                if v.sourceName == sourceName:
                    v.status = colorindex

        f.saveGlyph(glyph)
        self.setglyphState(glyph, l)
        self.RCJKI.unlockGlyphsNonOpen()

    def codeEditorButtonCallback(self, sender):
        scriptingWindow.ScriptingWindow(self.RCJKI)

    def pdfProoferButtonCallback(self, sender):
        self.RCJKI.pdf = PDFProofer.PDFEngine(self.RCJKI)
        self.RCJKI.pdf.interface.open()

    def textCenterButtonCallback(self, sender):
        # if self.RCJKI.textCenterWindow is None:
        self.RCJKI.textCenterWindows.append(textCenter.TextCenter(self.RCJKI))
        print(self.RCJKI.textCenterWindows)

    def atomicElementDesignStepPopUpButtonCallback(self, sender):
        state = sender.getItem()
        names = {
            "In Progress":colors.WIP_name,  
            "Checking 1":colors.CHECKING1_name,
            "Checking 2":colors.CHECKING2_name,
            "Checking 3":colors.CHECKING3_name,
            "Done":colors.DONE_name,
            }
        l = self.w.atomicElement
        if not l.getSelection():
            return
        name = l.get()[l.getSelection()[0]]
        glyph = self.currentFont[name]
        lock, _ = self.currentFont.lockGlyph(glyph)
        if not lock: return
        self.RCJKI.currentFont.markGlyph(glyph.name, colors.STATUS_COLORS[names[state]], names[state])
        # glyph.markColor = colors.STATUS_COLORS[names[state]]
        # self.RCJKI.currentFont.changeGlyphState(state = names[state], glyph = glyph)
        self.setGlyphToCanvas(sender, self.currentGlyph)
        self.w.atomicElementPreview.update()

    def deepComponentDesignStepPopUpButtonCallback(self, sender):
        state = sender.getItem()
        names = {
            "In Progress":colors.WIP_name,  
            "Checking 1":colors.CHECKING1_name,
            "Checking 2":colors.CHECKING2_name,
            "Checking 3":colors.CHECKING3_name,
            "Done":colors.DONE_name,
            }
        l = self.w.deepComponent
        if not l.getSelection():
            return
        name = l.get()[l.getSelection()[0]]
        glyph = self.currentFont[name]
        lock, _ = self.currentFont.lockGlyph(glyph)
        if not lock: return
        self.RCJKI.currentFont.markGlyph(glyph.name, colors.STATUS_COLORS[names[state]], names[state])
        # glyph.markColor = colors.STATUS_COLORS[names[state]]
        # self.RCJKI.currentFont.changeGlyphState(state = names[state], glyph = glyph)
        self.setGlyphToCanvas(sender, self.currentGlyph)
        self.w.deepComponentPreview.update()

    def characterGlyphDesignStepPopUpButtonCallback(self, sender):
        state = sender.getItem()
        names = {
            "In Progress":colors.WIP_name,  
            "Checking 1":colors.CHECKING1_name,
            "Checking 2":colors.CHECKING2_name,
            "Checking 3":colors.CHECKING3_name,
            "Done":colors.DONE_name,
            }
        l = self.w.characterGlyph
        if not l.getSelection():
            return
        name = l.get()[l.getSelection()[0]]["name"]
        glyph = self.currentFont[name]
        lock, _ = self.currentFont.lockGlyph(glyph)
        if not lock: return
        self.RCJKI.currentFont.markGlyph(glyph.name, colors.STATUS_COLORS[names[state]], names[state])
        # glyph.markColor = colors.STATUS_COLORS[names[state]]
        # self.RCJKI.currentFont.changeGlyphState(state = names[state], glyph = glyph)
        if colors.STATUS_COLORS[names[state]] == DONE:
            self.RCJKI.decomposeGlyphToBackupLayer(glyph)
        self.setGlyphToCanvas(sender, self.currentGlyph)
        self.w.characterGlyphPreview.update()

    def atomicElementSearchBoxCallback(self, sender):
        if not sender.get():
            self.filterAtomicElementCallback(None)
        else:
            name = str(sender.get())
            l = files._getFilteredListFromName(self.currentFont.staticAtomicElementSet(), name)
            if l:
                self.w.deepComponent.setSelection([])
                self.w.characterGlyph.setSelection([])
                self.w.atomicElement.setSelection([])
                self.w.atomicElement.set(l)
            else:
                self.filterAtomicElementCallback(None)
            
    def deepComponentSearchBoxCallback(self, sender):
        if not sender.get():
            self.filterDeepComponentCallback(None)
        else:
            name = str(sender.get())
            l = files._getFilteredListFromName(self.currentFont.staticDeepComponentSet(), name)
            if l:
                self.w.atomicElement.setSelection([])
                self.w.characterGlyph.setSelection([])
                self.w.deepComponent.setSelection([])
                self.w.deepComponent.set(l)
            else:
                self.filterDeepComponentCallback(None)

    def characterGlyphearchBoxCallback(self, sender):
        l = []
        if not sender.get():
            self.filterCharacterGlyphCallback(None)
        else:
            try:
                name = files.unicodeName(sender.get())
            except:
                name = str(sender.get())
            l = files._getFilteredListFromName(self.currentFont.staticCharacterGlyphSet(), name)
            self.w.atomicElement.setSelection([])
            self.w.deepComponent.setSelection([])
            self.w.characterGlyph.setSelection([])
            charSet = [dict(char = files.unicodeName2Char(x), name = x) for x in l]
            self.w.characterGlyph.set(charSet)
        if not l:
            self.filterCharacterGlyphCallback(None)

    def filterAtomicElementCallback(self, sender):
        aeList = self.currentFont.staticAtomicElementSet()
        if not self.RCJKI.currentFont.mysql:
            filteredList = self.filterGlyphs(
                "atomicElement",
                self.w.firstFilterAtomicElement.getItem(),
                self.w.secondFilterAtomicElement.getItem(),
                aeList,
                # list(set(aeList) & set([x for x in self.currentFont.locker.myLockedGlyphs]))
                set(aeList) & set([x for x in self.currentFont.currentUserLockedGlyphs()])
                )
        else:
            filteredList = self.mysqlFilterGlyphs(
                "atomicElement",
                self.w.firstFilterAtomicElement.getItem(),
                self.w.secondFilterAtomicElement.getItem(),
                )
        self.w.atomicElement.setSelection([])
        self.w.deepComponent.setSelection([])
        self.w.characterGlyph.setSelection([])
        self.w.atomicElement.set(sorted(filteredList))

    def filterDeepComponentCallback(self, sender):
        dcList = self.currentFont.staticDeepComponentSet()
        if not self.RCJKI.currentFont.mysql:
            filteredList = self.filterGlyphs(
                "deepComponent",
                self.w.firstFilterDeepComponent.getItem(),
                self.w.secondFilterDeepComponent.getItem(),
                dcList,
                # list(set(dcList) & set([x for x in self.currentFont.locker.myLockedGlyphs]))
                set(dcList) & set([x for x in self.currentFont.currentUserLockedGlyphs()])
                )
        else:
            filteredList = self.mysqlFilterGlyphs(
                "deepComponent",
                self.w.firstFilterDeepComponent.getItem(),
                self.w.secondFilterDeepComponent.getItem(),
                )
        self.w.atomicElement.setSelection([])
        self.w.deepComponent.setSelection([])
        self.w.characterGlyph.setSelection([])
        self.w.deepComponent.set(sorted(filteredList))

    def filterCharacterGlyphCallback(self, sender):
        cgList = self.currentFont.staticCharacterGlyphSet()
        if not self.RCJKI.currentFont.mysql:
            filteredList = self.filterGlyphs(
                "characterGlyph",
                self.w.firstFilterCharacterGlyph.getItem(),
                self.w.secondFilterCharacterGlyph.getItem(),
                cgList,
                # list(set(cgList) & set([x for x in self.currentFont.locker.myLockedGlyphs]))
                set(cgList) & set([x for x in self.currentFont.currentUserLockedGlyphs()])
                )
        else:
            filteredList = self.mysqlFilterGlyphs(
                "characterGlyph",
                self.w.firstFilterCharacterGlyph.getItem(),
                self.w.secondFilterCharacterGlyph.getItem(),
                )
        self.w.atomicElement.setSelection([])
        self.w.deepComponent.setSelection([])
        self.w.characterGlyph.setSelection([])
        charSet = [dict(char = files.unicodeName2Char(x), name = x) for x in sorted(filteredList)]
        self.w.characterGlyph.set(charSet)

    def mysqlFilterGlyphs(self, glyphType, option1, option2):
        if glyphType == 'atomicElement':
            glyphList = self.RCJKI.currentFont.client.atomic_element_list
        elif glyphType == 'deepComponent':
            glyphList = self.RCJKI.currentFont.client.deep_component_list
        else:
            glyphList = self.RCJKI.currentFont.client.character_glyph_list

        def reformatList(list):
            return [x["name"] for x in list["data"]]

        locked = option1 != "All those"
        if option2 == "that can be fully designed":
            #TODO
            return reformatList(glyphList(self.RCJKI.currentFont.uid, updated_by_current_user=locked))
        elif option2 == "that are not empty":
            return reformatList(glyphList(self.RCJKI.currentFont.uid, updated_by_current_user=locked, is_empty=False))
        elif option2 == "that have outlines":
            return reformatList(glyphList(self.RCJKI.currentFont.uid, updated_by_current_user=locked, has_outlines=True))
        elif option2 == "that are empty":
            return reformatList(glyphList(self.RCJKI.currentFont.uid, updated_by_current_user=locked, is_empty=True))
        elif option2 == "that are in font":
            return reformatList(glyphList(self.RCJKI.currentFont.uid, updated_by_current_user=locked))
        elif option2 == "that are in progress":
            return reformatList(glyphList(self.RCJKI.currentFont.uid, updated_by_current_user=locked, status = colors.WIP_name))
        elif option2 == "that are checking 1":
            return reformatList(glyphList(self.RCJKI.currentFont.uid, updated_by_current_user=locked, status = colors.CHECKING1_name))
        elif option2 == "that are checking 2":
            return reformatList(glyphList(self.RCJKI.currentFont.uid, updated_by_current_user=locked, status = colors.CHECKING2_name))
        elif option2 == "that are checking 3":
            return reformatList(glyphList(self.RCJKI.currentFont.uid, updated_by_current_user=locked, status = colors.CHECKING3_name))
        elif option2 == "that are done":
            return reformatList(glyphList(self.RCJKI.currentFont.uid, updated_by_current_user=locked, status = colors.DONE_name))
        else:
            return reformatList(glyphList(self.RCJKI.currentFont.uid, updated_by_current_user=locked))

    def filterGlyphs(self, glyphtype, option1, option2, allGlyphs, lockedGlyphs):
        lockedGlyphs = lockedGlyphs & set(allGlyphs)

        def getFilteredList(option1, l, lockedGlyphs):
            if option1 == "All those":
                return l
            else:
                return list(lockedGlyphs & set(l))

        if option2 == "that can be fully designed":
            l = []
            DCSet = set([x for x in self.RCJKI.currentFont.deepComponentSet if self.RCJKI.currentFont.get(x)._RGlyph.lib["robocjk.deepComponents"]])
            for name in self.currentFont.characterGlyphSet:
                try:
                    c = chr(int(name[3:].split(".")[0], 16))
                    self.RCJKI.currentFont.dataBase[c]
                except: continue
                compo = ["DC_%s_00"%files.normalizeUnicode(hex(ord(v))[2:].upper()) for v in self.RCJKI.currentFont.dataBase[c]]
                inside = len(set(compo) - DCSet) == 0
                if inside:
                    l.append(name)
            return getFilteredList(option1, l, lockedGlyphs)

        elif option2 == "that are not empty":
            if glyphtype == "characterGlyph":
                if option1 == "All those":
                    return [x for x in allGlyphs if self.RCJKI.currentFont.get(x)._deepComponents or len(self.RCJKI.currentFont.get(x))]
                else:
                    return [x for x in lockedGlyphs if self.RCJKI.currentFont.get(x)._deepComponents or len(self.RCJKI.currentFont.get(x))]
            elif glyphtype == "deepComponent":
                if option1 == "All those":
                    return [x for x in allGlyphs if self.RCJKI.currentFont.get(x)._deepComponents or len(self.RCJKI.currentFont.get(x))]
                else:
                    return [x for x in lockedGlyphs if self.RCJKI.currentFont.get(x)._deepComponents or len(self.RCJKI.currentFont.get(x))]
            else:
                if option1 == "All those":
                    return [x for x in allGlyphs if len(self.RCJKI.currentFont.get(x))]
                else:
                    return [x for x in lockedGlyphs if len(self.RCJKI.currentFont.get(x))]
            # return getFilteredList(option1, l, lockedGlyphs)

        elif option2 == "that have outlines":
            if option1 == "All those":
                return [x for x in allGlyphs if len(self.RCJKI.currentFont.get(x))]
            else:
                return [x for x in lockedGlyphs if len(self.RCJKI.currentFont.get(x))]
            # return getFilteredList(option1, l, lockedGlyphs)

        elif option2 == "that are empty":
            if glyphtype == "characterGlyph":
                if option1 == "All those":
                    return [x for x in allGlyphs if not self.RCJKI.currentFont.get(x)._deepComponents and not len(self.RCJKI.currentFont.get(x))]
                else:
                    return [x for x in lockedGlyphs if not self.RCJKI.currentFont.get(x)._deepComponents and not len(self.RCJKI.currentFont.get(x))]
            elif glyphtype == "deepComponent":
                if option1 == "All those":
                    return [x for x in allGlyphs if not self.RCJKI.currentFont.get(x)._deepComponents and not len(self.RCJKI.currentFont.get(x))]
                else:
                    return [x for x in lockedGlyphs if not self.RCJKI.currentFont.get(x)._deepComponents and not len(self.RCJKI.currentFont.get(x))]
            else:
                if option1 == "All those":
                    return [x for x in allGlyphs if not len(self.RCJKI.currentFont.get(x))]
                else:
                    return [x for x in lockedGlyphs if not len(self.RCJKI.currentFont.get(x))]

            # return getFilteredList(option1, l, lockedGlyphs)

        elif option2 == "that are in font":
            l = allGlyphs
            return getFilteredList(option1, l, lockedGlyphs)

        elif option2 == "that are not locked":
            pass

        elif option2 == "that are in progress":
            if option1 == "All those":
                return [x for x in allGlyphs if self.RCJKI.currentFont.get(x).markColor in [None, INPROGRESS]]
            else:
                return [x for x in lockedGlyphs if self.RCJKI.currentFont.get(x).markColor in [None, INPROGRESS]]
            # return getFilteredList(option1, l, lockedGlyphs)

        elif option2 == "that are checking 1":
            if option1 == "All those":
                return [x for x in allGlyphs if self.RCJKI.currentFont.get(x).markColor == CHECKING1]
            else:
                return [x for x in lockedGlyphs if self.RCJKI.currentFont.get(x).markColor == CHECKING1]
            # return getFilteredList(option1, l, lockedGlyphs)

        elif option2 == "that are checking 2":
            if option1 == "All those":
                return [x for x in allGlyphs if self.RCJKI.currentFont.get(x).markColor == CHECKING2]
            else:
                return [x for x in lockedGlyphs if self.RCJKI.currentFont.get(x).markColor == CHECKING2]
            # return getFilteredList(option1, l, lockedGlyphs)

        elif option2 == "that are checking 3":
            if option1 == "All those":
                return [x for x in allGlyphs if self.RCJKI.currentFont.get(x).markColor == CHECKING3]
            else:
                return [x for x in lockedGlyphs if self.RCJKI.currentFont.get(x).markColor == CHECKING3]
            # return getFilteredList(option1, l, lockedGlyphs)

        elif option2 == "that are done":
            if option1 == "All those":
                return [x for x in allGlyphs if self.RCJKI.currentFont.get(x).markColor == DONE]
            else:
                return [x for x in lockedGlyphs if self.RCJKI.currentFont.get(x).markColor == DONE]
            # return getFilteredList(option1, l, lockedGlyphs)

        else:
            return allGlyphs

    def windowCloses(self, sender):
        for w in AllWindows():
            try:
                w.close()
            except:
                pass
        for textCenter in list(self.RCJKI.textCenterWindows):
            textCenter.close()
        # if self.RCJKI.textCenterWindows is not None:
        #     self.RCJKI.textCenterWindow.close()
        if self.RCJKI.get('currentFont'):
            if self.currentFont is not None:
                if self.currentGlyph:
                    self.currentFont.saveGlyph(self.currentGlyph)
                else:
                    self.currentFont.save()
                # self.currentFont.save()
            self.RCJKI.toggleWindowController(False)
        self.RCJKI.toggleObservers(forceKill=True)

    def fontInfosCallback(self, sender):
        sheets.FontInfosSheet(self.RCJKI, self.w, (420, 225))

    def lockControllerDCButtonCallback(self, sender):
        self.lockController = sheets.LockController(self.RCJKI, self.w)
        self.lockController.open()

    def teamManagerButtonCallback(self, sender):
        self.RCJKI.teamManager = teamManager.TeamManagerController(self.RCJKI)
        self.RCJKI.teamManager.launchInterface()

    def generateFontButtonCallback(self, sender):
        # axis = self.RCJKI.currentFont._RFont.lib['robocjk.fontVariations']
        # print(axis)

        """
        - Decompose les DC
        - Crée un glyph pour chaque DC
        - Dico équivalence reglage DC, glyphName
        - Parse les CG
        - import les DC comme Compo normal + offset
        """
        
        f = NewFont(showUI = False)

        deepCompo2Compo = {}
        for n in self.RCJKI.currentFont.characterGlyphSet:
            g = self.RCJKI.currentFont[n]

            if len(g):
                f.insertGlyph(g, name=n)
                continue

            # g.preview.computeDeepComponents()
            f.newGlyph(n)
            f[n].width = g.width

            # print(g.computedDeepComponentsVariation)
            # print("\n")
            # print(g.computedDeepComponents)
            # print("\n")
            # print("\n")

            for i, e in enumerate(g.computedDeepComponents):
                index = 0

                print(e, '\n')
                
                while True:
                    name = list(e.keys())[0] + "_" + str(index).zfill(2)
                    if name not in deepCompo2Compo.keys():
                        break
                    index += 1
                # if e in deepCompo2Compo: continue
                dc = RGlyph()
                dc.width = g.width
                for dcCoord, l in e.values():
                    for dcAtomicElements in l:
                        for atomicInstanceGlyph, _, _ in dcAtomicElements.values():
                            for c in atomicInstanceGlyph:
                                dc.appendContour(c)
                dc.name = name

                f.insertGlyph(dc)

                deepCompo2Compo[name] = [f[dc.name], list(e.values())[0]]
                f[n].appendComponent(dc.name)
                # print(list(e.values())[0], '\n')



            # print(g.computedDeepComponents)
            # # for deepComponent in g._deepComponents:
            #     if deepComponent in deepCompo2Compo: continue

            # print(g._deepComponents)
            # f.newGlyph(n)
            # f[n].width = g.width

            # for atomicInstance in g.atomicInstances:
            #     for c in atomicInstance:
            #         f[n].appendContour(c) 

            # preview = g.computeDeepComponents(g, False)
            # for d in preview:
            #     for a in d.values():
            #         for c in a[0]:
            #            f[n].appendContour(c) 
                    


        # for n in self.RCJKI.currentFont.characterGlyphSet:
        #     g = self.RCJKI.currentFont[n]
        #     preview = g.computeDeepComponents(g, False)
        #     f.newGlyph(n)
        #     f[n].width = g.width
        #     for _, AEInstance in g._getAtomicInstanceGlyph(preview):
        #         for c in AEInstance:
        #             f[n].appendContour(c)


        f.save(os.path.join(self.RCJKI.currentFont.fontPath, "teeest.ufo"))
        
    # def loadProjectButtonCallback(self, sender):
    #     folder = getFolder()
    #     if not folder: return
    #     self.RCJKI.projectRoot = folder[0]
    #     sheets.UsersInfos(self.RCJKI, self.w)
    def loadProjectButtonCallback(self, sender):
        # folder = getFolder()
        # if not folder: return
        # self.RCJKI.projectRoot = folder[0]
        sheets.Login(self.RCJKI, self.w)

    def saveProjectButtonCallback(self, sender):
        if self.RCJKI.get('currentFont'):
            if self.currentFont is not None:
                self.currentFont.save()
                self.RCJKI.unlockGlyphsNonOpen()

    def newProjectButtonCallback(self, sender):
        if not self.RCJKI.mysql:
            folder = putFile()
            if not folder: return
            askYesNo('Would you like to create a private locker repository?', resultCallback = self.askYesNocallback)
            path = '{}.rcjk'.format(folder)
            files.makepath(os.path.join(path, 'folder.proofer'))
            self.RCJKI.projectRoot = os.path.split(path)[0]
            self.RCJKI.setGitEngine()
            self.setrcjkFiles()
        else:
            projectName = AskString('', value = "Untitled", title = "Font Name")
            response = self.RCJKI.client.font_create(self.RCJKI.currentProjectUID, projectName)
            self.RCJKI.fontsList = {x["name"]:x for x in self.RCJKI.client.font_list(self.RCJKI.currentProjectUID)["data"]}
            self.setmySQLRCJKFiles()

    def askYesNocallback(self, sender):
        self.RCJKI.privateLocker = sender

    @property
    def mysql(self):
        return self.RCJKI.mysql

    @gitCoverage()
    def setrcjkFiles(self):
        rcjkFiles = ["Select a font"]
        rcjkFiles.extend(list(filter(lambda x: x.endswith(".rcjk"), 
            os.listdir(self.RCJKI.projectRoot))))
        self.w.rcjkFiles.setItems(rcjkFiles)
        self.rcjkFilesSelectionCallback(self.w.rcjkFiles)

    def setmySQLRCJKFiles(self):
        # if self.RCJKI.mysql is None:
        # if not self.RCJKI.mysql:
        #     rcjkFiles = []
        # else:
        #     rcjkFiles = [x[1] for x in self.RCJKI.mysql.select_fonts()]
        # rcjkFiles.append("-- insert .rcjk project")  
        fontList = ["Select a font"] + list(self.RCJKI.fontsList.keys())
        self.w.rcjkFiles.setItems(fontList)
        self.rcjkFilesSelectionCallback(self.w.rcjkFiles)

    @gitCoverage()
    def reloadProjectCallback(self, sender):
        self.rcjkFilesSelectionCallback(self.w.rcjkFiles)

    def rcjkFilesSelectionCallback(self, sender):
        import time
        start = time.time()
        self.w.rcjkFiles.enable(True)
        self.currentrcjkFile = sender.getItem()
        if self.currentrcjkFile is None: 
            return

        self.w.atomicElement.setSelection([])
        self.w.deepComponent.setSelection([])
        self.w.characterGlyph.setSelection([])
        for w in AllWindows():
            try:
                w.close()
            except:
                pass
        # return
        # if self.RCJKI.get('currentFont'):
        #     if self.currentFont is not None:
                # self.currentFont.save()
                # self.currentFont.close()
        self.currentrcjkFile = sender.getItem() 
        # if self.currentrcjkFile is None:
        #     self.currentrcjkFile = ""
        if self.currentrcjkFile == "-- insert .rcjk project":
            paths = getFolder()
            folderpath = paths[0]
            fontname = os.path.basename(folderpath).split(".rcjk")[0]
            self.RCJKI.loadProject(folderpath, fontname)
            message("Load done")

            self.setmySQLRCJKFiles()
        elif self.currentrcjkFile == "Select a font":
            self.w.newProjectButton.enable(True)
            pass
        else:
            # self.RCJKI.dataBase = {}
            self.w.saveProjectButton.enable(True)
            self.w.fontInfos.enable(True)
            # self.w.generateFontButton.enable(True)
            # self.w.teamManagerButton.enable(True)
            
            self.w.textCenterButton.enable(True)
            self.w.codeEditorButton.enable(True)
            self.w.lockControllerDCButton.enable(True)
            self.w.pdfProoferButton.enable(True)
            self.w.firstFilterAtomicElement.enable(True)
            self.w.secondFilterAtomicElement.enable(True)
            self.w.firstFilterDeepComponent.enable(True)
            self.w.secondFilterDeepComponent.enable(True)
            self.w.firstFilterCharacterGlyph.enable(True)
            self.w.secondFilterCharacterGlyph.enable(True)
            self.w.atomicElementSearchBox.enable(True)
            self.w.characterGlyphSearchBox.enable(True)
            self.w.deepComponentSearchBox.enable(True)
            self.w.newAtomicElement.enable(True)
            self.w.newDeepComponent.enable(True)
            self.w.newCharacterGlyph.enable(True)
            self.w.removeAtomicElement.enable(True)
            self.w.duplicateAtomicElement.enable(True)
            self.w.removeDeepComponent.enable(True)
            self.w.duplicateDeepComponent.enable(True)
            self.w.removeCharacterGlyph.enable(True)
            self.w.duplicateCharacterGlyph.enable(True)
            self.w.localiseAtomicElement.enable(True)
            self.w.localiseDeepComponent.enable(True)
            self.w.localiseCharacterGlyph.enable(True)
            # self.w.atomicElementDesignStepPopUpButton.enable(True)
            # self.w.deepComponentDesignStepPopUpButton.enable(True)
            # self.w.characterGlyphDesignStepPopUpButton.enable(True)
            
            self.RCJKI.currentFont = font.Font()
            if not self.RCJKI.mysql:
                fontPath = os.path.join(self.RCJKI.projectRoot, self.currentrcjkFile)
                if 'fontLib.json' in os.listdir(fontPath):
                    libPath = os.path.join(fontPath, 'fontLib.json')
                    with open(libPath, 'r') as file:
                        fontLib = json.load(file)
                        version = fontLib.get('robocjk.version', False)
                        if version:
                            if version > self.RCJKI._version:
                                message("Warning you are not using the good RoboCJK version")
                                return
                self.RCJKI.currentFont._init_for_git(fontPath, 
                    self.RCJKI.gitUserName, 
                    self.RCJKI.gitPassword, 
                    self.RCJKI.gitHostLocker, 
                    self.RCJKI.gitHostLockerPassword, 
                    self.RCJKI.privateLocker,
                    self.RCJKI._version
                    )
                if 'database.json' in os.listdir(fontPath):
                    with open(os.path.join(fontPath, 'database.json'), 'r', encoding = "utf-8") as file:
                        self.RCJKI.currentFont.dataBase = json.load(file)

                
            else:
                print("hello")
                # self.RCJKI.dataBase = True
                f = self.RCJKI.client.font_get(self.RCJKI.fontsList[self.currentrcjkFile]['uid'])
                self.RCJKI.currentFont._init_for_mysql(f, self.RCJKI.client, self.RCJKI.mysql_userName, self.RCJKI.hiddenSavePath)
                version = self.RCJKI.currentFont.fontLib.get("robocjk.version", 0)
                if version > self.RCJKI._version:
                    message("Warning you are not using the good RoboCJK version")
                    return
                # self.RCJKI.currentFont.loadMysqlDataBase()
                # self.RCJKI.currentFont.dataBase
                # self.RCJKI.dataBase = self.RCJKI.currentFont.dataBase

            self.RCJKI.currentFont.deepComponents2Chars = {}
            for k, v in self.RCJKI.currentFont.dataBase.items():
                for dc in v:
                    if dc not in self.RCJKI.currentFont.deepComponents2Chars:
                        self.RCJKI.currentFont.deepComponents2Chars[dc] = set()
                    self.RCJKI.currentFont.deepComponents2Chars[dc].add(k)
            

            self.RCJKI.toggleWindowController()

            self.w.atomicElement.set(sorted(list(self.currentFont.staticAtomicElementSet())))
            self.w.deepComponent.set(sorted(list(self.currentFont.staticDeepComponentSet())))
            charSet = [dict(char = files.unicodeName2Char(x), name = x) for x in sorted(list(self.currentFont.staticCharacterGlyphSet()))]
            self.w.characterGlyph.set(charSet)
            stop = time.time()
            print("total to load", stop-start)

    def GlyphsListDoubleClickCallback(self, sender):
        items = sender.get()
        selection = sender.getSelection()
        if not selection: return
        glyphName = items[selection[0]]
        if sender == self.w.characterGlyph:
            glyphName = glyphName["name"]
        try:
            CurrentGlyphWindow().close()
        except:pass
        self.RCJKI.currentGlyph = self.currentFont[glyphName]
        openGlyphWindowIfLockAcquired(self.RCJKI, self.RCJKI.currentGlyph)

    def GlyphsListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel or self.prevGlyphName is None or self.currentFont is None: 
            return
        newGlyphName = sender.get()[sel[0]]
        if sender == self.w.characterGlyph:
            newGlyphName = newGlyphName["name"]
        if newGlyphName == self.prevGlyphName: return

        message = 'Are you sure to rename %s to %s?'%(self.prevGlyphName, newGlyphName)
        answer = AskYesNoCancel(
            message, 
            title='Rename Glyph', 
            default=-1, 
            informativeText="",
            )
        if answer != 1: 
            self.w.atomicElement.set(self.currentFont.atomicElementSet)
            self.w.deepComponent.set(self.currentFont.deepComponentSet)
            charSet = [dict(char = files.unicodeName2Char(x), name = x) for x in self.currentFont.characterGlyphSet]
            self.w.characterGlyph.set(charSet)
            return False
        else:
            renamed = self.currentFont.renameGlyph(self.prevGlyphName, newGlyphName)
        if not renamed:
            if sender == self.w.characterGlyph:
                sender.set([dict(char = files.unicodeName2Char([x["name"], self.prevGlyphName][x["name"] == newGlyphName]), name = [x["name"], self.prevGlyphName][x["name"] == newGlyphName]) for x in sender.get()])
            else:
                sender.set([[x, self.prevGlyphName][x == newGlyphName] for x in sender.get()])
        else:
            self.prevGlyphName = newGlyphName
            if sender == self.w.characterGlyph:
                charSet = [dict(char = files.unicodeName2Char(x["name"]), name = x["name"]) for x in sender.get()]
                sender.set(charSet)
            self.setGlyphToCanvas(sender, self.currentFont[newGlyphName])

            self.w.atomicElement.setSelection([])
            self.w.deepComponent.setSelection([])
            self.w.characterGlyph.setSelection([])

            self.w.atomicElement.set(self.currentFont.atomicElementSet)
            self.w.deepComponent.set(self.currentFont.deepComponentSet)
            charSet = [dict(char = files.unicodeName2Char(x), name = x) for x in self.currentFont.characterGlyphSet]
            self.w.characterGlyph.set(charSet)
            if sender != self.w.characterGlyph:
                index = sender.get().index(newGlyphName)
                sender.setSelection([index])
            else:
                for i, x in enumerate(sender.get()):
                    if x["name"] == newGlyphName:
                        sender.setSelection([i])       
                        break

    def GlyphsListSelectionCallback(self, sender):
        start = time.time()
        selected = sender.getSelection()
        if not selected: 
            if sender == self.w.atomicElement:
                self.w.atomicElementStatusList.enable(False)
            elif sender == self.w.deepComponent:
                self.w.deepComponentStatusList.enable(False)
            elif sender == self.w.characterGlyph:
                self.w.characterGlyphStatusList.enable(False)
            return
        if sender == self.w.atomicElement:
            self.w.atomicElementStatusList.enable(True)
            # state = self.w.atomicElementDesignStepPopUpButton
        elif sender == self.w.deepComponent:
            self.w.deepComponentStatusList.enable(True)
            # state = self.w.deepComponentDesignStepPopUpButton
        elif sender == self.w.characterGlyph:
            self.w.characterGlyphStatusList.enable(True)
            # state = self.w.characterGlyphDesignStepPopUpButton

        for lists in self.lists:
            if lists != sender:
                lists.setSelection([])
        prevGlyphName = sender.get()[sender.getSelection()[0]]
        # if sender == self.w.characterGlyph:
        #     self.prevGlyphName = prevGlyphName["name"]
        #     self.RCJKI.currentFont.loadCharacterGlyph(self.prevGlyphName)
        # else:
        if not isinstance(prevGlyphName, str):
            self.prevGlyphName = prevGlyphName["name"]
        else:
            self.prevGlyphName = prevGlyphName
        glyph = self.currentFont[self.prevGlyphName]
        preview_start = time.time()
        user = self.RCJKI.currentFont.glyphLockedBy(glyph)
        preview_stop = time.time()
        print("get locked-by:", preview_stop-preview_start, "seconds to get locked-by for %s"%glyph.name)
        # color = glyph.markColor
        # if color is None:
        #     state.set(0)
        # elif color == INPROGRESS:
        #     state.set(0)
        # elif color == CHECKING1:
        #     state.set(1)
        # elif color == CHECKING2:
        #     state.set(2)
        # elif color == CHECKING3:
        #     state.set(3)
        # elif color == DONE:
        #     state.set(4)
        # else:
        #     state.set(0)
        # self.currentFont[self.prevGlyphName].update()
        preview_start = time.time()
        glyph.createPreviewLocationsStore()
        preview_stop = time.time()
        print("calculate preview:", preview_stop-preview_start, "seconds to calculate preview of %s"%glyph.name)
        self.setGlyphToCanvas(sender, glyph)
        self.setglyphState(glyph, sender)
        # if not self.RCJKI.mysql:
        #     user = self.RCJKI.currentFont.locker.potentiallyOutdatedLockingUser(self.currentFont[self.prevGlyphName])
        # else:
        #     user = self.RCJKI.mysql.who_locked_cglyph(self.currentrcjkFile, prevGlyphName)
        # user = self.RCJKI.currentFont.glyphLockedBy(self.currentFont[self.prevGlyphName])
        if user: 
            self.w.lockerInfoTextBox.set('Locked by: ' + user)
        else:
            self.w.lockerInfoTextBox.set("")
        stop = time.time()
        print("display glyph:", stop-start, 'seconds to display %s'%glyph.name)

    def setglyphState(self, glyph, sender=None):
        if sender is None:
            if glyph.type == "atomicElement":
                sender = self.w.atomicElement
            elif glyph.type == "deepComponent":
                sender = self.w.deepComponent
            else:
                sender = self.w.characterGlyph
        l = [
            dict(color = NSColor.colorWithCalibratedRed_green_blue_alpha_(*colors.colors[glyph._status].rgba), 
                sourceName = "default", 
                status = colors.names[glyph._status]
                )
        ]
        for source in glyph._glyphVariations:
            l.append(dict(color = NSColor.colorWithCalibratedRed_green_blue_alpha_(*colors.colors[source.status].rgba), 
                        sourceName = source.sourceName, 
                        status = colors.names[source.status]
                        ))
        if sender == self.w.atomicElement:
            self.w.atomicElementStatusList.set(l)
        elif sender == self.w.deepComponent:
            self.w.deepComponentStatusList.set(l)
        elif sender == self.w.characterGlyph:
            self.w.characterGlyphStatusList.set(l)

    def setGlyphToCanvas(self, sender, glyph):
        if sender == self.w.atomicElement:
            self.w.atomicElementPreview.glyph = glyph
            self.w.atomicElementPreview.update()
        elif sender == self.w.deepComponent:
            self.w.deepComponentPreview.glyph = glyph
            self.w.deepComponentPreview.update()
        elif sender == self.w.characterGlyph:
            self.w.characterGlyphPreview.glyph = glyph
            self.w.characterGlyphPreview.update()

    @property
    def currentFont(self):
        return self.RCJKI.currentFont

    @property
    def currentGlyph(self):
        return self.RCJKI.currentGlyph

    def newCharacterGlyphCallback(self, sender):
        sheets.NewCharacterGlyph(self.RCJKI, self.w)
        # name = self.dumpName('characterGlyph', self.currentFont.characterGlyphSet)
        # self.currentFont.newGlyph('characterGlyph', name)
        # self.w.characterGlyph.set(self.currentFont.characterGlyphSet)

    def newDeepComponentCallback(self, sender):
        sheets.NewDeepComponent(self.RCJKI, self.w)
        # name = self.dumpName('deepComponent', self.currentFont.deepComponentSet)
        # self.currentFont.newGlyph('deepComponent', name)
        # # self.RCJKI.currentFont.locker.batchLock([self.RCJKI.currentFont[name]])
        # # self.RCJKI.currentFont.batchLockGlyphs([self.RCJKI.currentFont[name]])
        # self.w.deepComponent.setSelection([])
        # self.w.deepComponent.set(self.currentFont.deepComponentSet)

    def newAtomicElementCallback(self, sender):
        sheets.NewAtomicElement(self.RCJKI, self.w)
        # name = self.dumpName('atomicElement', self.currentFont.atomicElementSet)
        # self.currentFont.newGlyph('atomicElement', name)
        # # self.RCJKI.currentFont.locker.batchLock([self.RCJKI.currentFont[name]])
        # # self.RCJKI.currentFont.batchLockGlyphs([self.RCJKI.currentFont[name]])
        # self.w.atomicElement.setSelection([])
        # self.w.atomicElement.set(self.currentFont.atomicElementSet)

    def duplicateAtomicElementCallback(self, sender):
        newGlyphName = self._duplicateGlyph(self.w.atomicElement, self.RCJKI.currentFont.staticAtomicElementSet())
        if newGlyphName:
            # self.prevGlyphName = newGlyphName
            glyphset = sorted(list(self.currentFont.staticAtomicElementSet(update = True)))
            index = glyphset.index(newGlyphName)
            self.w.atomicElement.setSelection([])
            self.w.atomicElement.set(glyphset)
            self.w.atomicElement.setSelection([index])

    def duplicateDeepComponentCallback(self, sender):
        newGlyphName = self._duplicateGlyph(self.w.deepComponent, self.RCJKI.currentFont.staticDeepComponentSet())
        if newGlyphName:
            # self.prevGlyphName = newGlyphName
            glyphset = sorted(list(self.currentFont.staticDeepComponentSet(update = True)))
            index = glyphset.index(newGlyphName)
            self.w.deepComponent.setSelection([])
            self.w.deepComponent.set(glyphset)
            self.w.deepComponent.setSelection([index])

    def duplicateCharacterGlyphCallback(self, sender):
        newGlyphName = self._duplicateGlyph(self.w.characterGlyph, self.RCJKI.currentFont.staticCharacterGlyphSet())
        if newGlyphName:
            # self.prevGlyphName = newGlyphName
            glyphset = sorted(list(self.currentFont.staticCharacterGlyphSet(update = True)))
            index = glyphset.index(newGlyphName)
            self.w.characterGlyph.setSelection([])
            self.w.characterGlyph.set([dict(char = files.unicodeName2Char(x), name = x) for x in glyphset])
            self.w.characterGlyph.setSelection([index])

    def _duplicateGlyph(self, UIList, glyphset):
        sel = UIList.getSelection()
        if not sel: return False
        glyphName = UIList[sel[0]]
        if UIList == self.w.characterGlyph:
            glyphName = glyphName["name"]
        glyph = self.currentFont[glyphName]
        # user = self.RCJKI.currentFont.locker.potentiallyOutdatedLockingUser(glyph)
        
        glyphtype = glyph.type
        # if user != self.RCJKI.currentFont.locker._username:
        if not self.RCJKI.currentFont.mysql:
            user = self.RCJKI.currentFont.glyphLockedBy(glyph)
            if user != self.RCJKI.currentFont.lockerUserName:
                PostBannerNotification(
                    'Impossible', "You must lock the glyph before"
                    )
                return False
        glyphSet = glyphset
        message = f"Duplicate '{glyphName}' as:"
        i = 0
        while True:
            if glyphtype == "deepComponent":
                newName = "%s%s"%(glyphName[:-2], str(i).zfill(2))    
            else:
                newName = "%s.alt%s"%(glyphName, str(i).zfill(2))
            if newName not in glyphSet:
                break
            i += 1
        newGlyphName = AskString(message, value = newName, title = "Duplicate Glyph")
        if newGlyphName is None: return False
        if newGlyphName in glyphset: 
            PostBannerNotification(
                'Impossible', "'%s' already exist"%newGlyphName
                )
            return False
        self.RCJKI.currentFont.duplicateGlyph(glyphName, newGlyphName)
        # self.RCJKI.currentFont.locker.batchLock([self.RCJKI.currentFont[newGlyphName]])
        if not self.RCJKI.currentFont.mysql:
            self.RCJKI.currentFont.batchLockGlyphs([self.RCJKI.currentFont[newGlyphName]])
        else:
            self.RCJKI.currentFont.batchLockGlyphs([newGlyphName])
        return newGlyphName

    def localiseAtomicElementCallback(self, sender):
        sel = self.w.atomicElement.getSelection()
        if not sel:
            return
        glyphName = self.w.atomicElement.get()[sel[0]]
        sheets.LocaliseGlyphSheet(self.RCJKI, self, self.w, glyphName, glyphset = self.RCJKI.currentFont.staticAtomicElementSet, sender = self.w.atomicElement)

    def localiseDeepComponentCallback(self, sender):
        sel = self.w.deepComponent.getSelection()
        if not sel:
            return
        glyphName = self.w.deepComponent.get()[sel[0]]
        sheets.LocaliseGlyphSheet(self.RCJKI, self, self.w, glyphName, dependencies_glyphset = self.RCJKI.currentFont.staticAtomicElementSet(), glyphset = self.RCJKI.currentFont.staticDeepComponentSet, sender = self.w.deepComponent)

    def localiseCharacterGlyphCallback(self, sender):
        sel = self.w.characterGlyph.getSelection()
        if not sel:
            return
        glyphName = self.w.characterGlyph.get()[sel[0]]
        sheets.LocaliseGlyphSheet(self.RCJKI, self, self.w, glyphName, dependencies_glyphset = self.RCJKI.currentFont.staticDeepComponentSet(), glyphset = self.RCJKI.currentFont.staticCharacterGlyphSet, sender = self.w.characterGlyph)

    def removeGlyph(self, UIList, glyphset, glyphTypeImpacted):
        sel = UIList.getSelection()
        if not sel: return False
        glyphName = UIList[sel[0]]
        # user = self.RCJKI.currentFont.locker.potentiallyOutdatedLockingUser(self.currentFont[glyphName])
        glyph = self.currentFont[glyphName]
        user = self.RCJKI.currentFont.glyphLockedBy(glyph)
        if not self.RCJKI.currentFont.mysql:
            # if user != self.RCJKI.currentFont.locker._username:
            if user != self.RCJKI.currentFont.lockerUserName:
                PostBannerNotification(
                    'Impossible', "You must lock the glyph before"
                    )
                return False
        else:
            if user != None and user != self.RCJKI.currentFont.lockerUserName:
                PostBannerNotification(
                    'Impossible', "This glyph is locked by someone else"
                    )
                return False

        glyphType = glyph.type
        GlyphsthatUse = set()
        if (glyph.type == "atomicElement" and len(glyph)) or (glyph.type == "deepComponent" and glyph._deepComponents):
            if not self.RCJKI.currentFont.mysql:
                if glyphType != 'characterGlyph':
                    for name in glyphset:
                        glyph = self.RCJKI.currentFont.get(name)
                        if glyphType == 'atomicElement':
                            d =  glyph._deepComponents
                        elif glyphType == 'deepComponent':
                            d =  glyph._deepComponents
                        for ae in d:
                            if ae["name"] == glyphName:
                                GlyphsthatUse.add(name)
                                break
            else:
                if glyphType != 'characterGlyph':
                    if glyphType == 'atomicElement':
                        GlyphsthatUse = set([x["name"] for x in self.RCJKI.currentFont.client.atomic_element_get(self.RCJKI.currentFont.uid, glyphName)["data"]["used_by"]])
                    else:
                        GlyphsthatUse = set([x["name"] for x in self.RCJKI.currentFont.client.deep_component_get(self.RCJKI.currentFont.uid, glyphName)["data"]["used_by"]])
        if not len(GlyphsthatUse):
            message = f"Are you sure you want to delete '{glyphName}'? This action is not undoable"
            answer = AskYesNoCancel(
                message, 
                title='Remove Glyph', 
                default=-1, 
                informativeText="",
                )
            if answer != 1: return False
            else:
                self.RCJKI.currentFont.removeGlyph(glyphName)
        else:
            GlyphsUsed = ""
            for name in list(GlyphsthatUse)[:30]:
                GlyphsUsed += "\n\t-" + name 
            if len(GlyphsthatUse) > 30:
                GlyphsUsed += "\n\t..."
            informativeText = f"'{glyphName}' is use in {len(GlyphsthatUse)} {glyphTypeImpacted}{['', 's'][len(GlyphsthatUse) != 1]}:{GlyphsUsed}"
            message = f"Are you sure you want to delete '{glyphName}'? This action is not undoable"
            answer = AskYesNoCancel(
                message, 
                title='Remove Glyph', 
                default=-1, 
                informativeText=informativeText,
                )
            if answer != 1: return False
            else:
                print("-----------")
                print(f"{GlyphsthatUse} will be impacted by the deletion of '{glyphName}'")
                print("-----------")
                self.RCJKI.currentFont.removeGlyph(glyphName)
        return True

    def removeAtomicElementCallback(self, sender):
        aeName = self.w.atomicElement[self.w.atomicElement.getSelection()[0]]
        if not self.RCJKI.currentFont.mysql:
            glyphset = self.RCJKI.currentFont.staticDeepComponentSet()
        else:
            glyphset = []
            uid = self.RCJKI.currentFont.uid
            for char in self.RCJKI.currentFont.client.atomic_element_get(uid, aeName)["data"]["used_by"]:
                glyphset.append(char["name"])
        remove = self.removeGlyph(self.w.atomicElement, glyphset, "deepComponent")
        if remove:
            self.w.atomicElement.setSelection([])
            self.w.atomicElement.set(sorted(list(self.currentFont.atomicElementSet)))
            self.prevGlyphName = ""
            self.setGlyphToCanvas(self.w.atomicElement, None)
            self.w.lockerInfoTextBox.set("")

    def removeDeepComponentCallback(self, sender):
        dcName = self.w.deepComponent[self.w.deepComponent.getSelection()[0]]
        if not self.RCJKI.currentFont.mysql:
            try:
                char = chr(int(dcName.split("_")[1], 16))
                glyphset = [x for x in set(["uni%s"%hex(ord(y))[2:].upper() for y in self.RCJKI.currentFont.deepComponents2Chars[char]])&self.RCJKI.currentFont.staticCharacterGlyphSet()]
            except:
                glyphset = self.RCJKI.currentFont.staticCharacterGlyphSet()
        else:
            glyphset = []
            uid = self.RCJKI.currentFont.uid
            for char in self.RCJKI.currentFont.client.deep_component_get(uid, dcName)["data"]["used_by"]:
                glyphset.append(char["name"])

        remove = self.removeGlyph(self.w.deepComponent, glyphset, "characterGlyph")
        if remove:
            self.w.deepComponent.setSelection([])
            self.w.deepComponent.set(sorted(list(self.currentFont.deepComponentSet)))
            self.prevGlyphName = ""
            self.setGlyphToCanvas(self.w.deepComponent,None)
            self.w.lockerInfoTextBox.set("")

    def removeCharacterGlyphCallback(self, sender):
        sel = self.w.characterGlyph.getSelection()
        if not sel: return
        glyphName = self.w.characterGlyph[sel[0]]["name"]
        glyph = self.RCJKI.currentFont[glyphName]
        # user = self.RCJKI.currentFont.locker.potentiallyOutdatedLockingUser(self.currentFont[glyphName])
        user = self.RCJKI.currentFont.glyphLockedBy(glyph)
        # if user != self.RCJKI.currentFont.locker._username:
        if not self.RCJKI.currentFont.mysql:
            if user != self.RCJKI.currentFont.lockerUserName:
                PostBannerNotification(
                    'Impossible', "You must lock the glyph before"
                    )
                return
        else:
            if user != None and user != self.RCJKI.currentFont.lockerUserName:
                PostBannerNotification(
                    'Impossible', "This glyph is locked by someone else"
                    )
                return False
        glyphType = glyph.type
        GlyphsthatUse = set()
        if not self.RCJKI.currentFont.mysql:
            for name in self.RCJKI.currentFont.staticCharacterGlyphSet():
                glyph = self.RCJKI.currentFont[name]
                for compo in glyph.components:
                    if glyphName == compo.baseGlyph:
                        GlyphsthatUse.add(name)
        else:
            uid = self.RCJKI.currentFont.uid
            pass
            # print(self.RCJKI.currentFont.client.character_glyph_get(uid, glyphName, return_layers=False, return_related=False)["data"])
            # for char in self.RCJKI.currentFont.client.character_glyph_get(uid, glyphName, return_layers=False, return_related=False)["data"]["used_by"]:
            #     GlyphsthatUse.add(char["name"])
        if not len(GlyphsthatUse):
            message = f"Are you sure you want to delete '{glyphName}'? This action is not undoable"
            answer = AskYesNoCancel(
                message, 
                title='Remove Glyph', 
                default=-1, 
                informativeText="",
                )
            if answer != 1: return
            else:
                self.RCJKI.currentFont.removeGlyph(glyphName)
        else:
            GlyphsUsed = ""
            for name in list(GlyphsthatUse)[:30]:
                GlyphsUsed += "\n\t-" + name 
            if len(GlyphsthatUse) > 30:
                GlyphsUsed += "\n\t..."
            informativeText = f"'{glyphName}' is use in {len(GlyphsthatUse)} characterGlyph{['', 's'][len(GlyphsthatUse) != 1]}:{GlyphsUsed}"
            message = f"Are you sure you want to delete '{glyphName}'? This action is not undoable"
            answer = AskYesNoCancel(
                message, 
                title='Remove Glyph', 
                default=-1, 
                informativeText=informativeText,
                )
            if answer != 1: return
            else:
                print("-----------")
                print(f"{GlyphsthatUse} will be impacted by the deletion of '{glyphName}'")
                print("-----------")
                self.RCJKI.currentFont.removeGlyph(glyphName)
        self.w.characterGlyph.setSelection([])
        self.w.characterGlyph.set([dict(char = files.unicodeName2Char(x), name = x) for x in sorted(list(self.currentFont.staticCharacterGlyphSet()))])
        self.prevGlyphName = ""
        self.setGlyphToCanvas(self.w.characterGlyph, None)
        self.w.lockerInfoTextBox.set("")


class ImportDeepComponentFromAnotherCharacterGlyph:

    def updateView(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.w.canvas.update()
        return wrapper

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.w = FloatingWindow((200, 150), "Import DC From CG")
        self.refGlyph = None
        self.index = None
        self.w.searchGlyph = SearchBox(
            (10, 10, -10, 20),
            callback = self.searchGlyphCallback
            )
        self.w.deepComponentList = List(
            (10, 40, 50, -10),
            [],
            doubleClickCallback = self.deepComponentListDoubleClickCallback,
            selectionCallback = self.deepComponentListSelectionCallback
            )
        self.w.canvas = CanvasGroup(
            (60, 40, -0, -0), 
            delegate = self
            )

    def open(self):
        self.w.open()

    def close(self):
        self.w.close()

    @updateView
    def searchGlyphCallback(self, sender):
        try:
            name = files.unicodeName(sender.get())
        except:
            name = str(sender.get())
        if not set([name]) & self.RCJKI.currentFont.staticCharacterGlyphSet():
            return
        self.charName = name
        self.refGlyph = self.RCJKI.currentFont[name]
        # self.refGlyph.preview.computeDeepComponents(update = False)
        self.deepComponents = self.refGlyph._deepComponents
        self.glyphVariations = self.refGlyph._glyphVariations
        self.deepComponentsName = [chr(int(dc["name"].split("_")[1], 16)) for dc in self.deepComponents]
        self.w.deepComponentList.set(self.deepComponentsName)

    @updateView
    def deepComponentListDoubleClickCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            self.index = None
            return
        self.index = sel[0]
        dc = copy.deepcopy(self.deepComponents[self.index])
        if dc.name in self.RCJKI.get_cg_used_by(self.RCJKI.currentFont, self.RCJKI.currentGlyph.name, []):
            message("Impossible to import this variable component, it will trigger an infinite loop")
            return
        self.RCJKI.currentGlyph.addDeepComponentNamed(dc.name, dc)

        if len(self.glyphVariations) == len(self.RCJKI.currentGlyph._glyphVariations):
            for i, variation in enumerate(self.RCJKI.currentGlyph._glyphVariations):
                dc = copy.deepcopy(self.glyphVariations[i].deepComponents[self.index])
                self.RCJKI.currentGlyph._glyphVariations[i].deepComponents[-1].set(dc._toDict())

        self.RCJKI.updateDeepComponent()

    def draw(self):
        if self.refGlyph is None: return
        mjdt.save()
        mjdt.translate(20, 21)
        mjdt.scale(.09)
        # loc = {}
        # if self.refGlyph.selectedSourceAxis:
            # loc = {self.refGlyph.selectedSourceAxis:1}
        for i, atomicElement in enumerate(self.refGlyph.preview({}, forceRefresh=False)):
            if i == self.index:
                mjdt.fill(.7, 0, .15, 1)
            else:
                mjdt.fill(0, 0, 0, 1)
            mjdt.drawGlyph(atomicElement.glyph)
        mjdt.restore()

    @updateView
    def deepComponentListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            self.index = None
            return
        self.index = sel[0]

from fontTools.ufoLib.glifLib import readGlyphFromString

class HistoryGlyph:

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.w = Window((300, 300), 'History Glyph')
        self.w.saveStateButton = Button((0, 0, -0, 20), 'Save current glyph state', callback = self.saveStateButtonCallback)
        self.w.historyTitle = TextBox((0, 30, -0, 20), 'History', alignment = 'center')
        self.w.historyList = List((0, 50, -0, -60), self.glyphHistoryList)
        self.w.restoreGlyphState = Button((0, -50, -0, 20), 'Restore glyph from selected state', callback = self.restoreGlyphStateCallback)
        self.w.clearHistoryButton = Button((0, -20, -0, 20), 'Clear History', callback = self.clearHistoryButtonCallback)
        self.w.open()


    def close(self):
        self.w.close()


    @property
    def glyphHistoryList(self):
        if os.path.exists(self.glyphFolder):
            return sorted(os.listdir(self.glyphFolder), reverse = True)
        return []
    

    @property
    def glyphFolder(self):
        return "/".join([self.RCJKI.currentFont._hiddenSavePath, "%s-%s"%(self.RCJKI.currentFont.uid, self.RCJKI.currentFont._clientFont["data"]["name"]), self.RCJKI.currentGlyph.type, self.RCJKI.currentGlyph.name])    


    def storingHistoryGlyphPath(self, glyph):
        now = str(datetime.now()).replace(" ", "_").replace(":", "-").split(".")[0]
        path = "/".join([self.glyphFolder, "%s__%s.glif"%(now, glyph.name)])
        return path 


    def saveStateButtonCallback(self, sender):
        currentGlyph = self.RCJKI.currentGlyph
        if currentGlyph is None: return
        storingpath = self.storingHistoryGlyphPath(currentGlyph)
        files.makepath(storingpath)
        currentGlyph.save()
        data = currentGlyph._RGlyph.dumpToGLIF()
        with open(storingpath, 'w', encoding = 'utf-8') as file:
            file.write(data)
        self.w.historyList.set(self.glyphHistoryList)


    @refresh
    def restoreGlyphStateCallback(self, sender):
        sel = self.w.historyList.getSelection()
        if not sel: return
        message = 'Are you sure to restore this glyph?'
        answer = AskYesNoCancel(
            message, 
            title='restore glyph?', 
            default=-1, 
            informativeText="This action is not undoable",
            )
        if answer != 1: return

        file = self.w.historyList.get()[sel[0]]
        path = "/".join([self.glyphFolder, file])
        with open(path, 'r', encoding = 'utf-8') as file:
            string = file.read()
        rGlyph = RGlyph()
        pen = rGlyph.naked().getPointPen()
        readGlyphFromString(string, rGlyph.naked(), pen)

        self.RCJKI.currentGlyph._RGlyph.lib.update(rGlyph.lib)

        self.RCJKI.currentGlyph._initWithLib(rGlyph.lib)
        self.RCJKI.currentGlyph.update()

        self.RCJKI.updateDeepComponent(update = False)
        self.RCJKI.currentGlyph.redrawSelectedElementSource = True
        self.RCJKI.currentGlyph.redrawSelectedElementPreview = True
        self.RCJKI.currentGlyph.reinterpolate = True

        self.RCJKI.disabledEditingUIIfValidated()

        self.RCJKI.glyphInspectorWindow.axesItem.setList()
        self.RCJKI.glyphInspectorWindow.sourcesItem.setList()
        self.RCJKI.glyphInspectorWindow.deepComponentListItem.setList()
        self.RCJKI.glyphInspectorWindow.propertiesItem.setglyphState()
        

    def clearHistoryButtonCallback(self, sender):
        message = 'Are you sure to clear glyph history?'
        answer = AskYesNoCancel(
            message, 
            title='Glyph history', 
            default=-1, 
            informativeText="This action is not undoable",
            )
        if answer != 1: return
        for file in self.glyphHistoryList:
            path = "/".join([self.glyphFolder, file])
            os.remove(path)
        self.w.historyList.set(self.glyphHistoryList)


def update(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        UpdateCurrentGlyphView()
    return wrapper


class CharacterGlyphViewer:


    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.selectedGlyph = None
        self.interpovalues = {}
        self._getGlyphList()

        self.w = FloatingWindow((300, 300), "Character Glyph Viewer")
        self.w.glyphList = List((10, 10, 100, -30), 
            self.glyphList, 
            columnDescriptions = [{"title": "char", "width":30}, {"title": "name"}],
            selectionCallback = self.glyphListSelectionCallback, 
            drawFocusRing = False)
        self.w.glyphList.setSelection([])
        self.w.deselectButton = Button((10, -30, 100, 20), "deselect", callback = self.deselectCallback)
        self.w.axes = List((110, 10, -10, 200), 
            [], 
            columnDescriptions=[{"title": "axes", "width":40}, {"title": "values", "cell": SliderListCell()}], 
            editCallback = self.axesEditCallback, 
            drawFocusRing = False)
        self.observer()
        self.w.open()
        self.w.bind("close", self.windowWillClose)

    def deselectCallback(self, sender):
        self.w.glyphList.setSelection([])

    def _getGlyphList(self):
        self.currentFont = self.RCJKI.currentFont
        self.currentGlyphName = self.RCJKI.currentGlyph.name
        self.glyphList = []
        for x in self.currentFont.client.deep_component_get(self.currentFont.uid, self.currentGlyphName)["data"]["used_by"]:
            name = x["name"]
            try:
                char = chr(int(name[3:],16))
            except:
                char = ""
            self.glyphList.append(dict(char = char, name = name))

    def close(self):
        self.w.close()

    def disableUI(self):
        self.w.glyphList.enable(False)
        self.w.axes.enable(False)

    def enableUI(self):
        self._getGlyphList()
        self.w.glyphList.set(self.glyphList)
        self.w.glyphList.enable(True)
        self.w.axes.enable(True)

    @update
    def axesEditCallback(self, sender):
        for e in sender.get():
            axis = self.selectedGlyph._axes.get(e["axes"])
            if e.get("values"):
                value = axis.minValue + (axis.maxValue-axis.minValue)*int(e["values"])/100 
            else:
                value = axis.defaultValue
            self.interpovalues[axis.name] = value


    @update
    def windowWillClose(self, sender):
        self.observer(remove = True)


    def observer(self, remove = False):
        if not remove:
            addObserver(self, "drawBackground", "drawBackground")
            addObserver(self, "drawBackground", "drawInactive")
            return
        removeObserver(self, "drawBackground")
        removeObserver(self, "drawInactive")


    def drawBackground(self, info):
        if self.selectedGlyph is None: return
        g = self.selectedGlyph
        mjdt.save()
        mjdt.fill(1,0,1,.8)
        mjdt.stroke(0,0,0,0)
        g.createPreviewLocationsStore()
        preview = g.preview(self.interpovalues)
        for i, element in enumerate(preview):
            mjdt.save()
            mjdt.translate(element.transformation["x"], element.transformation["y"])
            mjdt.scale(element.transformation["scalex"], element.transformation["scaley"])
            mjdt.drawGlyph(element.resultGlyph)
            mjdt.restore()
        mjdt.restore()


    @update
    def glyphListSelectionCallback(self, sender):
        sel = sender.getSelection()
        print(sel)
        if not sel:
            self.selectedGlyph = None
            return
        selectedGlyphName = sender.get()[sel[0]]["name"]
        self.RCJKI.currentFont.getmySQLGlyph(selectedGlyphName, exception = self.currentGlyphName)
        self.selectedGlyph = self.RCJKI.currentFont[selectedGlyphName]
        l = [{"axes": x.name, "values": x.defaultValue} for x in self.selectedGlyph._axes]
        self.w.axes.set(l)



class CopySettingsFromSource:

    
    def updateView(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.w.canvas.update()
        return wrapper

    
    def __init__(self, RCJKI, *args, **kwargs):
        self.RCJKI = RCJKI
        if self.currentGlyph is None:
            return
        self.glyphName = ""
        self.glyph = None
        self.selectedDeepComponentIndex = None
        self.selectedDeepComponentName = None
        self.selectedDeepComponentGlyph = None
        self.location = {}
        self.w = FloatingWindow((350, 200))
        self.characterLists = []
        self.DC2CG = {}
        self.w.searchGlyph = EditText((0, 0, 150, 20), "",
            callback = self._searchGlyphCallback,
            continuous = False)
        self.w.charlist = List((0, 20, 150, -20), self.characterLists, 
            columnDescriptions=[{"title": "char", "width":20}, {"title": "name"}],
            drawFocusRing = False,
            showColumnTitles = False,
            selectionCallback = self._charlistSelectionCallback
            )
        self.preview = 0
        self.w.preview = CheckBox((5, -20, 150, 20), 'preview', 
            value = self.preview, callback = self.previewCallback,
            sizeStyle = "small")
        self.w.canvas = Canvas((150, 0, 150, 200), delegate = self)
        self.w.apply = SquareButton((300, 0, 50, -0), "Apply", callback = self.applyCallback)
        self.observer()
        self.w.bind("close", self.windowWillClose)
        self.w.open()


    @property
    def currentGlyph(self):
        return self.RCJKI.currentGlyph
    

    def applyCallback(self, sender):
        if self.glyph is None:
            return
        selectedSourceAxisindex = self.RCJKI.currentGlyph.selectedElement[0]
        if not self.RCJKI.currentGlyph.selectedSourceAxis:
            DCSettings = self.glyph._deepComponents[self.selectedDeepComponentIndex]
            self.RCJKI.currentGlyph._deepComponents[selectedSourceAxisindex].set(DCSettings)
        else:
            for source in self.glyph._glyphVariations:
                if source.location == self.location:
                    DCSettings = source["deepComponents"][self.selectedDeepComponentIndex]
                    selectedSourceAxisname = self.RCJKI.currentGlyph.selectedSourceAxis
                    s = self.RCJKI.currentGlyph._glyphVariations.getFromSourceName(selectedSourceAxisname)
                    s.deepComponents[selectedSourceAxisindex].set(DCSettings)
                    break

        self.RCJKI.updateDeepComponent(update = False)
        self.RCJKI.currentGlyph.redrawSelectedElementSource = True
        self.RCJKI.currentGlyph.redrawSelectedElementPreview = True
        self.RCJKI.currentGlyph.reinterpolate = True


    def windowWillClose(self, sender):
        self.observer(remove = True)
        self.RCJKI.copyDCSettingsFromAnotherGlyphWindow = None
        UpdateCurrentGlyphView()


    def observer(self, remove = False):
        if not remove:
            addObserver(self, 'drawGlyphWindow', 'draw')
            addObserver(self, 'drawGlyphWindow', 'drawInactive')
            addObserver(self, 'drawGlyphWindow', 'drawBackground')
            addObserver(self, 'drawGlyphWindow', 'drawPreview')
            return
        removeObserver(self, 'draw')
        removeObserver(self, 'drawInactive')
        removeObserver(self, 'drawBackground')
        removeObserver(self, 'drawPreview')


    def drawGlyphWindow(self, info):
        if self.selectedDeepComponentGlyph is None: return
        if not self.preview: return
        try:
            mjdt.save()
            mjdt.stroke(1, 0, 0, 1)
            mjdt.fill(1, 0, 0, .1)
            mjdt.drawGlyph(self.selectedDeepComponentGlyph)
            mjdt.restore()
        except Exception as e:
            print("Exception", e)


    def previewCallback(self, sender):
        self.preview = sender.get()
        UpdateCurrentGlyphView()


    def _searchGlyphCallback(self, sender):
        elem = sender.get()
        name, char, index = None, None, None
        if len(elem) == 1:
            char = elem
        else:
            name = elem
        for i, x in enumerate(self.characterLists):
            if name is not None and name in x["name"]:
                index = i
                break
            elif char is not None and x["char"] == char:
                index = i
                break
        if index is not None:
            self.w.charlist.setSelection([index])
        
        
    def _setGlyphName(self, name):
        try:
            self.glyphName = name
            self.glyph = self.RCJKI.currentFont[name]
            self.selectedDeepComponentIndex = None
            for i, dc in enumerate(self.glyph._deepComponents):
                if dc["name"] == self.selectedDeepComponentName:
                    self.selectedDeepComponentIndex = i
                    break
            self.w.canvas.update()
        except Exception as e:
            print("_setGlyphName exception:", e)
            pass
        
        
    def setLocation(self, location):
        self.location = location
        self.w.canvas.update()


    def _getAndSetCharlist_queue(self, queue):
        name = queue.get()
        self.w.charlist.enable(False)
        if name is None:
            self.characterLists = []
            self.selectedDeepComponentIndex = None
            self.selectedDeepComponentName = None
            self.selectedDeepComponentGlyph = None
            self.glyph = None
        else:
            f = self.RCJKI.currentFont
            used_by = f.client.deep_component_get(f.uid, name)["data"]["used_by"]
            characters = sorted([x["name"] for x in used_by])
            self.characterLists = [
                dict(
                    name=x, 
                    char=chr(int(x.split(".")[0][3:],16))
                    ) for x in characters
                ]
            self.DC2CG[name] = self.characterLists
        self.w.charlist.set(self.characterLists)
        self.w.charlist.setSelection([])
        # self._searchGlyphCallback(self.w.searchGlyph)
        self.w.charlist.enable(True)
        self.w.canvas.update()
        queue.task_done()
    
    
    def _setCharList(self):
        name = self.selectedDeepComponentName
        if name in self.DC2CG:
            self.characterLists = self.DC2CG[name]
            self.w.charlist.set(self.characterLists)
            self.w.charlist.setSelection([])
            self._searchGlyphCallback(self.w.searchGlyph)
            self.w.canvas.update()
        else:
            self.queue = queue.Queue()
            threading.Thread(target=self._getAndSetCharlist_queue, args = (self.queue,), daemon=True).start()
            self.queue.put(self.selectedDeepComponentName)
 
    
    def _charlistSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            return
        name = sender.get()[sel[0]]["name"]
        self._setGlyphName(name)
        UpdateCurrentGlyphView()
            
        
    def setSelectedDeepComponentIndexAndName(self, index):
        if index is not None:
            self.selectedDeepComponentName = self.currentGlyph._deepComponents[index].name
        else:
            self.selectedDeepComponentName = None

        self._setCharList()
        


    def setUI(self, empty = False):
        if empty:
            self.setLocation({})
            self.setSelectedDeepComponentIndexAndName(None)
            return
        g = self.RCJKI.currentGlyph
        if g is None: return
        selection = self.RCJKI.getSelectionIndex(g)
        location = self.RCJKI.getLocationOfCurrentSelectedSource(g)
        self.setLocation(location)
        self.setSelectedDeepComponentIndexAndName(selection)
        
        
    def draw(self):
        if self.glyph is None: return
        mjdt.save()
        mjdt.translate(17, 51)
        mjdt.scale(.12)
        for i, atomicElement in enumerate(self.glyph.preview(self.location, forceRefresh=True)):
            if i == self.selectedDeepComponentIndex:
                self.selectedDeepComponentGlyph = atomicElement.glyph
                UpdateCurrentGlyphView()
                mjdt.fill(.7, 0, .15, 1)
            else:
                mjdt.fill(0, 0, 0, 1)
            mjdt.drawGlyph(atomicElement.glyph)
        mjdt.restore()
