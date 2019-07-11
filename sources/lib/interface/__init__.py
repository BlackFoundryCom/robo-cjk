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
from mojo.events import addObserver, removeObserver, installTool, uninstallTool

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
from interface.GlyphSet import GlyphSet
from interface.GlyphData import GlyphData
from interface.DeepComponentsInstantiator import DeepComponentsInstantiator
from interface.Layers import Layers
from interface.GlyphLayers import GlyphLayers

from interface.DesignFrame import DesignFrame

from drawers.CurrentGlyphViewDrawer import CurrentGlyphViewDrawer

from offTools.smartSelector import SmartSelector

from Helpers import deepolation
# from interface.MiniFonts import MiniFonts
# from interface.Selection2Component import Selection2Component
# from interface.FlatComponent import FlatComponent
import Global
reload(Global)

cwd = os.getcwd()
rdir = os.path.abspath(os.path.join(cwd, os.pardir))

ProjectEditorPDF = os.path.join(rdir, "resources/ProjectEditor.pdf")
PreferencesPDF = os.path.join(rdir, "resources/Preferences.pdf")
SpaceCenterPDF = os.path.join(rdir, "resources/SpaceCenter.pdf")
SavePDF = os.path.join(rdir, "resources/Save.pdf")

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
        self.windowWidth, self.windowHeight = 1000,600
        self.w = Window((self.windowWidth, self.windowHeight), "Robo CJK", minSize = (300,300), maxSize = (2500,2000))

        self.font = CurrentFont()
        self.glyph = CurrentGlyph()
        self.glyphset = list()

        self.font2Storage = dict()
        self.layerList = list()
        self.glyphsSetDict = dict()

        self.newDeepComponent_active = False

        self.activeMaster = True
        self.deepCompoWillDrag = False

        self.temp_DeepCompo_slidersValuesList = []
        self.current_DeepComponents = {}
        self.deepCompo_DeltaX, self.deepCompo_DeltaY = 0, 0

        self.current_DeepComponent_selection = None 

        self.selectedCompositionGlyphName = ""
        self.selectedVariantName = ""

        toolbarItems = [
            {   
                'itemIdentifier': "saveUFO(s)",
                'label': 'Save UFO(s)',
                'callback': self._saveUFOs_callback,
                'imagePath': SavePDF
            },
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
                'itemIdentifier': "masterOverview",
                'label': 'Master Overview',
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

        segmentedElements = ["Active Master", "Deep Components Editor"]
        self.w.main_segmentedButton = SegmentedButton((10,40,-180,20), 
                [dict(title=e, width = (self.windowWidth-224)/len(segmentedElements)) for e in segmentedElements],
                callback = self._main_segmentedButton_callback,
                sizeStyle='regular')
        self.w.main_segmentedButton.set(0)

        self.getCompositionGlyph()

        self.w.activeMasterGroup = Group((10,70,-205,-20))
        self.w.deepComponentsEditorGroup = Group((10,70,-205,-20))
        self.w.deepComponentsEditorGroup.show(0)

        ####### FONT GROUP #######
        

        ####### GLYPHSET #######
        self.w.activeMasterGroup.glyphSet = GlyphSet((225,0,-0,-200), self)

        ####### GLYPHSET #######
        self.w.activeMasterGroup.glyphData = GlyphData((0,180,215,-0), self)

        self.w.activeMasterGroup.DeepComponentsInstantiator = DeepComponentsInstantiator((225,-190,-0,-0), self)

        # self.w.deepComponentsEditorGroup.fontsGroup = Fonts((0,0,215,170), self)

        self.w.deepComponentsEditorGroup.Layers = Layers((0,150,215,-0), self)

        self.w.deepComponentsEditorGroup.GlyphLayers = GlyphLayers((225,0,-0,-0), self)

        ####### MINIFONT GROUP #######
        # self.minifonts = MiniFonts((0,0,-0,-0), self)

        ####### REFERENCE VIEWER #######
        self.referenceViewer = ReferenceViewer((0,0,-0,-0), self)

        ###### DESIGN FRAMES ######
        self.designFrame = DesignFrame((0,0,-0,-0), self)

        self.w.fontsGroup = Fonts((10,70,215,170), self)
        ###### SELECTION TO COMPONENT ######
        # self.selection2component = Selection2Component((0,0,-0,-0), self)

        # ###### IMPORT COMPONENT ######
        # self.flatComponent = FlatComponent((0,0,-0,-0), self)

        # ###### SMART COMPONENT ######
        # self.smartComponent = SmartComponents((0,0,-0,-0), self)
        # segmentedElements = ["Select Deep Component", "New Deep Component"]
        # self.w.activeMasterGroup.deepCompo_segmentedButton = SegmentedButton((225,-190,-0,20), 
        #         [dict(title=e, width = (550)/len(segmentedElements)) for e in segmentedElements],
        #         callback = self._deepCompo_segmentedButton_callback,
        #         sizeStyle='regular')
        # self.w.activeMasterGroup.deepCompo_segmentedButton.set(0)

        ###### ACCORDION VIEW ######
        self.accordionViewDescriptions = [
                       # dict(label="Fonts", view=self.fontsGroup, size=100, collapsed=False, canResize=1),
                       # dict(label="Mini Fonts", view=self.minifonts, size=120, collapsed=True, canResize=1),
                       # dict(label="Smart Components", view=self.smartComponent, size=260, collapsed=False, canResize=1),
                       # dict(label="Flat Components", view=self.flatComponent, size=125, collapsed=True, canResize=1),
                       # dict(label="Selection to Components", view=self.selection2component, size=100, collapsed=True, canResize=1),
                       dict(label="Reference Viewer", view=self.referenceViewer, size=55, collapsed=True, canResize=0),
                       dict(label="Design Frame", view=self.designFrame, size=173, collapsed=True, canResize=0),
                       ]

        self.w.accordionView = AccordionView((-200, 40, -0, -20), self.accordionViewDescriptions,
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

        self.smartSelector = SmartSelector(self)
        installTool(self.smartSelector)

        ###### OBSERVER ######
        self.observer()
        self.w.bind('close', self.windowWillClose)
        self.w.bind('resize', self.windowDidResize)

        ###### LAUNCH WINDOW ######        
        self.w.open()

    def _darkMode_checkBox_checkBox(self, sender):
        self.darkMode = sender.get()
        Helpers.setDarkMode(self.w, self.darkMode)


    def _saveUFOs_callback(self, sender):
        for f1, f2 in self.font2Storage.items():
            f1.save() 
            f2.save()
            
    def _projectsSettings_callback(self, sender):
        ProjectEditor(self)

    def _preference_callback(self, sender):
        message("Work in Progress...")
        Preferences(self)

    def _spaceCenter_callback(self, sender):
        message("Work in Progress...")        

    def _main_segmentedButton_callback(self, sender):
        sel = sender.get()
        self.activeMaster = abs(sel-1)
        self.w.activeMasterGroup.show(abs(sel-1))
        self.w.deepComponentsEditorGroup.show(sel)

        self.w.fontsGroup.getMiniFont.show(self.activeMaster)

        if not sel:
            glyphset_ListSel = self.w.activeMasterGroup.glyphSet.glyphset_List.getSelection()
            if glyphset_ListSel:
                name = self.glyphset[glyphset_ListSel[0]]
                self.glyph = self.font[name]
        self.setLayer_List()

    def setLayer_List(self):

        self.layerList = []
        if self.font2Storage and self.font:
            if self.font2Storage[self.font] is not None:
                self.layerList = [layer.name for layer in self.font2Storage[self.font].layers]
        self.w.deepComponentsEditorGroup.Layers.layers_list.set(self.layerList)
        self.w.deepComponentsEditorGroup.Layers.layers_list.setSelection([])

        self.w.deepComponentsEditorGroup.GlyphLayers.set_glyphset_List()

    def observer(self, remove = False):
        if not remove:
            addObserver(self, "currentGlyphChanged", "currentGlyphChanged")
            addObserver(self, "draw", "draw")
            addObserver(self, "draw", "drawPreview")
            addObserver(self, "draw", "drawInactive")
            addObserver(self, "mouseDown", "mouseDown")
            addObserver(self, "mouseUp", "mouseUp")
            return
        removeObserver(self, "currentGlyphChanged")
        removeObserver(self, "draw")
        removeObserver(self, "drawPreview")
        removeObserver(self, "drawInactive")
        removeObserver(self, "mouseDown")
        removeObserver(self, "mouseUp")

    def mouseDown(self, info):
        x, y = info['point']
        for deepComp in self.current_DeepComponents:
            if deepComp.pointInside((x, y)):
                addObserver(self, "mouseDragged", "mouseDragged")
                self.current_DeepComponent_selection = deepComp

    def mouseDragged(self, info):
        self.deepCompoWillDrag = True
        self.deepCompo_DeltaX = int(info['delta'].x)
        self.deepCompo_DeltaY = int(info['delta'].y)
        UpdateCurrentGlyphView()

    def mouseUp(self, info):
        if self.deepCompoWillDrag:
            glyphName = self.current_DeepComponents[self.current_DeepComponent_selection][0]
            value = self.glyph.lib["deepComponentsGlyph"][glyphName]
            
            ID = value[0]
            offset_x, offset_Y = self.glyph.lib["deepComponentsGlyph"][glyphName][1]

            self.glyph.lib["deepComponentsGlyph"][glyphName] = [ID, [offset_x+self.deepCompo_DeltaX, offset_Y+self.deepCompo_DeltaY]]
            self.current_DeepComponent_selection = None

            self.deepCompo_DeltaX, self.deepCompo_DeltaY = 0, 0
            self.getDeepComponents_FromCurrentGlyph()
            
            removeObserver(self, "mouseDragged")
            UpdateCurrentGlyphView()

        self.deepCompoWillDrag = False

    def currentGlyphChanged(self, info):
        self.glyph = info['glyph']
        if self.glyph is None:
            sel = self.w.activeMasterGroup.glyphSet.glyphset_List.getSelection()
            if sel:
                name = self.glyphset[sel[0]]
                self.glyph = self.font[name]
        
        self.current_DeepComponent_selection = None 
        self.getDeepComponents_FromCurrentGlyph()
        UpdateCurrentGlyphView()

    def getDeepComponents_FromCurrentGlyph(self):
        self.current_DeepComponents = {}

        if "deepComponentsGlyph" in self.glyph.lib:
            storageFont = self.font2Storage[self.font]

            for glyphName, value in self.glyph.lib["deepComponentsGlyph"].items():
                ID = value[0]
                offset_x, offset_Y = value[1]
                layersInfo = storageFont.lib["deepComponentsGlyph"][glyphName][ID]

                newGlyph = deepolation(RGlyph(), storageFont[glyphName].getLayer("foreground"), layersInfo)
                newGlyph.moveBy((offset_x, offset_Y))

                self.current_DeepComponents[newGlyph] = (glyphName, [ID, [offset_x, offset_Y]])

    def draw(self, info):
        if self.glyph is None: return
        CurrentGlyphViewDrawer(self).draw(info)

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
        self.w.fontsGroup.fonts_list.set(self.fontList)
        # self.w.deepComponentsEditorGroup.fontsGroup.fonts_list.set(self.fontList)
        # self.setUIMiniFonts()

    def getCompositionGlyph(self):
        self.compositionGlyph = []
        if self.glyph is not None and self.glyphCompositionData and self.glyph.unicode:
            uni = normalizeUnicode(hex(self.glyph.unicode)[2:].upper())
            if uni in self.glyphCompositionData:
                self.compositionGlyph = [dict(Char = chr(int(name.split('_')[0],16)), Name = name) for name in self.glyphCompositionData[uni]]

    # def _setUI_with_CurrentGlyph(self):
    #     if self.glyph is not None:
    #         self.getCompositionGlyph()
    #         self.selection2component.suggestComponent_list.set(self.compositionGlyph)
    #         self.flatComponent.suggestComponent_list.set(self.compositionGlyph)

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
            # self._setUI_with_CurrentGlyph()
        # print(self.fonts)

    ##### MINI FONT #####
    def setMiniFontsView(self, collapsed = False):
        for desc in self.accordionViewDescriptions:
            if desc['label'] == "Mini Fonts":
                desc["collapsed"] = collapsed
        delattr(self.w, "accordionView")
        self.w.accordionView = AccordionView((-200, 40, -0, -20), self.accordionViewDescriptions,
            backgroundColor=NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 1, 1))
        Helpers.setDarkMode(self.w, self.darkMode)

    # def setUIMiniFonts(self):
    #     try:
    #         self.minifontList = os.listdir(self.projectPath+"/Temp") 
    #     except:
    #         self.minifontList = []
    #     if len(self.minifontList):
    #         self.setMiniFontsView(collapsed = False)
    #     else:
    #         self.setMiniFontsView(collapsed = True)
    #     self.minifonts.minifonts_list.set(self.minifontList)

    ##### CLOSE #####
    def windowWillClose(self, sender):
        self.observer(remove = True)
        uninstallTool(self.smartSelector)
        UpdateCurrentGlyphView()

    def windowDidResize(self, sender):
        _, _, self.windowWidth, self.windowHeight = sender.getPosSize()