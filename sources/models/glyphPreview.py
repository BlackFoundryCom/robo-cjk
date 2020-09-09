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
# reload(component)
# reload(deepComponent)
from utils import interpolation, decorators
# reload(interpolation)
# reload(decorators)
glyphUndo = decorators.glyphUndo
import copy
import threading
import queue
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

    def __init__(self, 
            glyph:RGlyph = None, 
            scalex:float = 1.0, 
            scaley:float = 1.0, 
            x:int = 0, 
            y:int = 0, 
            rotation:float = 0.0, 
            coord:dict = {},
            rcenterx:int = 0,
            rcentery:int = 0):
        self.glyph = glyph
        self.scalex = scalex
        self.scaley = scaley
        self.x = x
        self.y = y
        self.rotation = rotation
        self.coord = coord
        self._transformedGlyph = None
        self.rcenterx = rcenterx * scalex
        self.rcentery = rcentery * scaley

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)

    @property
    def transformedGlyph(self):
        if self._transformedGlyph is None:
            self.getTransformedGlyph()
        return self._transformedGlyph

    def getTransformedGlyph(self, round:bool = False) -> RGlyph:
        glyph = self.glyph.copy()
        glyph.scaleBy((self.scalex, self.scaley))
        glyph.rotateBy(self.rotation, (self.rcenterx, self.rcentery))
        glyph.moveBy((self.x, self.y))
        if round:
            glyph.round()
        self._transformedGlyph = glyph
        return glyph

    def getFlatComponentGlyph(self, round:bool = False) -> FlatComponentInstance:
        glyph = self.glyph.copy()
        glyph.scaleBy((self.scalex, self.scaley), (self.rcenterx, self.rcentery))
        glyph.rotateBy(self.rotation, (self.rcenterx, self.rcentery))
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
        self._queue = queue.Queue()

    def _generateOutlinesPreview(self, sourceList:list = [], filtered:list = [], update:bool = True):
        layersInfos = {}
        if not len(self.glyph.foreground): return
        if not sourceList:
            sourceList = self.glyph.sourcesList

        for axis in sourceList:
            layer = self.glyph._glyphVariations[axis['Axis']].layerName
            value = axis['PreviewValue']
            if not filtered:
                layersInfos[layer] = value
            else:
                if axis['Axis'] in filtered:
                    if len(self.glyph._RGlyph.getLayer(axis['Axis'])) == len(self.glyph.foreground):
                        layersInfos[axis['Axis']] = value

        return interpolation.deepolation(
            RGlyph(), 
            self.glyph.foreground, 
            layersInfos
            )

    def _generateDeepComponent(self, glyph:RGlyph = None, preview:bool = True, update:bool = True):
        if update:
            glyph.update()

        axisPreview = []
        parentFont = self.glyph.getParent()
        for i, deepComponent in enumerate(glyph._deepComponents):
            # p_queue = queue.Queue()
            # threading.Thread(target = self._queue__generateDeepComponent, args = (p_queue, axisPreview, parentFont), daemon = True).start()
            # p_queue.put(deepComponent)
            try:
                layersInfos = {}
                dc = parentFont.get(deepComponent.name)
                deepComponentGlyph = dc.foreground
                variationGlyph = dc._glyphVariations

                # print(">>>>>>>", glyph._glyphVariations)
                
                for axisName, layerName in deepComponent.coord.items():
                    if variationGlyph[axisName] is None: continue
                    layersInfos[variationGlyph[axisName].layerName] = deepComponent.coord[axisName]

                axisPreview.append(self._getAtomicInstance(deepComponentGlyph, layersInfos, deepComponent, variationGlyph))
            except:
                continue

        return axisPreview

    # def _queue__generateDeepComponent(self, p_queue, axisPreview, parentFont):
    #     deepComponent = p_queue.get()
    #     try:
    #         layersInfos = {}
    #         dc = parentFont[deepComponent.name]
    #         deepComponentGlyph = dc.foreground
    #         variationGlyph = dc._glyphVariations
            
    #         for axisName, layerName in deepComponent.coord.items():
    #             if variationGlyph[axisName] is None: continue
    #             layersInfos[variationGlyph[axisName].layerName] = deepComponent.coord[axisName]

    #         axisPreview.append(self._getAtomicInstance(deepComponentGlyph, layersInfos, deepComponent, variationGlyph))
    #     except:
    #         pass
    #     p_queue.task_done()

    def _getPreviewGlyph(self, deepComponents = [], variationGlyph = {}, axisInfos = [], glyphName = "PreviewGlyph"):
        ddpolated = interpolation.deepdeepolation(deepComponents, variationGlyph, axisInfos)
        previewGlyph = deepComponent.DeepComponent(glyphName)
        previewGlyph._deepComponents = DeepComponents(ddpolated)

        for i, dc in enumerate(previewGlyph._deepComponents):
            dc.rcenterx = deepComponents[i].rcenterx
            dc.rcentery = deepComponents[i].rcentery
            for variation in previewGlyph._glyphVariations.values():
                variation[i].rcenterx = deepComponents[i].rcenterx
                variation[i].rcentery = deepComponents[i].rcentery

        return previewGlyph

    def _getAtomicInstance(self, deepComponentGlyph, layersInfos, deepComponent, coord):
        axisMinValue = deepComponent.get("axisMinValue", 0.)
        axisMaxValue = deepComponent.get("axisMaxValue", 1.)
        atomicInstance = AtomicInstance(
            glyph = interpolation.deepolation(RGlyph(), deepComponentGlyph, layersInfos, axisMinValue, axisMaxValue),
            # name = deepComponent.name,
            scalex = deepComponent.scalex,
            scaley = deepComponent.scaley,
            rotation = deepComponent.rotation,
            x = deepComponent.x, 
            y = deepComponent.y,
            coord = coord,
            rcenterx = deepComponent.rcenterx,
            rcentery = deepComponent.rcentery,
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
        # self._queue_DCP = queue.Queue()

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
        pen = previewGlyph.getPen()
        for atomicInstance in variationPreview:
            g = atomicInstance.getTransformedGlyph()
            g.draw(pen)
            # for c in atomicInstance.getTransformedGlyph():
            #     previewGlyph.appendContour(c)
        return previewGlyph

    def _generateDeepComponentVariation(self, axis:str = "",  preview:bool = True):
        axisPreview = []
        glyphParent = self.glyph.getParent()
        for i, variation in enumerate(self.glyph._glyphVariations[axis]):
            # dc_queue = queue.Queue()
            # threading.Thread(target = self._queue_generateDeepComponentVariation, args = (dc_queue, axis, axisPreview), daemon = True).start()
            # dc_queue.put((i, variation))
            _atomicElement = copy.deepcopy(variation)
            _atomicElement.coord.clear()
            
            masterAtomicElement = self.glyph._deepComponents[i]
            layersInfos = {}
            deepComponentGlyph = glyphParent.get(masterAtomicElement.name).foreground
            variationGlyph = self.glyph._glyphVariations 
    
            for atomicAxisName, layerVariation in glyphParent.get(masterAtomicElement.name)._glyphVariations.items():
                _atomicElement.coord[atomicAxisName] = 0
                if atomicAxisName in self.glyph._glyphVariations[axis][i].coord:
                    _atomicElement.coord[atomicAxisName] = self.glyph._glyphVariations[axis][i].coord[atomicAxisName]
                layersInfos[layerVariation.layerName] = _atomicElement.coord[atomicAxisName]

            axisPreview.append(self._getAtomicInstance(deepComponentGlyph, layersInfos, variation, _atomicElement.coord.__dict__))

        return axisPreview

    # def _queue_generateDeepComponentVariation(self, dc_queue, axis, axisPreview):
    #     i, variation = dc_queue.get()
    #     _atomicElement = copy.deepcopy(variation)
    #     _atomicElement.coord.clear()
        
    #     masterAtomicElement = self.glyph._deepComponents[i]
    #     layersInfos = {}
    #     deepComponentGlyph = self.glyph.getParent()[masterAtomicElement.name].foreground
    #     variationGlyph = self.glyph._glyphVariations 

    #     for atomicAxisName, layerVariation in self.glyph.getParent()[masterAtomicElement.name]._glyphVariations.items():
    #         _atomicElement.coord[atomicAxisName] = 0
    #         if atomicAxisName in self.glyph._glyphVariations[axis][i].coord:
    #             _atomicElement.coord[atomicAxisName] = self.glyph._glyphVariations[axis][i].coord[atomicAxisName]
    #         layersInfos[layerVariation.layerName] = _atomicElement.coord[atomicAxisName]

    #     axisPreview.append(self._getAtomicInstance(deepComponentGlyph, layersInfos, variation, _atomicElement.coord.__dict__))
    #     dc_queue.task_done()


class CharacterGlyphPreview(Preview):

    def __init__(self, glyph):
        super().__init__(glyph = glyph)
        # self._queue_CGP = queue.Queue()

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
        pen = glyph.getPen() 
        axisPreview = self._generateDeepComponent(previewGlyph, preview=True, update = False)
        for atomicInstance in axisPreview:
            g = atomicInstance.getTransformedGlyph()
            g.draw(pen)
            # for c in atomicInstance.getTransformedGlyph():
            #     glyph.appendContour(c)
        deepComponentInstance = DeepComponentInstance(
            axisPreview = axisPreview,
            # name = deepComponent.name,
            glyph = glyph,
            coord = deepComponent['coord'],
            scalex = deepComponent['scalex'],
            scaley = deepComponent['scaley'],
            x = deepComponent['x'],
            y = deepComponent['y'],
            rotation = deepComponent['rotation'],
            rcenterx = deepComponent['rcenterx'],
            rcentery = deepComponent['rcentery'],
            )
        return deepComponentInstance

    def _generateCharacterGlyphVariation(self, axis:str = "", preview:bool = True):
        axisPreview = []
        glyphParent = self.glyph.getParent()
        for i, deepComponent in enumerate(self.glyph._glyphVariations[axis]):
            deepComponentName = self.glyph._deepComponents[i].name
            masterDeepComponent = glyphParent.get(deepComponentName)._deepComponents
            deepComponentVariations = glyphParent.get(deepComponentName)._glyphVariations
            axisPreview.append(self._getDeepComponentInstance(self._getPreviewGlyph(masterDeepComponent, deepComponentVariations, deepComponent.coord), deepComponent))
    
        return axisPreview

    def _generateCharacterGlyph(self, glyph:RGlyph = None, preview:bool = True, update:bool = True):
        if update:
            glyph.update()

        axisPreview = []
        glyphParent = self.glyph.getParent()
        for i, deepComponent in enumerate(glyph._deepComponents):
            deepComponentGlyph = glyphParent.get(deepComponent.name)

            axisPreview.append(self._getDeepComponentInstance(self._getPreviewGlyph(deepComponentGlyph._deepComponents, deepComponentGlyph._glyphVariations, deepComponent.coord), deepComponent))

        return axisPreview

    def _generateCharacterGlyphPreview(self, sourcelist:list = [], update:bool = True):
        if update:
            self.glyph.update()

        glyphParent = self.glyph.getParent()
        variationPreview = []

        characterGlyphAxisInfos = {}

        _deepComponents = copy.deepcopy(self.glyph._deepComponents)
        _glyphVariations = copy.deepcopy(self.glyph._glyphVariations)

        for i, dc in enumerate(_deepComponents):
            variations = glyphParent.get(_deepComponents[i]["name"])._glyphVariations
            for coord, value in dc["coord"].items():
                dc["coord"][coord] = value/variations[coord].axisMaxValue
            for var in _glyphVariations.values():
                for coord, value in var.content.deepComponents[i].coord.items():
                    var.content.deepComponents[i].coord[coord] = value/variations[coord].axisMaxValue                    
        for i, UICharacterGlyphVariation in enumerate(sourcelist):
            characterGlyphAxisInfos[UICharacterGlyphVariation['Axis']] = UICharacterGlyphVariation['PreviewValue']

        if not characterGlyphAxisInfos:return

        outputCG = interpolation.deepdeepolation(
            _deepComponents, 
            _glyphVariations, 
            characterGlyphAxisInfos
            )

        for j, deepComponentInstance in enumerate(outputCG):
            try:
                glyph = glyphParent.get(deepComponentInstance['name'])
                deepComponentInstance["rcenterx"] = _deepComponents[j].rcenterx
                deepComponentInstance["rcentery"] = _deepComponents[j].rcentery
                variationPreview.append(self._getDeepComponentInstance(self._getPreviewGlyph(glyph._deepComponents,  glyph._glyphVariations,  deepComponentInstance['coord']), deepComponentInstance))                
            except Exception as e:
                raise e

        outlinesPreview = RGlyph()
        if glyphParent.fontVariations:
            outlinesPreview = self._generateOutlinesPreview(
                sourceList = sourcelist, 
                filtered = glyphParent.fontVariations
                )

        previewGlyph = RGlyph()
        pen = previewGlyph.getPen()
        previewGlyph.name = self.glyph.name
        for atomicInstance in variationPreview:
            g = atomicInstance.getTransformedGlyph()
            g.draw(pen)

        if outlinesPreview is not None:
            g = outlinesPreview
            g.draw(pen)
        return previewGlyph
