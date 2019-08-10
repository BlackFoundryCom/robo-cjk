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

    def __init__(self, interface, parentWindow, selectedContours):
        self.ui = interface
        # self.gd = glyphdata
        self.compositionName = None
        self.selectedContours = selectedContours

        self.ui.getCompositionGlyph()

        self.sheet = Sheet((330, 650), parentWindow)
        self.font = self.ui.font
        # self.storageFont = self.ui.font2Storage[self.font]
        # print(self.ui.glyph)
        self.sheet.compositionGlyph_TextBox = TextBox((10, 7, -10, 20), 
            "Glyph Composition", 
            sizeStyle = "regular", 
            alignment = "center")
        self.sheet.compositionGlyph_List = List((10, 30, -10, 160),
            self.ui.compositionGlyph,
            columnDescriptions = [
                                {"title": "Char", "width" : 30},
                                {"title": "Name", "width" : 105},                  
                                ],
            selectionCallback = self._compositionGlyph_List_selectionCallback, 
            drawFocusRing=False)

        self.selectedName = ""

        self.variantsNames = []#[value["Name"] for value in self.gd.variantsName]

        self.sheet.variantsNames_TextBox = TextBox((10, 197, 150, 20), 
            "Variants", 
            sizeStyle = "regular", 
            alignment = "center")
        self.sheet.variantsNames_List = List((10, 220, 150, 130),
            self.variantsNames,
            selectionCallback = self._variantsNames_List_selectionCallback,
            drawFocusRing=False,
            allowsMultipleSelection = False)
        self.sheet.variantsNames_List.setSelection([])

        self.sheet.newName_button = Button((10, 350, 150, 20), 
            "New Variant",
            callback = self._newName_button_callback)

        self.selectedLayer = ""
        self.existingLayers = []

        self.sheet.existingLayers_TextBox = TextBox((170, 197, 150, 20), 
            "Layers", 
            sizeStyle = "regular", 
            alignment = "center")
        self.sheet.existingLayers_List = List((170, 220, 150, 130),
            self.existingLayers,
            selectionCallback = self._existingLayers_List_selectionCallback,
            editCallback = self._existingLayers_List_editCallback,
            drawFocusRing=False,
            allowsEmptySelection = False,
            allowsMultipleSelection = False)

        self.sheet.newLayerbutton = Button((170, 350, 150, 20), 
            "New Layer",
            callback = self._newLayer_button_callback)
        
        self.sheet.newLayerbutton.show(False)

        self.sheet.glyphPreview = GlyphPreview((0, -275, -0, -0))

        self.sheet.addButton = Button((110, -30, -10, -10), 
            "add", 
            callback = self._addButton_callback)

        self.sheet.cancelButton = Button((10, -30, 100, -10), 
            "cancel", 
            callback = self._cancelButton_callback)

        Helpers.setDarkMode(self.sheet, self.ui.darkMode)

        self.sheet.bind('close', self.ui.killdcSheet)
        self.sheet.open()

    def _compositionGlyph_List_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            self.compositionName = None
            return
        self.compositionName = self.ui.compositionGlyph[sel[0]]['Name']
        # self.variantsName = [dict(Sel=name in self.ui.currentGlyph_DeepComponents['NewDeepComponents'], Name = name) for name in list(filter(lambda x: self.ui.selectedCompositionGlyphName["Name"] in x, list(self.storageFont.keys())))]
        self.variantsNames = list(filter(lambda x: self.compositionName in x, self.ui.font2Storage[self.font].keys()))
        self.sheet.variantsNames_List.set(self.variantsNames)

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

        self.sheet.close()

    def _cancelButton_callback(self, sender):
        print(self.sheet.__dict__.keys())
        self.sheet.close()
        print(self.sheet.__dict__.keys())

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
                self.sheet.newLayerbutton.show(False)

            elif "deepComponentsLayer" not in f[self.selectedName].lib or not f[self.selectedName].lib["deepComponentsLayer"]:
                self.existingLayers = ["foreground"]
                self.sheet.newLayerbutton.show(False)

            else:
                self.existingLayers = [layer.name for layer in f.layers]
                print(self.existingLayers)
                self.sheet.newLayerbutton.show(True)

            self.sheet.existingLayers_List.setSelection([])
            self.sheet.existingLayers_List.set(self.existingLayers)

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
        self.sheet.glyphPreview.setGlyph(g)

    def _newName_button_callback(self, sender):
        i = 0
        while True:
            index = "_%s"%str(i).zfill(2)
            name =  self.compositionName + index
            if name not in self.variantsNames:
                break
            i += 1

        self.sheet.variantsNames_List.append(name)
        self.sheet.variantsNames_List.setSelection([len(self.sheet.variantsNames_List.get())-1])

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

        self.sheet.existingLayers_List.append(name)

        