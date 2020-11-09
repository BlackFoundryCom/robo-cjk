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
# reload(decorators)
glyphUndo = decorators.glyphUndo
# reload(interpolation)
from models import deepComponent, component
# reload(component)
import copy
import math
# from fontTools.misc.transform import Transform

# reload(deepComponent)
DeepComponents = component.DeepComponents

INPROGRESS = (1, 0, 0, 1)
CHECKING1 = (1, .5, 0, 1)
CHECKING2 = (1, 1, 0, 1)
CHECKING3 = (0, .5, 1, 1)
DONE = (0, 1, .5, 1)
STATE_COLORS = {
    INPROGRESS:"INPROGRESS", 
    CHECKING1:"CHECKING1", 
    CHECKING2:"CHECKING2", 
    CHECKING3:"CHECKING3", 
    DONE:"DONE"}

# def compute(func):
#     def wrapper(self, *args, **kwargs):
#         func(self, *args, **kwargs)
#         # self.preview.computeDeepComponents(update = False)
#         # self.preview.computeDeepComponentsPreview(update = False)
#     return wrapper

def _getKeys(glyph):
    if glyph.type == "characterGlyph":
        return 'robocjk.deepComponents', 'robocjk.axes', 'robocjk.variationGlyphs'
    else:
        return 'robocjk.deepComponents', 'robocjk.axes', 'robocjk.variationGlyphs'

# import operator
# class _MathMixin:

#     def __add__(self, other):
#         return self._doBinaryOperator(other, operator.add)

#     def __sub__(self, other):
#         return self._doBinaryOperator(other, operator.sub)

#     def __mul__(self, scalar):
#         return self._doBinaryOperatorScalar(scalar, operator.mul)

#     def __rmul__(self, scalar):
#         return self._doBinaryOperatorScalar(scalar, operator.mul)

