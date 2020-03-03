from mojo.roboFont import *
from imp import reload
from models import glyph
reload(glyph)
from utils import interpolation
reload(interpolation)
import copy
Glyph = glyph.Glyph

atomicElementsKey = 'robocjk.deepComponent.atomicElements'
glyphVariationsKey = 'robocjk.deepComponent.glyphVariations'

class DeepComponent(Glyph):
    def __init__(self, name):
        super().__init__()
        self._atomicElements = []
        self._glyphVariations = {}
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
        self._atomicElements = list(self._RGlyph.lib[atomicElementsKey])      
        self._glyphVariations = dict(self._RGlyph.lib[glyphVariationsKey])      

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
        self._glyphVariations[newAxisName] = [{k:v for k,v in d.items() if k!='name'} for d in self._atomicElements]
        for name in self.currentFont.characterGlyphSet:
            g = self.currentFont[name]
            g.addVariationAxisToDeepComponentNamed(newAxisName, self.name)

    def removeGlyphVariation(self, axisName):
        del self._glyphVariations[axisName]
        for name in self.currentFont.characterGlyphSet:
            g = self.currentFont[name]
            g.removeVariationAxisToDeepComponentNamed(axisName, self.name)

    def updateAtomicElementCoord(self, axisName, value):
        if self.selectedSourceAxis is not None:
            self._glyphVariations[self.selectedSourceAxis][self.selectedElement[0]]['coord'][axisName]=value
        else:
            self._atomicElements[self.selectedElement[0]]['coord'][axisName]=value

    def addAtomicElementNamed(self, atomicElementName, items = False):
        d = items
        if not items:
            d = {
                'x': 0,
                'y': 0,
                'scalex': 1, 
                'scaley': 1, 
                'rotation': 0,
                'coord': {}
                }
            for k in self.currentFont[atomicElementName]._glyphVariations.keys():
                d['coord'][k] = 0
        d["name"] = atomicElementName

        self._atomicElements.append(d)

        variation_d = {k:v for k, v in d.items() if k!='name'}
        for k, v in self._glyphVariations.items():
            v.append(variation_d)

    def removeAtomicElementAtIndex(self):
        if not self.selectedElement: return
        for index in self.selectedElement:
            self._atomicElements.pop(index)
            for k, v in self._glyphVariations.items():
                v.pop(index)
            self.selectedElement = []

    def addVariationToGlyph(self, name):
        dcgv = copy.deepcopy(self._atomicElements)
        for e in dcgv:
            del e["name"]

        self._glyphVariations[name] = dcgv
        # check all existing characterGlyph's deep components and add glyph variation to coord
        for glyphname in self.currentFont.characterGlyphSet:
            g2 = self.currentFont[glyphname]
            for d in g2._deepComponents:
                if d["name"] != self.name: continue
                d['coord'][name] = 0

    def renameVariationAxis(self, oldName, newName):
        v = copy.deepcopy(self._glyphVariations[oldName])
        del self._glyphVariations[oldName]
        self._glyphVariations[newName] = v

        def _rename(d, oldName, newName):
            v = copy.deepcopy(d['coord'][oldName])
            del d['coord'][oldName]
            d['coord'][newName] = v

        for glyphname in self.currentFont.characterGlyphSet:
            g2 = self.currentFont[glyphname]

            for i, d in enumerate(g2._deepComponents):
                if d["name"] != self.name: continue
                _rename(d, oldName, newName)
                # v = copy.deepcopy(d['coord'][oldName])
                # del d['coord'][oldName]
                # d['coord'][newName] = v
                for e in g2._glyphVariations.values():
                    _rename(e[i], oldName, newName)
                    # v = copy.deepcopy(e[i]['coord'][oldName])
                    # del e[i]['coord'][oldName]
                    # e[i]['coord'][newName] = v
        # self.selectedSourceAxis = newName

    def removeVariationAxis(self, name):
        del self._glyphVariations[name]

        for glyphname in self.currentFont.characterGlyphSet:
            g2 = self.currentFont[glyphname]
            for d in g2._deepComponents:
                if d["name"] != self.name: continue
                if name in d['coord']:
                    del d['coord'][name]
            for v, l in g2._glyphVariations.items():
                for d in l:
                    if d["name"] != self.name: continue
                    if name in d['coord']:
                        del d['coord'][name]

    # def removeAtomicElement(self):
    #     if not self.selectedElement: return
    #     for index in self.selectedElement:
    #         self._atomicElements.pop(index)
    #         for k, v in self._glyphVariations.items():
    #             v.pop(index)

    def addVariationAxisToAtomicElementNamed(self, axisName, atomicElementName):
        for d in self._atomicElements:
            if atomicElementName == d['name']:
                d['coord'][axisName] = 0

        for gvAxisName, l in self._glyphVariations.items():
            for i, d in enumerate(l):
                if atomicElementName == self._atomicElements[i]['name']:
                    d['coord'][axisName] = 0
    
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

    def computeDeepComponentsPreview(self):
        self.preview = []

        deepComponentAxisInfos = {}
        for UIDeepComponentVariation in self.sourcesList:
            deepComponentAxisInfos[UIDeepComponentVariation['Axis']] = UIDeepComponentVariation['PreviewValue']
        if not deepComponentAxisInfos: return

        deepdeepolatedDeepComponent = interpolation.deepdeepolation(
            self._atomicElements, 
            self._glyphVariations, 
            deepComponentAxisInfos
            )

        previewGlyph = DeepComponent("PreviewGlyph")
        previewGlyph._atomicElements = deepdeepolatedDeepComponent
        
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
                        _atomicElement['coord'][atomicAxisName] = deepComponentVariation[i]['coord'][atomicAxisName]
                        # if self.selectedElement == (i, masterAtomicElement['name']) and self.sliderName == atomicAxisName  and preview == False and self.sliderValue:
                        #     _atomicElement['coord'][atomicAxisName] = float(self.sliderValue)
                        layersInfos[atomicLayerName] = _atomicElement['coord'][atomicAxisName]
        
                    atomicElementGlyph = self.currentFont[masterAtomicElement['name']].foreground#getLayer('foreground')
                    atomicSelectedSourceInstanceGlyph = interpolation.deepolation(
                        RGlyph(), 
                        atomicElementGlyph, 
                        layersInfos
                        )

                    atomicSelectedSourceInstanceGlyph.scaleBy((sourceAtomicElements['scalex'], sourceAtomicElements['scaley']))
                    atomicSelectedSourceInstanceGlyph.rotateBy(sourceAtomicElements['rotation'])
                    atomicSelectedSourceInstanceGlyph.moveBy((sourceAtomicElements['x'], sourceAtomicElements['y']))
                       
                    atomicSelectedSourceInstances.append({masterAtomicElement['name']:(atomicSelectedSourceInstanceGlyph, deepComponentVariation, deepComponentVariation[i]['coord'])})
                
                    _deepComponentVariation.append(_atomicElement)   
                                 
                _lib[deepComponentAxisName] = _deepComponentVariation 

        self._glyphVariations = _lib
        return atomicSelectedSourceInstances

    def save(self):
        self.lib.clear()
        lib = RLib()
        lib[atomicElementsKey] = self._atomicElements
        lib[glyphVariationsKey] = self._glyphVariations
        self.lib.update(lib)