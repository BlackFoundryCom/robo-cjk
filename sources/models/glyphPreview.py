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
from models import component, deepComponent
reload(component)
reload(deepComponent)
from utils import interpolation, decorators
reload(interpolation)
reload(decorators)
glyphUndo = decorators.glyphUndo
import copy
Glyph = glyph.Glyph

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


class FlatComponentInstance:

    def __init__(self, glyph:RGlyph = None, x: int = 0, y:int = 0):
        self.glyph = glyph
        self.x = x
        self.y = y

class AtomicInstance:

    def __init__(self, glyph:RGlyph = None, scalex:float = 1.0, scaley:float = 1.0, x:int = 0, y:int = 0, rotation:float = 0.0, coord:dict = {}):
        self.glyph = glyph
        self.scalex = scalex
        self.scaley = scaley
        self.x = x
        self.y = y
        self.rotation = rotation
        self.coord = coord

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)

    def getTransformedGlyph(self, round:bool = False) -> RGlyph:
        glyph = self.glyph.copy()
        glyph.scaleBy((self.scalex, self.scaley))
        glyph.rotateBy(self.rotation)
        glyph.moveBy((self.x, self.y))
        if round:
            glyph.round()
        return glyph

    def getFlatComponentGlyph(self, round:bool = False) -> FlatComponentInstance:
        glyph = self.glyph.copy()
        glyph.scaleBy((self.scalex, self.scaley))
        glyph.rotateBy(self.rotation)
        if round:
            glyph.round()
        return FlatComponentInstance(glyph, self.x, self.y)

class DeepComponentInstance(AtomicInstance):

    def __init__(self, axisPreview:list = [], **kwargs):
        super().__init__(**kwargs)
        self.axisPreview = axisPreview

class Preview:

    def __init__(self, glyph):
        self.glyph = glyph
        self.axisPreview = []
        self.variationPreview = RGlyph() 

    def _generateOutlinesPreview(self, sourceList:list = [], filtered:list = [], update:bool = True):
        layersInfos = {}
        for axis in sourceList:
            layer = self.glyph._glyphVariations[axis['Axis']].layerName
            value = axis['PreviewValue']
            if not filtered:
                layersInfos[layer] = value
            else:
                if layer in filtered:
                    if len(self.glyph._RGlyph.getLayer(layer)):
                        layersInfos[layer] = value

        return interpolation.deepolation(
            RGlyph(), 
            self.glyph.foreground, 
            layersInfos
            )

    def _generateDeepComponent(self, glyph:RGlyph = None, preview:bool = True, update:bool = True):
        if update:
            glyph.update()

        axisPreview = []

        for i, deepComponent in enumerate(glyph._deepComponents):
            layersInfos = {}
            deepComponentGlyph = self.glyph.getParent()[deepComponent.name].foreground
            variationGlyph = self.glyph.getParent()[deepComponent.name]._glyphVariations
            
            for axisName, layerName in deepComponent.coord.items():
                layersInfos[variationGlyph[axisName].layerName] = deepComponent.coord[axisName]

            axisPreview.append(self._getAtomicInstance(deepComponentGlyph, layersInfos, deepComponent, variationGlyph))

        return axisPreview

    def _getPreviewGlyph(self, deepComponents = [], variationGlyph = {}, axisInfos = [], glyphName = "PreviewGlyph"):
        ddpolated = interpolation.deepdeepolation(deepComponents, variationGlyph, axisInfos)
        previewGlyph = deepComponent.DeepComponent(glyphName)
        previewGlyph._deepComponents = DeepComponents(ddpolated)
        return previewGlyph

    def _getAtomicInstance(self, deepComponentGlyph, layersInfos, deepComponent, coord):
        atomicInstance = AtomicInstance(
            glyph = interpolation.deepolation(RGlyph(), deepComponentGlyph, layersInfos),
            # name = deepComponent.name,
            scalex = deepComponent.scalex,
            scaley = deepComponent.scaley,
            rotation = deepComponent.rotation,
            x = deepComponent.x, 
            y = deepComponent.y,
            coord = coord
            )
        return atomicInstance

class AtomicElementPreview(Preview):

    def __init__(self, glyph):
        super().__init__(glyph = glyph)

    def computeDeepComponentsPreview(self, sourceList:list = [], filtered:list = [], update:bool = True):
        self.variationPreview = self._generateOutlinesPreview(sourceList = sourceList, filtered = filtered, update = update)

