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
from models import component, glyphPreview
reload(component)
reload(glyphPreview)
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


class DeepComponent(Glyph):
    def __init__(self, name):
        super().__init__()
        self._deepComponents = DeepComponents()
        self._glyphVariations = VariationGlyphs()
        self.selectedSourceAxis = None
        self.computedAtomicSelectedSourceInstances = []
        self.computedAtomicInstances = []
        self.selectedElement = []
        self.name = name
        self.type = "deepComponent"
        self.preview = glyphPreview.DeepComponentPreview(self)
        self.save()

    @property
    def atomicElements(self):
        return self._deepComponents

    @property
    def glyphVariations(self):
        return self._glyphVariations
    
    def _initWithLib(self):
        try:
            if variationGlyphsKey not in self._RGlyph.lib.keys():
                deepComponents = self._RGlyph.lib[atomicElementsKey]
                variationGlyphs = self._RGlyph.lib[glyphVariationsKey]
            else:
                deepComponents = self._RGlyph.lib[deepComponentsKey]
                variationGlyphs = self._RGlyph.lib[variationGlyphsKey]
            self._deepComponents = DeepComponents(deepComponents)
            self._glyphVariations = VariationGlyphs(variationGlyphs)
        except:
            self._deepComponents = DeepComponents()
            self._glyphVariations = VariationGlyphs()

    @property
    def atomicInstancesGlyphs(self) -> "Index, AtomicInstanceGlyph":
        if self.computedAtomicSelectedSourceInstances:
            elements = self.computedAtomicSelectedSourceInstances
        else:
            elements = self.computedAtomicInstances

        for i, d in enumerate(elements):
            for atomicInstanceGlyph, _, _ in d.values():
                yield i, atomicInstanceGlyph

    @property
    def selectedElementCoord(self) -> dict:
        index = self.selectedElement[0]
        if self.computedAtomicSelectedSourceInstances:
            return list(self.computedAtomicSelectedSourceInstances[index].values())[0][1][index]['coord']
        elif self.computedAtomicInstances:
            return list(self.computedAtomicInstances[index].values())[0][2]

    def duplicateSelectedElements(self):
        for selectedElement in self._getSelectedElement():
            if selectedElement.get("name"):
                self.addAtomicElementNamed(selectedElement["name"], copy.deepcopy(selectedElement))

    def _getElements(self):
        # if self.computedAtomicInstances:
        #     return self._deepComponents
        # elif self.computedAtomicSelectedSourceInstances:
        #     return self._glyphVariations[self.selectedSourceAxis]

        if self.selectedSourceAxis:
            return self._glyphVariations[self.selectedSourceAxis]
        else:
            return self._deepComponents

    def addGlyphVariation(self, newAxisName):
        self._glyphVariations.addAxis(newAxisName, self._deepComponents)

    def removeGlyphVariation(self, axisName):
        self._glyphVariations.removeAxis(axisName)

    def updateAtomicElementCoord(self, axisName, value):
        if self.selectedSourceAxis is not None:
            self._glyphVariations[self.selectedSourceAxis][self.selectedElement[0]]['coord'][axisName] = value
            self._glyphVariations
        else:
            self._deepComponents[self.selectedElement[0]]['coord'][axisName] = value

    def getAtomicElementMinMaxValue(self, axisName):
        if not self.selectedElement: return
        selectedAtomicElementName = self._deepComponents[self.selectedElement[0]].name
        atomicElement = self.currentFont[selectedAtomicElementName ]._glyphVariations[axisName]
        return atomicElement.minValue, atomicElement.maxValue

    def addAtomicElementNamed(self, atomicElementName, items = False):
        if not items:
            d = DeepComponentNamed(atomicElementName)
            for axis in self.currentFont[atomicElementName]._glyphVariations.axes:
                d.coord.add(axis, 0)
        else:
            d = items
            d.name = atomicElementName

        self._deepComponents.addDeepComponent(d)
        self._glyphVariations.addDeepComponent(d)

    def removeAtomicElementAtIndex(self):
        if not self.selectedElement: return
        self._glyphVariations.removeDeepComponents(self.selectedElement)
        self._deepComponents.removeDeepComponents(self.selectedElement)
        self.selectedElement = []
        
    def addVariationToGlyph(self, name):
        if name in self._glyphVariations.axes: return
        self._glyphVariations.addAxis(name, self._deepComponents)

    def renameVariationAxis(self, oldName, newName):
        self._glyphVariations.addAxis(newName, self._glyphVariations[oldName])
        self._glyphVariations.removeAxis(oldName)

    def removeVariationAxis(self, name):
        self._glyphVariations.removeAxis(name)

    # def computeDeepComponents(self, update = True):
    #     #### IN PREVIEW CLASS
    #     if update:
    #         self.update()
    #     self.computedAtomicSelectedSourceInstances = []
    #     self.computedAtomicInstances = []
        
    #     if self.selectedSourceAxis is None:
    #         self.computedAtomicInstances = self.generateDeepComponent(
    #             self, 
    #             preview=False,
    #             update = False
    #             )
    #     else:
    #         self.computedAtomicSelectedSourceInstances = self.generateDeepComponentVariation(
    #             self.selectedSourceAxis,
    #             preview=False,
    #             )

    # def computeDeepComponentsPreview(self, sourcelist = [], update = True):
    #     if update:
    #         self.update()
    #     self.preview = []

    #     if not sourcelist:
    #         sourcelist = self.sourcesList

    #     deepComponentAxisInfos = {}
    #     for UIDeepComponentVariation in sourcelist:
    #         deepComponentAxisInfos[UIDeepComponentVariation['Axis']] = UIDeepComponentVariation['PreviewValue']
    #     if not deepComponentAxisInfos: return

    #     deepdeepolatedDeepComponent = interpolation.deepdeepolation(
    #         self._deepComponents, 
    #         self._glyphVariations, 
    #         deepComponentAxisInfos
    #         )

    #     previewGlyph = DeepComponent("PreviewGlyph")
    #     previewGlyph._deepComponents = DeepComponents(deepdeepolatedDeepComponent)

    #     self.preview = self.generateDeepComponent(
    #         previewGlyph, 
    #         preview=True, update = False
    #         )

    # def generateDeepComponentVariation(self, selectedSourceAxis,  preview=True):
    #     #### IN PREVIEW CLASS
    #     ### CLEANING TODO ###
    #     _lib = {}
    #     atomicSelectedSourceInstances = []
    #     for deepComponentAxisName, deepComponentVariation in self._glyphVariations.items():
    #         _lib[deepComponentAxisName] = deepComponentVariation
            
    #         if deepComponentAxisName == selectedSourceAxis:
    #             _deepComponentVariation = VariationGlyphsInfos()
    #             for i, sourceAtomicElements in enumerate(deepComponentVariation):
    #                 _atomicElement = copy.deepcopy(sourceAtomicElements)
    #                 _atomicElement['coord'] = {}
                    
    #                 masterAtomicElement = self._deepComponents[i]
                     
    #                 layersInfos = {}
    #                 atomicVariations = self.currentFont[masterAtomicElement['name']]._glyphVariations
            
    #                 for atomicAxisName, layerInfos in atomicVariations.items():
    #                     if atomicAxisName in deepComponentVariation[i]['coord']:
    #                         _atomicElement['coord'][atomicAxisName] = deepComponentVariation[i]['coord'][atomicAxisName]
    #                     else:
    #                         _atomicElement['coord'][atomicAxisName] = 0
    #                     # if self.selectedElement == (i, masterAtomicElement['name']) and self.sliderName == atomicAxisName  and preview == False and self.sliderValue:
    #                     #     _atomicElement['coord'][atomicAxisName] = float(self.sliderValue)
    #                     layersInfos[layerInfos.layerName] = _atomicElement['coord'][atomicAxisName]
        
    #                 atomicElementGlyph = self.currentFont[masterAtomicElement['name']].foreground#getLayer('foreground')
    #                 atomicSelectedSourceInstanceGlyph = interpolation.deepolation(
    #                     RGlyph(), 
    #                     atomicElementGlyph, 
    #                     layersInfos
    #                     )

    #                 atomicSelectedSourceInstanceGlyph.scaleBy((sourceAtomicElements['scalex'], sourceAtomicElements['scaley']))
    #                 atomicSelectedSourceInstanceGlyph.rotateBy(sourceAtomicElements['rotation'])
    #                 atomicSelectedSourceInstanceGlyph.moveBy((sourceAtomicElements['x'], sourceAtomicElements['y']))
    #                 # atomicSelectedSourceInstanceGlyph.round()
    #                 atomicSelectedSourceInstances.append({masterAtomicElement['name']:(atomicSelectedSourceInstanceGlyph, deepComponentVariation, deepComponentVariation[i]['coord'])})
                
    #                 _deepComponentVariation.initContent(_atomicElement)   
                                 
    #             _lib[deepComponentAxisName] = _deepComponentVariation 
    #     # self._glyphVariations = VariationGlyphs(_lib)
    #     return atomicSelectedSourceInstances

    def save(self):
        self.lib.clear()
        lib = RLib()
        lib[atomicElementsKey] = self._deepComponents.getList()
        lib[glyphVariationsKey] = self._glyphVariations.getDict()

        for variations in self._glyphVariations.values():
            variations.setAxisWidth(self.currentFont.defaultGlyphWidth)

        lib[deepComponentsKey] = self._deepComponents.getList()
        lib[variationGlyphsKey] = self._glyphVariations.getDict()
        self.lib.update(lib)
