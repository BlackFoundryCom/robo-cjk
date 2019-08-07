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
from vanilla import *
from mojo.roboFont import *
from mojo.UI import OpenGlyphWindow, CurrentGlyphWindow
from mojo.canvas import Canvas
from AppKit import NSAppearance, NSColor
from drawers.LayersCanvas import LayersCanvas
# from drawers.LayersPreviewCanvas import LayersPreviewCanvas
from drawers.Tester_DeepComponentDrawer import TesterDeepComponent
from lib.cells.colorCell import RFColorCell
from Helpers import normalizeUnicode

class DeepComponentsCreator(Group):

    def __init__(self, posSize, interface):
        super(DeepComponentsCreator, self).__init__(posSize)
        self.ui = interface

        self.storageGlyph = None
        self.storageGlyphName = ""
        self.StorageGlyphCurrentLayer = ""

        self.title = TextBox((10, 5, -10, 20),
            "Deep Component Creator",
            alignment = "center")

        self.top = Group((0, 0, -0, -0))

        self.top.jumpTo = SearchBox((0,30,195,20),
            placeholder = "Char/Name",
            sizeStyle = "small",
            callback = self._jumpTo_callback
            )

        self.displayGlyphset_settingList = ['find Char/Name', "Sort by key"]
        self.displaySettings = 'find Char/Name'
        self.top.displayGlyphset_setting = PopUpButton((0, 10, 195, 20),
            self.displayGlyphset_settingList,
            sizeStyle = "small",
            callback = self._displayGlyphset_setting_callback)

        self.glyphset = []
        self.top.glyphset_List = List((0,50,195,-0),
            self.glyphset,
            columnDescriptions = [
                                {"title": "Char", "width" : 30},
                                {"title": "Name", "width" : 105},                  
                                ],
            drawFocusRing=False, 
            selectionCallback = self._glyphset_List_selectionCallback,
            )

        self.set_glyphset_List()

        self.top.layersCanvas = Canvas((195,10,-0,-0), 
            delegate=LayersCanvas(self.ui, self),
            hasHorizontalScroller=False, 
            hasVerticalScroller=False)

        self.bottom = Group((0, 0, -0, -0))

        self.bottom.layersTextBox = TextBox((0,5,195,20), 
                'Layers',
                sizeStyle = "small")

        self.layerList = []
        self.bottom.layers_list = List((0,25,195,-50), 
                self.layerList,
                drawFocusRing = False,
                selectionCallback = self._layers_list_selectionCallback,
                editCallback = self._layers_list_editCallback)

        self.bottom.newLayer_Button = SquareButton((0, -50, 30, 30),
            '+',
            sizeStyle="small",
            callback = self._newLayer_Button_callback)

        self.bottom.assignLayerToGlyph_Button = SquareButton((30, -50, 165, 30),
            'Assign Layer to Glyph ->',
            sizeStyle="small",
            callback = self._assignLayerToGlyph_Button_callback)

        slider = SliderListCell(minValue = 0, maxValue = 1000)
        self.slidersValuesList = []
        self.bottom.sliderList = List((195,0,-0,-20),self.slidersValuesList,
            columnDescriptions = [{"title": "Layer" }, 
                                    {"title": "Values", "cell": slider}],
            editCallback = self._sliderList_editCallback,
            drawFocusRing = False,
            allowsMultipleSelection = False)

        paneDescriptors = [
            dict(view=self.top, identifier="top"),
            dict(view=self.bottom, identifier="bottom"),
        ]

        self.mainSplitView = SplitView((0, 20, -0, -0), 
            paneDescriptors,
            isVertical = False,
            dividerStyle="thin"
            )

    def getGlyphset(self):
        return [dict(Char=chr(int(name.split("_")[0],16)), Name = name) for name in self.ui.font2Storage[self.ui.font].keys()]

    def _displayGlyphset_setting_callback(self, sender):
        self.displaySettings = self.displayGlyphset_settingList[sender.get()]
        if self.displaySettings == 'find Char/Name':
            self.ui.glyphset = self.ui.font.lib['public.glyphOrder']
            # glyphset = [dict(Char=chr(int(name.split("_")[0],16)), Name = name) for name in self.ui.font2Storage[self.ui.font].keys()]
            self.glyphset = self.getGlyphset()
            self.top.glyphset_List.set(self.glyphset)

    def set_glyphset_List(self):
        if self.ui.font in self.ui.glyphsSetDict and self.displaySettings == 'find Char/Name':
            self.glyphset = self.getGlyphset()
            self.top.glyphset_List.set(self.glyphset)
            self.layerList = [layer.name for layer in self.ui.font2Storage[self.ui.font].layers]
            self.bottom.layers_list.set(self.layerList)


    def _glyphset_List_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            self.storageGlyph = None
            TesterDeepComponent.translateX = 0
            TesterDeepComponent.translateY = 0
            self.ui.w.mainCanvas.update()
            return
        self.storageFont = self.ui.font2Storage[self.ui.font]
        self.storageGlyphName = sender.get()[sel[0]]["Name"]
        self.storageGlyph = self.ui.font2Storage[self.ui.font][self.storageGlyphName]

        self.setSliderList()

        self.top.layersCanvas.update()
        # self.layersPreviewCanvas.update()

    def setSliderList(self):
        self.slidersValuesList = [dict(Layer=layerName, Values=0) for layerName in self.storageGlyph.lib['deepComponentsLayer'] if layerName != "foreground"]
        self.bottom.sliderList.set(self.slidersValuesList)

    def _sliderList_editCallback(self, sender):
        self.slidersValuesList = sender.get()
        self.ui.w.mainCanvas.update()

    def _layers_list_editCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        
        newName = sender.get()[sel[0]]
        oldName = self.layerList[sel[0]]
        

        for storageFont in self.ui.font2Storage.values():
            for layer in storageFont.layers:
                if layer.name == oldName:
                    layer.name = newName

        storageFont = self.ui.font2Storage[self.ui.font]
        self.layerList = [layer.name for layer in storageFont.layers]
        self.selectedLayerName = newName

    def _layers_list_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return

        self.selectedLayerName = sender.get()[sel[0]]
        self.top.layersCanvas.update()

    def _newLayer_Button_callback(self, sender):
        i=0
        while True:
            index = "_%s"%str(i).zfill(2)
            name = "NewLayer"+index
            if not name in self.layerList:
                break
            i+=1

        for storageFont in self.ui.font2Storage.values():
            # storageFont = self.ui.font2Storage[self.ui.font]
            storageFont.newLayer(name)

        self.layerList.append(name)
        self.bottom.layers_list.set(self.layerList)

    def _assignLayerToGlyph_Button_callback(self, sender):
        storageGlyphName = self.storageGlyphName
        StorageGlyphCurrentLayer = self.StorageGlyphCurrentLayer

        if storageGlyphName is None:
            message("Warning there is no selected glyph")
            return

        if not self.selectedLayerName:
            message("Warning there is no selected layer")
            return

        storageFont = self.ui.font2Storage[self.ui.font]
        layer = StorageGlyphCurrentLayer

        if not layer:
            layer = storageFont[storageGlyphName]

        layer.round()
        
        for stgFont in self.ui.font2Storage.values():
            if self.selectedLayerName not in stgFont[storageGlyphName].lib["deepComponentsLayer"]:
                stgFont.getLayer(self.selectedLayerName).insertGlyph(layer)
                stgFont[storageGlyphName].lib["deepComponentsLayer"].append(self.selectedLayerName)

        storageFont[storageGlyphName].update()

        self.top.layersCanvas.update()  

        self.setSliderList()      

    def _jumpTo_callback(self, sender):
        string = sender.get()
        if not string:
            self.top.glyphset_List.setSelection([])
            self.top.glyphset_List.set(self.glyphset)
            self.ui.glyphset = self.ui.font.lib['public.glyphOrder']
            return

        try: 
            if self.displaySettings == 'find Char/Name':
                glyphSet = [e["Name"].split('_')[0] for e in self.glyphset]
                if string.startswith("uni"):
                    index = glyphSet.index(string[3:])

                elif len(string) == 1:
                    code = "uni"+normalizeUnicode(hex(ord(string[3:]))[2:].upper())
                    index = glyphSet.index(code)

                else:
                    index = glyphSet.index(string)

                self.top.glyphset_List.setSelection([index])

            elif self.displaySettings == 'Sort by key':
                glyphSet = [e["Name"] for e in self.glyphset]
                name = string
                if  string.startswith("uni"):
                    name = string[3:]
                elif len(string) == 1:
                    name = normalizeUnicode(hex(ord(string))[2:].upper())
                self.top.glyphset_List.set([dict(Name = names, Char = chr(int(names.split('_')[0],16))) for names in glyphSet if name in names])
        except:
            pass
