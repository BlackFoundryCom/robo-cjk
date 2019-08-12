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

from utils import files
from views import tableDelegate
reload(files)

kMissingColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1)
kThereColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 1, 0, 1)
kEmptyColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 1, 1)
kLockedColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 0, 0, 1)


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

        self.w.glyphSetList = List((0,85,200,-0),
                [],
                columnDescriptions = [
                                {"title": "#", "width" : 20},
                                {"title": "Char", "width" : 30},
                                {"title": "Name", "width" : 100},
                                {"title": "MarkColor", "width" : 30, "editable": True}
                                ],
                selectionCallback = self.glyphSetListSelectionCallback,
                doubleClickCallback = self.glyphSetListdoubleClickCallback,
                showColumnTitles = False,
                drawFocusRing = False)

        self.controller.loadProjectFonts()
        self.w.fontsList.setSelection([])

        self.delegate = tableDelegate.TableDelegate.alloc().initWithMaster(self)
        tableView = self.w.glyphSetList.getNSTableView()
        tableView.setDelegate_(self.delegate)

        self.dummyCell = NSCell.alloc().init()
        self.dummyCell.setImage_(None)

        self.w.bind('close', self.windowCloses)
        self.w.open()

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

        state = 'missing'
        markColor = None
        if self.RCJKI.currentFont:
            if uiGlyphName in self.RCJKI.currentFont:
                state = 'there'
                markColor = self.RCJKI.currentFont[uiGlyphName].markColor
                if len(self.RCJKI.currentFont[uiGlyphName]) == 0 and not self.RCJKI.currentFont[uiGlyphName].components:
                    state = 'empty'
        if uiGlyphName in self.RCJKI.lockedGlyphs:
            state = 'locked'

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
            elif state == 'locked':
                cell.setBackgroundColor_(kLockedColor)
            else:
                cell.setDrawsBackground_(False)
                cell.setBezeled_(False)
        elif colID == 'MarkColor':
            cell.setDrawsBackground_(True)
            cell.setBezeled_(False)
            if markColor is not None:
                cell.setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(markColor[0], markColor[1], markColor[2], markColor[3]))
            else:
                cell.setDrawsBackground_(False)
                cell.setBezeled_(False)
        return cell
