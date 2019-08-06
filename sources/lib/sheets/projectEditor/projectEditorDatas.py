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
from vanilla.dialogs import getFile
import json

class Datas(Group):

    def __init__(self, posSize, interface, sheet):
        super(Datas, self).__init__(posSize)
        self.ui = interface
        self.s = sheet

        checkBox = CheckBoxListCell()

        self.characterSet_list = List((10, 0, -10, 150), 
                self.s.characterSet_list, 
                columnDescriptions = [{"title": "Get", "width":23, "cell": checkBox}, 
                                    {"title": "CharactersSets", "width":400}, 
                                    {"title": "Glyphs", "width":60}],
                editCallback = self._characterSet_list_editCallback,
                drawFocusRing = False)

        self.loadGlyphsCompositionData_textBox = TextBox((10,170,285,20), 
        		'Glyph Composition Data',
        		sizeStyle = "small")
        self.loadGlyphsCompositionData_button = Button((10,190,285,20),
                "Load...",
                sizeStyle="small",
                callback = self._loadGlyphsCompositionData_button_callback)

        self.loadDeepComponentExtremsData_textBox = TextBox((10,220,285,20),
        		"Deep Component Extrems Data",
                sizeStyle="small")
        self.loadDeepComponentExtremsData_button = Button((10,240,285,20),
                "Load...",
                sizeStyle="small",
                callback = self._loadDeepComponentExtremsData_button_callback)

        self.stepOption_textBox = TextBox((315,170,285,20), "Design Steps", sizeStyle = "small")
        self.stepOption_radioGroup = RadioGroup((320,190,285,80), 
                ["Initial Design", "Deep Components Creator", "Glyphs Development"], 
                isVertical = True,
                sizeStyle = "small",
                callback = self._stepOption_radioGroup_callback)
        self.stepOption_radioGroup.set(self.s.designStep)

    def _characterSet_list_editCallback(self, sender):
        # Edit selected characters sets
        self.s.selectedCharactersSets = [elem["CharactersSets"] for elem in sender.get() if elem["Get"]]

    def _loadGlyphsCompositionData_button_callback(self, sender):
        getFile(messageText=u"Load Glyph Composition Data",
                allowsMultipleSelection=False,
                fileTypes=["json"],
                parentWindow=self.s.w,
                resultCallback=self._loadGlyphsCompositionData_callback)

    def _loadGlyphsCompositionData_callback(self, path):
        path = path[0]
        with open(path, "r") as file:
            self.s.glyphCompositionData = json.load(file)
            self.loadGlyphsCompositionData_button.setTitle(path.split("/")[-1])

    def _loadDeepComponentExtremsData_button_callback(self, sender):
        getFile(messageText=u"Load Deep Component Extrems Data",
                allowsMultipleSelection=False,
                fileTypes=["json"],
                parentWindow=self.s.w,
                resultCallback=self._loadDeepComponentExtremsData_callback)

    def _loadDeepComponentExtremsData_callback(self, path):
        path = path[0]
        with open(path, "r") as file:
            self.s.deepComponentExtremsData = json.load(file)
            self.loadDeepComponentExtremsData_button.setTitle(path.split("/")[-1])

    def _stepOption_radioGroup_callback(self, sender):
    	self.s.designStep = sender.get()




