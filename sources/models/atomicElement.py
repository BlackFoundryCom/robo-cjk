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
from mojo.roboFont import *
from imp import reload
from models import glyph
from utils import interpolation, decorators
reload(decorators)
reload(interpolation)
reload(glyph)
glyphUndo = decorators.glyphUndo
import copy
Glyph = glyph.Glyph

glyphVariationsKey = 'robocjk.atomicElement.glyphVariations'

class AtomicElement(Glyph):
    def __init__(self, name):
        super().__init__()
        self._glyphVariations = {}
        self.name = name
        self.type = "atomicElement"
        self.save()

    @property
    def foreground(self):
        return self.currentFont._RFont[self.name].getLayer('foreground')
    
    @property
    def glyphVariations(self):
        return self._glyphVariations
    
    def _initWithLib(self):
        self._glyphVariations = dict(self._RGlyph.lib[glyphVariationsKey])

    def addGlyphVariation(self, newAxisName, newLayerName):
        self._glyphVariations[newAxisName] = newLayerName

        glyph = AtomicElement(self.name)
        txt = self.currentFont._RFont.getLayer(newLayerName)[self.name].dumpToGLIF()
        self.currentFont.insertGlyph(glyph, txt, newLayerName)

        for name in self.currentFont.deepComponentSet:
            g = self.currentFont[name]
            g.addVariationAxisToAtomicElementNamed(newAxisName, self.name)

    def removeGlyphVariation(self, axisName):
        del self._glyphVariations[axisName]
        for name in self.currentFont.deepComponentSet:
            g = self.currentFont[name]
            g.removeVariationAxisToAtomicElementNamed(axisName, self.name)

    def computeDeepComponentsPreview(self):
        layersInfos = {}
        for d in self.sourcesList:
            layer = self._glyphVariations[d['Axis']]
            value = d['PreviewValue']
            layersInfos[layer] = value

        self.preview = interpolation.deepolation(
            RGlyph(), 
            self.foreground, 
            layersInfos
            )

    def save(self):
        self.lib.clear()
        lib = RLib()
        lib[glyphVariationsKey] = self._glyphVariations
        self.lib.update(lib)