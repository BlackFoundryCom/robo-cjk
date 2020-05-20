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

# Deprecated keys
atomicElementsKey = 'robocjk.deepComponent.atomicElements'
glyphVariationsKey = 'robocjk.deepComponent.glyphVariations'

# Actual keys
deepComponentsKey = 'robocjk.deepComponents'
variationGlyphsKey = 'robocjk.variationGlyphs'


class DeepComponent(Glyph):
    def __init__(self, name):
        super().__init__()
        self._atomicElements = DeepComponents()
        self._glyphVariations = VariationGlyphs()
        self.selectedSourceAxis = None
        self.computedAtomicSelectedSourceInstances = []
        self.computedAtomicInstances = []
        self.selectedElement = []
        self.name = name
        self.type = "deepComponent"
        self.save()

    @property
    def atomicElements(self):
        return self._atomicElements

    @property
    def glyphVariations(self):
        return self._glyphVariations
    
    def _initWithLib(self):
        self._atomicElements = DeepComponents(self._RGlyph.lib[atomicElementsKey])
        self._glyphVariations = VariationGlyphs(self._RGlyph.lib[glyphVariationsKey])

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
        if self.computedAtomicInstances:
            return self._atomicElements
        elif self.computedAtomicSelectedSourceInstances:
            return self._glyphVariations[self.selectedSourceAxis]


    def addGlyphVariation(self, newAxisName):
        self._glyphVariations.addAxis(newAxisName, self._atomicElements)

        ################ DEPENDENCY WITH CHARACTERGLYPH ################
        #                             |                                #
        #                             V                                #
        ################################################################
        for name in self.currentFont.characterGlyphSet:
            g = self.currentFont[name]
            g.addVariationAxisToDeepComponentNamed(newAxisName, self.name)

    def removeGlyphVariation(self, axisName):
        self._glyphVariations.removeAxis(axisName)

        ################ DEPENDENCY WITH CHARACTERGLYPH ################
        #                             |                                #
        #                             V                                #
        ################################################################
        for name in self.currentFont.characterGlyphSet:
            g = self.currentFont[name]
            g.removeVariationAxisToDeepComponentNamed(axisName, self.name)

    def updateAtomicElementCoord(self, axisName, value):
        if self.selectedSourceAxis is not None:
            self._glyphVariations[self.selectedSourceAxis][self.selectedElement[0]]['coord'][axisName] = value
            self._glyphVariations
        else:
            self._atomicElements[self.selectedElement[0]]['coord'][axisName] = value

    def getAtomicElementMinMaxValue(self, axisName):
        if not self.selectedElement: return
        selectedAtomicElementName = self._atomicElements[self.selectedElement[0]].name
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

        self._atomicElements.addComponent(d)
        self._glyphVariations.addComponent(d)

    def removeAtomicElementAtIndex(self):
        if not self.selectedElement: return
        self._glyphVariations.removeComponents(self.selectedElement)
        self._atomicElements.removeComponents(self.selectedElement)
        self.selectedElement = []
        
    def addVariationToGlyph(self, name):
        if name in self._glyphVariations.axes: return
        self._glyphVariations.addAxis(name, self._atomicElements)

        ################ DEPENDENCY WITH CHARACTERGLYPH ################
        #                             |                                #
        #                             V                                #
        ################################################################
        for glyphname in self.currentFont.characterGlyphSet:
            g2 = self.currentFont[glyphname]
            for d in g2._deepComponents:
                if d["name"] != self.name: continue
                d['coord'][name] = 0

    def renameVariationAxis(self, oldName, newName):
        self._glyphVariations.addAxis(newName, self._glyphVariations[oldName])
        self._glyphVariations.removeAxis(oldName)

        ################ DEPENDENCY WITH CHARACTERGLYPH ################
        #                             |                                #
        #                             V                                #
        ################################################################
        def _rename(d, oldName, newName):
            if oldName not in d['coord']: return
            v = copy.deepcopy(d['coord'][oldName])
            del d['coord'][oldName]
            d['coord'][newName] = v

        for glyphname in self.currentFont.characterGlyphSet:
            g2 = self.currentFont[glyphname]

            for i, d in enumerate(g2._deepComponents):
                if d["name"] != self.name: continue
                print(glyphname)
                _rename(d, oldName, newName)
                for e in g2._glyphVariations.values():
                    _rename(e[i], oldName, newName)

    def removeVariationAxis(self, name):
        self._glyphVariations.removeAxis(name)

        ################ DEPENDENCY WITH CHARACTERGLYPH ################
        #                             |                                #
        #                             V                                #
        ################################################################
        for glyphname in self.currentFont.characterGlyphSet:
            g2 = self.currentFont[glyphname]

            def _remove(d, name):
                if name in d['coord']:
                    del d['coord'][name]

            for i, d in enumerate(g2._deepComponents):
                if d["name"] != self.name: continue
                _remove(d, name)
                for e in g2._glyphVariations.values():
                    _remove(e[i], name)


    ################ DEPENDENCY WITH ATOMIC ELEMENT ################
    #                             |                                #
    #                             V                                #
    ################################################################
    def addVariationAxisToAtomicElementNamed(self, axisName, atomicElementName):
        for d in self._atomicElements:
            if atomicElementName == d['name']:
                d['coord'][axisName] = 0

        for gvAxisName, l in self._glyphVariations.items():
            for i, d in enumerate(l):
                if atomicElementName == self._atomicElements[i]['name']:
                    d['coord'][axisName] = 0
    
    ################ DEPENDENCY WITH ATOMIC ELEMENT ################
    #                             |                                #
    #                             V                                #
    ################################################################
    def removeVariationAxisToAtomicElementNamed(self, axisName, atomicElementName):
        for d in self._atomicElements:
            if atomicElementName == d['name']:
                del d['coord'][axisName]

        for gvAxisName, l in self._glyphVariations.items():
            for i, d in enumerate(l):
                if atomicElementName == self._atomicElements[i]['name']:
                    del d['coord'][axisName]

    def computeDeepComponents(self):
        self.computedAtomicSelectedSourceInstances = []
        self.computedAtomicInstances = []
        
        if self.selectedSourceAxis is None:
            self.computedAtomicInstances = self.generateDeepComponent(
                self, 
                preview=False,
                )
        else:
            self.computedAtomicSelectedSourceInstances = self.generateDeepComponentVariation(
                self.selectedSourceAxis,
                preview=False,
                )

    def computeDeepComponentsPreview(self, sourcelist = []):
        self.preview = []

        if not sourcelist:
            sourcelist = self.sourcesList

        deepComponentAxisInfos = {}
        for UIDeepComponentVariation in sourcelist:
            deepComponentAxisInfos[UIDeepComponentVariation['Axis']] = UIDeepComponentVariation['PreviewValue']
        if not deepComponentAxisInfos: return

        deepdeepolatedDeepComponent = interpolation.deepdeepolation(
            self._atomicElements, 
            self._glyphVariations, 
            deepComponentAxisInfos
            )

        previewGlyph = DeepComponent("PreviewGlyph")
        previewGlyph._atomicElements = DeepComponents(deepdeepolatedDeepComponent)

        self.preview = self.generateDeepComponent(
            previewGlyph, 
            preview=True
            )

    def generateDeepComponentVariation(self, selectedSourceAxis,  preview=True):
        ### CLEANING TODO ###
        _lib = {}
        atomicSelectedSourceInstances = []
        for deepComponentAxisName, deepComponentVariation in self._glyphVariations.items():
            _lib[deepComponentAxisName] = deepComponentVariation
            
            if deepComponentAxisName == selectedSourceAxis:
                _deepComponentVariation = []
                for i, sourceAtomicElements in enumerate(deepComponentVariation):
                    _atomicElement = copy.deepcopy(sourceAtomicElements)
                    _atomicElement['coord'] = {}
                    
                    masterAtomicElement = self._atomicElements[i]
                     
                    layersInfos = {}
                    atomicVariations = self.currentFont[masterAtomicElement['name']]._glyphVariations
            
                    for atomicAxisName, atomicLayerName in atomicVariations.items():
                        if atomicAxisName in deepComponentVariation[i]['coord']:
                            _atomicElement['coord'][atomicAxisName] = deepComponentVariation[i]['coord'][atomicAxisName]
                        else:
                            _atomicElement['coord'][atomicAxisName] = 0
                        # if self.selectedElement == (i, masterAtomicElement['name']) and self.sliderName == atomicAxisName  and preview == False and self.sliderValue:
                        #     _atomicElement['coord'][atomicAxisName] = float(self.sliderValue)
                        layersInfos[str(atomicLayerName)] = _atomicElement['coord'][atomicAxisName]
        
                    atomicElementGlyph = self.currentFont[masterAtomicElement['name']].foreground#getLayer('foreground')
                    atomicSelectedSourceInstanceGlyph = interpolation.deepolation(
                        RGlyph(), 
                        atomicElementGlyph, 
                        layersInfos
                        )

                    atomicSelectedSourceInstanceGlyph.scaleBy((sourceAtomicElements['scalex'], sourceAtomicElements['scaley']))
                    atomicSelectedSourceInstanceGlyph.rotateBy(sourceAtomicElements['rotation'])
                    atomicSelectedSourceInstanceGlyph.moveBy((sourceAtomicElements['x'], sourceAtomicElements['y']))
                    # atomicSelectedSourceInstanceGlyph.round()
                    atomicSelectedSourceInstances.append({masterAtomicElement['name']:(atomicSelectedSourceInstanceGlyph, deepComponentVariation, deepComponentVariation[i]['coord'])})
                
                    _deepComponentVariation.append(_atomicElement)   
                                 
                _lib[deepComponentAxisName] = _deepComponentVariation 

        self._glyphVariations = VariationGlyphs(_lib)
        return atomicSelectedSourceInstances

    def save(self):
        self.lib.clear()
        lib = RLib()
        lib[atomicElementsKey] = self._atomicElements.getList()
        lib[glyphVariationsKey] = self._glyphVariations.getDict()
        self.lib.update(lib)