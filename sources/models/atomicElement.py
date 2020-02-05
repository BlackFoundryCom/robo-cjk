from fontTools.ufoLib.glifLib import readGlyphFromString, writeGlyphToString
from mojo.roboFont import *
from imp import reload
from models import glyph
from utils import interpolation
import copy
reload(interpolation)
reload(glyph)
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