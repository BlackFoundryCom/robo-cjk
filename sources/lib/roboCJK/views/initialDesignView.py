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

kMissingColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 0, 0, 1)
kThereColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 1, 0, 1)
kEmptyColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 1, 1)


class InitialDesignWindow(BaseWindowController):
    def __init__(self, controller):
        super(InitialDesignWindow, self).__init__()
        self.controller = controller
        self.RCJKI = self.controller.RCJKI
        self.RCJKI.allFonts = []
        self.selectedGlyph = None
        self.fontsList = []
        for name, file in self.RCJKI.project.masterFontsPaths.items():
            path = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Masters', file)
            self.RCJKI.allFonts.append({name:OpenFont(path, showInterface=False)})
            self.fontsList.append(name)
        self.w = Window((200, 0, 800, 600), 'Initial Design', minSize = (300,300), maxSize = (2500,2000))
        
        self.w.fontsList = List((0,0,200,85),
                self.fontsList,
                selectionCallback = self.fontsListSelectionCallback,
                drawFocusRing = False)

        self.w.glyphSetList = List((0,85,200,-0),
                [],
                columnDescriptions = [
                                {"title": "#", "width" : 20},
                                {"title": "Char", "width" : 30},
                                {"title": "Name", "width" : 150}                
                                ],
                selectionCallback = self.glyphSetListSelectionCallback,
                doubleClickCallback = self.glyphSetListdoubleClickCallback,
                showColumnTitles = False,
                drawFocusRing = False)

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
        self.RCJKI.currentFont = self.RCJKI.allFonts[sel[0]][self.fontsList[sel[0]]]
        self.controller.updateGlyphSetList()

    def glyphSetListdoubleClickCallback(self, sender):
        if not sender.getSelection(): return
        self.selectedGlyph = sender.getSelection()[0]
        name = self.w.glyphSetList.get()[self.selectedGlyph]['Name']
        if name not in self.RCJKI.currentFont:
            self.RCJKI.currentFont.newGlyph(name)
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
        if self.RCJKI.currentFont:
            if uiGlyphName in self.RCJKI.currentFont:
                state = 'there'
                if len(self.RCJKI.currentFont[uiGlyphName]) == 0 and not self.RCJKI.currentFont[uiGlyphName].components:
                    state = 'empty'

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

        return cell
