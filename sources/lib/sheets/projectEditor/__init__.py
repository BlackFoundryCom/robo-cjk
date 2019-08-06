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

from sheets.projectEditor.projectEditorMasters import Masters
from sheets.projectEditor.projectEditorDatas import Datas
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
        self.deepComponentExtremsData = []

        self.designStep = 0
        self.fontsInfos = {}

        Global.fontsList.reload()

        self.ui = interface
        self.w = Sheet((600,500), self.ui.w)

        UpdateCurrentGlyphView()

        self.w.loadProject_button = Button((10, 10, 150, 20), 
                'Load a project', 
                callback = self._loadProject_button_callback)

        self.w.projectName_title = TextBox((200, 12, 95, 20), 
                'Project Name:',
                alignment = 'right')
        self.w.projectName_editText = EditText((305, 11, -10, 20), 
                placeholder = self.projectName, 
                callback = self._projectName_editText_callback)

        self.charactersSets_Dict, self.characterSet_list = Global.CharactersSets.get()


        segmentedElements = ["Masters", "Datas", "Design Frame", "Reference Viewer", "Calendar"]
        self.w.segmentedButton = SegmentedButton((10,45,-10,20), 
                [dict(title=e, width = 576/len(segmentedElements)) for e in segmentedElements],
                callback = self._segmentedButton_callback)
        self.w.segmentedButton.set(0)

        self.glyph = CurrentGlyph()
        # Design Frame Group
        self.w.m = Masters((0,80,-0,-40), self.ui, self)
        # Design Frame Group
        self.w.d = Datas((0,80,-0,-40), self.ui, self)
        # Design Frame Group
        self.w.df = DesignFrame((0,80,-0,-40), self.ui, self)
        # Reference Viewer Group
        self.w.rv = ReferenceViewer((0,80,-0,-40), self.ui, self)
        # Calendar Group
        self.w.c = Group((0,80,-0,-30))

        self.w.m.show(1)
        self.w.d.show(0)
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
        self.w.d.stepOption_radioGroup.set(self.designStep)
        self.w.rv.reference_list.set(self.referenceViewerList)
        
    def _projectName_editText_callback(self, sender):
        # Edit project Name
        self.projectName = sender.get()

    def _segmentedButton_callback(self, sender):
        sel = sender.get()
        if not sel:
            self.w.m.show(1)
            self.w.d.show(0)
            self.w.df.show(0)
            self.w.rv.show(0)
            self.w.c.show(0)
        elif sel == 1:
            self.w.m.show(0)
            self.w.d.show(1)
            self.w.df.show(0)
            self.w.rv.show(0)
            self.w.c.show(0)
        elif sel == 2:
            self.w.m.show(0)
            self.w.d.show(0)
            self.w.df.show(1)
            self.w.rv.show(0)
            self.w.c.show(0)
        elif sel == 3:
            self.w.m.show(0)
            self.w.d.show(0)
            self.w.df.show(0)
            self.w.rv.show(1)
            self.w.c.show(0)
        else:
            self.w.m.show(0)
            self.w.d.show(0)
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

        font2storagePath = {}
        for master in self.masterslist:
            # Get the master info
            familyName = master["FamilyName"]
            styleName = master["StyleName"]
            # Get the master path
            masterPath =  "/Design/%s-%s.ufo"%(familyName, styleName)
            storagePath =  "/Storage/deepComponents%s-%s.ufo"%(familyName, styleName)

            fullPath = folderpath[0] + masterPath
            fullStoragePath = folderpath[0] + storagePath

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
            try:
                storageF = OpenFont(fullStoragePath, showUI = False)

            except:
                makepath(fullStoragePath)
                storageF = NewFont(familyName = familyName+" DeepComponents", 
                            styleName = styleName, 
                            showUI = False)
                storageF.info.ascender = 750
                storageF.info.capHeight = 750
                storageF.info.descender = -250
                storageF.info.unitsPerEm = 1000
                storageF.info.xHeight = 500

            # Set the glyphOrder to the font, save it and close it
            if glyphOrder:
                f.lib['public.glyphOrder'] = glyphOrder

            f.save(fullPath)
            f.close()

            storageF.save(fullStoragePath)
            storageF.close()

            font2storagePath[masterPath] = storagePath

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
            "UFOsPaths" : font2storagePath,
            "DesignFrame" : self.designFrameSettings,
            "ReferenceViewer" : self.referenceViewerSettings,
            "Calendar" : self.calendar,
            "glyphCompositionData": self.glyphCompositionData,
            "deepComponentExtremsData": self.deepComponentExtremsData,
            "designStep": self.designStep,
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