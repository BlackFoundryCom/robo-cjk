"""
Copyright 2020 Black Foundry.

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
from mojo.events import addObserver, removeObserver, extractNSEvent, installTool, uninstallTool, getActiveEventTool
from imp import reload

from utils import interpolation
# reload(interpolation)

from views import roboCJKView, sheets
# reload(roboCJKView)
# reload(sheets)

from resources import characterSets, chars2deepCompo
# reload(characterSets)
# reload(chars2deepCompo)

charsets = characterSets.characterSets
CG2DC = chars2deepCompo.Chars2DC

from utils import files

from controllers import teamManager
# reload(files)

from views import movie

from utils import gitEngine as git
# reload(git)

from views import drawer
# reload(drawer)

from views import canvasGroups
# reload(canvasGroups)

from views import popover
# reload(popover)

from models import deepComponent
# reload(deepComponent)

from tools import transformationTool
# reload(transformationTool)

from views import PDFProofer
# reload(PDFProofer)

from views import accordionViews

import os
from mojo.UI import UpdateCurrentGlyphView, CurrentGlyphWindow, SetCurrentLayerByName
import mojo.drawingTools as mjdt
from mojo.roboFont import *
from mojo.extensions import getExtensionDefault, setExtensionDefault

import math
import json
import copy 
import time

# import mySQLCollabEngine

# from rcjk2mysql import BF_engine_mysql as BF_engine_mysql
# from rcjk2mysql import BF_rcjk2mysql
# from rcjk2mysql import BF_init as BF_init

import shutil

# curpath = os.path.dirname(__file__)
# print(curpath)
# curpath = mySQLCollabEngine.__path__._path[0]
# bf_log = BF_init.init_log('/Users/gaetanbaehr/Desktop/test')
import sys
# print(os.path.join(os.getcwd(), 'rcjk2mysql'))
# print('sys path', sys.path)
# bf_log = BF_init.init_log(os.path.join(os.getcwd(), 'rcjk2mysql'))
# try:
#     dict_persist_params, _  = BF_init.init_params(bf_log, None, BF_init._REMOTE, None)
# except:
#     pass

from utils import decorators
# reload(decorators)
refresh = decorators.refresh
lockedProtect = decorators.lockedProtect

from AppKit import NSSearchPathForDirectoriesInDomains
APPNAME = 'RoboFont'

import threading
import queue


blackrobocjk_glyphwindowPosition = "com.black-foundry.blackrobocjk_glyphwindowPosition"

class RoboCJKController(object):


    hiddenSavePath = os.path.join(NSSearchPathForDirectoriesInDomains(14, 1, True)[0], APPNAME, 'mySQLSave')
    files.makepath(hiddenSavePath)

    _version = 1.5

    def __init__(self):
        self.observers = False
        self.drawer = drawer.Drawer(self)
        self.transformationTool = transformationTool.TransformationTool(self)
        self.componentWindow = None
        self.characterWindow = None
        self.currentGlyph = None
        self.menuItems = []
        self.openedGlyphName = ""
        self.HistoryGlyphWindow = None
        self.CharacterGlyphViewer = None
        self.gitUserName = ''
        self.gitPassword = ''
        self.gitHostLocker = ''
        self.gitHostLockerPassword = ''
        self.privateLocker = True
        self.glyphWindowPosSize = getExtensionDefault(blackrobocjk_glyphwindowPosition, (0, 180, 1000, 600))
        self.drawOnlyInterpolation = False
        self.textCenterWindows = []
        # self.teamManager = teamManager.TeamManagerController(self)
        self.locked = False

        self.glyphView = canvasGroups.GlyphView(
            self,
            posSize = (20, -80, -20, -20), 
            delegate = self
            )

        self.roundToGrid = False
        self.transformationToolIsActiv = False
        self.importDCFromCG = None
        self.sliderValue = None
        self.sliderName = None
        self.copy = []
        self.px, self.py = 0,0

        self.mysql = True
        self.mysql_userName = ""
        self.mysql_password = ""
        # self.bf_log = bf_log

        self.glyphInspectorWindow = None

        self.updateDeepComponentQueue = queue.Queue()

    def connect2mysql(self):
        pass
        # dict_persist_params, _  = BF_init.init_params(bf_log, None, BF_init._REMOTE, None)
        # bf_log.info("will connect to mysql")
        # self.mysql = BF_engine_mysql.Rcjk2MysqlObject(dict_persist_params)
        # self.mysql.logout(self.mysql_userName, self.mysql_password)
        # self.mysql.login(self.mysql_userName, self.mysql_password)
        # bf_log.info("did connect to mysql")
        # bf_log.info(self.mysql.login(self.mysql_userName, self.mysql_password))

    def loadProject(self, folderpath, fontname):
        pass
        # bfont = BF_rcjk2mysql.read_font_from_disk(bf_log, folderpath, fontname)
        # BF_rcjk2mysql.delete_font_from_mysql(bf_log, fontname, self.mysql)
        # BF_rcjk2mysql.insert_newfont_to_mysql(bf_log, bfont, self.mysql)

    def getmySQLParams(self):
        pass
        # curpath = mySQLCollabEngine.__path__._path[0]
        # self.bf_log = BF_init.__init_log(curpath)
        # self.dict_persist_params, _  = BF_init.__init_params(self.bf_log, curpath, BF_init._REMOTE)

    def get(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        return None

    @property
    def isAtomic(self):
        return self.currentGlyph.type == 'atomicElement'

    @property
    def isDeepComponent(self):
        return self.currentGlyph.type == 'deepComponent'

    @property
    def isCharacterGlyph(self):
        return self.currentGlyph.type == 'characterGlyph'
        
    def toggleWindowController(self, add = True):
        windowController = self.roboCJKView.w.getNSWindowController()
        windowController.setShouldCloseDocument_(True)
        document = self.currentFont.shallowDocument()
        if add:
            document.addWindowController_(windowController)
            return
        document.removeWindowController_(windowController)
        
    def _launchInterface(self):
        self.roboCJKView = roboCJKView.RoboCJKView(self)

    # def connect2mysql(self):
    #     self.mysql = BF_engine_mysql.Rcjk2MysqlObject(dict_persist_params)
    #     self.mysql.login(self.mysql_userName, self.mysql_password)

    def setGitEngine(self):
        global gitEngine
        gitEngine = git.GitEngine(self.projectRoot)
        self.user = gitEngine.user()
        self.gitEngine = gitEngine

    def toggleObservers(self, forceKill=False):
        if self.observers or forceKill:
            removeObserver(self, "fontDidSave")
            removeObserver(self, "glyphAdditionContextualMenuItems")
            # removeObserver(self, "glyphWindowWillOpen")
            removeObserver(self, "glyphWindowWillClose")
            removeObserver(self, "draw")
            removeObserver(self, "drawPreview")
            removeObserver(self, "drawInactive")
            removeObserver(self, "currentGlyphChanged")
            removeObserver(self, "mouseDown")
            removeObserver(self, "mouseUp")
            removeObserver(self, "keyDown")
            removeObserver(self, "keyUp")
            removeObserver(self, "didUndo")
        else:
            addObserver(self, "fontDidSave", "fontDidSave")
            addObserver(self, "glyphAdditionContextualMenuItems", "glyphAdditionContextualMenuItems")
            # addObserver(self, "glyphWindowWillOpen", "glyphWindowWillOpen")
            addObserver(self, "glyphWindowWillClose", "glyphWindowWillClose")
            addObserver(self, "observerDraw", "draw")
            addObserver(self, "observerDrawPreview", "drawPreview")
            addObserver(self, "observerDraw", "drawInactive")
            addObserver(self, "currentGlyphChanged", "currentGlyphChanged")
            addObserver(self, "mouseDown", "mouseDown")
            addObserver(self, "mouseUp", "mouseUp")
            addObserver(self, "keyDown", "keyDown")
            addObserver(self, "keyUp", "keyUp")
            addObserver(self, "didUndo", "didUndo")
        self.observers = not self.observers

    def fontDidSave(self, info):
        if self.currentFont and CurrentFont() in [self.currentFont._RFont, self.currentFont._fullRFont]:
            if self.mysql:
                if self.currentGlyph:
                    self.currentFont.saveGlyph(self.currentGlyph)
                else:
                    self.currentFont.save()  
                    self.unlockGlyphsNonOpen()
            else:
                self.currentFont.save()
        else:
            print('no font object')

    def didUndo(self, info):
        self.updateDeepComponent(update = False)

    @refresh
    def updateDeepComponent(self, update = False):
        if not self.currentGlyph.selectedSourceAxis:
            self.currentGlyph.selectedSourceAxis = {}#{x.name:0 for x in self.currentGlyph._axes}

    def decomposeGlyphToBackupLayer(self, glyph):
        def _decompose(glyph, axis, layername):
            if layername not in self.currentFont._RFont.layers:
                self.currentFont._RFont.newLayer(layername)
            if axis:
                glyphAxis = glyph._axes.get(axis)
                ais = glyph.preview({axis:glyphAxis.maxValue})
            else:
                ais = glyph.preview()
            f = self.currentFont._RFont.getLayer(layername)
            f.newGlyph(glyph.name)
            g1 = f[glyph.name]
            g1.clear()
            for ai in ais:
                for c in ai.glyph:
                    g1.appendContour(c)
            g1.round()

        for axis in self.currentFont.fontVariations:
            axisLayerName = "backup_%s"%axis
            _decompose(glyph, axis, axisLayerName)
        masterLayerName = "backup_master"
        _decompose(glyph, '', masterLayerName)


    def _currentSourceValidated(self) -> bool:
        validated = 4
        disabled = False
        if self.currentGlyph.selectedSourceAxis:
            sourceName = self.currentGlyph.selectedSourceAxis
            source = self.currentGlyph._glyphVariations.getFromSourceName(sourceName)
            if source is None: return False
            sourceStatus = source.status
        else:
            sourceName = "default"
            sourceStatus = self.currentGlyph._status

        if sourceStatus != validated: return False
        return True


    def disabledEditingUIIfValidated(self):
        validated = self._currentSourceValidated()
        removeObserver(self, "glyphAdditionContextualMenuItems")
        addObserver(self, "glyphAdditionContextualMenuItems", "glyphAdditionContextualMenuItems")

        if not validated: 
            
            if self.currentGlyph.type != "atomicElement":
                self.glyphInspectorWindow.deepComponentAxesItem.show(True)
                self.glyphInspectorWindow.transformationItem.show(True)
                if self.currentGlyph.type == "characterGlyph":
                    self.glyphInspectorWindow.compositionRulesItem.show(True)
            self.installCustomTool(install = True, sender = "disabledEditingUIIfValidated true")
            return

        
        if self.currentGlyph.type != "atomicElement":
            self.glyphInspectorWindow.deepComponentAxesItem.show(False)
            self.glyphInspectorWindow.transformationItem.show(False)
            if self.currentGlyph.type == "characterGlyph":
                self.glyphInspectorWindow.compositionRulesItem.show(False)
        self.installCustomTool(install = False, sender = "disabledEditingUIIfValidated false")
        

    def unlockGlyphsNonOpen(self):
        glyphsList = []
        for l in [self.currentFont.client.atomic_element_list, self.currentFont.client.deep_component_list, self.currentFont.client.character_glyph_list]:
            for x in l(self.currentFont.uid, is_locked_by_current_user = True)["data"]:
                name = x["name"]
                if name != self.openedGlyphName:
                    glyphsList.append(name)
        self.currentFont.batchUnlockGlyphs(glyphsList)
        # AElist = [x["name"] for x in self.currentFont.client.atomic_element_list(self.currentFont.uid, is_locked_by_current_user = True)["data"]]
        # DClist = [x["name"] for x in self.currentFont.client.deep_component_list(self.currentFont.uid, is_locked_by_current_user = True)["data"]]
        # CGlist = [x["name"] for x in self.currentFont.client.character_glyph_list(self.currentFont.uid, is_locked_by_current_user = True)["data"]]

    def glyphWindowWillClose(self, notification):
        start = time.time()
        self.roboCJKView.setglyphState(self.currentGlyph)
        self.openedGlyphName = ""
        if self.glyphInspectorWindow is not None:
            self.glyphInspectorWindow.closeWindow()
            self.glyphInspectorWindow = None
        try:
            posSize = CurrentGlyphWindow().window().getPosSize()
            setExtensionDefault(blackrobocjk_glyphwindowPosition, posSize)
            self.glyphWindowPosSize = getExtensionDefault(blackrobocjk_glyphwindowPosition)
        except:pass
        if self.currentGlyph.type != "atomicElement":
            self.window.removeGlyphEditorSubview(self.glyphView)

        self.drawer.refGlyph = None 
        self.drawer.refGlyphPos = [0, 0]
        self.drawer.refGlyphScale = [1, 1]  

        self.currentFont.fontLib.update(self.currentFont._RFont.lib.asDict())
        self.currentFont._fullRFont.lib.update(self.currentFont._RFont.lib)

        if not self.mysql:
            self.currentFont.save()
            if self.currentGlyph is not None:
                self.currentFont.getGlyph(self.currentGlyph)
            self.currentFont.clearRFont()  
        else:
            self.currentFont.saveGlyph(self.currentGlyph)
            self.currentFont.saveFontlib()
            self.currentFont.batchUnlockGlyphs([self.currentGlyph.name])
        if self.HistoryGlyphWindow is not None:
            self.HistoryGlyphWindow.close()
            self.HistoryGlyphWindow = None
        if self.CharacterGlyphViewer is not None:
            self.CharacterGlyphViewer.disableUI()
            # self.CharacterGlyphViewer.close()
            # self.CharacterGlyphViewer = None
        stop = time.time()
        print(stop-start, "to close %s"%self.currentGlyph.name)
              

    def closeimportDCFromCG(self):
        if self.importDCFromCG is not None:
            self.importDCFromCG.close()
            self.importDCFromCG = None

    def sortDeepComponentAxesList(self, dclist):
        initial = ["_na", "_fl", "_mi"]
        final = ["_bo"]
        newList = []
        endList = []
        oldList = copy.deepcopy(dclist)
        toDel = []
        for init in initial:
            for i, axis in enumerate(oldList):
                if axis["Axis"].endswith(init):
                    newList.append(axis)
                    toDel.append(i)
        for fina in final:
            for i, axis in enumerate(oldList):
                if axis["Axis"].endswith(fina):
                    endList.append(axis)
                    toDel.append(i)
        oldList = [x for i, x in enumerate(oldList) if i not in toDel]
        keys = sorted([x["Axis"] for x in oldList])
        oldList = [y for x in keys for y in oldList if y["Axis"] == x]
        newList.extend(oldList)
        newList.extend(endList)
        return newList


    def installCustomTool(self, install = True, sender = None):
        if install:
            if self.currentGlyph.type =='atomicElement':
                uninstallTool(self.transformationTool)
            else:
                installTool(self.transformationTool)
        else:
            uninstallTool(self.transformationTool)


    @lockedProtect
    def currentGlyphChanged(self, notification):
        glyph = notification['glyph']
        if glyph is None: return
        changed = False
        if glyph.name != self.currentGlyph.name:
            changed = True
            self.closeimportDCFromCG()
        self.currentGlyph = self.currentFont[glyph.name]
        if changed:
            # self.currentGlyph.sourcesList = []
            # for axis, variation in zip(self.currentGlyph._axes, self.currentGlyph._glyphVariations):
            #     self.currentGlyph.sourcesList.append({"Axis":axis["name"], "Layer":variation["layerName"], "PreviewValue":{axis["name"]:0}, "MinValue":axis["minValue"], "MaxValue":axis["maxValue"]})
            # self.currentGlyph.sourcesList = self.sortDeepComponentAxesList(self.currentGlyph.sourcesList)
            # self.currentViewSourceList.glyphVariationAxesList.set(self.currentGlyph.sourcesList)
            self.glyphInspectorWindow.sourcesItem.setList()
            self.glyphInspectorWindow.axesItem.setList()
            self.currentViewSourceValue.set("")
        if not self._currentSourceValidated():
            self.installCustomTool(install = True, sender = "currentGlyphChanged True")
        else:
            self.installCustomTool(install = False, sender = "currentGlyphChanged False")
        # if self.currentGlyph.type =='atomicElement':
        #     uninstallTool(self.transformationTool)
        # else:
        #     if not self._currentSourceValidated():
        #         installTool(self.transformationTool)

        if self.currentGlyph.type != "atomicElement":
            self.addSubView()
        self.openGlyphInspector()
        self.updateDeepComponent()

        if self.CharacterGlyphViewer is not None:
            self.CharacterGlyphViewer.enableUI()
        self.glyphInspectorWindow.updatePreview()

    def exportDataBase(self):
        self.currentFont.exportDataBase()

    # def closeCharacterWindow(self):
    #     if self.characterWindow is not None:
    #         self.characterWindow.close()
    #         self.characterWindow = None

    # def closeComponentWindow(self):
    #     if self.componentWindow is not None:
    #         self.componentWindow.close()
    #         self.componentWindow = None

    @property 
    def currentView(self):
        if self.isAtomic:
            return self.atomicView
        elif self.isDeepComponent:
            return self.deepComponentView
        elif self.isCharacterGlyph:
            return self.characterGlyphView

    @property 
    def currentViewSourceList(self):
        return self.glyphInspectorWindow.glyphVariationAxesItem

    @property 
    def currentViewSliderList(self):
        return self.glyphInspectorWindow.deepComponentAxesItem

    @property 
    def currentViewSourceValue(self):
        if self.isAtomic:
            return self.atomicView.atomicElementsSliderValue
        elif self.isDeepComponent:
            return self.deepComponentView.sourcesSliderValue
        elif self.isCharacterGlyph:
            return self.characterGlyphView.sourcesSliderValue

    def openGlyphInspector(self):
        glyphVariationsAxes = []
        if self.glyphInspectorWindow is not None:
            return
        if self.isAtomic: # TODO
            for axis, var in zip(self.currentGlyph._axes, self.currentGlyph._glyphVariations):
                axisName = axis.name
                minValue = axis.minValue
                maxValue = axis.maxValue
                layerName = var.layerName
                glyphVariationsAxes.append({"Axis":axisName, "Layer":layerName, "PreviewValue":0, "MinValue":minValue, "MaxValue":maxValue})
            self.glyphInspectorWindow = accordionViews.AtomicElementInspector(self, glyphVariationsAxes)
        elif self.isDeepComponent or self.isCharacterGlyph:
            if self.currentGlyph._axes:
                glyphVariationsAxes = []
                for axis in self.currentGlyph._axes:
                    pos = {a.name:0 for a in self.currentGlyph._axes} # should find hos to give multiple axis
                    pos = 0
                    glyphVariationsAxes.append({"Axis":axis.name, "PreviewValue":pos, "MinValue":axis.minValue, "MaxValue":axis.maxValue})
            if self.isDeepComponent:
                self.glyphInspectorWindow = accordionViews.DeepComponentInspector(self, glyphVariationsAxes)    
            else:
                self.glyphInspectorWindow = accordionViews.CharacterGlyphInspector(self, glyphVariationsAxes)
        

    # def draw(self):
    #     mjdt.save()
    #     mjdt.fill(1, 1, 1, .7)
    #     mjdt.roundedRect(0, 0, 300, [525, 425][self.currentGlyph.type == "atomicElement"], 10)
    #     scale = .15
    #     glyphwidth = self.currentFont._RFont.lib.get('robocjk.defaultGlyphWidth', 1000)
    #     mjdt.translate((glyphwidth*scale/2), [300, 200][self.currentGlyph.type == "atomicElement"])
    #     mjdt.fill(.15)

        
    #     mjdt.scale(scale, scale)
    #     mjdt.translate(0, abs(self.currentFont._RFont.info.descender))
    #     self.drawer.drawGlyph(
    #         self.currentGlyph,
    #         scale,
    #         (0, 0, 0, 1),
    #         (0, 0, 0, 0),
    #         (0, 0, 0, 1),
    #         drawSelectedElements = False
    #         )
    #     mjdt.restore()

    def observerDraw(self, notification):
        if hasattr(self.currentGlyph, 'type'):
            self.drawer.draw(
                notification,
                onlyPreview = self.drawOnlyInterpolation
                )

    def observerDrawPreview(self, notification):
        if self.currentGlyph is None: return
        self.drawer.draw(
            notification, 
            customColor=(0, 0, 0, 1), 
            onlyPreview = self.drawOnlyInterpolation
            )

    def getRegressionPercentage(self, name):
        def getChar(dcname):
            try:
                code = dcname.split("_")[1]
                return chr(int(code, 16))
            except Exception as e:
                # print("getRegressionPercentage", e)
                return False

        glyph = self.currentFont[name]
        response = self.currentFont.mysqlGlyphData.get(name, False)
        try:
            values = []
            if response:
                for dc in response["made_of"]:
                    char = getChar(dc["name"])
                    if not char: continue
                    values.append(round((len(dc["used_by"])/len(self.currentFont.deepComponents2Chars[char]))*100))
            return (100*len(values)-sum(values))//len(values)
        except Exception as e:
            return False

    @refresh
    def mouseDown(self, point):
        if self.isAtomic:
            return
        event = extractNSEvent(point)
        modifiers = getActiveEventTool().getModifiers()
        option = modifiers['optionDown']
        command = modifiers['commandDown']
        if not all([option, command]):
            if not event["shiftDown"]:
                self.currentGlyph.selectedElement = []
            try: self.px, self.py = point['point'].x, point['point'].y
            except: return
            
            self.currentGlyph.pointIsInside((self.px, self.py), event["shiftDown"])
            self.currentViewSliderList.deepComponentAxesList.set([])
            self.currentViewSliderList.deepComponentName.set("")
            if self.currentGlyph.selectedElement: 
                self.setListWithSelectedElement()
                if point['clickCount'] == 2 and not self._currentSourceValidated():
                    popover.EditPopoverAlignTool(
                        self, 
                        point['point'], 
                        self.currentGlyph
                        )
        else:
            self.currentGlyph.setTransformationCenterToSelectedElements((point['point'].x, point['point'].y))
            addObserver(self, 'mouseDragged', 'mouseDragged')
        if not self.isAtomic:
            self.glyphInspectorWindow.deepComponentListItem.setList()
            self.glyphInspectorWindow.transformationItem.setTransformationsField()

    def mouseDragged(self, point):
        try:
            self.currentGlyph.setTransformationCenterToSelectedElements((point['point'].x, point['point'].y))
        except:
            pass

    def setListWithSelectedElement(self):
        element = self.currentViewSliderList
        if not self.currentGlyph.selectedSourceAxis:
            data = self.currentGlyph._deepComponents
        else:
            for x in self.currentGlyph._glyphVariations:
                if x.sourceName == self.currentGlyph.selectedSourceAxis:
                    data = x.deepComponents
                    break
        l = []

        if len(self.currentGlyph.selectedElement) == 1 and data:
            i = self.currentGlyph.selectedElement[0]
            dc = data[i]
            dc_name = self.currentGlyph._deepComponents[i].name
            glyph = self.currentFont.get(dc_name)
            for axis in glyph._axes:
                minValue = axis.minValue
                maxValue = axis.maxValue
                axisName = axis.name
                value = self.systemValue(dc["coord"].get(axisName, minValue), minValue, maxValue)
                l.append({'Axis':axisName, 'PreviewValue':value, 'MinValue':minValue, 'MaxValue':maxValue})
        l = self.sortDeepComponentAxesList(l)
        element.deepComponentAxesList.setSelection([])
        element.deepComponentAxesList.set(l)
        if data and hasattr(data[self.currentGlyph.selectedElement[0]], 'name'):
                element.deepComponentName.set(data[self.currentGlyph.selectedElement[0]].name)
        self.sliderValue = None

    @refresh
    def mouseUp(self, info):
        self.currentGlyph.reinterpolate = False
        removeObserver(self, 'mouseDragged')
        if self.isAtomic:
            return
        if self.transformationToolIsActiv and self.currentGlyph.selectedElement: return
        try: x, y = info['point'].x, info['point'].y
        except: return
        self.currentViewSliderList.deepComponentAxesList.set([])
        self.currentGlyph.selectionRectTouch(
            *sorted([x, self.px]), 
            *sorted([y, self.py])
            )
        if self.currentGlyph.selectedElement:
            self.setListWithSelectedElement()
        if not self.isAtomic:
            self.glyphInspectorWindow.deepComponentListItem.setList()

    
    def doUndo(self):
        def _getKeys(glyph):
            if glyph.type == "characterGlyph":
                return 'robocjk.deepComponents', 'robocjk.axes', 'robocjk.variationGlyphs'
            else:
                return 'robocjk.deepComponents', 'robocjk.axes', 'robocjk.variationGlyphs'

        if len(self.currentGlyph.stackUndo_lib) >= 1:
            if self.currentGlyph.indexStackUndo_lib > 0:
                self.currentGlyph.indexStackUndo_lib -= 1

                if self.currentGlyph.indexStackUndo_lib == len(self.currentGlyph.stackUndo_lib)-1:    
                    deepComponentsKey, axesKey, glyphVariationsKey = _getKeys(self.currentGlyph)
                    # glyphVariationsKey = 'robocjk.characterGlyph.glyphVariations'
                    lib = RLib()
                    lib[deepComponentsKey] = copy.deepcopy(self.currentGlyph._deepComponents.getList())
                    lib[axesKey] = copy.deepcopy(self.currentGlyph._axes.getList())
                    lib[glyphVariationsKey] = copy.deepcopy(self.currentGlyph._glyphVariations.getList())
                    self.currentGlyph.stackUndo_lib.append(lib)
            else:
                self.currentGlyph.indexStackUndo_lib = 0
            lib = copy.deepcopy(self.currentGlyph.stackUndo_lib[self.currentGlyph.indexStackUndo_lib])
            self.currentGlyph._initWithLib(lib)

            self.updateDeepComponent()
            self.glyphInspectorWindow.sourcesItem.setList()
            self.glyphInspectorWindow.axesItem.setList()
            self.setListWithSelectedElement()

    def doRedo(self):
        if self.currentGlyph.stackUndo_lib:

            if self.currentGlyph.indexStackUndo_lib < len(self.currentGlyph.stackUndo_lib)-1:
                self.currentGlyph.indexStackUndo_lib += 1 
            else:
                self.currentGlyph.indexStackUndo_lib = len(self.currentGlyph.stackUndo_lib)-1

            lib = copy.deepcopy(self.currentGlyph.stackUndo_lib[self.currentGlyph.indexStackUndo_lib])
            self.currentGlyph._initWithLib(lib)

            self.updateDeepComponent()
            self.glyphInspectorWindow.sourcesItem.setList()
            self.glyphInspectorWindow.axesItem.setList()
            self.setListWithSelectedElement()

    def keyUp(self, info):
        self.currentGlyph.reinterpolate = False

    @refresh
    def keyDown(self, info):
        if self.isAtomic:
            return
        event = extractNSEvent(info)
        try:
            character = info["event"].characters()
        except: return
        modifiers = [
            event['shiftDown'] != 0, 
            event['capLockDown'] != 0,
            event['optionDown'] != 0,
            event['controlDown'] != 0,
            event['commandDown'] != 0,
            ]
        arrowX = 0
        arrowY = 0

        if event['down']:
            arrowY = -1
        elif event['up']:
            arrowY = 1
        elif event['left']:
            arrowX = -1
        elif event['right']:
            arrowX = 1
            
        inputKey = [arrowX, arrowY]

        if self.isAtomic: return

        if modifiers[4] and character == 'z':
            self.doUndo()
        elif modifiers[4] and modifiers[0] and character == 'Z':
            self.doRedo()
        if character == ' ':
            self.currentGlyph.selectedSourceAxis = None
            if len(self.currentGlyph) and self.currentGlyph.type != "deepComponent":
                SetCurrentLayerByName("foreground")

            self.updateDeepComponent()
            # self.currentViewSourceList.glyphVariationAxesList.setSelection([])
            self.glyphInspectorWindow.sourcesItem.sourcesList.setSelection([])
            self.glyphInspectorWindow.axesItem.axesList.setSelection([])
            self.glyphView.setSelectedSource()
            self.disabledEditingUIIfValidated()
        if self._currentSourceValidated(): return
        self.currentGlyph.keyDown((modifiers, inputKey, character))

    def glyphAdditionContextualMenuItems(self, notification):
        self.menuItems = []
        validated = self._currentSourceValidated()
        if self.isDeepComponent:
            if not validated:
                item = ('Add Atomic Element', self.addAtomicElement)
                self.menuItems.append(item)
            item = ('Animate this variable glyph', self.animateThisVariableGlyph)
            self.menuItems.append(item)
            if self.currentGlyph.selectedElement and not validated:
                item = ('Remove Selected Atomic Element', self.removeAtomicElement)
                self.menuItems.append(item)
            item = ('Open History Glyph', self.openHistoryGlyph)
            self.menuItems.append(item)
            item = ('Character Glyph Viewer', self.displayReferenceGlyph)
            self.menuItems.append(item)
        elif self.isCharacterGlyph:
            if not validated:
                item = ('Add Deep Component', self.addDeepComponent)
                self.menuItems.append(item)
                item = ('Import Deep Component from another Character Glyph', self.importDeepComponentFromAnotherCharacterGlyph)
                self.menuItems.append(item)

            if self.currentGlyph.selectedElement:
                if not validated:
                    item = ('Remove Selected Deep Component', self.removeDeepComponent)
                    self.menuItems.append(item)
                item = ('go to selected deepComponent', self.gotoselectedDC)
                self.menuItems.append(item)
            variationsAxes = self.currentGlyph._axes.names
            if len(self.currentGlyph):
                if all([*(self.currentFont._RFont.getLayer(x)[self.currentGlyph.name] for x in variationsAxes)]):
                    item = ('Fix Glyph Compatiblity', self.fixGlyphCompatibility)
                    self.menuItems.append(item)
            item = ('Open History Glyph', self.openHistoryGlyph)
            self.menuItems.append(item)

        else:
            layersNames = ["foreground"]+[x.layerName for x in self.currentGlyph._glyphVariations]
            if len(self.currentGlyph):
                if all([*(self.currentFont._RFont.getLayer(x)[self.currentGlyph.name] for x in layersNames)]):
                    item = ('Fix Glyph Compatiblity', self.fixGlyphCompatibility)
                    self.menuItems.append(item)

        if "." in self.currentGlyph.name:
            item = ('Import Axes and Sources from baseglyph', self.importAxesAndSourcesFromBaseglyph)
            self.menuItems.append(item)

        notification["additionContextualMenuItems"].extend(self.menuItems)

    def displayReferenceGlyph(self, sender):
        self.CharacterGlyphViewer = roboCJKView.CharacterGlyphViewer(self)

    def openHistoryGlyph(self, sender):
        self.HistoryGlyphWindow = roboCJKView.HistoryGlyph(self)

    def importAxesAndSourcesFromBaseglyph(self, sender):
        name = self.currentGlyph.name
        glyph = self.currentGlyph
        f = self.currentFont

        basename = name.split(".")[0]
        baseglyph = f[basename]

        if sorted(list(glyph._axes.names)) != sorted(list(baseglyph._axes.names)):
            missing = []
            for x in list(baseglyph._axes.names):
                if x not in list(glyph._axes.names):
                    missing.append(x)
            for n in missing:
                axis = baseglyph._axes.get(n)
                glyph.addAxis(n, axis.minValue, axis.maxValue, axis.defaultValue)
             
        gsourcesnames = [x.sourceName for x in glyph._glyphVariations]
        for bsi, source in enumerate(baseglyph._glyphVariations):
            if source.sourceName not in gsourcesnames:
                glyph.addSource(source.sourceName, dict(source.location), source.layerName)
                for dci, dc in enumerate(baseglyph._deepComponents):
                    if dc["name"] == glyph._deepComponents[dci]["name"]:
                        gcoord = glyph._glyphVariations[-1].deepComponents[dci].coord
                        gtransform = glyph._glyphVariations[-1].deepComponents[dci].transform
                        bcoord = baseglyph._glyphVariations[bsi].deepComponents[dci].coord
                        btransform = baseglyph._glyphVariations[bsi].deepComponents[dci].transform
                        for k in gcoord:
                            gcoord.setValue(k, bcoord[k])
                        for t in gtransform:
                            gtransform.setValue(t, btransform[t])
                            
        glyph.update()
        self.glyphInspectorWindow.axesItem.setList()
        self.glyphInspectorWindow.sourcesItem.setList()

    def gotoselectedDC(self, sender):
        g = self.currentGlyph
        selectedDCName = g._deepComponents[g.selectedElement[0]].name
        CurrentGlyphWindow().close()
        self.currentGlyph = self.currentFont[selectedDCName]
        roboCJKView.openGlyphWindowIfLockAcquired(self, self.currentGlyph)

    def animateThisVariableGlyph(self, sender):
        movie.Movie(self)

    def addAtomicElement(self, sender):
        sheets.SelectAtomicElementSheet(self, self.currentFont.atomicElementSet)

    def addDeepComponent(self, sender):
        sheets.SelectDeepComponentSheet(self, self.currentFont.deepComponentSet)

    def fixGlyphCompatibility(self, sender):
        sheets.FixGlyphCompatibility(self, self.currentGlyph)        

    def removeAtomicElement(self, sender):
        self.currentGlyph.removeAtomicElementAtIndex()
        self.currentViewSliderList.deepComponentAxesList.set([])
        self.updateDeepComponent()
        self.glyphInspectorWindow.deepComponentListItem.setList()

    def removeDeepComponent(self, sender):
        self.currentGlyph.removeDeepComponentAtIndexToGlyph()
        self.currentViewSliderList.deepComponentAxesList.set([])
        self.updateDeepComponent()
        self.glyphInspectorWindow.deepComponentListItem.setList()

    def importDeepComponentFromAnotherCharacterGlyph(self, sender):
        self.importDCFromCG = roboCJKView.ImportDeepComponentFromAnotherCharacterGlyph(self)
        self.importDCFromCG.open()
        self.glyphInspectorWindow.deepComponentListItem.setList()

    @lockedProtect
    @refresh
    def updateListInterface(self):
        # l = []
        # if self.isAtomic:
        #     for axis, variation in zip(self.currentGlyph._axes, self.currentGlyph._glyphVariations):
        #         l.append({"Axis":axis.name, "Layer":variation.layerName, "PreviewValue":0, "MinValue":axis.minValue, "MaxValue":axis.maxValue})
            
        # elif self.isDeepComponent:
        #     if self.currentGlyph._axes:
        #         l = [{'Axis':x.name, 'PreviewValue':0, "MinValue":x.minValue, "MaxValue":x.maxValue} for x in self.currentGlyph._axes]
            
        # elif self.isCharacterGlyph:
        #     if self.currentGlyph._glyphVariations:
        #         l = [{'Axis':x.name, 'PreviewValue':0, "MinValue":x.minValue, "MaxValue":x.maxValue} for x in self.currentGlyph._axes]

        self.currentViewSourceList.glyphVariationAxesList.set(l)
        self.glyphInspectorWindow.sourcesItem.setList()
        self.glyphInspectorWindow.axesItem.setList()
        # self.currentGlyph.sourcesList = l

    def userValue(self, value, minValue, maxValue):
        value = minValue + (maxValue - minValue) * value 
        # if math.ceil(value) - value < 0.001:
        #     value = math.ceil(value)
        return value

    def systemValue(self, value, minValue, maxValue):
        if maxValue  - minValue == 0:
            return 0
        return (value - minValue) / (maxValue - minValue)

    @refresh
    def addSubView(self):
        self.window = CurrentGlyphWindow()
        if self.window is None: return
        self.glyphView.show(True)
        self.window.addGlyphEditorSubview(self.glyphView)
        self.glyphView.setSelectedSource()

    def opaque(self):
        return False

    def acceptsFirstResponder(self):
        return False

    def acceptsMouseMoved(self):
        return True

    def becomeFirstResponder(self):
        return False

    def resignFirstResponder(self):
        return False

    def shouldDrawBackground(self):
        return False




