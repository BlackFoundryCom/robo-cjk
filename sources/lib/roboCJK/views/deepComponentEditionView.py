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
from vanilla.dialogs import askYesNo
from defconAppKit.windows.baseWindow import BaseWindowController

from AppKit import *

from mojo.UI import OpenGlyphWindow, AllGlyphWindows, CurrentGlyphWindow, PostBannerNotification
from mojo.roboFont import *
from mojo.canvas import *
from mojo.events import addObserver, removeObserver
from lib.cells.colorCell import RFColorCell
# from fontTools.pens import cocoaPen

import os
import json
# import Quartz

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

        

        self.canvasDrawer = mainCanvas.MainCanvas(self.RCJKI, self)
        self.w.mainCanvas = Canvas((200,0,-0,-240), 
            delegate=self.canvasDrawer,
            canvasSize=(5000, 5000),
            hasHorizontalScroller=False, 
            hasVerticalScroller=False)

        self.w.extremsList = PopUpButton((200, 0, 200, 20), 
            [], 
            sizeStyle = 'small',
            callback = self.extremsListCallback)

        self.w.dcOffsetXTextBox = TextBox((235, -260, 15, 20), "x:", sizeStyle = 'small')
        self.w.dcOffsetYTextBox = TextBox((285, -260, 15, 20), "y:", sizeStyle = 'small')

        self.deepComponentTranslateX = 0
        self.w.dcOffsetXEditText = EditText((250, -260, 50, 20), 
            self.deepComponentTranslateX,
            sizeStyle = "small",
            callback = self.dcOffsetXEditTextCallback,
            continuous = False)

        self.w.dcOffsetXEditText.getNSTextField().setBordered_(False)
        self.w.dcOffsetXEditText.getNSTextField().setDrawsBackground_(False)

        self.deepComponentTranslateY = 0
        self.w.dcOffsetYEditText = EditText((300, -260, 50, 20), 
            self.deepComponentTranslateY,
            sizeStyle = "small",
            callback = self.dcOffsetYEditTextCallback,
            continuous = False)

        self.w.dcOffsetYEditText.getNSTextField().setBordered_(False)
        self.w.dcOffsetYEditText.getNSTextField().setDrawsBackground_(False)

        slider = SliderListCell(minValue = 0, maxValue = 1000)
        # checkbox = CheckBoxListCell()
        self.slidersValuesList = []
        self.w.slidersList = List((200, -240, -0, -20),
            self.slidersValuesList,
            columnDescriptions = [
                                    {"title": "Layer", "editable": False, "width": 0},
                                    {"title": "Image", "editable": False, "cell": ImageListCell(), "width": 60}, 
                                    {"title": "Values", "cell": slider, "width": 520}
                                    # {"title": "Lock", "cell": checkbox, "width": 20},
                                   # {"title": "YValue", "cell": slider, "width": 250},
                                    
                                    ],
            editCallback = self.slidersListEditCallback,
            doubleClickCallback = self.sliderListDoubleClickCallback,
            drawFocusRing = False,
            allowsMultipleSelection = False,
            rowHeight = 50.0,
            showColumnTitles = False
            )

        self.w.addNLIButton = Button((-300, -20, 100, 20),
            'NLI',
            callback = self.addNLIButtonCallback)
        self.w.addLayerButton = Button((-200, -20, 100, 20), 
            "+",
            callback = self.addLayerButtonCallback)
        self.w.removeLayerButton = Button((-100, -20, 100, 20), 
            "-",
            callback = self.removeLayerButtonCallback)

        self.w.colorPicker = ColorWell((200,-260,20,20),
                callback=self.colorPickerCallback, 
                color=NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 0))

        self.delegate = tableDelegate.TableDelegate.alloc().initWithMaster(self)
        tableView = self.w.glyphSetList.getNSTableView()
        tableView.setDelegate_(self.delegate)

        self.dummyCell = NSCell.alloc().init()
        self.dummyCell.setImage_(None)

        self.observer()

        self.w.bind('close', self.windowCloses)
        self.w.bind('became main', self.windowBecameMain)
        self.w.open()

    def observer(self, remove=False):
        if not remove:
            addObserver(self, "glyphAdditionContextualMenuItems", "glyphAdditionContextualMenuItems")
            return
        removeObserver(self, "glyphAdditionContextualMenuItems")

    def glyphAdditionContextualMenuItems(self, info):
        info['additionContextualMenuItems'].append(("Import layer from next master", self.importLayerFromNextMaster))

    def importLayerFromNextMaster(self, sender):
        font = None
        for f in self.RCJKI.DCFonts2Fonts.keys():
            if f == self.RCJKI.currentFont: continue
            font = f 
        glyph = self.RCJKI.currentGlyph
        name = glyph.name
        glyph.prepareUndo()
        glyph.clear()
        glyph.appendGlyph(font[name].getLayer(glyph.layer.name))
        glyph.performUndo()
        glyph.update()

    def UpdateDCOffset(self):
        self.w.dcOffsetXEditText.set(self.deepComponentTranslateX)
        self.w.dcOffsetYEditText.set(self.deepComponentTranslateY)

    def dcOffsetXEditTextCallback(self, sender):
        try:
            self.deepComponentTranslateX = int(sender.get())
        except:
            sender.set(self.deepComponentTranslateX)
        self.w.mainCanvas.update()

    def dcOffsetYEditTextCallback(self, sender):
        try:
            self.deepComponentTranslateY = int(sender.get())
        except:
            sender.set(self.deepComponentTranslateY)
        self.w.mainCanvas.update()

    def addNLIButtonCallback(self, sender):
        self.RCJKI.deepComponentEditionController.makeNLIPaths(reset=True)

    def addLayerButtonCallback(self, sender):
        g = self.RCJKI.currentGlyph
        f = self.RCJKI.currentFont
        if len(f.getLayer("foreground")[g.name]):
            newGlyphLayer = list(filter(lambda l: not len(g.getLayer(l.name)), f.layers))[0]
            f.getLayer(newGlyphLayer.name).insertGlyph(g.getLayer("foreground"))
            self.RCJKI.currentGlyph = f.getLayer(newGlyphLayer.name)[g.name]
            self.slidersValuesList.append({'Layer': newGlyphLayer.name,
                                        'Image': None,
                                        'Values': 0
                                        # 'Lock':1,
                                        # 'YValue': 0
                                        })
        else:

            self.RCJKI.currentGlyph = f.getLayer("foreground")[g.name]
            self.RCJKI.currentGlyph.appendGlyph(self.RCJKI.DCFonts2Fonts[self.RCJKI.currentFont][self.selectedGlyphName])

        self.RCJKI.openGlyphWindow(self.RCJKI.currentGlyph)
        self.updateImageSliderList()
        self.RCJKI.updateViews()
        # self.setSliderList()

    def removeLayerButtonCallback(self, sender):
        sel = self.w.slidersList.getSelection()
        if not sel:
            PostBannerNotification("Error", "No selected layer")
            return

        layerName = self.slidersValuesList[sel[0]]['Layer']
        self.RCJKI.currentFont.getLayer(layerName)[self.RCJKI.currentGlyph.name].clear()

        self.slidersValuesList.pop(sel[0])
        del self.RCJKI.layersInfos[layerName]

        self.RCJKI.deepComponentGlyph = self.RCJKI.getDeepComponentGlyph()

        self.w.slidersList.set(self.slidersValuesList)
        self.w.mainCanvas.update()

    def saveLocalFontButtonCallback(self, sender):
        self.RCJKI.deepComponentEditionController.saveSubsetFonts()
        self.w.mainCanvas.update()
        
    def pullMasterGlyphsButtonCallback(self, sender):
        self.controller.pullDCMasters()
        self.w.mainCanvas.update()

    def pushBackButtonCallback(self, sender):
        self.controller.pushDCMasters()
        self.w.mainCanvas.update()

    def windowBecameMain(self, sender):
        self.updateImageSliderList()

    def updateImageSliderList(self):
        slidersValuesList = []
        for item in self.slidersValuesList:

            layerName = item["Layer"]
            g = self.RCJKI.currentFont[self.RCJKI.currentGlyph.name].getLayer(layerName)
            emDimensions = self.RCJKI.project.settings['designFrame']['em_Dimension']
            pdfData = self.RCJKI.getLayerPDFImage(g, emDimensions)

            d = {'Layer': layerName,
                'Image': NSImage.alloc().initWithData_(pdfData),
                'Values': item["Values"]
                # 'YValue': item["YValue"],
                # 'Lock': item["Lock"]
                }

            slidersValuesList.append(d)
        self.slidersValuesList = slidersValuesList
        self.w.slidersList.set(self.slidersValuesList)

    def setSliderList(self):
        self.RCJKI.layersInfos = {}
        self.slidersValuesList = []
        layers = [l.name for l in list(filter(lambda l: len(self.RCJKI.currentFont[self.RCJKI.currentGlyph.name].getLayer(l.name)), self.RCJKI.currentFont.layers))]
        for layerName in layers:
            if layerName == "foreground": continue
            g = self.RCJKI.currentFont[self.RCJKI.currentGlyph.name].getLayer(layerName)
            emDimensions = self.RCJKI.project.settings['designFrame']['em_Dimension']
            pdfData = self.RCJKI.getLayerPDFImage(g, emDimensions)

            d = {'Layer': layerName,
                'Image': NSImage.alloc().initWithData_(pdfData),
                'Values': 0
                # 'YValue': 0,
                # 'Lock': 1
                }

            self.slidersValuesList.append(d)
            self.RCJKI.layersInfos[layerName] = 0
        self.w.slidersList.set(self.slidersValuesList)

    def slidersListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return

        layersInfo = sender.get()
        layerInfo = layersInfo[sel[0]]

        selectedLayerName = layerInfo["Layer"]
        image = layerInfo["Image"]
        # lock = layerInfo["Lock"]
        value = layerInfo["Values"]
        # YValue = layerInfo["YValue"]

        # changed = False
        # # if lock:
        #     if Value != self.slidersValuesList[sel[0]]["Value"]:
        #         YValue = XValue
        #         changed = True

        #     elif YValue != self.slidersValuesList[sel[0]]["YValue"]:
        #         XValue = YValue
        #         changed = True

        # if lock != self.slidersValuesList[sel[0]]["Lock"]:
            # changed = True 

        self.RCJKI.layersInfos[selectedLayerName] = value
        self.slidersValuesList[sel[0]]["Values"] = value
        # self.slidersValuesList[sel[0]]["YValue"] = YValue 
        # self.slidersValuesList[sel[0]]["Lock"] = lock

        #if changed:
        # d = {'Layer': selectedLayerName,
        #     'Image': image,
        #     'Values': value
        #     # 'YValue': YValue,
        #     # 'Lock': lock
        #     }
        # layers = [e if i != sel[0] else d for i, e in enumerate(layersInfo)]
        # sender.set(layers)
        # sender.setSelection(sel)

        self.RCJKI.currentGlyph = self.RCJKI.currentFont[self.selectedDeepComponentGlyphName]
        self.RCJKI.deepComponentGlyph = self.RCJKI.getDeepComponentGlyph()
        self.w.mainCanvas.update()

    def sliderListDoubleClickCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        layerName = sender.get()[sel[0]]['Layer']
        self.RCJKI.currentGlyph = self.RCJKI.currentFont.getLayer(layerName)[self.RCJKI.currentGlyph.name]
        self.RCJKI.openGlyphWindow(self.RCJKI.currentGlyph)

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
        self.deepComponentTranslateX, self.deepComponentTranslateY = 0, 0
        self.w.dcOffsetXEditText.set(self.deepComponentTranslateX)
        self.w.dcOffsetYEditText.set(self.deepComponentTranslateY)
        self.w.mainCanvas.update()

    def glyphSetListdoubleClickCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        selectedGlyphName = sender.get()[sel[0]]['Name']
        self.RCJKI.openGlyphWindow(self.RCJKI.DCFonts2Fonts[self.RCJKI.currentFont][selectedGlyphName])

    def deepComponentsSetListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        self.RCJKI.deepComponentEditionController.makeNLIPaths()

        self.selectedDeepComponentGlyphName = sender.get()[sel[0]]['Name']

        self.controller.updateExtemeList(self.selectedDeepComponentGlyphName)
        if self.selectedDeepComponentGlyphName in self.RCJKI.currentFont:
            self.RCJKI.currentGlyph = self.RCJKI.currentFont[self.selectedDeepComponentGlyphName]

            if self.RCJKI.currentGlyph.markColor is None:
                r, g, b, a = 0, 0, 0, 0
            else: 
                r, g, b, a = self.RCJKI.currentGlyph.markColor
            self.w.colorPicker.set(NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, a))
        else:
            self.RCJKI.currentGlyph = None
        self.setSliderList()

        self.RCJKI.deepComponentGlyph = self.RCJKI.getDeepComponentGlyph()

        self.deepComponentTranslateX, self.deepComponentTranslateY = 0, 0
        self.w.dcOffsetXEditText.set(self.deepComponentTranslateX)
        self.w.dcOffsetYEditText.set(self.deepComponentTranslateY) 
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
        askYesNo('Do you want to save fonts?', "Without saving you'll loose unsaved modification", alertStyle = 2, parentWindow = None, resultCallback = self.yesnocallback)
        if CurrentGlyphWindow() is not None:
            CurrentGlyphWindow().close()
        self.RCJKI.currentGlyphWindow = None
        self.RCJKI.deepComponentEditionController.interface = None
        self.observer(True)

    def yesnocallback(self, yes):
        if yes:
            self.RCJKI.deepComponentEditionController.saveSubsetFonts()

    def tableView_dataCellForTableColumn_row_(self, tableView, tableColumn, row):
        self.RCJKI.tableView_dataCellForTableColumn_row_(tableView, tableColumn, row, self.w, '_deepComponentsEdition_glyphs', self.RCJKI.DCFonts2Fonts[self.RCJKI.currentFont])