class DeepComponentPreview(Preview):

    def __init__(self, glyph):
        super().__init__(glyph = glyph)

    def computeDeepComponents(self, axis:str = "", update:bool = True):
        if axis or self.glyph.selectedSourceAxis:
            if not axis:
                axis = self.glyph.selectedSourceAxis
            self.axisPreview = self._generateDeepComponentVariation(axis = axis, preview=False)
        else:
            self.axisPreview = self._generateDeepComponent(glyph = self.glyph, preview = False, update = False)
    def computeDeepComponentsPreview(self, axes:list = [], update:bool = True):
        if not axes:
            axes = self.glyph.sourcesList
        self.variationPreview = self._generateDeepComponentsPreview(axes, update = update)

    def _generateDeepComponentsPreview(self, sourcelist:list = [], update:bool = True):
        if update:
            self.glyph.update()

        if not sourcelist:
            sourcelist = self.glyph.sourcesList

        deepComponentAxisInfos = {}
        for UIDeepComponentVariation in sourcelist:
            deepComponentAxisInfos[UIDeepComponentVariation['Axis']] = UIDeepComponentVariation['PreviewValue']
        if not deepComponentAxisInfos: return

        variationPreview = self._generateDeepComponent(
            self._getPreviewGlyph(self.glyph._deepComponents, self.glyph._glyphVariations, deepComponentAxisInfos), 
            preview=True, update = False)

        previewGlyph = RGlyph()
        for atomicInstance in variationPreview:
            for c in atomicInstance.getTransformedGlyph():
                previewGlyph.appendContour(c)
        return previewGlyph

    def _generateDeepComponentVariation(self, axis:str = "",  preview:bool = True):
        axisPreview = []

        for i, variation in enumerate(self.glyph._glyphVariations[axis]):
            _atomicElement = copy.deepcopy(variation)
            _atomicElement.coord.clear()
            
            masterAtomicElement = self.glyph._deepComponents[i]
            layersInfos = {}
            deepComponentGlyph = self.glyph.getParent()[masterAtomicElement.name].foreground
            variationGlyph = self.glyph._glyphVariations 
    
            for atomicAxisName, layerVariation in self.glyph.getParent()[masterAtomicElement.name]._glyphVariations.items():
                _atomicElement.coord[atomicAxisName] = 0
                if atomicAxisName in self.glyph._glyphVariations[axis][i].coord:
                    _atomicElement.coord[atomicAxisName] = self.glyph._glyphVariations[axis][i].coord[atomicAxisName]
                layersInfos[layerVariation.layerName] = _atomicElement.coord[atomicAxisName]

            axisPreview.append(self._getAtomicInstance(deepComponentGlyph, layersInfos, variation, _atomicElement.coord.__dict__))

        return axisPreview

class CharacterGlyphPreview(Preview):

    def __init__(self, glyph):
        super().__init__(glyph = glyph)

    def computeDeepComponents(self, axis:str = "", update:bool = True):
        """
        Generate a static instance
        """
        if axis or self.glyph.selectedSourceAxis:
            if not axis:
                axis = self.glyph.selectedSourceAxis
            self.axisPreview = self._generateCharacterGlyphVariation(axis = axis, preview=False)
        else:
            self.axisPreview = self._generateCharacterGlyph(glyph = self.glyph, preview = False, update = False)
            
    def computeDeepComponentsPreview(self, axes: list = [], update:bool = True):
        """
        Generate a variable instance with parameters
        """
        if not axes:
            axes = self.glyph.sourcesList
        self.variationPreview = self._generateCharacterGlyphPreview(axes, update = update)

    def _getDeepComponentInstance(self, previewGlyph, deepComponent):
        glyph = RGlyph()
        axisPreview = self._generateDeepComponent(previewGlyph, preview=True, update = False)
        for atomicInstance in axisPreview:
            for c in atomicInstance.getTransformedGlyph():
                glyph.appendContour(c)
        deepComponentInstance = DeepComponentInstance(
            axisPreview = axisPreview,
            # name = deepComponent.name,
            glyph = glyph,
            coord = deepComponent.coord,
            scalex = deepComponent.scalex,
            scaley = deepComponent.scaley,
            x = deepComponent.x,
            y = deepComponent.y,
            rotation = deepComponent.rotation,
            )
        return deepComponentInstance

    def _generateCharacterGlyphVariation(self, axis:str = "", preview:bool = True):
        axisPreview = []
                
        for i, deepComponent in enumerate(self.glyph._glyphVariations[axis]):
            deepComponentName = self.glyph._deepComponents[i].name
            masterDeepComponent = self.glyph.getParent()[deepComponentName]._deepComponents
            deepComponentVariations = self.glyph.getParent()[deepComponentName]._glyphVariations
            axisPreview.append(self._getDeepComponentInstance(self._getPreviewGlyph(masterDeepComponent, deepComponentVariations, deepComponent.coord), deepComponent))
    
        return axisPreview

    def _generateCharacterGlyph(self, glyph:RGlyph = None, preview:bool = True, update:bool = True):
        if update:
            glyph.update()

        axisPreview = []

        for i, deepComponent in enumerate(glyph._deepComponents):
            deepComponentGlyph = self.glyph.getParent()[deepComponent.name]

            axisPreview.append(self._getDeepComponentInstance(self._getPreviewGlyph(deepComponentGlyph._deepComponents, deepComponentGlyph._glyphVariations, deepComponent.coord), deepComponent))

        return axisPreview

    def _generateCharacterGlyphPreview(self, sourcelist:list = [], update:bool = True):
        if update:
            self.glyph.update()

        variationPreview = []

        characterGlyphAxisInfos = {}
        for UICharacterGlyphVariation in sourcelist:
            characterGlyphAxisInfos[UICharacterGlyphVariation['Axis']] = UICharacterGlyphVariation['PreviewValue']
        if not characterGlyphAxisInfos: return

        outputCG = interpolation.deepdeepdeepolation(
            self.glyph._deepComponents, 
            self.glyph._glyphVariations, 
            characterGlyphAxisInfos
            )

        for j, deepComponentInstance in enumerate(outputCG):
            glyph = self.glyph.getParent()[deepComponentInstance['name']]

            variationPreview.append(self._getDeepComponentInstance(self._getPreviewGlyph(glyph._deepComponents,  glyph._glyphVariations,  deepComponentInstance['coord']), self.glyph._deepComponents[j]))                

        outlinesPreview = []
        if self.glyph.getParent()._RFont.lib.get('robocjk.fontVariations', ''):

            outlinesPreview = self._generateOutlinesPreview(
                sourceList = sourcelist, 
                filtered = self.glyph.getParent()._RFont.lib['robocjk.fontVariations']
                )

        previewGlyph = RGlyph()
        for preview in [variationPreview, outlinesPreview]:
            for atomicInstance in preview:
                for c in atomicInstance.getTransformedGlyph():
                    previewGlyph.appendContour(c)
        return previewGlyph