class Glyph(RGlyph):

    def __init__(self):
        super().__init__()
        self.type = None
        self._RFont = None
        # self.preview = None
        self.sourcesList = []
        self._designState = ""

        self.model = None
        self.deltas = None

        # self.frozenPreview = []

    def _setStackUndo(self):
        # if self.type != 'atomicElement':
        lib = RLib()
        deepComponentsKey, axesKey, glyphVariationsKey = _getKeys(self)
        lib[deepComponentsKey] = copy.deepcopy(self._deepComponents)
        lib[axesKey] = copy.deepcopy(self._axes)
        lib[glyphVariationsKey] = copy.deepcopy(self._glyphVariations)
        self.stackUndo_lib = [lib]
        self.indexStackUndo_lib = 0
        # self.transformationWithMouse = False

    def __bool__(self):
        if bool(self._glyphVariations):
            return True
        else:
            return bool(self._deepComponents)

    # def instantiate(self, location):
    #     if self.model is None:
    #         return self  # XXX raise error?
    #     if self.deltas is None:
    #         self.deltas = self.model.getDeltas([self] + self.variations)
    #     location = normalizeLocation(location, self.axes)
    #     return self.model.interpolateFromDeltas(location, self.deltas)

    # def _doBinaryOperatorScalar(self, scalar, op):
    #     result = self.__class__()
    #     result.name = self.name
    #     result.unicodes = self.unicodes
    #     result.width = op(self.width, scalar)
    #     # result.outline = op(self.outline, scalar)
    #     # result.components = [op(compo, scalar) for compo in self.components]
    #     return result

    # def _doBinaryOperator(self, other, op):
    #     result = self.__class__()
    #     result.name = self.name
    #     result.unicodes = self.unicodes
    #     result.width = op(self.width, other.width)
    #     # result.outline = op(self.outline, other.outline)
    #     # result.components = [
    #     #     op(compo1, compo2)
    #     #     for compo1, compo2 in zip(self.components, other.components)
    #     # ]
    #     return result

    # @property
    # def designState(self):
    #     self.designState = STATE_COLORS.get(self.stateColor, "")
    #     return self._designState

    # @designState.setter
    # def designState(self, value):
    #     self._designState = value    

    # @property
    # def stateColor(self):
    #     mark = self._RGlyph.markColor
    #     if mark is None:
    #         mark = (1, 1, 1, 1)
    #     return mark

    # @stateColor.setter
    # def stateColor(self, value:tuple):
    #     self._RGlyph.markColor = value
    # def _transformGlyph(self, glyph, transform):
    #     glyph.scaleBy((transform["scalex"], transform["scaley"]))
    #     glyph.rotateBy(transform["rotation"], (transform["tcenterx"], transform["tcentery"]))
    #     glyph.moveBy((transform["x"], transform["y"]))
    #     return glyph

    # def makeTransform(self, x, y, rotation, scalex, scaley, tcenterx, tcentery, scaleUsesCenter=False):
    #     rotation = math.radians(rotation)
    #     if not scaleUsesCenter:
    #         tcenterx *= scalex
    #         tcentery *= scaley
    #         t = Transform()
    #         t = t.translate(x + tcenterx, y + tcentery)
    #         t = t.rotate(rotation)
    #         t = t.translate(-tcenterx, -tcentery)
    #         t = t.scale(scalex, scaley)
    #     else:
    #         t = Transform()
    #         t = t.translate(x + tcenterx, y + tcentery)
    #         t = t.rotate(rotation)
    #         t = t.scale(scalex, scaley)
    #         t = t.translate(-tcenterx, -tcentery)
    #     return t

    def _transformGlyph(self, glyph, transform):
        t = interpolation.makeTransform(**transform)
        # for c in glyph:
        glyph.transformBy(tuple(t))
        return glyph

    def getLocation(self):
        loc = {}
        if self.selectedSourceAxis:
            loc = {self.selectedSourceAxis:1}
        return loc

    def save(self):
        # print("glyohsave", self.name, self.stateColor)
        color = self.markColor
        self.lib.clear()
        self.markColor = color
        # print("glyohsave", self.name, self.stateColor)

    def getParent(self):
        return self.currentFont

    def setParent(self, currentFont):
        self.currentFont = currentFont

    @property
    def _RGlyph(self):
        return self._RFont[self.name]

    @property
    def flatComponents(self):
        return self._RGlyph.components

    def update(self):
        return #should readapt this fonction to the new format
        if self.type == 'atomicElement':
            return
        deepComponentToRemove = []
        glyphset = set(self.currentFont.glyphSet())
        # print("self._glyphVariations before update", self._deepComponents)
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
            index = 0
            for i, x in enumerate(self._axes):
                if x.name == self.selectedSourceAxis:
                    index = i
            return self._glyphVariations[index].deepComponents
        else:
            return self._deepComponents

    def _getSelectedElement(self):
        element = self._getElements()
        if element is None: return
        for index in self.selectedElement:
            yield element[index].transform
    
    # @compute
    def setRotationAngleToSelectedElements(self, rotation: int, append: bool = True):
        for selectedElement in self._getSelectedElement():
            if append:
                selectedElement.rotation += int(rotation)
            else:
                selectedElement.rotation = -int(rotation)

    # @compute
    def setPositionToSelectedElements(self, position: list):
        for selectedElement in self._getSelectedElement():
            selectedElement.x += position[0]
            selectedElement.y += position[1]

    # @compute
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

    # @compute
    def setTransformationCenterToSelectedElements(self, center):
        tx, ty = center
        for index in self.selectedElement:
            self._deepComponents[index]["transform"]["tcenterx"] = int((tx-self._deepComponents[index]["transform"]["x"])/self._deepComponents[index]["transform"]["scalex"])
            self._deepComponents[index]["transform"]["tcentery"] = int((ty-self._deepComponents[index]["transform"]["y"])/self._deepComponents[index]["transform"]["scaley"])
            for variation in self._glyphVariations:
                variation.deepComponents[index]["transform"]["tcenterx"] = int((tx-self._deepComponents[index]["transform"]["x"])/self._deepComponents[index]["transform"]["scalex"])
                variation.deepComponents[index]["transform"]["tcentery"] = int((ty-self._deepComponents[index]["transform"]["y"])/self._deepComponents[index]["transform"]["scaley"])
            # for variations in self._glyphVariations.values():
            #     variations[index].tcenterx = int((tx-self._deepComponents[index].x)/self._deepComponents[index].scalex)
            #     variations[index].tcentery = int((ty-self._deepComponents[index].y)/self._deepComponents[index].scaley)

    def pointIsInside(self, point, multipleSelection = False):
        px, py = point
        # preview = self.frozenPreview
        # if not preview:
        #     preview = self.preview({})
        for index, atomicInstanceGlyph in enumerate(self.preview({})):
            atomicInstanceGlyph.selectedContour = False
            if atomicInstanceGlyph.pointInside((px, py)):
                atomicInstanceGlyph.selectedContour = True
                if index not in self.selectedElement:
                    self.selectedElement.append(index)
                if not multipleSelection: return

    def selectionRectTouch(self, x: int, w: int, y: int, h: int):
        # preview = self.frozenPreview
        # if not preview:
        #     preview = self.preview({})
        for index, atomicInstanceGlyph in enumerate(self.preview({})):
            inside = False
            atomicInstanceGlyph.selectedContour = False
            for c in atomicInstanceGlyph:
                for p in c.points:
                    if p.x > x and p.x < w and p.y > y and p.y < h:
                        inside = True
                        atomicInstanceGlyph.selectedContour = True
            if inside:
                if index in self.selectedElement: continue
                self.selectedElement.append(index)

    def getDeepComponentMinMaxValue(self, axisName):
        if not self.selectedElement: return
        selectedAtomicElementName = self._deepComponents[self.selectedElement[0]].name
        for x in self.currentFont[selectedAtomicElementName ]._axes:
            if x.name == axisName:
                return x.minValue, x.maxValue
        # atomicElement = self.currentFont[selectedAtomicElementName ]._glyphVariations[axisName]
        # return atomicElement.minValue, atomicElement.maxValue



