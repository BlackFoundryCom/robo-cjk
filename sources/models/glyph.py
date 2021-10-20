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
from utils import colors
# from fontTools.misc.transform import Transform

# reload(deepComponent)
DeepComponents = component.DeepComponents
VariationGlyphs = component.VariationGlyphs

# INPROGRESS = (1, 0, 0, 1)
# CHECKING1 = (1, .5, 0, 1)
# CHECKING2 = (1, 1, 0, 1)
# CHECKING3 = (0, .5, 1, 1)
# DONE = (0, 1, .5, 1)

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

    class ResultGlyph:

        def __init__(self, resultGlyph, transformation={}):
            self.resultGlyph = resultGlyph
            self._transformation = transformation

        @property
        def transformation(self):
            return self._transformation

        @transformation.setter
        def transformation(self, t):
            self._transformation = t

        @property
        def glyph(self):
            return interpolation._transformGlyph(self.resultGlyph.copy(), self.transformation)


    def __init__(self):
        super().__init__()
        self.type = None
        self._RFont = None
        self._status = 0
        # self.preview = None
        self.sourcesList = []
        self._designState = ""

        self.model = None
        self.deltas = None

        self.redrawSelectedElementSource = False
        self.redrawSelectedElementPreview = False
        self.reinterpolate = False

        self._glyphVariations = VariationGlyphs()
        self.previewLocationsStore = {}

    def _temp_set_Status_value(self):
        mark = self._RGlyph.markColor
        marked = False
        for i, color in enumerate(colors.colors):
            if mark == color.rgba:
                self._status = i
                for v in self._glyphVariations:
                    v.status = i
                marked = True

        if not marked:
            self._status = 0
            for v in self._glyphVariations:
                v.status = 0

    def createPreviewLocationsStore(self):
        # print('locations', self.locations)
        self.previewLocationsStore = {','.join([k+':'+str(v) for k,v in loc.items()]): list(self.preview(loc)) for loc in [{}]+self.locations}

    def updatePreviewLocationStore(self, loc):
        self.previewLocationsStore[','.join([k+':'+str(v) for k,v in loc.items()])] = list(self.preview(loc))

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
        if self.type != "atomicElement":
            if bool(self._glyphVariations):
                return True
            else:
                return bool(self._deepComponents)
        else:
            return bool(self._glyphVariations)

    def getLocation(self):
        loc = {}
        if self.selectedSourceAxis:
            for source in self._glyphVariations:
                if source.sourceName == self.selectedSourceAxis:
                    loc = source.location
        return loc

    def _locations(self):
        return [source.location for source in self._glyphVariations]

    @property
    def locations(self):
        return self._locations()

    def normalizedValue(self, v, minv, maxv, defaultValue):
        return (v-defaultValue)/(maxv-minv)

    def normalizedValueToMinMaxValue_clamped(self, loc, g):
        position = {}
        for k, v in loc.items():
            axis = g._axes.get(k)
            if axis is not None:
                if v > axis.maxValue:
                    v = axis.maxValue
                elif v < axis.minValue:
                    v = axis.minValue
                vx = self.normalizedValue(v, axis.minValue, axis.maxValue, axis.defaultValue)
                position[k] = vx
        return position

    def normalizedValueToMinMaxValue(self, loc, g):
        position = {}
        for k, v in loc.items():
            axis = g._axes.get(k)
            if axis is not None:
                position[k] = self.normalizedValue(v, axis.minValue, axis.maxValue, axis.defaultValue)
        return position

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
        if self.type == 'atomicElement':
            return
        deepComponentToRemove = []
        # glyphset = set(self.currentFont.glyphSet())
        glyphset = self.currentFont.staticCharacterGlyphSet() | self.currentFont.staticDeepComponentSet() | self.currentFont.staticAtomicElementSet()
        for index, deepComponent in enumerate(self._deepComponents):
            if set([deepComponent["name"]]) - glyphset:
                deepComponentToRemove.append(index)
            else:
                deepComponentGlyph = self.currentFont[deepComponent["name"]]
                deepComponentGlyphAxes = deepComponentGlyph._axes
                axesTodel = [x for x in deepComponent["coord"] if x not in deepComponentGlyphAxes.names]

                for oldAxis in axesTodel:
                    self._deepComponents[index].coord.remove(oldAxis)
                    for glyphVariation in self._glyphVariations:
                        glyphVariation.deepComponents[index].coord.remove(oldAxis)

                axesToadd = [x for x in deepComponentGlyphAxes if x.name not in deepComponent["coord"]]
                for axis in axesToadd:
                    self._deepComponents[index].coord.add(axis.name, axis.defaultValue)
                    for glyphVariation in self._glyphVariations:
                        glyphVariation.deepComponents[index].coord.add(axis.name, axis.defaultValue)

        #commenté juste par sécurité
        #self.removeDeepComponents(deepComponentToRemove)

    def renameDeepComponent(self, index, newName):
        currentCoords = list(self._deepComponents[index]["coord"].keys())
        currentCoordsValues = dict(self._deepComponents[index]["coord"])
        currentVariationCoordsValues = [dict(x["deepComponents"][index]["coord"]) for x in self._glyphVariations]
        currentTransformValues = dict(self._deepComponents[index]["transform"])
        currentVariationTransformValues = [dict(x["deepComponents"][index]["transform"]) for x in self._glyphVariations]
        dc = self.getParent()[newName]
        dcCoords = [x.name for x in dc._axes]
        print("currentCoords", currentCoords)
        print("dcCoords", dcCoords, "\n")
        if sorted(currentCoords) != sorted(dcCoords):
            if self.type == 'deepComponent':
                self.removeAtomicElementAtIndex([index])
                self.addAtomicElementNamed(newName)
            elif self.type == 'characterGlyph':
                self.removeDeepComponentAtIndexToGlyph([index])
                self.addDeepComponentNamed(newName)
            for k, v in self._deepComponents[-1]["coord"].items():
                if k in currentCoordsValues:
                    self._deepComponents[-1]["coord"][k] = currentCoordsValues[k]
            for k in self._deepComponents[-1]["transform"]:
                self._deepComponents[-1]["transform"][k] = currentTransformValues[k]

            for i, var in enumerate(self._glyphVariations):
                for k, v in var["deepComponents"][-1]["coord"].items():
                    if k in currentVariationCoordsValues[i]:
                        self._glyphVariations[i]["deepComponents"][-1]["coord"][k] = currentVariationCoordsValues[i][k]
            for i, var in enumerate(self._glyphVariations):
                for k in var["deepComponents"][-1]["transform"]:
                    self._glyphVariations[i]["deepComponents"][-1]["transform"][k] = currentVariationTransformValues[i][k]

            # for coord_name in self._deepComponents[-1]["coord"]:
            #     if coord_name in dcCoords:
            #         value = dc._axes[dcCoords.index(coord_name)]
            #         self._deepComponents[-1]["coord"][coord_name] = value
            return False
        else:
            self._deepComponents[index]["name"] = newName

            self.redrawSelectedElementSource = True
            self.redrawSelectedElementPreview = True
            return True

    def addAxis(self, axisName="", minValue="", maxValue="", defaultValue =""):
        self._axes.addAxis(dict(name = axisName, minValue = minValue, maxValue = maxValue, defaultValue = defaultValue))
        self._glyphVariations.addAxisToLocations(axisName = axisName, defaultValue=defaultValue)

    def removeAxis(self, index):
        axisName = self._axes[index].name
        self._axes.removeAxis(index)
        self._glyphVariations.removeAxis(axisName)
        self._glyphVariations.desactivateDoubleLocations(self._axes)

    def addSource(self, sourceName="", location={}, layerName = "", copyFrom = ""):

        deepComponents = []
        if self.type != "atomicElement":
            if not copyFrom or copyFrom == "master":
                dcs = self._deepComponents
            else:
                dcs = self._glyphVariations.getFromSourceName(copyFrom).deepComponents
            for deepcomponent in dcs:
                items = {}
                for k, v in deepcomponent.items():
                    if k != "name":
                        items[k] = v
                deepComponents.append(items)
        self._glyphVariations.addVariation(dict(sourceName=sourceName, location=location, layerName=layerName, deepComponents = deepComponents), self._axes)

    def removeSource(self, selectedAxisIndex):
        self._glyphVariations.removeVariation(selectedAxisIndex)

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
            for i, x in enumerate(self._glyphVariations):
                if x.sourceName == self.selectedSourceAxis:
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
        self.redrawSelectedElementSource = True
        self.redrawSelectedElementPreview = True

    # @compute
    def setPositionToSelectedElements(self, position: list):
        for selectedElement in self._getSelectedElement():
            selectedElement.x += position[0]
            selectedElement.y += position[1]
        # self.previewGlyph = []
        # self.redrawSelectedElementSource = True
        self.redrawSelectedElementSource = True
        self.redrawSelectedElementPreview = True

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
        self.redrawSelectedElementSource = True
        self.redrawSelectedElementPreview = True

    # @compute
    def setTransformationCenterToSelectedElements(self, center):
        tx, ty = center
        for index in self.selectedElement:
            self._deepComponents[index]["transform"]["tcenterx"] = int((tx-self._deepComponents[index]["transform"]["x"])/self._deepComponents[index]["transform"]["scalex"])
            self._deepComponents[index]["transform"]["tcentery"] = int((ty-self._deepComponents[index]["transform"]["y"])/self._deepComponents[index]["transform"]["scaley"])
            for variation in self._glyphVariations:
                variation.deepComponents[index]["transform"]["tcenterx"] = int((tx-self._deepComponents[index]["transform"]["x"])/self._deepComponents[index]["transform"]["scalex"])
                variation.deepComponents[index]["transform"]["tcentery"] = int((ty-self._deepComponents[index]["transform"]["y"])/self._deepComponents[index]["transform"]["scaley"])
        self.redrawSelectedElementSource = True
        self.redrawSelectedElementPreview = True

    def pointIsInside(self, point, multipleSelection = False):
        px, py = point
        # preview = self.frozenPreview
        # if not preview:
        #     preview = self.preview({})
        for index, atomicInstanceGlyph in enumerate(self.preview(forceRefresh=False, axisPreview = True)):
            # atomicInstanceGlyph = interpolation._transformGlyph(*atomicInstanceGlyph)
            # atomicInstanceGlyph.glyph.selectedContour = False
            if atomicInstanceGlyph.glyph.pointInside((px, py)):
                # atomicInstanceGlyph.glyph.selectedContour = True
                if index not in self.selectedElement:
                    self.selectedElement.append(index)
                if not multipleSelection: return

    def selectionRectTouch(self, x: int, w: int, y: int, h: int):
        # preview = self.frozenPreview
        # if not preview:
        #     preview = self.preview({})
        for index, atomicInstanceGlyph in enumerate(self.preview({},forceRefresh=False)):
            inside = False
            # atomicInstanceGlyph = interpolation._transformGlyph(*atomicInstanceGlyph)
            # atomicInstanceGlyph.glyph.selectedContour = False
            for c in atomicInstanceGlyph.glyph:
                for p in c.points:
                    if p.x > x and p.x < w and p.y > y and p.y < h:
                        inside = True
                        # atomicInstanceGlyph.glyph.selectedContour = True
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



