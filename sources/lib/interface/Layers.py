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

class Layers(Group):

    def __init__(self, posSize, interface):
        super(Layers, self).__init__(posSize)
        self.ui = interface

        self.layersTextBox = TextBox((0,0,-0,20), 
                'Layers',
                sizeStyle = "small")

        self.layers_list = List((0,20,215,-70), 
                self.ui.layerList,
                drawFocusRing = False,
                selectionCallback = self._layers_list_selectionCallback,
                editCallback = self._layers_list_editCallback)

        self.newLayer_Button = SquareButton((0, -70, -0, 30),
            'New Layer',
            sizeStyle="small",
            callback = self._newLayer_Button_callback)

        self.assignLayerToGlyph_Button = SquareButton((0, -30, -0, 30),
            'Assign Layer to Glyph ->',
            sizeStyle="small",
            callback = self._assignLayerToGlyph_Button_callback)

    def _layers_list_editCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        
        newName = sender.get()[sel[0]]
        oldName = self.ui.layerList[sel[0]]
        storageFont = self.ui.font2Storage[self.ui.font]

        for layer in storageFont.layers:
            if layer.name == oldName:
                layer.name = newName

        self.ui.layerList = [layer.name for layer in storageFont.layers]
        self.selectedLayerName = newName

    def _layers_list_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return

        self.selectedLayerName = sender.get()[sel[0]]
        self.ui.w.deepComponentsEditorGroup.GlyphLayers.layersCanvas.update()

    def _newLayer_Button_callback(self, sender):
        i=0
        while True:
            index = "_%s"%str(i).zfill(2)
            name = "NewLayer"+index
            if not name in self.ui.layerList:
                break
            i+=1

        storageFont = self.ui.font2Storage[self.ui.font]
        storageFont.newLayer(name)

        self.ui.layerList.append(name)
        self.layers_list.set(self.ui.layerList)

    def _assignLayerToGlyph_Button_callback(self, sender):
        storageGlyphName = self.ui.w.deepComponentsEditorGroup.GlyphLayers.storageGlyphName
        StorageGlyphCurrentLayer = self.ui.w.deepComponentsEditorGroup.GlyphLayers.StorageGlyphCurrentLayer

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
        
        storageFont.getLayer(self.selectedLayerName).insertGlyph(layer)
        storageFont[storageGlyphName].lib["deepComponentsLayer"].append(self.selectedLayerName)
        storageFont[storageGlyphName].update()

        self.ui.w.deepComponentsEditorGroup.GlyphLayers.layersCanvas.update()  

        self.ui.w.deepComponentsEditorGroup.GlyphLayers.setSliderList()      
