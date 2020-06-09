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
        self.preview.computeDeepComponents(update = False)
        self.preview.computeDeepComponentsPreview(update = False)
    return wrapper


class Glyph(RGlyph):

    def __init__(self):
        super().__init__()
        self.type = None
        # self.preview = None
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

    def update(self):
        if self.type == 'atomicElement':
            return
        deepComponentToRemove = []
        glyphset = set(self.currentFont.glyphSet())
        for index, deepComponent in enumerate(self._deepComponents):
            if set([deepComponent.name]) - glyphset:
                deepComponentToRemove.append(index)
            else:
                deepComponentGlyph = self.currentFont[deepComponent.name]
                deepComponentGlyphAxes = set(deepComponentGlyph._glyphVariations.axes)

                # remove old axes in both deepComponent and variationGlyph
                todel = set(deepComponent.coord.axes) - deepComponentGlyphAxes
                for oldAxis in todel:
                    deepComponent.coord.remove(oldAxis)
                    for glyphVariation in self._glyphVariations.infos:
                        glyphVariation.content.deepComponents[index].coord.remove(oldAxis)

                # add new axes to both deepComponent and variationGlyph
                toadd = deepComponentGlyphAxes - set(deepComponent.coord)
                for axis in toadd:
                    deepComponent.coord.add(axis, 0)
                    for glyphVariation in self._glyphVariations.infos:
                        glyphVariation.content.deepComponents[index].coord.add(axis, 0)

        self.removeDeepComponents(deepComponentToRemove)

    def removeDeepComponents(self, deepComponents:list = []):
        self._deepComponents.removeDeepComponents(deepComponents)
        self._glyphVariations.removeDeepComponents(deepComponents)

    @glyphUndo
    def keyDown(self, keys):
        modifiers, inputKey, character = keys
        # element = self._getElements()
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

    def _getElements(self):
        if self.selectedSourceAxis:
            return self._glyphVariations[self.selectedSourceAxis]
        else:
            return self._deepComponents

    def _getSelectedElement(self):
        element = self._getElements()
        if element is None: return
        for index in self.selectedElement:
            yield element[index]
    
    @compute
    def setRotationAngleToSelectedElements(self, rotation: int, append: bool = True):
        for selectedElement in self._getSelectedElement():
            if append:
                selectedElement.rotation += int(rotation)
            else:
                selectedElement.rotation = -int(rotation)

    @compute
    def setPositionToSelectedElements(self, position: list):
        for selectedElement in self._getSelectedElement():
            selectedElement.x += position[0]
            selectedElement.y += position[1]

    @compute
    def setScaleToSelectedElements(self, scale: list):
        x, y = scale
        for selectedElement in self._getSelectedElement():
            rotation = selectedElement.rotation
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
            selectedElement.scalex += x
            selectedElement.scaley += y

    @compute
    def setTransformationCenterToSelectedElements(self, center):
        tx, ty = center
        for index in self.selectedElement:
            self._deepComponents[index].transformx = int(tx)
            self._deepComponents[index].transformy = int(ty)
            for variations in self._glyphVariations.values():
                variations[index].transformx = int(tx)
                variations[index].transformy = int(ty)

    def pointIsInside(self, point, multipleSelection = False):
        px, py = point
        for index, atomicInstanceGlyph in enumerate(self.preview.axisPreview):
            atomicInstanceGlyph.selected = False
            if atomicInstanceGlyph.getTransformedGlyph().pointInside((px, py)):
                atomicInstanceGlyph.selected = True
                if index not in self.selectedElement:
                    self.selectedElement.append(index)
                if not multipleSelection: return

    def selectionRectTouch(self, x: int, w: int, y: int, h: int):
        for index, atomicInstanceGlyph in enumerate(self.preview.axisPreview):
            inside = False
            atomicInstanceGlyph.selected = False
            for c in atomicInstanceGlyph.getTransformedGlyph():
                for p in c.points:
                    if p.x > x and p.x < w and p.y > y and p.y < h:
                        inside = True
                        atomicInstanceGlyph.selected = True
            if inside:
                if index in self.selectedElement: continue
                self.selectedElement.append(index)
