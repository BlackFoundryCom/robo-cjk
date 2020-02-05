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
        self.selectedElement = {}
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

    def pointIsInside(self, point):
        px, py = point
        self.selectedElement = {}
        if self.computedAtomicSelectedSourceInstances:
            for i, d in enumerate(self.computedAtomicSelectedSourceInstances):
                for atomicElementName, (atomicInstanceGlyph, deepComponentSourceVariations, atomicCoord) in d.items():
                    if atomicInstanceGlyph.pointInside((px, py)):
                        self.selectedElement = dict(index = i, element = atomicElementName)
                        return deepComponentSourceVariations[i]['coord']

        elif self.computedAtomicInstances:
            for i, d in enumerate(self.computedAtomicInstances):
                for atomicElementName, (atomicInstanceGlyph, atomicVariations, atomicCoord) in d.items():
                    if atomicInstanceGlyph.pointInside((px, py)):
                        self.selectedElement = dict(index = i, element = atomicElementName)
                        return atomicCoord
        return False

    def keyDown(self, keys):
        if self.computedAtomicInstances:
            self.transform(self._atomicElements, self.computedAtomicInstances, keys)
        elif self.computedAtomicSelectedSourceInstances:
            self.transform(self._glyphVariations[self.selectedSourceAxis], self.computedAtomicSelectedSourceInstances, keys)

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
            self._glyphVariations[self.selectedSourceAxis][self.selectedElement.get('index')]['coord'][axisName]=value
        else:
            self._atomicElements[self.selectedElement.get('index')]['coord'][axisName]=value

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
        self._atomicElements.pop(self.selectedElement.get("index"))
        for k, v in self._glyphVariations.items():
            v.pop(index)
        self.selectedElement = {}

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

    def removeAtomicElement(self):
        if not self.selectedElement: return
        self._atomicElements.pop(self.selectedElement.get("index"))
        for k, v in self._glyphVariations.items():
            v.pop(self.selectedElement.get("index"))

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