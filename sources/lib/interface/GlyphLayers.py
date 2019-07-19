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
from Helpers import normalizeUnicode

class GlyphLayers(Group):

    def __init__(self, posSize, interface):
        super(GlyphLayers, self).__init__(posSize)
        self.ui = interface

        self.storageGlyph = None
        self.storageGlyphName = ""
        self.StorageGlyphCurrentLayer = ""

        self.jumpTo = SearchBox((0,0,165,20),
            placeholder = "Char/Name",
            sizeStyle = "small",
            callback = self._jumpTo_callback
            )

        self.displayGlyphset_settingList = ['find Char/Name', "Sort by key"]
        self.displaySettings = 'find Char/Name'
        self.displayGlyphset_setting = PopUpButton((170, 0, 200, 20),
            self.displayGlyphset_settingList,
            sizeStyle = "small",
            callback = self._displayGlyphset_setting_callback)

        self.glyphset = []
        self.glyphset_List = List((0,20,165,-200),
            self.glyphset,
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
        self.sliderList = List((0,-190,350,-0),self.slidersValuesList,
            columnDescriptions = [{"title": "Layer" }, 
                                    {"title": "Values", "cell": slider}],
            editCallback = self._sliderList_editCallback,
            drawFocusRing = False,
            allowsMultipleSelection = False)

        self.layersPreviewCanvas = Canvas((350,-190,-0,-0), 
            delegate=LayersPreviewCanvas(self.ui, self),
            hasHorizontalScroller=False, 
            hasVerticalScroller=False)

    def getGlyphset(self):
        return [dict(Char=chr(int(name.split("_")[0],16)), Name = name) for name in self.ui.font2Storage[self.ui.font].keys()]

    def _displayGlyphset_setting_callback(self, sender):
        self.displaySettings = self.displayGlyphset_settingList[sender.get()]
        if self.displaySettings == 'find Char/Name':
            self.ui.glyphset = self.ui.font.lib['public.glyphOrder']
            # glyphset = [dict(Char=chr(int(name.split("_")[0],16)), Name = name) for name in self.ui.font2Storage[self.ui.font].keys()]
            self.glyphset = self.getGlyphset()
            self.glyphset_List.set(self.glyphset)

    def set_glyphset_List(self):
        if self.ui.font in self.ui.glyphsSetDict and self.displaySettings == 'find Char/Name':
            self.glyphset = self.getGlyphset()
            self.glyphset_List.set(self.glyphset)

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

    def _jumpTo_callback(self, sender):
        string = sender.get()
        if not string:
            self.glyphset_List.setSelection([])
            self.glyphset_List.set(self.glyphset)
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

                self.glyphset_List.setSelection([index])

            elif self.displaySettings == 'Sort by key':
                glyphSet = [e["Name"] for e in self.glyphset]
                name = string
                if  string.startswith("uni"):
                    name = string[3:]
                elif len(string) == 1:
                    name = normalizeUnicode(hex(ord(string))[2:].upper())
                self.glyphset_List.set([dict(Name = names, Char = chr(int(names.split('_')[0],16))) for names in glyphSet if name in names])
        except:
            pass
