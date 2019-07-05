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
from vanilla.dialogs import getFile, message
from mojo.UI import AccordionView, UpdateCurrentGlyphView
from mojo.events import addObserver, removeObserver

from mojo.roboFont import *
from AppKit import *

from imp import reload
import os, json, Helpers
reload(Helpers)
from Helpers import readCurrentProject, normalizeUnicode, SmartTextBox

from sheets.preferences import Preferences
from sheets.projectEditor import ProjectEditor
import offTools.PowerRuler as PowerRuler
reload(PowerRuler)
import offTools.BalanceHandles as BalanceHandles
reload(BalanceHandles)
import offTools.OpenSelectedComponent as OpenSelectedComponent
reload(OpenSelectedComponent)
from interface.SmartComponents import SmartComponents
from interface.ReferenceViewer import ReferenceViewer
from interface.Fonts import Fonts
from interface.DesignFrame import DesignFrame
from interface.MiniFonts import MiniFonts
from interface.Selection2Component import Selection2Component
from interface.FlatComponent import FlatComponent
import Global
reload(Global)

cwd = os.getcwd()
rdir = os.path.abspath(os.path.join(cwd, os.pardir))

ProjectEditorPDF = os.path.join(rdir, "resources/ProjectEditor.pdf")
PreferencesPDF = os.path.join(rdir, "resources/Preferences.pdf")
SpaceCenterPDF = os.path.join(rdir, "resources/SpaceCenter.pdf")

