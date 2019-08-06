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

class Masters(Group):

    def __init__(self, posSize, interface, sheet):
        super(Masters, self).__init__(posSize)
        self.ui = interface
        self.s = sheet

        y = 0
        self.masters_list = List((10, y, -10, 150), 
                [],
                columnDescriptions = [{"title": "FamilyName"}, {"title": "StyleName"}],
                editCallback = self._master_list_editCallback,
                drawFocusRing = False)
        y+=155
        self.importMasters_button = Button((10, y, 190, 20), 
                "Import",
                sizeStyle = "small",
                callback = self._importMasters_button_callback)
        self.createMasters_button = Button((206, y, 190, 20), 
                "Create",
                sizeStyle = "small",
                callback = self._createMasters_button_callback)
        self.removeMasters_button = Button((402, y, 190, 20), 
                "Remove",
                sizeStyle = "small",
                callback = self._removeMasters_button_callback)

        # fontsInfos = [
        # "info.versionMajor",
        # "info.versionMinor",
        # "info.year",
        # "info.copyright",
        # "info.trademark",
        # "info.licence",
        # "info.designer",
        # "info.designerURL",
        # "info.openTypeOS2VendorID",
        # "info.unitsPerEm",
        # "info.descender",
        # "info.xHeight",
        # "info.capHeight",
        # "info.ascender",
        # "info.italicAngle",
        # "info.openTypeHheaAscender",
        # "info.openTypeHheaDescender",
        # "info.openTypeHheaLineGap",
        # "info.openTypeHheaCaretSlopeRise",
        # "info.openTypeHheaCaretSlopeRun",
        # "info.openTypeHheaCaretOffset",
        # "openTypeOS2TypoAscender",
        # "openTypeOS2TypoDescender",
        # "openTypeOS2TypoLineGap",
        # "openTypeOS2WinAscent",
        # "openTypeOS2WinDescent",
        # ]

        # x, y = 10, 150
        # for index, info in enumerate(fontsInfos):

        # 	infoName = info.split(".")[-1]

        # 	textBox = TextBox((x, y, 150, 20), infoName, sizeStyle = "small")
        # 	editText = EditText((x+150, y, 200, 20), sizeStyle = "small")

        # 	setattr(self, "%s_TextBox"%infoName, textBox)
        # 	setattr(self, "%s_EditText"%infoName, editText)

        # 	if index != 0 and not index%14:
        # 		y = 150
        # 		x += 350
        # 	else:
        # 		y += 20


    def _master_list_editCallback(self, sender):
        if not sender.getSelection(): return
        # Edit masters List
        self.s.masterslist = sender.get()

    def _importMasters_button_callback(self, sender):
        # Import UFO(s) file
        getFile(messageText=u"Add new UFO",
                allowsMultipleSelection=True,
                fileTypes=["ufo"],
                parentWindow=self.s.w,
                resultCallback=self._importMasters_callback)

    def _importMasters_callback(self, paths):
        # Open the UFO(s) and build the masters list
        self.s.existingMastersPaths.extend(paths)
        for path in paths:
            # Get familyName and styleName from file name
            familyName, styleName = path.split("/")[-1][:-4].split("-")
            # Add item to the master list
            if {"FamilyName": familyName, "StyleName": styleName} not in self.s.masterslist:
                self.s.masterslist.append({"FamilyName": familyName, "StyleName": styleName}) 
            # Add the list to UI 
            self.masters_list.set(self.s.masterslist)

    def _createMasters_button_callback(self, sender):
        # Add item to the master list
        self.s.masterslist.append({"FamilyName": self.s.projectName, "StyleName": "Regular"}) 
        # Add the list to UI 
        self.masters_list.set(self.s.masterslist)

    def _removeMasters_button_callback(self, sender):
        # Get the masters list selection
        sel = self.masters_list.getSelection()
        if not sel: return
        # Delete the selection from the masters list
        self.s.masterslist = [e for i, e in enumerate(self.s.masterslist) if i not in sel]
        self.masters_list.set(self.masterslist)




