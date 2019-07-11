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
from mojo.UI import UpdateCurrentGlyphView
from mojo.roboFont import *
from Helpers import deepolation

class DeepComponentsInstantiator(Group):

    def __init__(self, posSize, interface):
        super(DeepComponentsInstantiator, self).__init__(posSize)
        self.ui = interface

        segmentedElements = ["Select Deep Component", "New Deep Component"]
        self.deepCompo_segmentedButton = SegmentedButton((0,0,-0,20), 
                [dict(title=e, width = (550)/len(segmentedElements)) for e in segmentedElements],
                callback = self._deepCompo_segmentedButton_callback,
                sizeStyle='regular')
        
        self.selectDeepCompo = Group((0, 30,-0, -0))
        self.newDeepCompo = Group((0, 30,-0, -0))

        self.selectDeepCompo.list = List((0, 0, 350, -0), [],
            drawFocusRing=False, )

        slider = SliderListCell(minValue = 0, maxValue = 1000)
        self.newDeepCompo.list = List((0, 0, 350, -0), 
            [],
            columnDescriptions = [{"title": "Layer" }, 
                                    {"title": "Values", "cell": slider}],
            drawFocusRing=False, 
            editCallback = self._newDeepCompo_List_editCallback)

        self.deepCompo_segmentedButton.set(0)
        self.newDeepCompo.show(0)

        self.addDeepCompo_button = SquareButton((-200, 30, -0, 30), 
            "Add", 
            sizeStyle = "small",
            callback = self._addDeepCompo_callback)

        self.replaceDeepCompo_button = SquareButton((-200, 65, -0, 30), 
            "Replace", 
            sizeStyle = "small",
            callback = self._replaceDeepCompo_callback)

    def _deepCompo_segmentedButton_callback(self, sender):
        sel = sender.get()
        self.selectDeepCompo.show(abs(sel-1))
        self.newDeepCompo.show(sel)
        if sel:
            self.ui.newDeepComponent_active = True
            self.ui.temp_DeepComponents = {}
            if self.ui.selectedVariantName:
                self.ui.temp_DeepComponents[self.ui.selectedVariantName] = {}
        else:
            self.ui.newDeepComponent_active = False
            self.ui.temp_DeepComponents = {}
        if sel:
            self.setSliderList()
        else:
            self.ui.temp_DeepComponents = {}
        if self.ui.temp_DeepComponents:
            self.newDeepCompo.list.set(self.ui.temp_DeepComponents[self.ui.selectedVariantName]['Values'])
        self.updateViews()

    def setSliderList(self):
        if hasattr(self.ui, "selectedVariantName") and self.ui.selectedVariantName and self.ui.newDeepComponent_active and self.ui.selectedVariantName in self.ui.temp_DeepComponents:
            storageFont = self.ui.font2Storage[self.ui.font]
            storageGlyph = storageFont[self.ui.selectedVariantName]
            self.ui.temp_DeepComponents[self.ui.selectedVariantName]['Values'] = [dict(Layer=layerName, Values=0) for layerName in storageGlyph.lib['deepComponentsLayer'] if layerName != "foreground"]
        else:
            self.ui.temp_DeepComponents = {}  
            # self.newDeepCompo.list.set([])          
        if self.ui.temp_DeepComponents:
            self.newDeepCompo.list.set(self.ui.temp_DeepComponents[self.ui.selectedVariantName]['Values'])

    def _newDeepCompo_List_editCallback(self, sender):
        if not sender.get(): return
        if self.ui.selectedVariantName not in self.ui.temp_DeepComponents:
            self.ui.temp_DeepComponents[self.ui.selectedVariantName] = {}
        values = self.ui.temp_DeepComponents[self.ui.selectedVariantName]['Values'] = sender.get()
        newGlyph = deepolation(RGlyph(), self.ui.font2Storage[self.ui.font][self.ui.selectedVariantName], layersInfo = {e["Layer"]:int(e["Values"]) for e in values})
        self.ui.temp_DeepComponents[self.ui.selectedVariantName]['Glyph'] = newGlyph
        if not 'Offset' in self.ui.temp_DeepComponents[self.ui.selectedVariantName]:
            self.ui.temp_DeepComponents[self.ui.selectedVariantName]['Offset'] = (0, 0)
        else:
            x, y = self.ui.temp_DeepComponents[self.ui.selectedVariantName]['Offset']
            newGlyph.moveBy((x, y))
        self.updateViews()

    def updateViews(self):
        self.ui.w.activeMasterGroup.glyphSet.canvas.update()
        UpdateCurrentGlyphView()

    def _replaceDeepCompo_callback(self, sender):
        if self.ui.current_DeepComponent_selection is None: return

        if self.ui.current_DeepComponent_selection in self.ui.current_DeepComponents:
            glyphName = self.ui.current_DeepComponents[self.ui.current_DeepComponent_selection][0]
            if glyphName in self.ui.glyph.lib["deepComponentsGlyph"]:
                del self.ui.glyph.lib["deepComponentsGlyph"][glyphName]

        self.addDeepCompo()

    def _addDeepCompo_callback(self, sender):
        self.addDeepCompo()

    def addDeepCompo(self):
        if not self.ui.selectedVariantName:
            message("Warning, there is no selected name")
            return
        f = self.ui.font2Storage[self.ui.font]

        if not self.ui.selectedVariantName in f.lib["deepComponentsGlyph"]:
            f.lib["deepComponentsGlyph"][self.ui.selectedVariantName] = {}

        i = 0
        while True:
            index = "_%s"%str(i).zfill(2)
            ID = self.ui.selectedVariantName + index
            if ID not in f.lib["deepComponentsGlyph"][self.ui.selectedVariantName]:
                break
            i+=1

        for temp_deepCompo in self.ui.temp_DeepComponents:

            f.lib["deepComponentsGlyph"][self.ui.selectedVariantName][ID] = {v["Layer"]: int(v["Values"]) for v in self.ui.temp_DeepComponents[temp_deepCompo]['Values']}
            offset_X, offset_Y = self.ui.temp_DeepComponents[temp_deepCompo]['Offset']

        if "deepComponentsGlyph" not in self.ui.glyph.lib:
            self.ui.glyph.lib["deepComponentsGlyph"] = {}

        self.ui.glyph.lib["deepComponentsGlyph"][self.ui.selectedVariantName] = (ID, (offset_X, offset_Y))

        self.ui.temp_DeepComponents = {}
        self.ui.getDeepComponents_FromCurrentGlyph()
        self.updateViews()

