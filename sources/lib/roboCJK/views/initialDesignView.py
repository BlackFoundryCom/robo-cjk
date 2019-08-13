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
from vanilla import *
import os
import json

from utils import files
from utils import git
from views import tableDelegate
reload(files)
reload(git)

kMissingColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1)
kThereColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 1, 0, 1)
kEmptyColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 1, 1)
kLockedColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 0, 0, 1)
kFreeColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1)
kReservedColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 1, 1)

class InitialDesignWindow(BaseWindowController):
    def __init__(self, controller):
        super(InitialDesignWindow, self).__init__()
        self.lock = False
        self.controller = controller
        self.RCJKI = self.controller.RCJKI
        self.RCJKI.allFonts = []
        self.selectedGlyph = None
    
        self.w = Window((200, 0, 800, 600), 'Initial Design', minSize = (300,300), maxSize = (2500,2000))
        
        self.w.fontsList = List((0,0,200,85),
                [],
                selectionCallback = self.fontsListSelectionCallback,
                drawFocusRing = False)

        self.w.glyphSetList = List((0,85,200,-40),
                [],
                columnDescriptions = [
                                {"title": "Reserved", "cell": CheckBoxListCell(), "width" : 20, "editable": True},
                                {"title": "#", "width" : 20},
                                {"title": "Char", "width" : 30, 'editable':False},
                                {"title": "Name", "width" : 80, 'editable':False},
                                {"title": "MarkColor", "width" : 30}
                                ],
                selectionCallback = self.glyphSetListSelectionCallback,
                doubleClickCallback = self.glyphSetListdoubleClickCallback,
                editCallback = self.glyphSetListEditCallback,
                showColumnTitles = False,
                drawFocusRing = False)

        # self.w.pullAndRefreshButton = Button((0,-40,200,20), 'Pull and Refresh', callback=self.pullAndRefreshButtonCallback)
        # self.w.saveAndCommitButton = Button((0,-20,200,20), 'Save, Commit and Push', callback=self.saveAndCommitButtonCallback)

        self.controller.loadProjectFonts()
        self.w.fontsList.setSelection([])

        self.delegate = tableDelegate.TableDelegate.alloc().initWithMaster(self)
        tableView = self.w.glyphSetList.getNSTableView()
        tableView.setDelegate_(self.delegate)

        self.dummyCell = NSCell.alloc().init()
        self.dummyCell.setImage_(None)

        self.w.bind('close', self.windowCloses)
        self.w.open()


    # def pullAndRefreshButtonCallback(self, sender):
    #     self.RCJKI.projectEditorController.pullPushRefresh()
    #     self.controller.updateGlyphSetList()

    # def saveAndCommitButtonCallback(self, sender):
    #     self.RCJKI.projectEditorController.saveAndCommitProjectAndCollab()

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

    def glyphSetListEditCallback(self, sender):
        if not sender.getSelection() or self.lock: return
        self.lock = True
        rootfolder = os.path.split(self.RCJKI.projectFileLocalPath)[0]
        gitEngine = git.GitEngine(rootfolder)
        stamp = "Pre-pull '%s' Commit" % self.RCJKI.project.name
        gitEngine.commit(stamp)
        gitEngine.pull()
        
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

        myLocker = self.RCJKI.collab._userLocker(self.RCJKI.user)
        if myLocker:
            print('update boxes view')
            for d in sender.get():
                if d['Name'] in myLocker.glyphs:
                    d['Reserved'] = True
                if d['Name'] in myLocker._allOtherLockedGlyphs:
                    d['Reserved'] = False

            reservedGlyphs = [d['Name'] for d in sender.get() if d['Reserved'] == True and d['Name'] not in myLocker._allOtherLockedGlyphs]
            freeGlyphs = [d['Name'] for d in sender.get() if d['Reserved'] == False or d['Name'] in myLocker._allOtherLockedGlyphs]
        
            myLocker._addGlyphs(reservedGlyphs)
            myLocker._removeGlyphs(freeGlyphs)
            self.RCJKI.lockedGlyphs = myLocker._allOtherLockedGlyphs
            self.RCJKI.reservedGlyphs = myLocker.glyphs
        else:
            myLocker = self.RCJKI.collab._addLocker(self.RCJKI.user)

        self.RCJKI.projectEditorController.saveCollab()
        self.RCJKI.projectEditorController.pushRefresh()
        self.lock = False


    def glyphSetListdoubleClickCallback(self, sender):
        if not sender.getSelection(): return
        self.selectedGlyph = sender.getSelection()[0]
        name = self.w.glyphSetList.get()[self.selectedGlyph]['Name']
        if name not in self.RCJKI.currentFont:
            self.RCJKI.currentFont.newGlyph(name)
            self.RCJKI.currentFont[name].width = self.RCJKI.project.settings['designFrame']['em_Dimension'][0]
        OpenGlyphWindow(self.RCJKI.currentFont[name])

    def glyphSetListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        self.selectedGlyph = sel[0]

    def windowCloses(self, sender):
        for i in range(len(AllGlyphWindows())):
            CurrentGlyphWindow().close()
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
        uiGlyphReserved = uiGlyph['Reserved']

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
            elif uiGlyphReserved == 1:
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
        elif colID == 'Reserved':
            if locked:
                cell = self.dummyCell
        return cell

