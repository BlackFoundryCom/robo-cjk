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
from models import glyph
reload(glyph)
from models import component, glyphPreview
# reload(component)
# reload(glyphPreview)
from utils import interpolation, decorators
# reload(interpolation)
# reload(decorators)
glyphUndo = decorators.glyphUndo
import copy
Glyph = glyph.Glyph
glyphAddRemoveUndo = decorators.glyphAddRemoveUndo

DeepComponentNamed = component.DeepComponentNamed
DeepComponents = component.DeepComponents
VariationGlyphs = component.VariationGlyphs
VariationGlyphsInfos = component.VariationGlyphsInfos

# Deprecated keys
atomicElementsKey = 'robocjk.deepComponent.atomicElements'
glyphVariationsKey = 'robocjk.deepComponent.glyphVariations'

# Actual keys
deepComponentsKey = 'robocjk.deepComponents'
variationGlyphsKey = 'robocjk.glyphVariationGlyphs'


class DeepComponent(Glyph):
    def __init__(self, name):
        super().__init__()
        self._deepComponents = DeepComponents()
        self._glyphVariations = VariationGlyphs()
        self.selectedSourceAxis = None
        self.computedAtomicSelectedSourceInstances = []
        self.computedAtomicInstances = []
        self.selectedElement = []
        self.name = name
        self.type = "deepComponent"
        self.preview = glyphPreview.DeepComponentPreview(self)
        self._setStackUndo()
        self.save()

    @property
    def atomicElements(self):
        return self._deepComponents

    @property
    def glyphVariations(self):
        return self._glyphVariations
    
    def _initWithLib(self, lib=None):
        # print("_initWithLib", self.name, lib)
        try:
            if lib:
                if variationGlyphsKey not in lib.keys():
                    deepComponents = lib[atomicElementsKey]
                    variationGlyphs = lib[glyphVariationsKey]
                else:
                    deepComponents = lib[deepComponentsKey]
                    variationGlyphs = lib[variationGlyphsKey]
            else:
                if variationGlyphsKey not in self._RGlyph.lib.keys():
                    deepComponents = self._RGlyph.lib[atomicElementsKey]
                    variationGlyphs = self._RGlyph.lib[glyphVariationsKey]
                else:
                    deepComponents = self._RGlyph.lib[deepComponentsKey]
                    variationGlyphs = self._RGlyph.lib[variationGlyphsKey]
            self._deepComponents = DeepComponents(deepComponents)
            self._glyphVariations = VariationGlyphs(variationGlyphs)
        except:
            self._deepComponents = DeepComponents()
            self._glyphVariations = VariationGlyphs()

    def duplicateSelectedElements(self):
        for selectedElement in self._getSelectedElement():
            if selectedElement.get("name"):
                self.addAtomicElementNamed(selectedElement["name"], copy.deepcopy(selectedElement))

    def addGlyphVariation(self, newAxisName):
        self._glyphVariations.addAxis(newAxisName, self._deepComponents)

    def removeGlyphVariation(self, axisName):
        self._glyphVariations.removeAxis(axisName)

    def updateAtomicElementCoord(self, axisName, value):
        if self.selectedSourceAxis is not None:
            self._glyphVariations[self.selectedSourceAxis][self.selectedElement[0]].coord[axisName] = value
        else:
            self._deepComponents[self.selectedElement[0]].coord[axisName] = value
    
    @glyphAddRemoveUndo
    def addAtomicElementNamed(self, atomicElementName, items = False):
        if not items:
            d = DeepComponentNamed(atomicElementName)
            for axis in self.currentFont[atomicElementName]._glyphVariations.axes:
                d.coord.add(axis, 0)
        else:
            d = items
            d.name = atomicElementName

        self._deepComponents.addDeepComponent(d)
        self._glyphVariations.addDeepComponent(d)

        self.preview.computeDeepComponentsPreview(update = False)
        self.preview.computeDeepComponents(update = False)

    @glyphAddRemoveUndo
    def removeAtomicElementAtIndex(self):
        if not self.selectedElement: return
        self.removeDeepComponents(self.selectedElement)
        self.selectedElement = []
        
    def addVariationToGlyph(self, name):
        if name in self._glyphVariations.axes: return
        self._glyphVariations.addAxis(name, self._deepComponents)

    def renameVariationAxis(self, oldName, newName):
        self._glyphVariations.addAxis(newName, self._glyphVariations[oldName])
        self._glyphVariations.removeAxis(oldName)

    def removeVariationAxis(self, name):
        self._glyphVariations.removeAxis(name)

    def save(self):
        color = self.markColor
        self.lib.clear()
        lib = RLib()

        for variations in self._glyphVariations.values():
            variations.setAxisWidth(self.currentFont.defaultGlyphWidth)

        lib[deepComponentsKey] = self._deepComponents.getList()
        lib[variationGlyphsKey] = self._glyphVariations.getDict()

        self.lib.update(lib)
        self.markColor = color
