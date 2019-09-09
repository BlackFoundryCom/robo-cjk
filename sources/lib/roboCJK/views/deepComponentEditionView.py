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
from vanilla import *
from defconAppKit.windows.baseWindow import BaseWindowController

from AppKit import *

from mojo.UI import OpenGlyphWindow, AllGlyphWindows, CurrentGlyphWindow, PostBannerNotification
from mojo.roboFont import *
from mojo.canvas import *
from lib.cells.colorCell import RFColorCell
from fontTools.pens import cocoaPen

import os
import json
import Quartz

from utils import files
from utils import git
from views import tableDelegate
from views import mainCanvas
from utils import interpolations
from resources import deepCompoMasters_AGB1_FULL

reload(files)
reload(git)
reload(mainCanvas)
reload(deepCompoMasters_AGB1_FULL)
reload(interpolations)

class DeepComponentEditionWindow(BaseWindowController):

    def __init__(self, controller):
        super(DeepComponentEditionWindow, self).__init__()
        self.controller = controller
        self.RCJKI = self.controller.RCJKI
        self.RCJKI.allFonts = []
        self.selectedGlyph = None
        self.RCJKI.layersInfos = {}

        self.w = Window((200, 0, 800, 800), 
                'Deep Component Edition', 
                minSize = (300,300), 
                maxSize = (2500,2000))

        self.w.fontsList = List((0,0,200,85),
                [],
                selectionCallback = self.fontsListSelectionCallback,
                drawFocusRing = False)

        self.w.glyphSetList = List((0,85,200,230),
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

        self.w.deepComponentsSetList = List((0, 315, 200, 200),
                [],
                columnDescriptions = [
                                {"title": "#", "width" : 20, 'editable':False},
                                {"title": "Char", "width" : 30, 'editable':False},
                                {"title": "Name", "width" : 80, 'editable':False},
                                {"title": "MarkColor", "width" : 30, 'editable':False}
                                ],
                selectionCallback = self.deepComponentsSetListSelectionCallback,
                doubleClickCallback = self.deepComponentsSetListDoubleClickCallback,
                # editCallback = self.glyphSetListEditCallback,
                showColumnTitles = False,
                drawFocusRing = False
            )

        self.w.saveLocalFontButton = Button((0,-60,200,20), 
            'Save', 
            callback=self.saveLocalFontButtonCallback)

        self.w.pushBackButton = Button((0,-40,200,20), 
            'Push', 
            callback=self.pushBackButtonCallback)

        self.w.pullMasterGlyphsButton = Button((0,-20,200,20), 
            'Pull', 
            callback=self.pullMasterGlyphsButtonCallback)

        self.canvasDrawer = mainCanvas.MainCanvas(self.RCJKI, self, '_deepComponentsEdition_glyphs')
        self.w.mainCanvas = Canvas((200,0,-0,-240), 
            delegate=self.canvasDrawer,
            canvasSize=(5000, 5000),
            hasHorizontalScroller=False, 
            hasVerticalScroller=False)

        self.w.extremsList = PopUpButton((200, 0, 200, 20), 
            [], 
            sizeStyle = 'small',
            callback = self.extremsListCallback)

        slider = SliderListCell(minValue = 0, maxValue = 1000)
        self.slidersValuesList = []
        self.w.slidersList = List((200, -240, -0, -0),
            self.slidersValuesList,
            columnDescriptions = [
                                    # {"title": "Layer", "editable": False, "width": 140},
                                    {"title": "Image", "editable": False, "cell": ImageListCell(), "width": 60}, 
                                    {"title": "Values", "cell": slider}],
            editCallback = self.slidersListEditCallback,
            # doubleClickCallback = self._sliderList_doubleClickCallback,
            drawFocusRing = False,
            allowsMultipleSelection = False,
            rowHeight = 60.0,
            showColumnTitles = False
            )

        self.w.colorPicker = ColorWell((200,-260,20,20),
                callback=self.colorPickerCallback, 
                color=NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 0))

        self.delegate = tableDelegate.TableDelegate.alloc().initWithMaster(self)
        tableView = self.w.glyphSetList.getNSTableView()
        tableView.setDelegate_(self.delegate)

        self.dummyCell = NSCell.alloc().init()
        self.dummyCell.setImage_(None)

        self.w.bind('close', self.windowCloses)

        self.w.open()

    def saveLocalFontButtonCallback(self, sender):
        self.RCJKI.deepComponentEditionController.saveSubsetFonts()
        self.w.mainCanvas.update()
        
    def pullMasterGlyphsButtonCallback(self, sender):
        self.controller.pullDCMasters()
        self.w.mainCanvas.update()

    def pushBackButtonCallback(self, sender):
        self.controller.pushDCMasters()
        self.w.mainCanvas.update()

    def setSliderList(self):
        self.RCJKI.layersInfos = {}
        self.slidersValuesList = []
        layers = [l.name for l in list(filter(lambda l: len(self.RCJKI.currentFont[self.RCJKI.currentGlyph.name].getLayer(l.name)), self.RCJKI.currentFont.layers))]
        for layerName in layers:
            if layerName == "foreground": continue
            g = self.RCJKI.currentFont[self.RCJKI.currentGlyph.name].getLayer(layerName)
            f = g.getParent()
            path = NSBezierPath.bezierPath()
            pen = cocoaPen.CocoaPen(f, path)
            g.draw(pen)
            margins = 200
            EM_Dimension_X, EM_Dimension_Y = self.RCJKI.project.settings['designFrame']['em_Dimension']
            mediaBox = Quartz.CGRectMake(-margins, -margins, EM_Dimension_X+2*margins, EM_Dimension_Y+2*margins)
            pdfData = Quartz.CFDataCreateMutable(None, 0)
            dataConsumer = Quartz.CGDataConsumerCreateWithCFData(pdfData)
            pdfContext = Quartz.CGPDFContextCreate(dataConsumer, mediaBox, None)
            Quartz.CGContextSaveGState(pdfContext)
            Quartz.CGContextBeginPage(pdfContext, mediaBox)

            for i in range(path.elementCount()):
                instruction, points = path.elementAtIndex_associatedPoints_(i)
                if instruction == NSMoveToBezierPathElement:
                    Quartz.CGContextMoveToPoint(pdfContext, points[0].x, points[0].y)
                elif instruction == NSLineToBezierPathElement:
                    Quartz.CGContextAddLineToPoint(pdfContext, points[0].x, points[0].y)
                elif instruction == NSCurveToBezierPathElement:
                    Quartz.CGContextAddCurveToPoint(pdfContext, points[0].x, points[0].y, points[1].x, points[1].y, points[2].x, points[2].y)
                elif instruction == NSClosePathBezierPathElement:
                    Quartz.CGContextClosePath(pdfContext)

            Quartz.CGContextSetRGBFillColor(pdfContext, 0.0, 0.0, 0.0, 1.0)
            # if self.ui.darkMode:
            #     Quartz.CGContextSetRGBFillColor(pdfContext, 1.0, 1.0, 1.0, 1.0)
            # else:
            #     Quartz.CGContextSetRGBFillColor(pdfContext, 0.0, 0.0, 0.0, 1.0)
    
            Quartz.CGContextFillPath(pdfContext)
            Quartz.CGContextEndPage(pdfContext)
            Quartz.CGPDFContextClose(pdfContext)
            Quartz.CGContextRestoreGState(pdfContext)

            d = {'Layer': layerName,
                'Image': NSImage.alloc().initWithData_(pdfData),
                'Values': 0}

            self.slidersValuesList.append(d)
            self.RCJKI.layersInfos[layerName]:0
        self.w.slidersList.set(self.slidersValuesList)

    def slidersListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        selectedLayerName = sender.get()[sel[0]]["Layer"]
        selectedLayerValue = sender.get()[sel[0]]["Values"]
        self.RCJKI.layersInfos[selectedLayerName] = selectedLayerValue
        self.RCJKI.currentGlyph = self.RCJKI.currentFont[self.selectedDeepComponentGlyphName]
        self.RCJKI.deepComponentGlyph = self.RCJKI.getDeepComponentGlyph()
        self.w.mainCanvas.update()

    def fontsListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            self.RCJKI.currentFont = None
            self.w.glyphSetList.setSelection([])
            self.w.glyphSetList.set([])
            self.selectedGlyph = None
            return
        self.RCJKI.currentFont = self.RCJKI.fonts2DCFonts[self.RCJKI.allFonts[sel[0]][self.controller.fontsList[sel[0]]]]
        self.controller.updateGlyphSetList()

    def glyphSetListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        self.selectedGlyphName = sender.get()[sel[0]]['Name']
        self.controller.updateDeepComponentsSetList(self.selectedGlyphName)
        self.w.mainCanvas.update()

    def glyphSetListdoubleClickCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        selectedGlyphName = sender.get()[sel[0]]['Name']
        self.RCJKI.openGlyphWindow(self.RCJKI.DCFonts2Fonts[self.RCJKI.currentFont][selectedGlyphName])

    def deepComponentsSetListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        self.selectedDeepComponentGlyphName = sender.get()[sel[0]]['Name']

        self.controller.updateExtemeList(self.selectedDeepComponentGlyphName)
        
        if self.selectedDeepComponentGlyphName in self.RCJKI.currentFont:
            self.RCJKI.currentGlyph = self.RCJKI.currentFont[self.selectedDeepComponentGlyphName]
            # self.RCJKI.deepComponentGlyph = interpolations.deepolation(RGlyph(), self.RCJKI.currentGlyph, self.RCJKI.layersInfos)
            self.RCJKI.deepComponentGlyph = self.RCJKI.getDeepComponentGlyph()
            if self.RCJKI.currentGlyph.markColor is None:
                r, g, b, a = 0, 0, 0, 0
            else: 
                r, g, b, a = self.RCJKI.currentGlyph.markColor
            self.w.colorPicker.set(NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, a))
        else:
            self.RCJKI.currentGlyph = None
        self.setSliderList()
        self.w.mainCanvas.update()

    def extremsListCallback(self, sender):
        char = sender.getItem()
        self.controller.setExtremDCGlyph(char)

    def deepComponentsSetListDoubleClickCallback(self, sender):
        if not sender.getSelection(): return
        
        if self.selectedDeepComponentGlyphName not in self.RCJKI.currentFont:
            self.RCJKI.currentGlyph = self.RCJKI.currentFont.newGlyph(self.selectedDeepComponentGlyphName)
            self.RCJKI.currentGlyph.width = self.RCJKI.project.settings['designFrame']['em_Dimension'][0]
        self.RCJKI.openGlyphWindow(self.RCJKI.currentGlyph)

    def colorPickerCallback(self, sender):
        if self.RCJKI.currentGlyph is None: return
        color = sender.get()
        r = color.redComponent()
        g = color.greenComponent()
        b = color.blueComponent()
        a = color.alphaComponent()
    
        self.RCJKI.currentGlyph.markColor = (r, g, b, a)
        self.controller.updateGlyphSetList()

    def windowCloses(self, sender):
        if CurrentGlyphWindow() is not None:
            CurrentGlyphWindow().close()
        self.RCJKI.currentGlyphWindow = None
        self.RCJKI.deepComponentEditionController.interface = None

    def tableView_dataCellForTableColumn_row_(self, tableView, tableColumn, row):
        self.RCJKI.tableView_dataCellForTableColumn_row_(tableView, tableColumn, row, self.w, '_deepComponentsEdition_glyphs', self.RCJKI.DCFonts2Fonts[self.RCJKI.currentFont])
