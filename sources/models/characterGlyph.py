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
from models import glyph, component
reload(glyph)
reload(component)
from utils import interpolation, decorators
reload(interpolation)
Glyph = glyph.Glyph
glyphAddRemoveUndo = decorators.glyphAddRemoveUndo
from models import deepComponent
reload(deepComponent)

DeepComponentNamed = component.DeepComponentNamed
DeepComponents = component.DeepComponents
VariationGlyphs = component.VariationGlyphs

import copy

# Deprecated keys
deepComponentsKeyOld = 'robocjk.characterGlyph.deepComponents'
glyphVariationsKey = 'robocjk.characterGlyph.glyphVariations'

# Actual keys
deepComponentsKey = 'robocjk.deepComponents'
variationGlyphsKey = 'robocjk.fontVariationGlyphs'

class CharacterGlyph(Glyph):
    def __init__(self, name):
        super().__init__()
        self._deepComponents = DeepComponents()
        self._glyphVariations = VariationGlyphs()
        self.selectedSourceAxis = None
        self.computedDeepComponents = []
        self.computedDeepComponentsVariation = []
        self.selectedElement = []
        self.name = name
        self.type = "characterGlyph"
        self.outlinesPreview = None

        lib = RLib()
        lib[deepComponentsKey] = copy.deepcopy(self._deepComponents)
        lib[glyphVariationsKey] = copy.deepcopy(self._glyphVariations)
        self.stackUndo_lib = [lib]
        self.indexStackUndo_lib = 0

        self.save()

    @property
    def foreground(self):
        return self.currentFont._RFont[self.name].getLayer('foreground')

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
                    deepComponents = lib[deepComponentsKeyOld]
                    glyphVariations = lib[glyphVariationsKey]
                else:
                    deepComponents = lib[deepComponentsKey]
                    glyphVariations = lib[variationGlyphsKey]
            else:
                if variationGlyphsKey not in self._RGlyph.lib.keys(): 
                    deepComponents = self._RGlyph.lib[deepComponentsKeyOld]
                    glyphVariations = self._RGlyph.lib[glyphVariationsKey]
                else:
                    deepComponents = self._RGlyph.lib[deepComponentsKey]
                    glyphVariations = self._RGlyph.lib[variationGlyphsKey]

            self._deepComponents = DeepComponents(deepComponents)      
            self._glyphVariations = VariationGlyphs(glyphVariations)
        except:
            self._deepComponents = DeepComponents()
            self._glyphVariations = VariationGlyphs()

    @property
    def selectedElementCoord(self) -> dict:
        index = self.selectedElement[0]
        if self.computedDeepComponents:
            return list(self.computedDeepComponents[index].values())[0][0]
        elif self.computedDeepComponentsVariation:
            return list(self.computedDeepComponentsVariation[index].values())[0][0]

    @property
    def atomicInstancesGlyphs(self) -> "Index, AtomicInstanceGlyph":
        if self.computedDeepComponentsVariation:
            elements = self.computedDeepComponentsVariation
        else:
            elements = self.computedDeepComponents

        for i, e in enumerate(elements):
            for dcCoord, l in e.values():
                for dcAtomicElements in l:
                    for atomicInstanceGlyph, _, _ in dcAtomicElements.values():
                        yield i, atomicInstanceGlyph

    def duplicateSelectedElements(self):
        for selectedElement in self._getSelectedElement():
            if selectedElement.get("name"):
                self.addDeepComponentNamed(selectedElement["name"], copy.deepcopy(selectedElement))

    def _getElements(self):
        if self.computedDeepComponents:
            return self._deepComponents
        elif self.computedDeepComponentsVariation:
            return self._glyphVariations[self.selectedSourceAxis]

    def updateDeepComponentCoord(self, nameAxis, value):
        if self.selectedSourceAxis is not None:
            self._glyphVariations[self.selectedSourceAxis][self.selectedElement[0]].coord[nameAxis] = value
        else:
            self._deepComponents[self.selectedElement[0]].coord[nameAxis]=value

    def removeVariationAxis(self, name):
        self._glyphVariations.removeAxis(name)

    @glyphAddRemoveUndo
    def addDeepComponentNamed(self, deepComponentName, items = False):
        if not items:
            d = DeepComponentNamed(deepComponentName)
            for axis in self.currentFont[deepComponentName]._glyphVariations.axes:
                d.coord.add(axis, 0)
        else:
            d = items
            d.name = deepComponentName

        self._deepComponents.addDeepComponent(d)
        self._glyphVariations.addDeepComponent(d)

        self.computeDeepComponentsPreview()
        self.computeDeepComponents()

    def computeDeepComponents(self, update = True):
        #### IN PREVIEW CLASS
        if update:
            self.update()
        self.computedDeepComponents = []
        self.computedDeepComponentsVariation = []

        if self.selectedSourceAxis is None:
            self.computedDeepComponents = self.generateCharacterGlyph(
                self, 
                preview=False, 
                update = False
                )
        else:
            self.computedDeepComponentsVariation = self.generateCharacterGlyphVariation(
                self.selectedSourceAxis,
                preview=False
                )

    def computeDeepComponentsPreview(self, sourcelist = [], update = True):
        if update:
            self.update()
        self.preview = []
        deepComponentsSelectedVariation = []

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

        for j, masterDeepComponentInstance in enumerate(outputCG):
            glyph = self.currentFont[masterDeepComponentInstance['name']]
            masterDeepComponent = glyph._deepComponents
            deepComponentVariations = glyph._glyphVariations
            deepComponentAxisInfos = masterDeepComponentInstance['coord']
        
            deepdeepolatedDeepComponent = interpolation.deepdeepolation(
                masterDeepComponent, 
                deepComponentVariations, 
                deepComponentAxisInfos
                )

            previewGlyph = deepComponent.DeepComponent("PreviewGlyph")
            previewGlyph._deepComponents = DeepComponents(deepdeepolatedDeepComponent)

            atomicInstancesPreview = self.generateDeepComponent(
                previewGlyph, 
                preview=True,
                update = False
                )

            for e in atomicInstancesPreview:
                for aeName, ae in e.items():
                    ae[0].scaleBy((masterDeepComponentInstance['scalex'], masterDeepComponentInstance['scaley']))
                    ae[0].moveBy((self._deepComponents[j]['x'], self._deepComponents[j]['y']))
                    ae[0].moveBy((masterDeepComponentInstance['x'], masterDeepComponentInstance['y']))
                    ae[0].rotateBy(masterDeepComponentInstance['rotation'])
                    # ae[0].round()
            deepComponentsSelectedVariation.append({self._deepComponents[j]['name']: (masterDeepComponentInstance['coord'], atomicInstancesPreview)})                

        if self.currentFont._RFont.lib.get('robocjk.fontVariations', ''):

            layersInfos = {}
            for d in sourcelist:
                layer = d['Axis']
                value = d['PreviewValue']
                if layer in self.currentFont._RFont.lib['robocjk.fontVariations']:
                    if len(self._RGlyph.getLayer(layer)):
                        layersInfos[layer] = value

            self.outlinesPreview = interpolation.deepolation(
                RGlyph(), 
                self.foreground, 
                layersInfos
                )

        self.preview = deepComponentsSelectedVariation

    def generateCharacterGlyphVariation(self, selectedSourceAxis, preview=True):
        #### IN PREVIEW CLASS
        ### CLEANING TODO ###
        _lib = {}
        cgdc = self._deepComponents
        deepComponentsSelectedVariation = []
        for characterGlyphAxisName, characterGlyphVariation in self._glyphVariations.items():
            _lib[characterGlyphAxisName] = characterGlyphVariation
            
            if characterGlyphAxisName == selectedSourceAxis:
                _lib[characterGlyphAxisName] = []
                
                for j, dc in enumerate(characterGlyphVariation):
                    # for index in self.selectedElement:
                    #     if index == j and self.sliderValue:
                    #         dc['coord'][self.sliderName] = float(self.sliderValue)
                
                    masterDeepComponent = self.currentFont[cgdc[j].name]._deepComponents
                    deepComponentVariations = self.currentFont[cgdc[j].name]._glyphVariations
                    deepComponentAxisInfos = {}

                    deepComponentAxisInfos = dc.coord

                    deepdeepolatedDeepComponent = interpolation.deepdeepolation(masterDeepComponent, deepComponentVariations, deepComponentAxisInfos)
                    previewGlyph = RGlyph()
                    previewGlyph._deepComponents = DeepComponents(deepdeepolatedDeepComponent)
            
                    atomicInstancesPreview = self.generateDeepComponent(previewGlyph, preview=True, update = False)
                    for e in atomicInstancesPreview:
                        for aeName, ae in e.items():
                            ae[0].scaleBy((dc['scalex'], dc['scaley']))
                            ae[0].moveBy((dc['x'], dc['y']))
                            ae[0].rotateBy(dc['rotation'])
                    deepComponentsSelectedVariation.append({cgdc[j]['name']: (dc['coord'], atomicInstancesPreview)})
                    
                    _lib[characterGlyphAxisName].append(dc)
                    
        self._glyphVariations = VariationGlyphs(_lib)
        return deepComponentsSelectedVariation

    def addCharacterGlyphNamedVariationToGlyph(self, name):
        if name in self._glyphVariations.axes: return
        self._glyphVariations.addAxis(name, self._deepComponents)

    @glyphAddRemoveUndo
    def removeDeepComponentAtIndexToGlyph(self):
        if not self.selectedElement: return
        self._deepComponents.removeDeepComponents(self.selectedElement)
        self._glyphVariations.removeDeepComponents(self.selectedElement)
        self.selectedElement = []

    def save(self):
        self.lib.clear()
        lib = RLib()

        for axis, variations in self._glyphVariations.items():
            variations.layerName = axis
            try:
                axisGlyph = self.currentFont._RFont.getLayer(variations.layerName)[self.name]
                variations.writeOutlines(axisGlyph)
                variations.setAxisWidth(axisGlyph.width)
            except:
                pass

        lib[deepComponentsKeyOld] = self._deepComponents.getList()
        lib[glyphVariationsKey] = self._glyphVariations.getDict()

        lib[deepComponentsKey] = self._deepComponents.getList()
        lib[variationGlyphsKey] = self._glyphVariations.getDict()
        self.lib.update(lib)