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
from vanilla.dialogs import askYesNo, getFile, getFolder, message

from mojo.roboFont import *
from mojo.events import addObserver, removeObserver
from mojo.UI import UpdateCurrentGlyphView

import os, json, copy
from AppKit import NSColor
import Helpers

from Helpers import normalizeUnicode, makepath, reformatNSDictionaryM, readCurrentProject, SmartTextBox

from imp import reload
reload(Helpers)
import Global
reload(Global)
from drawers.ProjectCanvas import ProjectCanvas
from drawers.ReferenceViewerDrawer import ReferenceViewerDraw
from drawers.DesignFrameDrawer import DesignFrameDrawer

from sheets.projectEditor.projectEditorDesignFrame import DesignFrame
from sheets.projectEditor.projectEditorReferenceViewer import ReferenceViewer

class ProjectEditor():

    def __init__(self, interface):

        self.projectPath = None
        self.projectName = "Untitled"
        self.folderPath = None
        self.selectedCharactersSets = []
        self.masterslist = []
        self.existingMastersPaths = []
        self.mastersPaths = []
        self.EM_Dimension_X = int()
        self.EM_Dimension_Y = int() 
        self.characterFace = int()
        self.overshootOutsideValue = int()
        self.overshootInsideValue = int()
        self.horizontalLine = int()
        self.verticalLine = int()
        self.customsFrames = []
        self.referenceViewerSettings = []
        self.referenceViewerList = []
        self.calendar = []
        self.glyphCompositionData = []

        Global.fontsList.reload()

        self.ui = interface
        self.w = Sheet((600,550), self.ui.w)

        UpdateCurrentGlyphView()

        self.w.loadProject_button = Button((10, 10, 150, 20), 
                'Load a project', 
                callback = self._loadProject_button_callback)

        self.w.projectName_title = TextBox((200, 12, 95, 20), 
                'Project Name:',
                alignment = 'right')
        self.w.projectName_editText = EditText((305, 11, -10, 20), 
                self.projectName, 
                callback = self._projectName_editText_callback)

        self.charactersSets_Dict, self.characterSet_list = Global.CharactersSets.get()

        checkBox = CheckBoxListCell()
        self.w.characterSet_title = TextBox((10, 50, 285, 15), 
                "Characters Sets", 
                sizeStyle = "small")
        self.w.characterSet_list = List((10, 70, 285, 100), 
                self.characterSet_list, 
                columnDescriptions = [{"title": "Get", "width":23, "cell": checkBox}, 
                                    {"title": "CharactersSets", "width":210}, 
                                    {"title": "Glyphs", "width":60}],
                editCallback = self._characterSet_list_editCallback,
                drawFocusRing = False)

        self.w.loadGlyphsCompositionData_button = Button((10,175,285,20),
                "Load Glyph Composition Data",
                sizeStyle="small",
                callback = self._loadGlyphsCompositionData_button_callback)

        self.w.masters_title = TextBox((305, 50, -10, 15), 
                "Masters", 
                sizeStyle = "small")
        self.w.masters_list = List((305, 70, -10, 100), 
                [],
                columnDescriptions = [{"title": "FamilyName"}, {"title": "StyleName"}],
                editCallback = self._master_list_editCallback,
                drawFocusRing = False)
        self.w.importMasters_button = Button((305, 175, 95, 20), 
                "Import",
                sizeStyle = "small",
                callback = self._importMasters_button_callback)
        self.w.createMasters_button = Button((400, 175, 95, 20), 
                "Create",
                sizeStyle = "small",
                callback = self._createMasters_button_callback)
        self.w.removeMasters_button = Button((495, 175, 95, 20), 
                "Remove",
                sizeStyle = "small",
                callback = self._removeMasters_button_callback)

        segmentedElements = ["Design Frame", "Reference Viewer", "Calendar"]
        self.w.segmentedButton = SegmentedButton((10,210,-10,20), 
                [dict(title=e, width = 576/len(segmentedElements)) for e in segmentedElements],
                callback = self._segmentedButton_callback)

        self.glyph = CurrentGlyph()
        # Design Frame Group
        self.w.df = DesignFrame((0,230,-0,-30), self.ui, self)
        # Reference Viewer Group
        self.w.rv = ReferenceViewer((0,230,-0,-30), self.ui, self)
        # Calendar Group
        self.w.c = Group((0,230,-0,-30))

        self.w.df.show(0)
        self.w.rv.show(0)
        self.w.c.show(0)

        self.w.close_button = Button((10, -30, 150, -10), 
                'Close', 
                callback = self._close_button_callback)
        self.w.exportProject_button = Button((170, -30, -10, -10), 
                'Export Project', 
                callback = self._exportProject_button_callback)

        self.observer()

        Helpers.setDarkMode(self.w, self.ui.darkMode)

        self.w.bind('close', self._windowWillClose)
        self.w.open()

    def _loadProject_button_callback(self, sender):
        getFile(messageText=u"Load a project",
                allowsMultipleSelection=True,
                fileTypes=["roboCJKproject", "json"],
                parentWindow=self.w,
                resultCallback=self._importProject_callback)

    def _importProject_callback(self, path):
        # self.folderPath = folderPath[0]
        path = path[0]
        with open(path, "r") as file:
            project = json.load(file)
            readCurrentProject(self, project)
            self.existingMastersPaths = self.mastersPaths
            self._setUI()

    def _setUI(self):
        self.w.projectName_editText.set(self.projectName)
        for e in self.characterSet_list:
            if e["CharactersSets"] in self.selectedCharactersSets:
                e["Get"] = 1
        self.w.characterSet_list.set(self.characterSet_list)
        self.w.masters_list.set(self.masterslist)
        self.w.df.EM_DimensionX_editText.set(self.EM_Dimension_X)
        self.w.df.EM_DimensionY_editText.set(self.EM_Dimension_Y)
        self.w.df.characterFace_editText.set(self.characterFace)
        self.w.df.overshootOutside_editText.set(self.overshootOutsideValue)
        self.w.df.overshootInside_editText.set(self.overshootInsideValue)
        self.w.df.horizontalLine_slider.set(self.horizontalLine)
        self.w.df.verticalLine_slider.set(self.verticalLine)
        self.w.df.customsFrames_list.set(self.customsFrames)
        self.w.rv.reference_list.set(self.referenceViewerList)

    def _characterSet_list_editCallback(self, sender):
        # Edit selected characters sets
        self.selectedCharactersSets = [elem["CharactersSets"] for elem in sender.get() if elem["Get"]]

    def _loadGlyphsCompositionData_button_callback(self, sender):
        getFile(messageText=u"Load Glyph Composition Data",
                allowsMultipleSelection=False,
                fileTypes=["json"],
                parentWindow=self.w,
                resultCallback=self._loadGlyphsCompositionData_callback)
    def _loadGlyphsCompositionData_callback(self, path):
        path = path[0]
        with open(path, "r") as file:
            self.glyphCompositionData = json.load(file)
        
    def _projectName_editText_callback(self, sender):
        # Edit project Name
        self.projectName = sender.get()

    def _master_list_editCallback(self, sender):
        if not sender.getSelection(): return
        # Edit masters List
        self.masterslist = sender.get()

    def _importMasters_button_callback(self, sender):
        # Import UFO(s) file
        getFile(messageText=u"Add new UFO",
                allowsMultipleSelection=True,
                fileTypes=["ufo"],
                parentWindow=self.w,
                resultCallback=self._importMasters_callback)

    def _importMasters_callback(self, paths):
        # Open the UFO(s) and build the masters list
        self.existingMastersPaths.extend(paths)
        for path in paths:
            # Get familyName and styleName from file name
            familyName, styleName = path.split("/")[-1][:-4].split("-")
            # Add item to the master list
            if {"FamilyName": familyName, "StyleName": styleName} not in self.masterslist:
                self.masterslist.append({"FamilyName": familyName, "StyleName": styleName}) 
            # Add the list to UI 
            self.w.masters_list.set(self.masterslist)

    def _createMasters_button_callback(self, sender):
        # Add item to the master list
        self.masterslist.append({"FamilyName": self.projectName, "StyleName": "Regular"}) 
        # Add the list to UI 
        self.w.masters_list.set(self.masterslist)

    def _removeMasters_button_callback(self, sender):
        # Get the masters list selection
        sel = self.w.masters_list.getSelection()
        if not sel: return
        # Delete the selection from the masters list
        self.masterslist = [e for i, e in enumerate(self.masterslist) if i not in sel]
        self.w.masters_list.set(self.masterslist)

    def _segmentedButton_callback(self, sender):
        sel = sender.get()
        if not sel:
            self.w.df.show(1)
            self.w.rv.show(0)
            self.w.c.show(0)
        elif sel == 1:
            self.w.df.show(0)
            self.w.rv.show(1)
            self.w.c.show(0)
        else:
            self.w.df.show(0)
            self.w.rv.show(0)
            self.w.c.show(1)
            message("Work in Progress...")

    def _close_button_callback(self, sender):
        # Close the project editor window
        self.w.close()

    def _exportProject_button_callback(self, sender):
        getFolder(messageText=u"Select the project Repository/Folder",
                allowsMultipleSelection=False,
                parentWindow=self.w,
                resultCallback=self._finalizeExport_callback)

    def _finalizeExport_callback(self, folderpath):
        # Get the glyphOrder with the selected characters sets
        glyphOrder = []
        for charset in self.selectedCharactersSets:
            glyphOrder.extend(["uni"+normalizeUnicode(hex(ord(c))[2:].upper()) for c in self.charactersSets_Dict[charset]])

        for master in self.masterslist:
            # Get the master info
            familyName = master["FamilyName"]
            styleName = master["StyleName"]
            # Get the master path
            masterPath =  "/Design/%s-%s.ufo"%(familyName, styleName)

            fullPath = folderpath[0] + masterPath

            try:
                # Open the ufo file if the path already exist
                f = OpenFont(fullPath, showUI = False)
            except:
                # Create the path if it do not already exist
                makepath(fullPath)
                # Create new font
                f = NewFont(familyName = familyName, 
                            styleName = styleName, 
                            showUI = False)
            # Set the glyphOrder to the font, save it and close it
            f.lib['public.glyphOrder'] = glyphOrder

            f.save(fullPath)
            f.close()

            if masterPath not in self.mastersPaths:
                self.mastersPaths.append(masterPath)
        # Get the project path
        self.projectPath = "/%s.roboCJKproject"%self.projectName
        # Create the project path
        makepath(folderpath[0] + self.projectPath)

        self.EM_Dimension = (self.EM_Dimension_X, self.EM_Dimension_Y)

        # Collect all the datas to create the project tree
        self.projectDescription = {
            "Path" : self.projectPath,
            "Name" : self.projectName
            }

        self.designFrameSettings = {
            "EM_Dimension" : self.EM_Dimension,
            "CharacterFace" : self.characterFace,
            "Overshoot" : {
                "Outside" : self.overshootOutsideValue,
                "Inside" : self.overshootInsideValue
                },
            "HorizontalLine" : self.horizontalLine,
            "VerticalLine" : self.verticalLine,
            "CustomsFrames" : reformatNSDictionaryM(self.customsFrames),
            }

        self.project = {
            "Project" : self.projectDescription,
            "CharactersSets" : self.selectedCharactersSets,
            "MastersPaths" : self.mastersPaths,
            "DesignFrame" : self.designFrameSettings,
            "ReferenceViewer" : self.referenceViewerSettings,
            "Calendar" : self.calendar,
            "glyphCompositionData": self.glyphCompositionData,
            }

        # Write the project file
        with open(folderpath[0] + self.projectPath, "w") as file:
            file.write(json.dumps(self.project))

        self.w.close()

    def currentGlyphChanged(self, info):
        if info["glyph"] == self.glyph: return
        self.glyph = info["glyph"]
        self.w.df.canvas.update()

    def observer(self, remove = False):
        if not remove:
            addObserver(self, "currentGlyphChanged", "currentGlyphChanged")
            return
        removeObserver(self, "currentGlyphChanged")

    def _windowWillClose(self, sender):
        self.observer(remove = True)