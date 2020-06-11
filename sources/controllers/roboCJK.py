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
reload(interpolation)

from views import roboCJKView, sheets
reload(roboCJKView)
reload(sheets)

from resources import characterSets, chars2deepCompo
reload(characterSets)
reload(chars2deepCompo)

charsets = characterSets.characterSets
CG2DC = chars2deepCompo.Chars2DC

from utils import files
reload(files)

from utils import gitEngine as git
reload(git)

from views import drawer
reload(drawer)

from views import canvasGroups
reload(canvasGroups)

from views import popover
reload(popover)

from models import deepComponent
reload(deepComponent)

from tools import transformationTool
reload(transformationTool)

from views import PDFProofer
reload(PDFProofer)

import os
from mojo.UI import UpdateCurrentGlyphView, CurrentGlyphWindow
import mojo.drawingTools as mjdt
from mojo.roboFont import *
from mojo.extensions import getExtensionDefault, setExtensionDefault

import math
import json
import copy 

from utils import decorators
reload(decorators)
refresh = decorators.refresh
lockedProtect = decorators.lockedProtect

blackrobocjk_glyphwindowPosition = "com.black-foundry.blackrobocjk_glyphwindowPosition"

class RoboCJKController(object):

    def __init__(self):
        self.observers = False
        self.drawer = drawer.Drawer(self)
        self.transformationTool = transformationTool.TransformationTool(self)
        self.componentWindow = None
        self.characterWindow = None
        self.gitUserName = ''
        self.gitPassword = ''
        self.gitHostLocker = ''
        self.gitHostLockerPassword = ''
        self.privateLocker = True
        self.glyphWindowPosSize = getExtensionDefault(blackrobocjk_glyphwindowPosition, (0, 180, 1000, 600))
        self.drawOnlyDeepolation = False
        # installTool(self.transformationTool)

        self.locked = False

        self.roundToGrid = False
        self.atomicView = canvasGroups.AtomicView(
            self,
            posSize = (20, 0, 300, -20), 
            delegate = self
            )
        self.deepComponentView = canvasGroups.DCCG_View(
            self,
            posSize = (20, 0, 300, -20), 
            delegate = self
            )

        self.characterGlyphView = canvasGroups.DCCG_View(
            self,
            posSize = (20, 0, 300, -20), 
            delegate = self
            )
        self.transformationToolIsActiv = False
        # self.pdf = PDFProofer.PDFEngine(self)
        self.importDCFromCG = None
        self.sliderValue = None
        self.sliderName = None
        self.dataBase = {}
        self.copy = []
        self.px, self.py = 0,0

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
            removeObserver(self, "currentGlyphChanged")
            removeObserver(self, "mouseDown")
            removeObserver(self, "mouseUp")
            removeObserver(self, "keyDown")
            removeObserver(self, "didUndo")
        else:
            addObserver(self, "fontDidSave", "fontDidSave")
            addObserver(self, "glyphAdditionContextualMenuItems", "glyphAdditionContextualMenuItems")
            # addObserver(self, "glyphWindowWillOpen", "glyphWindowWillOpen")
            addObserver(self, "glyphWindowWillClose", "glyphWindowWillClose")
            addObserver(self, "observerDraw", "draw")
            addObserver(self, "observerDrawPreview", "drawPreview")
            addObserver(self, "currentGlyphChanged", "currentGlyphChanged")
            addObserver(self, "mouseDown", "mouseDown")
            addObserver(self, "mouseUp", "mouseUp")
            addObserver(self, "keyDown", "keyDown")
            addObserver(self, "didUndo", "didUndo")
        self.observers = not self.observers

    def fontDidSave(self, info):
        if self.currentFont and self.currentFont._RFont == CurrentFont():
            self.currentFont.save()
        else:
            print('no font object')

    def didUndo(self, info):
        self.updateDeepComponent()

    @refresh
    def updateDeepComponent(self, update = True):
        self.currentGlyph.preview.computeDeepComponentsPreview(update = update)
        if self.isAtomic: return
        self.currentGlyph.preview.computeDeepComponents(axis = self.currentGlyph.selectedSourceAxis, update = False)

    def glyphWindowWillClose(self, notification):
        # self.closeimportDCFromCG()
        self.closeComponentWindow()
        self.closeCharacterWindow()

        try:
        # if CurrentGlyphWindow() is not None:
            posSize = CurrentGlyphWindow().window().getPosSize()
            setExtensionDefault(blackrobocjk_glyphwindowPosition, posSize)
            self.glyphWindowPosSize = getExtensionDefault(blackrobocjk_glyphwindowPosition)
        except:pass

        self.window.removeGlyphEditorSubview(self.atomicView)
        self.window.removeGlyphEditorSubview(self.deepComponentView)
        self.window.removeGlyphEditorSubview(self.characterGlyphView)
        self.roboCJKView.w.atomicElementPreview.update()
        self.roboCJKView.w.deepComponentPreview.update()
        self.roboCJKView.w.characterGlyphPreview.update()
        
        # self.currentFont.locker.unlock(self.currentGlyph)
        self.currentFont.save()
        if self.currentGlyph is not None:
            self.currentFont.getGlyph(self.currentGlyph)
        

    def closeimportDCFromCG(self):
        if self.importDCFromCG is not None:
            self.importDCFromCG.close()
            self.importDCFromCG = None

    @lockedProtect
    def currentGlyphChanged(self, notification):
        glyph = notification['glyph']
        if glyph is None: return
        if glyph.name != self.currentGlyph.name:
            # self.currentFont.locker.unlock(self.currentGlyph)
            self.closeimportDCFromCG()
        self.currentGlyph = self.currentFont[glyph.name]
        d = self.currentGlyph._glyphVariations
        if self.currentGlyph.type == "atomicElement":
            self.currentGlyph.sourcesList = [
                {"Axis":axisName, "Layer":layer.layerName, "PreviewValue":0, "MinValue":layer.minValue, "MaxValue":layer.maxValue} for axisName, layer in  d.items()
                ]
        else:
            self.currentGlyph.sourcesList = [
                {"Axis":axisName, "Layer":layerName, "PreviewValue":0} for axisName, layerName in  d.items()
                ]
        self.currentViewSourceList.set(self.currentGlyph.sourcesList)
        self.currentViewSourceValue.set("")
        if self.currentGlyph.type =='atomicElement':
            uninstallTool(self.transformationTool)
            self.closeComponentWindow()
        else:
            installTool(self.transformationTool)
            if self.dataBase:
                if self.currentGlyph.type =='characterGlyph':
                    self.closeCharacterWindow()
                    if self.currentGlyph.name.startswith("uni"):
                        if self.componentWindow is None:
                            self.componentWindow = roboCJKView.ComponentWindow(self)
                        self.componentWindow.setUI()
                        self.componentWindow.open()
                    else:
                        self.closeComponentWindow()
                elif self.currentGlyph.type == 'deepComponent':
                    self.closeComponentWindow()
                    if self.currentGlyph.name.startswith("DC_"):
                        if self.characterWindow is None:
                            self.characterWindow = roboCJKView.CharacterWindow(self)
                        self.characterWindow.setUI()
                        self.characterWindow.open()
                    else:
                        self.closeCharacterWindow()

        self.showCanvasGroups()
        self.addSubView()
        self.updateDeepComponent()

    def exportDataBase(self):
        with open(os.path.join(self.currentFont.fontPath, "database.json"), 'w', encoding="utf-8") as file:
            file.write(json.dumps(self.dataBase))

    def closeCharacterWindow(self):
        if self.characterWindow is not None:
            self.characterWindow.close()
            self.characterWindow = None

    def closeComponentWindow(self):
        if self.componentWindow is not None:
            self.componentWindow.close()
            self.componentWindow = None

    @property 
    def currentViewSourceList(self):
        if self.isAtomic:
            return self.atomicView.atomicElementsList
        elif self.isDeepComponent:
            return self.deepComponentView.sourcesList
        elif self.isCharacterGlyph:
            return self.characterGlyphView.sourcesList
    @property 
    def currentViewSliderList(self):
        if self.isDeepComponent:
            return self.deepComponentView.slidersList
        elif self.isCharacterGlyph:
            return self.characterGlyphView.slidersList

    @property 
    def currentViewSourceValue(self):
        if self.isAtomic:
            return self.atomicView.atomicElementsSliderValue
        elif self.isDeepComponent:
            return self.deepComponentView.sourcesSliderValue
        elif self.isCharacterGlyph:
            return self.characterGlyphView.sourcesSliderValue

    @refresh
    def addSubView(self):
        self.window = CurrentGlyphWindow()
        if self.window is None: return
        # add the view to the GlyphEditor
        self.showCanvasGroups()
        if self.isAtomic: 
            self.window.addGlyphEditorSubview(self.atomicView)
            self.updateListInterface()
            return
        elif self.isDeepComponent:
            self.window.addGlyphEditorSubview(self.deepComponentView)
            self.deepComponentView.setUI()
            self.updateListInterface()
            return
        elif self.isCharacterGlyph:
            self.window.addGlyphEditorSubview(self.characterGlyphView)
            self.characterGlyphView.setUI()
            self.updateListInterface()
            return

    def showCanvasGroups(self):
        self.atomicView.show(self.isAtomic)
        self.deepComponentView.show(self.isDeepComponent)
        self.characterGlyphView.show(self.isCharacterGlyph)

    def draw(self):
        mjdt.save()
        mjdt.fill(1, 1, 1, .7)
        mjdt.roundedRect(0, 0, 300, [525, 425][self.currentGlyph.type == "atomicElement"], 10)
        scale = .15
        glyphwidth = self.currentFont._RFont.lib.get('robocjk.defaultGlyphWidth', 1000)
        mjdt.translate((glyphwidth*scale/2), [300, 200][self.currentGlyph.type == "atomicElement"])
        mjdt.fill(.15)

        
        mjdt.scale(scale, scale)
        mjdt.translate(0, abs(self.currentFont._RFont.info.descender))
        self.drawer.drawGlyph(
            self.currentGlyph,
            scale,
            (0, 0, 0, 1),
            (0, 0, 0, 0),
            (0, 0, 0, 1),
            drawSelectedElements = False
            )
        mjdt.restore()

    def observerDraw(self, notification):
        self.showCanvasGroups()
        if hasattr(self.currentGlyph, 'type'):
            self.drawer.draw(
                notification,
                onlyPreview = self.drawOnlyDeepolation
                )

    def observerDrawPreview(self, notification):
        if self.currentGlyph is None: return
        self.drawer.draw(
            notification, 
            customColor=(0, 0, 0, 1), 
            onlyPreview = self.drawOnlyDeepolation
            )

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
            self.currentViewSliderList.set([])
            if self.currentGlyph.selectedElement: 
                self.setListWithSelectedElement()

                if point['clickCount'] == 2:
                    popover.EditPopoverAlignTool(
                        self, 
                        point['point'], 
                        self.currentGlyph
                        )
        else:
            self.currentGlyph.setTransformationCenterToSelectedElements((point['point'].x, point['point'].y))
            addObserver(self, 'mouseDragged', 'mouseDragged')

    def mouseDragged(self, point):
        self.currentGlyph.setTransformationCenterToSelectedElements((point['point'].x, point['point'].y))

    def setListWithSelectedElement(self):
        if self.isDeepComponent:
            element = self.deepComponentView
        elif self.isCharacterGlyph:
            element = self.characterGlyphView

        if not self.currentGlyph.selectedSourceAxis:
            data = self.currentGlyph._deepComponents
        else:
            data = self.currentGlyph._glyphVariations[self.currentGlyph.selectedSourceAxis]

        l = []
        if len(self.currentGlyph.selectedElement) == 1:
            for axisName, value in data[self.currentGlyph.selectedElement[0]].coord.items():
                l.append({'Axis':axisName, 'PreviewValue':value})
        element.slidersList.set(l)
        self.sliderValue = None

    @refresh
    def mouseUp(self, info):
        removeObserver(self, 'mouseDragged')
        if self.isAtomic:
            return
        if self.transformationToolIsActiv and self.currentGlyph.selectedElement: return
        try: x, y = info['point'].x, info['point'].y
        except: return
        self.currentViewSliderList.set([])
        self.currentGlyph.selectionRectTouch(
            *sorted([x, self.px]), 
            *sorted([y, self.py])
            )
        if self.currentGlyph.selectedElement:
            self.setListWithSelectedElement()
    
    def doUndo(self):
        if len(self.currentGlyph.stackUndo_lib) >= 1:
            if self.currentGlyph.indexStackUndo_lib > 0:
                self.currentGlyph.indexStackUndo_lib -= 1

                if self.currentGlyph.indexStackUndo_lib == len(self.currentGlyph.stackUndo_lib)-1:    
                    deepComponentsKey = 'robocjk.characterGlyph.deepComponents'
                    glyphVariationsKey = 'robocjk.characterGlyph.glyphVariations'
                    lib = RLib()
                    lib[deepComponentsKey] = copy.deepcopy(self.currentGlyph._deepComponents)
                    lib[glyphVariationsKey] = copy.deepcopy(self.currentGlyph._glyphVariations)
                    self.currentGlyph.stackUndo_lib.append(lib)
            else:
                self.currentGlyph.indexStackUndo_lib = 0

            lib = copy.deepcopy(self.currentGlyph.stackUndo_lib[self.currentGlyph.indexStackUndo_lib])
            self.currentGlyph._initWithLib(lib)

            self.updateDeepComponent()
            self.characterGlyphView.sourcesList.set(self.currentGlyph.sourcesList)

    def doRedo(self):
        if self.currentGlyph.stackUndo_lib:

            if self.currentGlyph.indexStackUndo_lib < len(self.currentGlyph.stackUndo_lib)-1:
                self.currentGlyph.indexStackUndo_lib += 1 
            else:
                self.currentGlyph.indexStackUndo_lib = len(self.currentGlyph.stackUndo_lib)-1

            lib = copy.deepcopy(self.currentGlyph.stackUndo_lib[self.currentGlyph.indexStackUndo_lib])
            self.currentGlyph._initWithLib(lib)

            

            self.updateDeepComponent()
            self.characterGlyphView.sourcesList.set(self.currentGlyph.sourcesList)

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
            self.updateDeepComponent()
            self.currentViewSourceList.setSelection([])

        self.currentGlyph.keyDown((modifiers, inputKey, character))

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

    def glyphAdditionContextualMenuItems(self, notification):
        menuItems = []
        # if self.isAtomic:
        #     item = ('Attach Layer to Atomic Element', self.addLayerToAtomicElement)
        #     menuItems.append(item)
        if self.isDeepComponent:
            item = ('Add Atomic Element', self.addAtomicElement)
            menuItems.append(item)
            if self.currentGlyph.selectedElement:
                item = ('Remove Selected Atomic Element', self.removeAtomicElement)
                menuItems.append(item)
        elif self.isCharacterGlyph:
            item = ('Add Deep Component', self.addDeepComponent)
            menuItems.append(item)
            item = ('Import Deep Component from another Character Glyph', self.importDeepComponentFromAnotherCharacterGlyph)
            menuItems.append(item)
            if self.currentGlyph.selectedElement:
                item = ('Remove Selected Deep Component', self.removeDeepComponent)
                menuItems.append(item)
        notification["additionContextualMenuItems"].extend(menuItems)

    def addAtomicElement(self, sender):
        sheets.SelectAtomicElementSheet(self, self.currentFont.atomicElementSet)

    def addDeepComponent(self, sender):
        sheets.SelectDeepComponentSheet(self, self.currentFont.deepComponentSet)

    def removeAtomicElement(self, sender):
        self.currentGlyph.removeAtomicElementAtIndex()
        self.currentViewSliderList.set([])
        self.updateDeepComponent()

    def removeDeepComponent(self, sender):
        self.currentGlyph.removeDeepComponentAtIndexToGlyph()
        self.currentViewSliderList.set([])
        self.updateDeepComponent()

    def importDeepComponentFromAnotherCharacterGlyph(self, sender):
        self.importDCFromCG = roboCJKView.ImportDeepComponentFromAnotherCharacterGlyph(self)
        self.importDCFromCG.open()
    # def addLayerToAtomicElement(self, sender):
    #     availableLayers = [l for l in self.currentGlyph._RGlyph.layers if l.layer.name!='foreground']
    #     if [l for l in self.currentGlyph._RGlyph.layers if l.name != 'foreground']:
    #         sheets.SelectLayerSheet(self, availableLayers)s

    @lockedProtect
    @refresh
    def updateListInterface(self):
        l = []
        if self.isAtomic:
            for axisName, layer in self.currentGlyph._glyphVariations.items():
                l.append({"Axis":axisName, "Layer":layer.layerName, "PreviewValue":0, "MinValue":layer.minValue, "MaxValue":layer.maxValue})
            
        elif self.isDeepComponent:
            if self.currentGlyph._glyphVariations:
                l = [{'Axis':axis, 'PreviewValue':0} for axis in self.currentGlyph._glyphVariations.axes]
            
        elif self.isCharacterGlyph:
            if self.currentGlyph._glyphVariations:
                l = [{'Axis':axis, 'PreviewValue':0} for axis in self.currentGlyph._glyphVariations.axes]

        self.currentViewSourceList.set(l)
        self.currentGlyph.sourcesList = l

    def userValue(self, value, minValue, maxValue):
        return minValue + (maxValue - minValue) * value

    def systemValue(self, value, minValue, maxValue):
        return (value - minValue) / (maxValue - minValue + 1e-10)
