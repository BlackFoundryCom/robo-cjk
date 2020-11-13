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
from fontTools.ufoLib.glifLib import readGlyphFromString, writeGlyphToString
from fontTools.pens.recordingPen import RecordingPen
from mojo.roboFont import *
from imp import reload
from models import glyph, component, glyphPreview
from utils import interpolation, decorators
# reload(decorators)
# reload(interpolation)
# reload(glyph)
# reload(component)
# reload(glyphPreview)
glyphUndo = decorators.glyphUndo
import copy
Glyph = glyph.Glyph
DictClass = component.DictClass
VariationGlyphs = component.VariationGlyphs
Axes = component.Axes
from fontTools.varLib.models import VariationModel
# Deprecated key 
glyphVariationsKey = 'robocjk.glyphVariationGlyphs'

# Actual key
axesKey = 'robocjk.axes'
variationGlyphsKey = 'robocjk.variationGlyphs'

class AtomicElement(Glyph):
    def __init__(self, name):
        super().__init__()
        self._axes = Axes()
        self._glyphVariations = VariationGlyphs()
        self.selectedSourceAxis = None
        self.name = name
        self.type = "atomicElement"
        self.previewGlyph = []
        # self.preview = glyphPreview.AtomicElementPreview(self)
        self.save()

    def preview(self, position:dict={}, font=None, forceRefresh=True):
        if not forceRefresh and self.previewGlyph: 
            print('AE has previewGlyph', self.previewGlyph)
            return self.previewGlyph
        # if not position:
        #     position = self.getLocation()
        # print(position)
        position = self.normalizedValueToMinMaxValue(position, self)
        # print(position)

        locations = [{}]
        locations.extend([self.normalizedValueToMinMaxValue(x["location"], self) for x in self._glyphVariations.getList() if x["on"]])
        # print(locations,'\n')
        # locations.extend([{k:self.normalizedValueToMinMaxValue(v, self) for k, v in x["location"].items()} for x in self._glyphVariations.getList() if x["on"]])

        # self.frozenPreview = []
        self.previewGlyph = []
        if font is None:
            font = self.getParent()
        model = VariationModel(locations)
        layerGlyphs = []
        for variation in self._glyphVariations.getList():
            if not variation.get("on"): continue
            try:
                g = font._RFont.getLayer(variation["layerName"])[self.name]
            except Exception as e: 
                print(e)
                continue
            layerGlyphs.append(font._RFont.getLayer(variation["layerName"])[self.name])
        resultGlyph = model.interpolateFromMasters(position, [self._RGlyph, *layerGlyphs])
        # resultGlyph.removeOverlap()
        # self.frozenPreview.append(resultGlyph)
        self.previewGlyph.append(resultGlyph)
        return resultGlyph

    @property
    def foreground(self):
        return self._RFont[self.name].getLayer('foreground')
    
    @property
    def glyphVariations(self):
        return self._glyphVariations
    
    def _initWithLib(self):
        if variationGlyphsKey not in self._RGlyph.lib.keys():
            key = dict(self._RGlyph.lib[glyphVariationsKey])
            self._axes = Axes()
            self._axes._init_with_old_format(key)
            self._glyphVariations = VariationGlyphs()
            self._glyphVariations._init_with_old_format(key)
            # self._glyphVariations = VariationGlyphs(dict(self._RGlyph.lib[glyphVariationsKey]))
        else:
            if axesKey in self._RGlyph.lib:
                self._axes = Axes(self._RGlyph.lib[axesKey])
                self._glyphVariations = VariationGlyphs(self._RGlyph.lib[variationGlyphsKey])
            else:
                self._axes = Axes()
                self._axes._init_with_old_format(dict(self._RGlyph.lib[variationGlyphsKey]))
                self._glyphVariations = VariationGlyphs()
                self._glyphVariations._init_with_old_format(dict(self._RGlyph.lib[variationGlyphsKey]))

    def addGlyphVariation(self, newAxisName, newLayerName):
        self._axes.addAxis({"name":newAxisName, "minValue":0, "maxValue":1})
        variation = {"location":{newAxisName:1}, "layerName":newLayerName}
        self._glyphVariations.addVariation(variation)

        glyph = AtomicElement(self.name)
        txt = self._RFont.getLayer(newLayerName)[self.name].dumpToGLIF()
        self.currentFont.insertGlyph(glyph, txt, newLayerName)

    def removeGlyphVariation(self, axisName):
        index = 0
        for i, x in enumerate(self._axes):
            if x.name == axisName:
                index = i
        self._glyphVariations.removeVariation(index)
        self._axes.removeAxis(index)

    def save(self):
        color = self.markColor
        self.lib.clear()
        lib = RLib()
        
        # for variations in self._glyphVariations.values():
        #     layersNames = [x.name for x in self._RFont.layers]
        #     if variations.layerName not in layersNames:
        #         continue
        #     axisGlyph = self._RFont.getLayer(variations.layerName)[self.name]
        #     variations.writeOutlines(axisGlyph)
        #     variations.setAxisWidth(axisGlyph.width)
    
        # lib[glyphVariationsKey] = self._glyphVariations.getList()
        lib[axesKey] = self._axes.getList()
        lib[variationGlyphsKey] = self._glyphVariations.getList(exception=["sourceName"])

        self.lib.update(lib)
        self.markColor = color