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
from models import glyph, component, glyphPreview
# reload(glyph)
# reload(component)
# reload(glyphPreview)
from utils import interpolation, decorators
# reload(interpolation)
Glyph = glyph.Glyph
glyphAddRemoveUndo = decorators.glyphAddRemoveUndo
from models import deepComponent
# reload(deepComponent)

DeepComponentNamed = component.DeepComponentNamed
DeepComponents = component.DeepComponents
Axes = component.Axes
VariationGlyphs = component.VariationGlyphs

import copy
from fontTools.varLib.models import VariationModel

# Deprecated keys
# deepComponentsKeyOld = 'robocjk.characterGlyph.deepComponents'
glyphVariationsKey = 'robocjk.fontVariationGlyphs'

# Actual keys
deepComponentsKey = 'robocjk.deepComponents'
axesKey = 'robocjk.axes'
variationGlyphsKey = 'robocjk.variationGlyphs'

class RCJKGlyph(RGlyph):

    def __init__(self, **kwargs):
        super().__init__()
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.selectedContour = False

class CharacterGlyph(Glyph):

    
    def __init__(self, name):
        super().__init__()
        self._deepComponents = DeepComponents()
        self._axes = Axes()
        self._glyphVariations = VariationGlyphs()
        self.selectedSourceAxis = None
        self.computedDeepComponents = []
        self.computedDeepComponentsVariation = []
        self.selectedElement = []
        self.name = name
        self.type = "characterGlyph"
        self.outlinesPreview = None
        # self.preview = glyphPreview
        # self.preview = glyphPreview.CharacterGlyphPreview(self)

        # lib = RLib()
        # lib[deepComponentsKey] = copy.deepcopy(self._deepComponents)
        # lib[glyphVariationsKey] = copy.deepcopy(self._glyphVariations)
        # self.stackUndo_lib = [lib]
        # self.indexStackUndo_lib = 0
        self._setStackUndo()
        self.save()

    def preview(self, position:dict={}, font = None):
        if not position:
            position = self.getLocation()
        position = self.normalizedValueToMinMaxValue(position)
        locations = [{}]
        locations.extend([x["location"] for x in self._glyphVariations])

        model = VariationModel(locations)
        masterDeepComponents = self._deepComponents
        axesDeepComponents = [variation.get("deepComponents") for variation in self._glyphVariations.getList() if variation.get("on")]

        result = []
        for i, deepComponent in enumerate(masterDeepComponents):
            variations = []
            for gv in axesDeepComponents:
                variations.append(gv[i])
            result.append(model.interpolateFromMasters(position, [deepComponent, *variations]))

        # resultGlyph = RGlyph()
        # self.frozenPreview = []
        if font is None:
            font = self.getParent()
        for i, dc in enumerate(result):
            name = dc.get("name")
            pos = dc.get("coord")
            resultGlyph = RCJKGlyph(**dc.get("transform"))
            if not set([name]) & (font.staticAtomicElementSet()|font.staticDeepComponentSet()|font.staticCharacterGlyphSet()): continue
            g = font[name].preview(pos, font)
            for c in g:
                c.draw(resultGlyph.getPen())
            self._transformGlyph(resultGlyph, dc.get("transform"))
            # g.draw(resultGlyph.getPen())
            # self.frozenPreview.append(resultGlyph)
            yield resultGlyph

        if len(self._RGlyph):
            layerGlyphs = []
            layerNames = self._axes.names
            for layerName in layerNames:
                try:
                    g = font._RFont.getLayer(layerName)[self.name]
                except Exception as e: 
                    print(e)
                    continue
                layerGlyphs.append(g)
            if len(layerGlyphs):
                resultGlyph = model.interpolateFromMasters(position, [self._RGlyph, *layerGlyphs])
                yield resultGlyph
            # g.draw(resultGlyph.getPen())

        # return resultGlyph

    @property
    def foreground(self):
        return self._RFont[self.name].getLayer('foreground')

    @property
    def deepComponents(self):
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
        except:
            self._deepComponents = DeepComponents()
            self._axes = Axes()   
            self._glyphVariations = VariationGlyphs()

    def duplicateSelectedElements(self): # TODO
        # for selectedElement in self._getSelectedElement():
        element = self._getElements()
        if element is None: return
        for index in self.selectedElement:
            selectedElement = element[index]
            if selectedElement.get("name"):
                self.addDeepComponentNamed(selectedElement["name"], copy.deepcopy(selectedElement))

    def updateDeepComponentCoord(self, nameAxis, value):
        if self.selectedSourceAxis:
            index = 0
            for i, x in enumerate(self._axes):
                if x.name == self.selectedSourceAxis:
                    index = i
            self._glyphVariations[i].deepComponents[self.selectedElement[0]].coord[nameAxis] = value
            # self._glyphVariations[self.selectedSourceAxis][self.selectedElement[0]].coord[nameAxis] = value
        else:
            self._deepComponents[self.selectedElement[0]].coord[nameAxis]=value

    def removeVariationAxis(self, name):
        index = 0
        for i, x in enumerate(self._axes):
            if x.name == name:
                index = i
        self._glyphVariations.removeAxis(index)
        self._axes.removeAxis(index)

    @glyphAddRemoveUndo
    def addDeepComponentNamed(self, deepComponentName, items = False):
        if not items:
            d = DeepComponentNamed(deepComponentName)
            dcglyph = self.currentFont[deepComponentName]
            for i, axis in enumerate(dcglyph._axes):
                value = dcglyph._axes[i].minValue
                d.coord.add(axis.name, value)
        else:
            d = items
            d.name = deepComponentName

        self._deepComponents.addDeepComponent(d)
        if self._axes:
            self._glyphVariations.addDeepComponent(d)

        # self.preview.computeDeepComponentsPreview(update = False)
        # self.preview.computeDeepComponents(update = False)

        # font = self.getParent()
        # glyph = font[self.name]
        # font.writeGlif(glyph)


    def addCharacterGlyphNamedVariationToGlyph(self, name):
        if name in self._axes: return
        self._axes.addAxis({"name":name, "minValue":0, "maxValue":1})
        self._glyphVariations.addVariation({"deepComponents":self._deepComponents, "location":{name:1}})

    @glyphAddRemoveUndo
    def removeDeepComponentAtIndexToGlyph(self):
        if not self.selectedElement: return
        self.removeDeepComponents(self.selectedElement)
        self.selectedElement = []

    def save(self):
        color = self.markColor
        self.lib.clear()
        lib = RLib()

        # for axis, variations in self._glyphVariations.items():
        #     variations.layerName = axis
        #     try:
        #         axisGlyph = self._RFont.getLayer(variations.layerName)[self.name]
        #         variations.writeOutlines(axisGlyph)
        #         variations.setAxisWidth(axisGlyph.width)
        #     except:
        #         pass

        # lib[deepComponentsKeyOld] = self._deepComponents.getList()
        # lib[glyphVariationsKey] = self._glyphVariations.getList()

        lib[deepComponentsKey] = self._deepComponents.getList()
        lib[axesKey] = self._axes.getList()
        lib[variationGlyphsKey] = self._glyphVariations.getList()
        self.lib.update(lib)
        self.markColor = color