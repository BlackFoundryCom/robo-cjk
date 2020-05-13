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
from models import glyph, component
from utils import interpolation, decorators
reload(decorators)
reload(interpolation)
reload(glyph)
reload(component)
glyphUndo = decorators.glyphUndo
import copy
Glyph = glyph.Glyph
DictClass = component.DictClass

glyphVariationsKey = 'robocjk.atomicElement.glyphVariations'

class GlyphVariations(DictClass):
    
    def __init__(self, **kwargs):
        super().__init__()
        for k, v in kwargs.items():
            setattr(self, k, v)

    def addAxis(self, axisName: str, layerName: str):
        """
        Add new axis 
        """
        setattr(self, axisName, layerName)

    def removeAxis(self, axisName: str):
        """
        Remove a variation axis
        """
        if not hasattr(self, axisName):
            return
        delattr(self, axisName)
        
    @property
    def axes(self):
        return self.keys()
        
    @property
    def layers(self):
        return self.values()

class AtomicElement(Glyph):
    def __init__(self, name):
        super().__init__()
        self._glyphVariations = GlyphVariations()
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
        self._glyphVariations = GlyphVariations(**dict(self._RGlyph.lib[glyphVariationsKey]))

    def addGlyphVariation(self, newAxisName, newLayerName):
        self._glyphVariations.addAxis(newAxisName, newLayerName)

        glyph = AtomicElement(self.name)
        txt = self.currentFont._RFont.getLayer(newLayerName)[self.name].dumpToGLIF()
        self.currentFont.insertGlyph(glyph, txt, newLayerName)

        ################ DEPENDENCY WITH DEEPCOMPONENTS ################
        #                             |                                #
        #                             V                                #
        ################################################################

        for name in self.currentFont.deepComponentSet:
            g = self.currentFont[name]
            g.addVariationAxisToAtomicElementNamed(newAxisName, self.name)

    def removeGlyphVariation(self, axisName):
        # del self._glyphVariations[axisName]
        self._glyphVariations.removeAxis(axisName)

        ################ DEPENDENCY WITH DEEPCOMPONENTS ################
        #                             |                                #
        #                             V                                #
        ################################################################

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
        lib[glyphVariationsKey] = self._glyphVariations.__dict__
        self.lib.update(lib)