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
from mojo.UI import UpdateCurrentGlyphView, CurrentGlyphWindow
import Helpers

class Select2DeepCompoSheet():

    def __init__(self, interface, selectedContours):
        self.ui = interface
        # self.gd = glyphdata
        self.compositionName = None
        self.selectedContours = selectedContours

        self.ui.getCompositionGlyph()

        self.w = Sheet((330, 650), CurrentGlyphWindow().window())
        self.font = self.ui.font
        # self.storageFont = self.ui.font2Storage[self.font]
        # print(self.ui.glyph)
        self.w.compositionGlyph_TextBox = TextBox((10, 7, -10, 20), 
            "Glyph Composition", 
            sizeStyle = "regular", 
            alignment = "center")
        self.w.compositionGlyph_List = List((10, 30, -10, 160),
            self.ui.compositionGlyph,
            columnDescriptions = [
                                {"title": "Char", "width" : 30},
                                {"title": "Name", "width" : 105},                  
                                ],
            selectionCallback = self._compositionGlyph_List_selectionCallback, 
            drawFocusRing=False)

        self.selectedName = ""

        self.variantsNames = []#[value["Name"] for value in self.gd.variantsName]

        self.w.variantsNames_TextBox = TextBox((10, 197, 150, 20), 
            "Variants", 
            sizeStyle = "regular", 
            alignment = "center")
        self.w.variantsNames_List = List((10, 220, 150, 130),
            self.variantsNames,
            selectionCallback = self._variantsNames_List_selectionCallback,
            drawFocusRing=False,
            allowsMultipleSelection = False)
        self.w.variantsNames_List.setSelection([])

        self.w.newName_button = Button((10, 350, 150, 20), 
            "New Variant",
            callback = self._newName_button_callback)

        self.selectedLayer = ""
        self.existingLayers = []

        self.w.existingLayers_TextBox = TextBox((170, 197, 150, 20), 
            "Layers", 
            sizeStyle = "regular", 
            alignment = "center")
        self.w.existingLayers_List = List((170, 220, 150, 130),
            self.existingLayers,
            selectionCallback = self._existingLayers_List_selectionCallback,
            editCallback = self._existingLayers_List_editCallback,
            drawFocusRing=False,
            allowsEmptySelection = False,
            allowsMultipleSelection = False)

        self.w.newLayerbutton = Button((170, 350, 150, 20), 
            "New Layer",
            callback = self._newLayer_button_callback)
        
        self.w.newLayerbutton.show(False)

        self.w.glyphPreview = GlyphPreview((0, -275, -0, -0))

        self.w.addButton = Button((110, -30, -10, -10), 
            "add", 
            callback = self._addButton_callback)

        self.w.cancelButton = Button((10, -30, 100, -10), 
            "cancel", 
            callback = self._cancelButton_callback)
# 
        Helpers.setDarkMode(self.w, self.ui.darkMode)
        self.w.open()

    def _compositionGlyph_List_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            self.compositionName = None
            return
        self.compositionName = self.ui.compositionGlyph[sel[0]]['Name']
        # self.variantsName = [dict(Sel=name in self.ui.currentGlyph_DeepComponents['NewDeepComponents'], Name = name) for name in list(filter(lambda x: self.ui.selectedCompositionGlyphName["Name"] in x, list(self.storageFont.keys())))]
        self.variantsNames = list(filter(lambda x: self.compositionName in x, self.ui.font2Storage[self.font].keys()))
        self.w.variantsNames_List.set(self.variantsNames)

    def _addButton_callback(self, sender):
        if not self.selectedName:
            message("Warning, there is no selected name")
            return

        f = self.ui.font2Storage[self.font]
        # f = self.storageFont
     
        if self.selectedLayer not in f.layers:
            for storageFont in self.ui.font2Storage.values(): 
                storageFont.newLayer(self.selectedLayer)
                storageFont.update()
        
        if self.selectedName not in self.variantsNames:
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

        # self.gd.variantsName = [dict(Sel=0, Name = name) for name in list(filter(lambda x: self.ui.selectedCompositionGlyphName["Name"] in x, list(f.keys())))]
        # self.gd.variants_List.set(self.gd.variantsName)
        self.ui.w.deepComponentGroup.creator.storageFont_Glyphset.set_glyphset_List()

        self.ui.glyph.prepareUndo()

        if "deepComponentsGlyph" not in self.ui.glyph.lib:
            self.ui.glyph.lib["deepComponentsGlyph"] = {}

        self.ui.glyph.lib["deepComponentsGlyph"][self.selectedName] = (ID, (0, 0))
        self.ui.glyph.update()

        self.ui.glyph.performUndo()

        self.ui.currentGlyph_DeepComponents = {
                                            'CurrentDeepComponents':{}, 
                                            'Existing':{}, 
                                            'NewDeepComponents':{},
                                            }
        self.ui.getDeepComponents_FromCurrentGlyph()


        self.ui.updateViews()

        self.w.close()

    def _cancelButton_callback(self, sender):
        self.w.close()

    def _variantsNames_List_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            self.selectedName = ""
            self.existingLayers = []
            return
        try:
            self.selectedName = sender.get()[sel[0]]

            f = self.ui.font2Storage[self.font]
            # f = self.storageFont

            if self.selectedName not in f.keys():
                self.existingLayers = ["foreground"]
                self.w.newLayerbutton.show(False)

            elif "deepComponentsLayer" not in f[self.selectedName].lib or not f[self.selectedName].lib["deepComponentsLayer"]:
                self.existingLayers = ["foreground"]
                self.w.newLayerbutton.show(False)

            else:
                self.existingLayers = [layer.name for layer in f.layers]
                print(self.existingLayers)
                self.w.newLayerbutton.show(True)

            self.w.existingLayers_List.setSelection([])
            self.w.existingLayers_List.set(self.existingLayers)

            self.setGlyphPreview()
        except:pass

    def _existingLayers_List_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            self.selectedLayer = ""
            return
        self.selectedLayer = sender.get()[sel[0]]
        self.setGlyphPreview()

    def setGlyphPreview(self):
        f = self.ui.font2Storage[self.ui.font]
        if f is None:
            return
        if self.selectedName and self.selectedLayer and self.selectedName in self.variantsNames and self.selectedLayer in self.existingLayers:
            g = f[self.selectedName].getLayer(self.selectedLayer).copy()
        else:
            g = None
        self.w.glyphPreview.setGlyph(g)

    def _newName_button_callback(self, sender):
        i = 0
        while True:
            index = "_%s"%str(i).zfill(2)
            name =  self.compositionName + index
            if name not in self.variantsNames:
                break
            i += 1

        self.w.variantsNames_List.append(name)
        self.w.variantsNames_List.setSelection([len(self.w.variantsNames_List.get())-1])

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

        