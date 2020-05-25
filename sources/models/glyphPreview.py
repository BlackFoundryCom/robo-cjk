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
from models import component
reload(component)
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
class Preview:

    def __init__(self, glyph):
        self.glyph = glyph
        self.atomicInstances = []
        self.preview = []
        self.outlinesPreview = None

    def computeGlyph(self, axis:str = "", update:bool = True):
        if not axis:
            if self.glyph.type == 'deepComponent':
                self.atomicInstances = self._generateDeepComponent(glyph = self.glyph, preview = False, update = False)
            elif self.glyph.type == 'characterGlyph':
                self.atomicInstances = self._generateCharacterGlyph(glyph = self.glyph, preview = False, update = False)
        else:
            if self.glyph.type == 'deepComponent':
                self.atomicInstances = self._generateDeepComponentVariation(axis = axis, preview=False)
            elif self.glyph.type == 'characterGlyph':
                self.atomicInstances = self._generateCharacterGlyphVariation(axis = axis, preview=False)

    def computeGlyphPreview(self, axes: list = []):
        if self.glyph.type == 'deepComponent':
            self.preview = self._generateDeepComponentsPreview(axes)
        elif self.glyph.type == 'characterGlyph':
            self.preview = self._generateCharacterGlyphPreview(axes)

    def _generateOutlinesPreview(self, sourceList: list = [], filtered:list = [], update:bool = True):
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

        self.outlinesPreview = interpolation.deepolation(
            RGlyph(), 
            self.glyph.foreground, 
            layersInfos
            )

    ################ DEEP COMPONENTS ################

    def _generateDeepComponentsPreview(self, sourcelist:list = [], update:bool = True):
        if update:
            self.update()

        if not sourcelist:
            sourcelist = self.glyph.sourcesList

        deepComponentAxisInfos = {}
        for UIDeepComponentVariation in sourcelist:
            deepComponentAxisInfos[UIDeepComponentVariation['Axis']] = UIDeepComponentVariation['PreviewValue']
        if not deepComponentAxisInfos: return

        deepdeepolatedDeepComponent = interpolation.deepdeepolation(
            self.glyph._deepComponents, 
            self.glyph._glyphVariations, 
            deepComponentAxisInfos
            )

        previewGlyph = DeepComponent("PreviewGlyph")
        previewGlyph._deepComponents = DeepComponents(deepdeepolatedDeepComponent)

        self.preview = self._generateDeepComponent(
            previewGlyph, 
            preview=True, update = False
            )

    def _generateDeepComponent(self, glyph:RGlyph = None, preview:bool = True, update:bool = True):
        if update:
            glyph.update()

        atomicInstances = []

        for i, deepComponent in enumerate(glyph._deepComponents):
            layersInfos = {}
            deepComponentGlyph = self.glyph.getParent()[deepComponent.name].foreground
            variationGlyph = self.glyph.getParent()[deepComponent.name]._glyphVariations
            
            for axisName, layerName in deepComponent.coord.items():
                layersInfos[variationGlyph[axisName].layerName] = deepComponent.coord[axisName]

            atomicInstances.append(self._getAtomicInstance(deepComponentGlyph, layersInfos, deepComponent, variationGlyph))

        return atomicInstances

    def _generateDeepComponentVariation(self, selectedAxis:str = "",  preview:bool = True):
        atomicInstances = []

        for variations in self.glyph._glyphVariations[selectedAxis]
            for i, variation in enumerate(variations):
                _atomicElement = copy.deepcopy(variation)
                _atomicElement.coord.clear()
                
                masterAtomicElement = self.glyph._deepComponents[i]
                layersInfos = {}
                deepComponentGlyph = self.glyph.getParent()[masterAtomicElement.name].foreground
                variationGlyph = self.glyph._glyphVariations 
        
                for atomicAxisName, layerVariation in self.glyph.getParent()[masterAtomicElement.name]._glyphVariations.items():
                    _atomicElement.coord[atomicAxisName] = 0
                    if atomicAxisName in variations.content.deepComponents[i].coord:
                        _atomicElement.coord[atomicAxisName] = variations.content.deepComponents[i].coord[atomicAxisName]
                        
                    layersInfos[layerVariation.layerName] = _atomicElement.coord[atomicAxisName]
    
                atomicInstances.append(self._getAtomicInstance(deepComponentGlyph, layersInfos, variation.content.deepComponents, variationGlyph))

        return atomicInstances

    ################ CHARACTER GLYPHS ################

    def _generateCharacterGlyphVariation(self, selectedAxis:str = "", preview:bool = True):
        atomicInstances = []
                
        for variations in self.glyph._glyphVariations[selectedAxis]
            for i, variation in enumerate(variations):
                deepComponentName = self.glyph._deepComponents[i].name
                masterDeepComponent = self.glyph.getParent()[deepComponentName]._deepComponents
                deepComponentVariations = self.glyph.getParent()[deepComponentName]._glyphVariations

                deepdeepolatedDeepComponent = interpolation.deepdeepolation(masterDeepComponent, deepComponentVariations, variation.coord)
                previewGlyph = RGlyph()
                previewGlyph._deepComponents = DeepComponents(deepdeepolatedDeepComponent)

                atomicInstances.append(self._getDeepComponentInstance(previewGlyph, variation))
    
        return atomicInstances

    def _generateCharacterGlyph(self, glyph:RGlyph = None, preview:bool = True, update:bool = True):
        if update:
            glyph.update()

        atomicInstances = []

        for i, deepComponent in enumerate(glyph._deepComponents):
            deepComponentGlyph = self.glyph.getParent()[deepComponent.name]

            deepdeepolatedDeepComponent = interpolation.deepdeepolation(
                deepComponentGlyph._deepComponentsq, 
                deepComponentGlyph._glyphVariations, 
                deepComponent.coord
                )
            previewGlyph = deepComponent.DeepComponent("PreviewGlyph")
            previewGlyph._deepComponents = deepdeepolatedDeepComponent

            atomicInstances.append(self._getDeepComponentInstance(previewGlyph, deepComponent))

        return atomicInstances

    def _generateCharacterGlyphPreview(self, sourcelist:list = [], update:bool = True):
        if update:
            self.glyph.update()

        self.preview = []

        if not sourcelist:
            sourcelist = self.sourcesList

        characterGlyphAxisInfos = {}
        for UICharacterGlyphVariation in sourcelist:
            characterGlyphAxisInfos[UICharacterGlyphVariation['Axis']] = UICharacterGlyphVariation['PreviewValue']
        if not characterGlyphAxisInfos: return

        outputCG = interpolation.deepdeepdeepolation(
            self._deepComponents, 
            self._glyphVariations, 
            characterGlyphAxisInfos
            )

        for j, deepComponentInstance in enumerate(outputCG):
            glyph = self.currentFont[deepComponentInstance['name']]
        
            deepdeepolatedDeepComponent = interpolation.deepdeepolation(
                glyph._deepComponents, 
                glyph._glyphVariations, 
                deepComponentInstance['coord']
                )

            previewGlyph = deepComponent.DeepComponent("PreviewGlyph")
            previewGlyph._deepComponents = DeepComponents(deepdeepolatedDeepComponent)

            self.preview.append(self._getDeepComponentInstance(previewGlyph, deepComponentInstance))                

        if self.glyph.getParent()._RFont.lib.get('robocjk.fontVariations', ''):

            self._generateOutlinesPreview(
                sourcelist = sourcelist, 
                filtered = self.glyph.getParent()._RFont.lib['robocjk.fontVariations']
                )

    def _getAtomicInstance(self, deepComponentGlyph, layersInfos, deepComponent, variationGlyph):
        atomicInstance = AtomicInstance(
            glyph = interpolation.deepolation(RGlyph(), deepComponentGlyph, layersInfos),
            name = deepComponent.name,
            scalex = deepComponent.scalex,
            scaley = deepComponent.scaley,
            rotation = deepComponent.rotation,
            x = deepComponent.x, 
            y = deepComponent.y,
            variationGlyph = variationGlyph
            )
        return atomicInstance

    def _getDeepComponentInstance(self, previewGlyph, deepComponent):
        deepComponentInstance = DeepComponentInstance(
            atomicInstances = self._generateDeepComponent(previewGlyph, preview=True, update = False),
            name = deepComponent.name,
            variationGlyph = deepComponent.coord,
            scalex = deepComponent.scalex,
            scaley = deepComponent.scaley,
            x = deepComponent.x,
            y = deepComponent.y,
            rotation = deepComponent.rotation,
            )
        return deepComponentInstance

class AtomicInstance:

    def __init__(self, 
            glyph:RGlyph = None, 
            name:str = "", 
            scalex:float = 0.0,
            scaley:float = 0.0, 
            rotation:int = 0, 
            x:float = 0.0,
            y:float = 0.0,
            variationGlyph:dict = {}):
        self.glyph = glyph
        self.name = name
        self.scalex = scalex
        self.scaley = scaley
        self.rotation = rotation
        self.x = x
        self.y = y
        self.variationGlyph = variationGlyph

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)

class DeepComponentInstance(AtomicInstance):

    def __init__(self, atomicInstance:list = [], **kwargs):
        super().__init__(**kwargs)
        self.atomicInstances = atomicInstance