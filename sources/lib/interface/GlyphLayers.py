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
from drawers.LayersPreviewCanvas import LayersPreviewCanvas
from lib.cells.colorCell import RFColorCell

class GlyphLayers(Group):

    def __init__(self, posSize, interface):
        super(GlyphLayers, self).__init__(posSize)
        self.ui = interface

        self.storageGlyph = None
        self.storageGlyphName = ""
        self.selectedLayer = ""

        self.goTo = EditText((0,0,165,20),
            placeholder = "🔎 Char/Name",
            sizeStyle = "small")

        self.glyphset_List = List((0,20,165,-200),
            [],
            columnDescriptions = [
                                {"title": "Char", "width" : 30},
                                {"title": "Name", "width" : 105},                  
                                ],
            drawFocusRing=False, 
            selectionCallback = self._glyphset_List_selectionCallback,
            )

        self.set_glyphset_List()

        self.layersCanvas = Canvas((165,20,-0,-200), 
            delegate=LayersCanvas(self.ui, self),
            hasHorizontalScroller=False, 
            hasVerticalScroller=False)

        slider = SliderListCell(minValue = 0, maxValue = 1000)
        self.slidersValuesList = []
        # self.slidersValuesList = [dict(Layer=layer.name, Values=0) for layer in self.availableLayers if layer.name != "foreground"]
        self.sliderList = List((0,-190,350,-10),self.slidersValuesList,
            columnDescriptions = [{"title": "Layer" }, 
                                    {"title": "Values", "cell": slider}],
            editCallback = self._sliderList_editCallback,
            drawFocusRing = False,
            allowsMultipleSelection = False)

        self.layersPreviewCanvas = Canvas((350,-190,-0,-0), 
            delegate=LayersPreviewCanvas(self.ui, self),
            hasHorizontalScroller=False, 
            hasVerticalScroller=False)

    def set_glyphset_List(self):
        if self.ui.font in self.ui.glyphsSetDict:
            self.glyphset_List.set([dict(Char=chr(int(name.split("_")[0],16)), Name = name) for name in self.ui.font2Storage[self.ui.font].keys()])

    def _glyphset_List_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        self.storageFont = self.ui.font2Storage[self.ui.font]
        self.storageGlyphName = sender.get()[sel[0]]["Name"]
        self.storageGlyph = self.ui.font2Storage[self.ui.font][self.storageGlyphName]

        self.setSliderList()

        self.layersCanvas.update()
        self.layersPreviewCanvas.update()

    def setSliderList(self):
        self.slidersValuesList = [dict(Layer=layerName, Values=0) for layerName in self.storageGlyph.lib['deepComponentsLayer'] if layerName != "foreground"]
        self.sliderList.set(self.slidersValuesList)

    def _sliderList_editCallback(self, sender):
        self.slidersValuesList = sender.get()
        self.layersPreviewCanvas.update()