class RoboCJK():
    
    projects = {}
    projectPath = None
    projectName = "Untitled"
    selectedCharactersSets = []
    masterslist = []
    existingMastersPaths = []
    mastersPaths = []
    EM_Dimension_X = int()
    EM_Dimension_Y = int() 
    characterFace = int()
    overshootOutsideValue = int()
    overshootInsideValue = int()
    horizontalLine = int()
    verticalLine = int()
    customsFrames = []
    referenceViewerSettings = []
    calendar = []
    glyphCompositionData = []

    def __init__(self):
        self.w = Window((300,506), "Robo CJK", minSize = (300,300), maxSize = (300,2000))

        self.font = CurrentFont()
        self.glyph = CurrentGlyph()

        toolbarItems = [
            {
                'itemIdentifier': "projectEditor",
                'label': 'Projects Editor',
                'callback': self._projectsSettings_callback,
                'imagePath': ProjectEditorPDF
            },
            {
                'itemIdentifier': "spaceCenter",
                'label': 'Space Center',
                'callback': self._spaceCenter_callback,
                'imagePath': SpaceCenterPDF
            },
            {
                'itemIdentifier': NSToolbarFlexibleSpaceItemIdentifier,
            },
            {
                'itemIdentifier': "preference",
                'label': 'Preference',
                'callback': self._preference_callback,
                'imagePath': PreferencesPDF,
            },
        ]
        self.w.addToolbar("DesignSpaceToolbar", toolbarItems)

        self.project_popUpButton_list = ["Load a project..."]
        self.w.projects_popUpButton = PopUpButton((10,10,-10,20),
                self.project_popUpButton_list, 
                callback = self._projects_popUpButton_callback)

        self.getSuggestComponent()

        ####### FONT GROUP #######
        self.fontsGroup = Fonts((0,0,-0,-0), self)

        ####### MINIFONT GROUP #######
        self.minifonts = MiniFonts((0,0,-0,-0), self)

        ####### REFERENCE VIEWER #######
        self.referenceViewer = ReferenceViewer((0,0,-0,-0), self)

        ###### DESIGN FRAMES ######
        self.designFrame = DesignFrame((0,0,-0,-0), self)

        ###### SELECTION TO COMPONENT ######
        self.selection2component = Selection2Component((0,0,-0,-0), self)

        ###### IMPORT COMPONENT ######
        self.flatComponent = FlatComponent((0,0,-0,-0), self)

        ###### SMART COMPONENT ######
        self.smartComponent = SmartComponents((0,0,-0,-0), self)

        ###### ACCORDION VIEW ######
        self.accordionViewDescriptions = [
                       dict(label="Fonts", view=self.fontsGroup, size=100, collapsed=False, canResize=1),
                       dict(label="Mini Fonts", view=self.minifonts, size=120, collapsed=True, canResize=1),
                       dict(label="Smart Components", view=self.smartComponent, size=260, collapsed=False, canResize=1),
                       dict(label="Flat Components", view=self.flatComponent, size=125, collapsed=True, canResize=1),
                       dict(label="Selection to Components", view=self.selection2component, size=100, collapsed=True, canResize=1),
                       dict(label="Reference Viewer", view=self.referenceViewer, size=30, collapsed=True, canResize=0),
                       dict(label="Design Frame", view=self.designFrame, size=113, collapsed=True, canResize=0),
                       ]

        self.w.accordionView = AccordionView((0, 40, -0, -20), self.accordionViewDescriptions,
            backgroundColor=NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 1, 1))
        
        ###### DARK MODE ######
        self.darkMode = 1
        Helpers.setDarkMode(self.w, self.darkMode)

        self.w.darkMode_checkBox = CheckBox((10,-20,-10,-0),
            "Dark Mode", 
            sizeStyle = "small",
            value = self.darkMode,
            callback = self._darkMode_checkBox_checkBox)

        ###### OFF TOOLS ######
        PowerRuler.Ruler(self)
        BalanceHandles.BalanceHandles(self)
        OpenSelectedComponent.OpenSelectedComponent(self)

        ###### OBSERVER ######
        self.observer()
        self.w.bind('close', self.windowWillClose)

        ###### LAUNCH WINDOW ######        
        self.w.open()

    def _darkMode_checkBox_checkBox(self, sender):
        self.darkMode = sender.get()
        Helpers.setDarkMode(self.w, self.darkMode)

    def _projectsSettings_callback(self, sender):
        ProjectEditor(self)

    def _preference_callback(self, sender):
        message("Work in Progress...")
        Preferences(self)

    def _spaceCenter_callback(self, sender):
        message("Work in Progress...")

    def observer(self, remove = False):
        if not remove:
            addObserver(self, "currentGlyphChanged", "currentGlyphChanged")
            return
        removeObserver(self, "currentGlyphChanged")

    def currentGlyphChanged(self, info):
        if self.glyph != info['glyph']: 
            self.flatComponent.resetComponentInfo()
            self.flatComponent.suggestComponent_list.setSelection([])
        self.glyph = info['glyph']
        self.font = CurrentFont()
        self._setUI_with_CurrentGlyph()
        UpdateCurrentGlyphView()

    def _projects_popUpButton_callback(self, sender):
        sel = sender.get()
        if sel == len(self.project_popUpButton_list)-1:
            getFile(messageText = u"Load a project...",
                allowsMultipleSelection = False,
                fileTypes = ["roboCJKproject", "json"],
                parentWindow = self.w,
                resultCallback = self._importProject_callback)
        else:
            self.projectName = self.project_popUpButton_list[sel]
            readCurrentProject(self, self.projects[self.projectName])
            self._setUI()
        UpdateCurrentGlyphView()

    def _setUI(self):
        # FONT GROUP
        self.fontsGroup.fonts_list.set(self.fontList)
        self.setUIMiniFonts()

    def getSuggestComponent(self):
        self.suggestComponent = []
        if self.glyph is not None and self.glyphCompositionData and self.glyph.unicode:
            uni = normalizeUnicode(hex(self.glyph.unicode)[2:].upper())
            if uni in self.glyphCompositionData:
                self.suggestComponent = [v for v in self.glyphCompositionData[uni]]

    def _setUI_with_CurrentGlyph(self):
        if self.glyph is not None:
            self.getSuggestComponent()
            self.selection2component.suggestComponent_list.set(self.suggestComponent)
            self.flatComponent.suggestComponent_list.set(self.suggestComponent)

    def _importProject_callback(self, projectPath):
        # get the path of .project file
        path = projectPath[0]
        with open(path, "r") as file:
            # read the project
            project = json.load(file)
            project["Project"]["Path"] = "/".join(path.split("/")[:-1])

            readCurrentProject(self, project)
            # the project to the projects dictionary
            self.projects[self.projectName] = project
            # Set items to the UI popUpButton
            self.project_popUpButton_list.insert(0, self.projectName)
            self.w.projects_popUpButton.setItems(self.project_popUpButton_list)
            # Reset all the UI
            self._setUI()
            self._setUI_with_CurrentGlyph()

    ##### MINI FONT #####
    def setMiniFontsView(self, collapsed = False):
        for desc in self.accordionViewDescriptions:
            if desc['label'] == "Mini Fonts":
                desc["collapsed"] = collapsed
        delattr(self.w, "accordionView")
        self.w.accordionView = AccordionView((0, 40, -0, -20), self.accordionViewDescriptions,
            backgroundColor=NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 1, 1))

    def setUIMiniFonts(self):
        try:
            self.minifontList = os.listdir(self.projectPath+"/Temp") 
        except:
            self.minifontList = []
        if len(self.minifontList):
            self.setMiniFontsView(collapsed = False)
        else:
            self.setMiniFontsView(collapsed = True)
        self.minifonts.minifonts_list.set(self.minifontList)

    ##### CLOSE #####
    def windowWillClose(self, sender):
        self.observer(remove = True)
        UpdateCurrentGlyphView()