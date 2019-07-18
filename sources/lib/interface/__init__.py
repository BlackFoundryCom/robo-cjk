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
from mojo.events import addObserver, removeObserver, installTool, uninstallTool, getActiveEventTool
from mojo.roboFont import *

from AppKit import *

import os, json, Helpers, Global

from sheets.preferences import Preferences
from sheets.projectEditor import ProjectEditor

import offTools.PowerRuler as PowerRuler
import offTools.BalanceHandles as BalanceHandles
import offTools.OpenSelectedComponent as OpenSelectedComponent
from offTools.smartSelector import SmartSelector

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

from Helpers import readCurrentProject, normalizeUnicode, SmartTextBox, deepolation

from testInstall import testInstall



cwd = os.getcwd()
rdir = os.path.abspath(os.path.join(cwd, os.pardir))

ProjectEditorPDF = os.path.join(rdir, "resources/ProjectEditor.pdf")
PreferencesPDF = os.path.join(rdir, "resources/Preferences.pdf")
TextCenterPDF = os.path.join(rdir, "resources/TextCenter.pdf")
MastersOverviewPDF = os.path.join(rdir, "resources/MastersOverview.pdf")
SavePDF = os.path.join(rdir, "resources/Save.pdf")
TestInstallPDF = os.path.join(rdir, "resources/TestInstall.pdf")


