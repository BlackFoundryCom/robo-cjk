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
from fontTools.varLib.models import VariationModel
# reload(interpolation)
# reload(decorators)
glyphUndo = decorators.glyphUndo
import copy
Glyph = glyph.Glyph
glyphAddRemoveUndo = decorators.glyphAddRemoveUndo

DeepComponentNamed = component.DeepComponentNamed
DeepComponents = component.DeepComponents
Axes = component.Axes
VariationGlyphs = component.VariationGlyphs
VariationGlyphsInfos = component.VariationGlyphsInfos

# Deprecated keys
# atomicElementsKey = 'robocjk.deepComponent.atomicElements'
glyphVariationsKey = 'robocjk.glyphVariationGlyphs'

# Actual keys
deepComponentsKey = 'robocjk.deepComponents'
axesKey = 'robocjk.axes'
variationGlyphsKey = 'robocjk.variationGlyphs'


class DeepComponent(Glyph):
    def __init__(self, name):
        super().__init__()
        self._deepComponents = DeepComponents()
        self._axes = Axes()
        self._glyphVariations = VariationGlyphs()
        self.selectedSourceAxis = None
        self.computedAtomicSelectedSourceInstances = []
        self.computedAtomicInstances = []
        self.selectedElement = []
        self.name = name
        self.type = "deepComponent"
        self.previewGlyph = []
        self.axisPreview = []
        # self.preview = glyphPreview.DeepComponentPreview(self)
        self._setStackUndo()
        self.save()

    def preview(self, position:dict={}, font = None, forceRefresh=True, axisPreview = False):
        if not self.redrawSelectedElement:
            if axisPreview and self.axisPreview:
                # print('DC has axisPreview', self.axisPreview)
                for e in self.axisPreview: yield e
                return
            elif not forceRefresh and self.previewGlyph and not axisPreview: 
                # print('DC has previewGlyph', self.previewGlyph)
                for e in self.previewGlyph: yield e
                return

        if not position:
            position = self.getLocation()

        locations = [{}]
        locations.extend([x["location"] for x in self._glyphVariations if x["on"]])
        model = VariationModel(locations)
        
        if self.selectedElement:
            masterDeepComponents = [x for i, x in enumerate(self._deepComponents) if i in self.selectedElement]
            axesDeepComponents = [[x for i, x in enumerate(variation.get("deepComponents")) if i in self.selectedElement] for variation in self._glyphVariations.getList() if variation.get("on")==1]
        else:
            masterDeepComponents = self._deepComponents
            axesDeepComponents = [variation.get("deepComponents") for variation in self._glyphVariations.getList() if variation.get("on")==1]
        result = []
        for i, deepComponent in enumerate(masterDeepComponents):
            variations = []
            for gv in axesDeepComponents:
                variations.append(gv[i])
            result.append(model.interpolateFromMasters(position, [deepComponent, *variations]))

        if axisPreview:
            if not self.selectedElement:
                preview = self.axisPreview = []
            if self.selectedElement:
                preview = self.axisPreview
        else:
            if not self.selectedElement:
                preview = self.previewGlyph = []
            if self.selectedElement:
                preview = self.previewGlyph

        if font is None:
            font = self.getParent()
        for i, dc in enumerate(result):
            name = dc.get("name")
            if not set([name]) & (font.staticAtomicElementSet()|font.staticDeepComponentSet()|font.staticCharacterGlyphSet()): continue
            g = font[name]
            position = dc.get("coord")
            
            if not self.selectedElement:
                resultGlyph = RGlyph()
                g = g.preview(position, font, forceRefresh=True)
                for c in g.glyph:
                    c.draw(resultGlyph.getPen())
                preview.append(self.ResultGlyph(resultGlyph, dc.get("transform")))
            elif self.selectedElement and not self.reinterpolate:
                preview[self.selectedElement[i]].transformation = dc.get("transform")
            else:
                resultGlyph = RGlyph()
                g = g.preview(position, font, forceRefresh=True)
                for c in g.glyph:
                    c.draw(resultGlyph.getPen())
                preview[self.selectedElement[i]].resultGlyph = resultGlyph   
                preview[self.selectedElement[i]].transformation = dc.get("transform")

        for resultGlyph in preview:
            yield resultGlyph

    @property
    def atomicElements(self):
        return self._deepComponents

    @property
    def glyphVariations(self):
        return self._glyphVariations
    
    def _initWithLib(self, lib=None):
        try:
            if lib:
                if variationGlyphsKey not in lib.keys():
                    deepComponents = lib[deepComponentsKey]
                    variationGlyphs = lib[glyphVariationsKey]
                else:
                    deepComponents = lib[deepComponentsKey]
                    variationGlyphs = lib[variationGlyphsKey]
                hasAxisKey = axesKey in lib.keys()
                axes = lib.get(axesKey)
            else:
                if variationGlyphsKey not in self._RGlyph.lib.keys():
                    deepComponents = self._RGlyph.lib[deepComponentsKey]
                    variationGlyphs = self._RGlyph.lib[glyphVariationsKey]
                else:
                    deepComponents = self._RGlyph.lib[deepComponentsKey]
                    variationGlyphs = self._RGlyph.lib[variationGlyphsKey]
                hasAxisKey = axesKey in self._RGlyph.lib.keys()
                axes = self._RGlyph.lib.get(axesKey)
            if hasAxisKey:
                self._deepComponents = DeepComponents(deepComponents)
                self._axes = Axes(axes)
                self._glyphVariations = VariationGlyphs(variationGlyphs)
            else:
                self._deepComponents = DeepComponents()
                self._deepComponents._init_with_old_format(deepComponents)
                self._axes = Axes()      
                self._axes._init_with_old_format(variationGlyphs)
                self._glyphVariations = VariationGlyphs()
                self._glyphVariations._init_with_old_format(variationGlyphs)
        except Exception as e:
            self._deepComponents = DeepComponents()
            self._axes = Axes()  
            self._glyphVariations = VariationGlyphs()

    def duplicateSelectedElements(self): # TODO
        element = self._getElements()
        if element is None: return
        for index in self.selectedElement:
            selectedElement = element[index]
            if selectedElement.get("name"):
                self.addAtomicElementNamed(selectedElement["name"], copy.deepcopy(selectedElement))
        #         self.selectedElement = [len(self._deepComponents)-1]
        self.redrawSelectedElement = True
        self.selectedElement = []

    def addGlyphVariation(self, newAxisName):
        self._axes.addAxis({"name":newAxisName, "minValue":0, "maxValue":1})
        self._glyphVariations.addVariation({"deepComponents":self._deepComponents, "location":{newAxisName:1}})

    def removeGlyphVariation(self, axisName):
        index = 0
        for i, x in enumerate(self._axes):
            if x.name == axisName:
                index = i
        self._glyphVariations.removeVariation(index)
        self._axes.removeAxis(index)

    def updateAtomicElementCoord(self, axisName, value):
        if self.selectedSourceAxis:
            index = 0
            print(self.selectedSourceAxis)
            for i, x in enumerate(self._glyphVariations):
                if x.sourceName == self.selectedSourceAxis:
                    index = i
            self._glyphVariations[i].deepComponents[self.selectedElement[0]].coord[axisName] = value
            # self._glyphVariations[self.selectedSourceAxis][self.selectedElement[0]].coord[axisName] = value
        else:
            self._deepComponents[self.selectedElement[0]].coord[axisName] = value
    
    @glyphAddRemoveUndo
    def addAtomicElementNamed(self, atomicElementName, items = False):
        if not items:
            d = DeepComponentNamed(atomicElementName)
            dcglyph = self.currentFont[atomicElementName]
            for i, axis in enumerate(dcglyph._axes):
                value = dcglyph._axes[i].minValue
                d.coord.add(axis.name, value)
        else:
            d = items
            d.name = atomicElementName

        self._deepComponents.addDeepComponent(d)
        if self._axes:
            self._glyphVariations.addDeepComponent(d)
        self.redrawSelectedElement = True
        self.selectedElement = []

        # self.preview.computeDeepComponentsPreview(update = False)
        # self.preview.computeDeepComponents(update = False)

    @glyphAddRemoveUndo
    def removeAtomicElementAtIndex(self):
        if not self.selectedElement: return
        self.removeDeepComponents(self.selectedElement)
        self.redrawSelectedElement = True
        self.selectedElement = []
        
    def addVariationToGlyph(self, name):
        if name in self._axes.names: return
        # if name in self._glyphVariations.axes: return
        self.addGlyphVariation(name)

        # self._glyphVariations.addVariation(name, self._deepComponents)

    def renameVariationAxis(self, oldName, newName):
        self._axes.renameAxis(oldName, newName)
        # for axis in self._axes:
        #     if axis.name == oldName:
        #         axis.name == newName
        self._glyphVariations.renameAxisInsideLocation(oldName, newName)

        # for variation in self._glyphVariations:
        #     if oldName in variation.location:
        #         variation.location[newName] = variation.location[oldName]
        #         del variation.location[oldName]
        # self._glyphVariations.addVariation(newName, self._glyphVariations[oldName])
        # self._glyphVariations.removeAxis(oldName)

    def removeVariationAxis(self, name):
        self.removeGlyphVariation(name)
        # self._glyphVariations.removeAxis(name)

    def save(self):
        color = self.markColor
        self.lib.clear()
        lib = RLib()

        # for variations in self._glyphVariations.values():
        #     variations.setAxisWidth(self.currentFont.defaultGlyphWidth)

        lib[deepComponentsKey] = self._deepComponents.getList()
        lib[axesKey] = self._axes.getList()
        lib[variationGlyphsKey] = self._glyphVariations.getList(exception=["layerName"])

        self.lib.update(lib)
        self.markColor = color
