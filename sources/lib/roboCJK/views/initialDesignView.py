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
from AppKit import NSCell, NSColor
from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.UI import OpenGlyphWindow, AllGlyphWindows, CurrentGlyphWindow
from mojo.roboFont import *
from mojo.canvas import *
from vanilla import *
import os
import json

from utils import files
from utils import git
from views import tableDelegate
from views import mainCanvas
reload(files)
reload(git)
reload(mainCanvas)

kMissingColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1)
kThereColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 1, 0, 1)
kEmptyColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 1, 1)
kLockedColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 0, 0, 1)
kFreeColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1)
kReservedColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 1, 1)

class InitialDesignWindow(BaseWindowController):
    def __init__(self, controller):
        super(InitialDesignWindow, self).__init__()
        self.controller = controller
        self.RCJKI = self.controller.RCJKI
        self.RCJKI.allFonts = []
        self.selectedGlyph = None
    
        self.w = Window((200, 0, 800, 600), 'Initial Design', minSize = (300,300), maxSize = (2500,2000))
        
        self.w.fontsList = List((0,0,200,85),
                [],
                selectionCallback = self.fontsListSelectionCallback,
                drawFocusRing = False)

        self.w.glyphSetList = List((0,85,200,-60),
                [],
                columnDescriptions = [
                                {"title": "#", "width" : 20, 'editable':False},
                                {"title": "Char", "width" : 30, 'editable':False},
                                {"title": "Name", "width" : 80, 'editable':False},
                                {"title": "MarkColor", "width" : 30, 'editable':False}
                                ],
                selectionCallback = self.glyphSetListSelectionCallback,
                doubleClickCallback = self.glyphSetListdoubleClickCallback,
                # editCallback = self.glyphSetListEditCallback,
                showColumnTitles = False,
                drawFocusRing = False)

        self.w.saveLocalFontButton = Button((0,-60,200,20), 'Save Fonts', callback=self.saveLocalFontButtonCallback)
        self.w.pullMasterGlyphsButton = Button((0,-40,200,20), 'Pull & Reload', callback=self.pullMasterGlyphsButtonCallback)
        self.w.pushBackButton = Button((0,-20,200,20), 'Push Glyphs to Masters', callback=self.pushBackButtonCallback)
        

        self.w.mainCanvas = Canvas((200,0,-0,-40), 
            delegate=mainCanvas.MainCanvas(self.RCJKI),
            canvasSize=(5000, 5000),
            hasHorizontalScroller=False, 
            hasVerticalScroller=False)

        self.w.colorPicker = ColorWell((200,-60,20,20),
                callback=self.colorPickerCallback, 
                color=NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 0))

        self.controller.loadProjectFonts()
        self.w.fontsList.setSelection([])

        self.delegate = tableDelegate.TableDelegate.alloc().initWithMaster(self)
        tableView = self.w.glyphSetList.getNSTableView()
        tableView.setDelegate_(self.delegate)

        self.dummyCell = NSCell.alloc().init()
        self.dummyCell.setImage_(None)

        self.w.bind('close', self.windowCloses)
        self.w.open()


    def saveLocalFontButtonCallback(self, sender):
        self.RCJKI.initialDesignController.saveSubsetFonts()
        self.w.mainCanvas.update()
        
    def pullMasterGlyphsButtonCallback(self, sender):
        self.RCJKI.initialDesignController.pullMastersGlyphs()
        self.w.mainCanvas.update()

    def pushBackButtonCallback(self, sender):
        rootfolder = os.path.split(self.RCJKI.projectFileLocalPath)[0]
        gitEngine = git.GitEngine(rootfolder)
        user = gitEngine.user()
        glyphsList = self.RCJKI.collab._userLocker(user).glyphs
        self.RCJKI.initialDesignController.injectGlyphsBack(glyphsList, user)

    def colorPickerCallback(self, sender):
        if self.RCJKI.currentGlyph is None: return
        color = sender.get()
        r = color.redComponent()
        g = color.greenComponent()
        b = color.blueComponent()
        a = color.alphaComponent()
    
        self.RCJKI.currentGlyph.markColor = (r, g, b, a)
        self.controller.updateGlyphSetList()

    def fontsListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            self.RCJKI.currentFont = None
            self.w.glyphSetList.setSelection([])
            self.w.glyphSetList.set([])
            self.selectedGlyph = None
            return
        self.RCJKI.currentFont = self.RCJKI.allFonts[sel[0]][self.controller.fontsList[sel[0]]]
        self.controller.updateGlyphSetList()

    # def glyphSetListEditCallback(self, sender):
    #     if not sender.getSelection(): return

    #     myLocker = self.RCJKI.collab._userLocker(self.RCJKI.user)
    #     if myLocker:
    #         self.RCJKI.lockedGlyphs = myLocker._allOtherLockedGlyphs
    #         self.RCJKI.reservedGlyphs = myLocker.glyphs
    #     else:
    #         myLocker = self.RCJKI.collab._addLocker(self.RCJKI.user)

        # self.RCJKI.projectEditorController.saveCollabToFile()
        # self.RCJKI.projectEditorController.pushRefresh()


    def glyphSetListdoubleClickCallback(self, sender):
        if not sender.getSelection(): return
        if self.selectedGlyphName not in self.RCJKI.currentFont:
            self.RCJKI.currentGlyph = self.RCJKI.currentFont.newGlyph(self.selectedGlyphName)
            self.RCJKI.currentGlyph.width = self.RCJKI.project.settings['designFrame']['em_Dimension'][0]
        OpenGlyphWindow(self.RCJKI.currentGlyph)

    def glyphSetListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        self.selectedGlyphName = sender.get()[sel[0]]['Name']
        if self.selectedGlyphName in self.RCJKI.currentFont:
            self.RCJKI.currentGlyph = self.RCJKI.currentFont[self.selectedGlyphName]
            r, g, b, a = self.RCJKI.currentGlyph.markColor
            self.w.colorPicker.set(NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, a))
        else:
            self.RCJKI.currentGlyph = None
        self.w.mainCanvas.update()

    def windowCloses(self, sender):
        # for i in range(len(AllGlyphWindows())):
        #     CurrentGlyphWindow().close()
        self.RCJKI.initialDesignController.interface = None

    def tableView_dataCellForTableColumn_row_(self, tableView, tableColumn, row):
        if tableColumn is None: return None
        cell = tableColumn.dataCell()
        if self.w is None:
            return cell
        if (row < 0) or (row >= len(self.w.glyphSetList)):
            return cell
        uiGlyph  = self.w.glyphSetList[row]
        uiGlyphName = uiGlyph['Name']
        uiGlyphReserved = uiGlyphName in self.RCJKI.collab._userLocker(self.RCJKI.user).glyphs

        state = 'missing'
        locked = False
        reserved = False
        markColor = None
        if self.RCJKI.currentFont:
            if uiGlyphName in self.RCJKI.currentFont:
                state = 'there'
                markColor = self.RCJKI.currentFont[uiGlyphName].markColor
                if len(self.RCJKI.currentFont[uiGlyphName]) == 0 and not self.RCJKI.currentFont[uiGlyphName].components:
                    state = 'empty'
        if uiGlyphName in self.RCJKI.lockedGlyphs:
            locked = True

        colID = tableColumn.identifier()
        if colID == '#':
            cell.setDrawsBackground_(True)
            cell.setBezeled_(False)
            if state == 'missing':
                cell.setBackgroundColor_(kMissingColor)
            elif state == 'there':
                cell.setBackgroundColor_(kThereColor)
            elif state == 'empty':
                cell.setBackgroundColor_(kEmptyColor)
            else:
                cell.setDrawsBackground_(False)
                cell.setBezeled_(False)
        elif colID == 'Name' or colID == 'Char':
            if locked:
                cell.setTextColor_(kLockedColor)
            elif uiGlyphReserved == True:
                cell.setTextColor_(kReservedColor)
            else:
                cell.setTextColor_(kFreeColor)
        elif colID == 'MarkColor':
            cell.setDrawsBackground_(True)
            cell.setBezeled_(False)
            if markColor is not None:
                cell.setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(markColor[0], markColor[1], markColor[2], markColor[3]))
            else:
                cell.setDrawsBackground_(False)
                cell.setBezeled_(False)
        return cell