"""
Deep component data structure
 _________________________________
|                                 |                                          
| Deep Components StorageFont lib | --> "deepComponentsGlyph" (dict) --> Deep componentName --> ID --> LayersInfos
|_________________________________|

 __________________________________
|                                  |                                          
| Deep Components StorageGlyph lib | --> "deepComponentsLayer" (list) --> layersName
|__________________________________|

 __________________
|                  |                                          
| Master Glyph lib | --> "deepComponentsGlyph" (dict) --> Deep componentName --> (ID , offsets)
|__________________|

"""

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
    key2Glyph = {}

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
        self.temp_DeepCompo_slidersValuesList = []
        self.temp_DeepComponents = {}

        self.activeMaster = True
        self.deepCompoWillDrag = False

        self.currentGlyph_DeepComponents = {
                                            'CurrentDeepComponents':{}, 
                                            'Existing':{}, 
                                            'NewDeepComponents':{},
                                            }
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
                'itemIdentifier': "testInstall",
                'label': 'Test Install',
                'callback': self._testInstall_callback,
                'imagePath': TestInstallPDF
            },
            {
                'itemIdentifier': NSToolbarFlexibleSpaceItemIdentifier,
            },
            {
                'itemIdentifier': "textCenter",
                'label': 'Text Center',
                'callback': self._textCenter_callback,
                'imagePath': TextCenterPDF
            },
            {
                'itemIdentifier': "mastersOverview",
                'label': 'Masters Overview',
                'callback': self._textCenter_callback,
                'imagePath': MastersOverviewPDF
            },
            {
                'itemIdentifier': NSToolbarFlexibleSpaceItemIdentifier,
            },
            {
                'itemIdentifier': "projectEditor",
                'label': 'Projects Editor',
                'callback': self._projectsSettings_callback,
                'imagePath': ProjectEditorPDF
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

        ####### FONT GROUP #######
        self.w.fontsGroup = Fonts((10,70,215,170), self)

        ###### ACCORDION VIEW ######
        self.accordionViewDescriptions = [
                       dict(label="Reference Viewer", view=self.referenceViewer, size=55, collapsed=True, canResize=0),
                       dict(label="Design Frame", view=self.designFrame, size=173, collapsed=False, canResize=0),
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

    def _textCenter_callback(self, sender):
        message("Work in Progress...")    

    def _testInstall_callback(self, sender):
        testInstall(self)

    def _main_segmentedButton_callback(self, sender):
        sel = sender.get()
        self.activeMaster = abs(sel-1)
        self.w.activeMasterGroup.show(abs(sel-1))
        self.w.deepComponentsEditorGroup.show(sel)

        self.w.fontsGroup.getMiniFont.show(self.activeMaster)

        if not sel:
            glyphset_ListSel = self.w.activeMasterGroup.glyphSet.glyphset_List.getSelection()
        else:
            glyphset_ListSel = self.w.deepComponentsEditorGroup.GlyphLayers.glyphset_List.getSelection()

        if glyphset_ListSel:
            name = self.glyphset[glyphset_ListSel[0]]
            self.glyph = self.font[name]
            self.currentGlyph_DeepComponents = {
                                            'CurrentDeepComponents':{}, 
                                            'Existing':{}, 
                                            'NewDeepComponents':{},
                                            }
            self.getDeepComponents_FromCurrentGlyph()
        else:
            self.glyph = None
        #     glyphset_ListSel = self.w.deepComponentsEditorGroup.GlyphLayers.glyphset_List.getSelection()

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
            addObserver(self, "keyDown", "keyDown")
            return
        removeObserver(self, "currentGlyphChanged")
        removeObserver(self, "draw")
        removeObserver(self, "drawPreview")
        removeObserver(self, "drawInactive")
        removeObserver(self, "mouseDown")
        removeObserver(self, "mouseUp")
        removeObserver(self, "keyDown")

    def mouseDown(self, info):
        self.deepCompoWillDrag = False

        x, y = info['point']
        clickDidInside = False

        for deepComp_Name, desc in self.currentGlyph_DeepComponents['NewDeepComponents'].items():
            if "Glyph" in desc:
                deepComp_glyph = desc['Glyph']

                if deepComp_glyph.pointInside((x, y)):
                    addObserver(self, "mouseDragged", "mouseDragged")
                    self.current_DeepComponent_selection = deepComp_glyph
                    clickDidInside = True

        if not clickDidInside:
            for name in self.currentGlyph_DeepComponents['Existing']:
                for desc in self.currentGlyph_DeepComponents['Existing'][name]:
                    deepComp_glyph = desc['Glyph']

                    if deepComp_glyph.pointInside((x, y)):
                        addObserver(self, "mouseDragged", "mouseDragged")
                        self.current_DeepComponent_selection = deepComp_glyph
                        clickDidInside = True
            
        if not clickDidInside:
            for deepComp_Name, desc in self.currentGlyph_DeepComponents['CurrentDeepComponents'].items():
                deepComp_glyph = desc['Glyph']

                if deepComp_glyph and deepComp_glyph.pointInside((x, y)):
                    addObserver(self, "mouseDragged", "mouseDragged")
                    self.current_DeepComponent_selection = deepComp_glyph
                    clickDidInside = True

        if not clickDidInside:
            self.current_DeepComponent_selection = None

        self.updateViews()

    def updateViews(self):
        self.w.activeMasterGroup.glyphSet.canvas.update()
        UpdateCurrentGlyphView()

    def mouseDragged(self, info):
        self.deepCompoWillDrag = True
        self.deepCompo_DeltaX = int(info['delta'].x)
        self.deepCompo_DeltaY = int(info['delta'].y)
        self.updateViews()

    def mouseUp(self, info):
        self.dragDeepComponent()

    def keyDown(self, info):
        """
            126
        123     124
            125
        """
        modifiers = getActiveEventTool().getModifiers()

        shift = modifiers['shiftDown']
        command = modifiers['commandDown']

        key = info['event'].keyCode()

        self.deepCompoWillDrag = True

        move = lambda x: int(str(x) + "".zfill(sum([shift, shift*command])))

        if key == 123:
            self.deepCompo_DeltaX = move(-1)

        elif key == 124:
            self.deepCompo_DeltaX = move(1)
        
        elif key == 125:
            self.deepCompo_DeltaY = move(-1)
            
        elif key == 126:
            self.deepCompo_DeltaY = move(1)
            
        self.dragDeepComponent()

    def dragDeepComponent(self):
        if self.deepCompoWillDrag and "deepComponentsGlyph" in self.glyph.lib:

            for deepComp_Name, desc in self.currentGlyph_DeepComponents['CurrentDeepComponents'].items():
                if not 'Glyph' in desc:continue
                if self.current_DeepComponent_selection == desc['Glyph']:
                    ID = desc['ID']
                    offset_x, offset_Y = desc['Offsets']

                    self.glyph.lib["deepComponentsGlyph"][deepComp_Name] = [ID, [offset_x+self.deepCompo_DeltaX, offset_Y+self.deepCompo_DeltaY]]
                    desc['Offsets'] = [offset_x+self.deepCompo_DeltaX, offset_Y+self.deepCompo_DeltaY]
                    desc['Glyph'].moveBy((self.deepCompo_DeltaX, self.deepCompo_DeltaY))

            for deepComp_Name, desc in self.currentGlyph_DeepComponents['NewDeepComponents'].items():
                if not 'Glyph' in desc:continue
                if self.current_DeepComponent_selection == desc['Glyph']:
                    offset_X, offset_Y = desc['Offsets']
                    desc['Offsets'] = [offset_X+self.deepCompo_DeltaX, offset_Y+self.deepCompo_DeltaY]
                    desc['Glyph'].moveBy((self.deepCompo_DeltaX, self.deepCompo_DeltaY))

            for name in self.currentGlyph_DeepComponents['Existing']:
                for desc in self.currentGlyph_DeepComponents['Existing'][name]:
                    if not 'Glyph' in desc:continue
                    if self.current_DeepComponent_selection == desc['Glyph']:
                        offset_X, offset_Y = desc['Offsets']
                        desc['Offsets'] = [offset_X+self.deepCompo_DeltaX, offset_Y+self.deepCompo_DeltaY]
                        desc['Glyph'].moveBy((self.deepCompo_DeltaX, self.deepCompo_DeltaY))

        self.deepCompo_DeltaX, self.deepCompo_DeltaY = 0, 0
        self.updateViews()
        self.glyph.update()
        removeObserver(self, "mouseDragged")
        self.deepCompoWillDrag = False

    def currentGlyphChanged(self, info):
        if self.glyph is None:
            sel = self.w.activeMasterGroup.glyphSet.glyphset_List.getSelection()
            if sel:
                name = self.glyphset[sel[0]]
                self.glyph = self.font[name]
            
        elif info['glyph'] and self.glyph.name != info['glyph'].name:
            self.glyph = info['glyph']
            self.currentGlyph_DeepComponents = {
                                            'CurrentDeepComponents':{}, 
                                            'Existing':{}, 
                                            'NewDeepComponents':{},
                                            }
        # self.glyph = info['glyph']
        
        self.current_DeepComponent_selection = None 
        self.getDeepComponents_FromCurrentGlyph()
        self.updateViews()

    def getDeepComponents_FromCurrentGlyph(self):
        
        
        if "deepComponentsGlyph" in self.glyph.lib:

            storageFont = self.font2Storage[self.font]

            for deepComp_Name, value in self.glyph.lib["deepComponentsGlyph"].items():

                ID = value[0]
                offset_x, offset_Y = value[1]

                layersInfo = storageFont.lib["deepComponentsGlyph"][deepComp_Name][ID]

                newGlyph = deepolation(RGlyph(), storageFont[deepComp_Name].getLayer("foreground"), layersInfo)
                if newGlyph:
                    newGlyph.moveBy((offset_x, offset_Y))

                self.currentGlyph_DeepComponents['CurrentDeepComponents'][deepComp_Name] = {"ID" : ID, "Offsets":[offset_x, offset_Y], "Glyph":newGlyph}

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
        self.updateViews()

    def _setUI(self):
        # FONT GROUP
        self.w.fontsGroup.fonts_list.set(self.fontList)

    def getCompositionGlyph(self):
        self.compositionGlyph = []
        if self.glyph is not None and self.glyphCompositionData and self.glyph.unicode:
            uni = normalizeUnicode(hex(self.glyph.unicode)[2:].upper())
            if uni in self.glyphCompositionData:
                self.compositionGlyph = [dict(Char = chr(int(name.split('_')[0],16)), Name = name) for name in self.glyphCompositionData[uni]]

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

    ##### CLOSE #####
    def windowWillClose(self, sender):
        self.observer(remove = True)
        uninstallTool(self.smartSelector)
        self.updateViews()

    def windowDidResize(self, sender):
        _, _, self.windowWidth, self.windowHeight = sender.getPosSize()