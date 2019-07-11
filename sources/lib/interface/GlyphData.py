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
from sheets.Select2DeepCompoSheet import Select2DeepCompoSheet

class GlyphData(Group):

    def __init__(self, posSize, interface):
        super(GlyphData, self).__init__(posSize)
        self.ui = interface

        self.glyphCompositionRules_TextBox = TextBox((0, 10, -0, 20),
            "Glyph composition rules",
            sizeStyle = "small")

        self.glyphCompositionRules_List = List((0, 30, -0, 100),
            self.ui.compositionGlyph,
            columnDescriptions = [
                                {"title": "Char", "width" : 30},
                                {"title": "Name", "width" : 175},                  
                                ],

            drawFocusRing=False, 
            selectionCallback = self._glyphCompositionRules_List_selectionCallback)

        self.selection2DeepCompo_Button = SquareButton((0, 130, -0, 30),
            "Selection to Deep Components",
            sizeStyle = "small",
            callback = self._selection2DeepCompo_Button_Callback)

        self.variants_TextBox = TextBox((0, 170, -0, 20),
            "Variants",
            sizeStyle = "small")

        self.existingName = []

        self.variants_List = List((0, 190, -0, -0),
            [],
            drawFocusRing=False, 
            selectionCallback = self._variants_List_selectionCallback)

    def _selection2DeepCompo_Button_Callback(self, sender):
        if not self.ui.selectedCompositionGlyphName:
            message("Warning, there is no selected composition glyph name")
            return
        if self.ui.glyph is None:
            message("Warning, there is no glyph")
            return
        selectedContours = [c for c in self.ui.glyph if c.selected or [p for p in c.points if p.selected]]
        if not selectedContours:
            message("Warning, there is no selectedContours")
            return
        Select2DeepCompoSheet(self.ui, self, self.ui.selectedCompositionGlyphName["Name"], selectedContours)

    def _glyphCompositionRules_List_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            self.ui.selectedCompositionGlyphName = ""
            return
        else:
            self.ui.selectedCompositionGlyphName = sender.get()[sel[0]]

        self.font = self.ui.font
        self.storageFont = self.ui.font2Storage[self.font]
        self.existingName = list(filter(lambda x: self.ui.selectedCompositionGlyphName["Name"] in x, list(self.storageFont.keys())))

        self.variants_List.set(self.existingName)
        if self.existingName:
            self.variants_List.setSelection([len(self.existingName)-1])
        else:
            self.variants_List.setSelection([])

    def _variants_List_selectionCallback(self, sender):
        sel = sender.getSelection()
        selectDeepCompoList = self.ui.w.activeMasterGroup.DeepComponentsInstantiator.selectDeepCompo.list
        selectDeepCompoButton = self.ui.w.activeMasterGroup.DeepComponentsInstantiator.deepCompo_segmentedButton
        
        if not sel :
            selectDeepCompoList.set([])
            self.ui.selectedVariantName = ""
            self.ui.w.activeMasterGroup.DeepComponentsInstantiator.setSliderList()
            self.ui.w.activeMasterGroup.DeepComponentsInstantiator.newDeepCompo.list.set([])
            return

        self.ui.selectedVariantName = sender.get()[sel[0]]
        f = self.storageFont

        if "deepComponentsGlyph" in f.lib:

            if self.ui.selectedVariantName in f.lib["deepComponentsGlyph"]:
                selectDeepCompoList.set(list(f.lib["deepComponentsGlyph"][self.ui.selectedVariantName].keys()))

            else:
                selectDeepCompoList.set([])

        if self.ui.newDeepComponent_active:
            self.ui.temp_DeepComponents[self.ui.selectedVariantName] = {}
        self.ui.w.activeMasterGroup.DeepComponentsInstantiator.setSliderList()
