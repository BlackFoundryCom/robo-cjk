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
        self.name = name
        self.type = "atomicElement"
        self.preview = glyphPreview.AtomicElementPreview(self)
        self.save()

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
        self._glyphVariations.addAxis(newAxisName, layerName = newLayerName)

        glyph = AtomicElement(self.name)
        txt = self._RFont.getLayer(newLayerName)[self.name].dumpToGLIF()
        self.currentFont.insertGlyph(glyph, txt, newLayerName)

    def removeGlyphVariation(self, axisName):
        self._glyphVariations.removeAxis(axisName)

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
    
        # lib[glyphVariationsKey] = self._glyphVariations.getDict()
        lib[axesKey] = self._axes.getList()
        lib[variationGlyphsKey] = self._glyphVariations.getDict()

        self.lib.update(lib)
        self.markColor = color