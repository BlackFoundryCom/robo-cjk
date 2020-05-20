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
from mojo.roboFont import *
from imp import reload
from utils import interpolation, decorators
reload(decorators)
glyphUndo = decorators.glyphUndo
reload(interpolation)
from models import deepComponent, component
reload(component)
import copy
# reload(deepComponent)

DeepComponents = component.DeepComponents

def compute(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        self.computeDeepComponents()
        self.computeDeepComponentsPreview()
    return wrapper


class Glyph(RGlyph):

    def __init__(self):
        super().__init__()
        self.type = None
        self.preview = None
        self.sourcesList = []
        # self.transformationWithMouse = False

    def save(self):
        self.lib.clear()

    def getParent(self):
        return self.currentFont

    def setParent(self, currentFont):
        self.currentFont = currentFont

    @property
    def _RGlyph(self):
        return self.currentFont._RFont[self.name]

    @property
    def flatComponents(self):
        return self._RGlyph.components

    @glyphUndo
    def keyDown(self, keys):
        modifiers, inputKey, character = keys
        element = self._getElements()
        if modifiers[2]:
            if character == '∂':
                self.duplicateSelectedElements()
            else:
                rotation = (-7*modifiers[0]*modifiers[4]*inputKey[0] - 4*modifiers[0]*inputKey[0] - 2*inputKey[0])*.5
                self.setRotationAngleToSelectedElements(rotation)
        elif modifiers[1]:
            x = round((9*modifiers[0]*inputKey[0] + inputKey[0])*.01, 3)
            y = round((9*modifiers[0]*inputKey[1] + inputKey[1])*.01, 3)
            self.setScaleToSelectedElements((x, y))
        else:
            x = 90*modifiers[0]*modifiers[4]*inputKey[0] + 9*modifiers[0]*inputKey[0] + inputKey[0] 
            y = 90*modifiers[0]*modifiers[4]*inputKey[1] + 9*modifiers[0]*inputKey[1] + inputKey[1]
            self.setPositionToSelectedElements((x, y))

    def _getSelectedElement(self):
        element = self._getElements()
        if element is None: return
        for index in self.selectedElement:
            yield element[index]

    @compute
    def setRotationAngleToSelectedElements(self, rotation: int, append: bool = True):
        for selectedElement in self._getSelectedElement():
            if append:
                selectedElement["rotation"] += int(rotation)
            else:
                selectedElement["rotation"] = -int(rotation)

    @compute
    def setPositionToSelectedElements(self, position: list):
        for selectedElement in self._getSelectedElement():
            selectedElement["x"] += position[0]
            selectedElement["y"] += position[1]

    @compute
    def setScaleToSelectedElements(self, scale: list):
        x, y = scale
        for selectedElement in self._getSelectedElement():
            rotation = selectedElement["rotation"]
            if -45 < rotation < 45:
                x, y = x, y
            elif -135 < rotation < -45 or 225 < rotation < 315:
                x, y = -y, x
            elif 45 < rotation < 135 or -315 < rotation < -225:
                x, y = y, -x
            elif -225 < rotation < -135 or 135 < rotation < 225:
                x, y = -x, -y
            elif -360 < rotation < -315 or 315 < rotation < 360:
                x, y = -x, -y
            selectedElement["scalex"] += x
            selectedElement["scaley"] += y

    def pointIsInside(self, point, multipleSelection = False):
        px, py = point
        for index, atomicInstanceGlyph in self.atomicInstancesGlyphs:
            if atomicInstanceGlyph.pointInside((px, py)):
                if index not in self.selectedElement:
                    self.selectedElement.append(index)
                if not multipleSelection: return

    def selectionRectTouch(self, x: int, w: int, y: int, h: int):
        for index, atomicInstanceGlyph in self.atomicInstancesGlyphs:
            inside = False
            for c in atomicInstanceGlyph:
                for p in c.points:
                    if p.x > x and p.x < w and p.y > y and p.y < h:
                        inside = True
            if inside:
                if index in self.selectedElement: continue
                self.selectedElement.append(index)

    def generateDeepComponent(self, g, preview=True):
        atomicInstances = []
        if not hasattr(g,"_atomicElements"): return
        for i, atomicElement in enumerate(g._atomicElements):
            layersInfos = {}
            
            # aeGlyph = self.getParent()[atomicElement['name']]
            atomicElementGlyph = self.currentFont[atomicElement['name']].foreground
            variationGlyph = self.currentFont[atomicElement['name']]._glyphVariations
            
            for axisName in atomicElement['coord'].keys():
                # if self.selected == (i, atomicElement['name']) and self.sliderName == axisName and preview == False and self.sliderValue:
                #     atomicElement['coord'][axisName] = float(self.sliderValue)
                layersInfos[str(variationGlyph[axisName])] = atomicElement['coord'][axisName]
                

            # print(layersInfos)
            # print(atomicElementGlyph)
            print(layersInfos)
            atomicInstanceGlyph = interpolation.deepolation(
                RGlyph(), 
                atomicElementGlyph, 
                layersInfos
                )
    
            atomicInstanceGlyph.scaleBy((atomicElement['scalex'], atomicElement['scaley']))
            atomicInstanceGlyph.rotateBy(atomicElement['rotation'])
            atomicInstanceGlyph.moveBy((atomicElement['x'], atomicElement['y']))  
            # atomicInstanceGlyph.round()
            atomicInstances.append({atomicElement['name']:(atomicInstanceGlyph, variationGlyph, atomicElement['coord'])})
        return atomicInstances


    def generateCharacterGlyph(self, g, preview=True):
        ### CLEANING TODO ###
        _lib = []

        deepComponents = []
        for j, dc in enumerate(g._deepComponents):
            # if self.selected == (j, dc['name']) and self.sliderValue and preview==False:
            #     dc['coord'][self.sliderName] = float(self.sliderValue)
                
            dcGlyph = self.getParent()[dc['name']]
            masterDeepComponent = dcGlyph._atomicElements
            deepComponentVariations = dcGlyph._glyphVariations
            deepComponentAxisInfos = {}

            deepComponentAxisInfos = dc['coord'] 

            deepdeepolatedDeepComponent = interpolation.deepdeepolation(
                masterDeepComponent, 
                deepComponentVariations, 
                deepComponentAxisInfos
                )
            previewGlyph = deepComponent.DeepComponent("PreviewGlyph")
            previewGlyph._atomicElements = deepdeepolatedDeepComponent
            
            atomicInstancesPreview = self.generateDeepComponent(previewGlyph, preview=True)
            for e in atomicInstancesPreview:
                for aeName, ae in e.items():
                    ae[0].scaleBy((dc['scalex'], dc['scaley']))
                    ae[0].moveBy((dc['x'], dc['y']))
                    ae[0].rotateBy(dc['rotation'])
                    # ae[0].round()
            deepComponents.append({dc['name']: (dc['coord'], atomicInstancesPreview)})
            _lib.append(dc)
        g._deepComponents = DeepComponents(_lib)
        return deepComponents

