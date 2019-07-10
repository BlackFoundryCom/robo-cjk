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
from vanilla.dialogs import message
from mojo.glyphPreview import GlyphPreview
from mojo.UI import UpdateCurrentGlyphView
import Helpers

class Select2DeepCompoSheet():

    def __init__(self, interface, glyphdata, compositionName, selectedContours):
        self.ui = interface
        self.gd = glyphdata
        self.compositionName = compositionName
        self.selectedContours = selectedContours

        self.w = Sheet((330, 350), self.ui.w)
        self.font = self.ui.font
        self.storageFont = self.ui.font2Storage[self.font]

        self.selectedName = ""

        self.existingName = self.gd.existingName
        self.w.existingName_List = List((10, 10, 150, 150),
            self.existingName,
            selectionCallback = self._existingName_List_selectionCallback,
            drawFocusRing=False,
            allowsMultipleSelection = False)
        self.w.existingName_List.setSelection([])

        self.w.newName_button = Button((10, 160, 150, 20), 
            "new Version",
            callback = self._newName_button_callback)

        self.selectedLayer = ""
        self.existingLayers = []

        self.w.existingLayers_List = List((170, 10, 150, 150),
            self.existingLayers,
            selectionCallback = self._existingLayers_List_selectionCallback,
            editCallback = self._existingLayers_List_editCallback,
            drawFocusRing=False,
            allowsEmptySelection = False,
            allowsMultipleSelection = False)

        self.w.newLayerbutton = Button((170, 160, 150, 20), 
            "new Layer",
            callback = self._newLayer_button_callback)
        
        self.w.newLayerbutton.show(False)

        self.w.GlyphPreview = GlyphPreview((0, 190, -0, -30))

        self.w.addButton = Button((110, -30, -10, -10), 
            "add", 
            callback = self._addButton_callback)

        self.w.cancelButton = Button((10, -30, 100, -10), 
            "cancel", 
            callback = self._cancelButton_callback)

        Helpers.setDarkMode(self.w, self.ui.darkMode)
        self.w.open()

    def _addButton_callback(self, sender):
        if not self.selectedName:
            message("Warning, there is no selected name")
            return
        f = self.storageFont
        
        if self.selectedLayer not in f.layers:
            print(self.selectedLayer)
            f.newLayer(self.selectedLayer)
        
        if self.selectedName not in self.existingName:
            f.newGlyph(self.selectedName)

        g = f[self.selectedName].getLayer(self.selectedLayer)
        g.clear()

        for c in self.selectedContours:
            g.appendContour(c)

        g.width = self.ui.EM_Dimension_X
        g.round()
        g.update()

        if "deepComponentsLayer" not in f[self.selectedName].lib:
            f[self.selectedName].lib["deepComponentsLayer"] = []

        if "deepComponentsGlyph" not in f.lib:
            f.lib["deepComponentsGlyph"] = {}

        f[self.selectedName].lib["deepComponentsLayer"].append(self.selectedLayer)

        if not self.selectedName in f.lib["deepComponentsGlyph"]:
            f.lib["deepComponentsGlyph"][self.selectedName] = {}

        i = 0
        while True:
            index = "_%s"%str(i).zfill(2)
            ID = self.selectedName + index
            if ID not in f.lib["deepComponentsGlyph"][self.selectedName]:
                break
            i+=1

        if self.selectedLayer == "foreground":
            f.lib["deepComponentsGlyph"][self.selectedName][ID] = {}
        else:
            f.lib["deepComponentsGlyph"][self.selectedName][ID] = {self.selectedLayer:1000}

        self.gd.existingName = list(filter(lambda x: self.ui.selectedCompositionGlyphName["Name"] in x, list(self.storageFont.keys())))
        self.gd.variants_List.set(self.gd.existingName)

        self.ui.glyph.prepareUndo()

        if "deepComponentsGlyph" not in self.ui.glyph.lib:
            self.ui.glyph.lib["deepComponentsGlyph"] = {}

        self.ui.glyph.lib["deepComponentsGlyph"][self.selectedName] = (ID, (0, 0))

        for c in self.selectedContours:
            self.ui.glyph.removeContour(c)

        self.ui.glyph.performUndo()

        UpdateCurrentGlyphView()

        self.w.close()

    def _cancelButton_callback(self, sender):
        self.w.close()

    def _existingName_List_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            self.selectedName = ""
            self.existingLayers = []
            return
        self.selectedName = sender.get()[sel[0]]

        f = self.storageFont

        if self.selectedName not in f.keys():
            self.existingLayers = ["foreground"]
            self.w.newLayerbutton.show(False)

        elif "deepComponentsLayer" not in f[self.selectedName].lib or not f[self.selectedName].lib["deepComponentsLayer"]:
            self.existingLayers = ["foreground"]
            self.w.newLayerbutton.show(False)

        else:
            self.existingLayers = [layer.name for layer in f.layers]
            self.w.newLayerbutton.show(True)

        self.w.existingLayers_List.set(self.existingLayers)
        self.setGlyphPreview()

    def _existingLayers_List_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            self.selectedLayer = ""
            return
        self.selectedLayer = sender.get()[sel[0]]
        self.setGlyphPreview()

    def setGlyphPreview(self):
        f = self.storageFont
        if self.selectedName and self.selectedLayer and self.selectedName in self.existingName and self.selectedLayer in self.existingLayers:
            g = f[self.selectedName].getLayer(self.selectedLayer)
            self.w.GlyphPreview.setGlyph(g)
        else:
            self.w.GlyphPreview.setGlyph(None)

    def _newName_button_callback(self, sender):
        i = 0
        while True:
            index = "_%s"%str(i).zfill(2)
            name =  self.compositionName + index
            if name not in self.existingName:
                break
            i += 1

        self.w.existingName_List.append(name)
        self.w.existingName_List.setSelection([len(self.w.existingName_List.get())-1])

    def _existingLayers_List_editCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        self.selectedLayer = sender.get()[sel[0]]

    def _newLayer_button_callback(self, sender):
        i = 0
        while True:
            index = "_%s"%str(i).zfill(2)
            name =  "NewLayer" + index
            if name not in self.existingLayers:
                break
            i += 1

        self.w.existingLayers_List.append(name)

        