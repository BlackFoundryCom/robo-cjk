from mojo.roboFont import *
from imp import reload
from models import glyph
reload(glyph)
from utils import interpolation
reload(interpolation)
Glyph = glyph.Glyph
import copy

from models import deepComponent
reload(deepComponent)

deepComponentsKey = 'robocjk.characterGlyph.deepComponents'
glyphVariationsKey = 'robocjk.characterGlyph.glyphVariations'

class CharacterGlyph(Glyph):
    def __init__(self, name):
        super().__init__()
        self._deepComponents = []
        self._glyphVariations = {}
        self.selectedSourceAxis = None
        self.computedDeepComponents = []
        self.computedDeepComponentsVariation = []
        self.selectedElement = []
        self.name = name
        self.type = "characterGlyph"
        self.save()

    @property
    def deepComponents(self):
        return self._deepComponents

    @property
    def glyphVariations(self):
        return self._glyphVariations

    def _initWithLib(self):
        try:
            self._deepComponents = list(self._RGlyph.lib[deepComponentsKey])      
            self._glyphVariations = dict(self._RGlyph.lib[glyphVariationsKey])
        except:
            self._deepComponents = []
            self._glyphVariations = {}

    @property
    def selectedElementCoord(self) -> dict:
        index = self.selectedElement[0]
        if self.computedDeepComponents:
            return list(self.computedDeepComponents[index].values())[0][0]
        elif self.computedDeepComponentsVariation:
            return list(self.computedDeepComponentsVariation[index].values())[0][0]

    @property
    def atomicInstances(self):
        preview = self.generateDeepComponent(self,  preview=False)
        for d in preview:
            for a in d.values():
                yield a[0]

    def pointIsInside(self, point, multipleSelection = False):
        def checkInside(elements: list):
            for i, atomicInstanceGlyph in self._getAtomicInstanceGlyph(elements):
                if atomicInstanceGlyph.pointInside((px, py)):
                    self.selectedElement.append(i)
                    if not multipleSelection: return

        px, py = point
        if self.computedDeepComponents:
            checkInside(self.computedDeepComponents)
                                
        elif self.computedDeepComponentsVariation:
            checkInside(self.computedDeepComponentsVariation)

    def _getAtomicInstanceGlyph(self, elements):
        for i, e in enumerate(elements):
            for dcCoord, l in e.values():
                for dcAtomicElements in l:
                    for atomicInstanceGlyph, _, _ in dcAtomicElements.values():
                        yield i, atomicInstanceGlyph

    def selectionRectTouch(self, x: int, w: int, y: int, h: int):
        def checkInside(elements: list):
            for i, atomicInstanceGlyph in self._getAtomicInstanceGlyph(elements):
                inside = False
                for c in atomicInstanceGlyph:
                    for p in c.points:
                        if p.x > x and p.x < w and p.y > y and p.y < h:
                            inside = True
                if inside:
                    if i in self.selectedElement: continue
                    self.selectedElement.append(i)

        if self.computedDeepComponents:
            checkInside(self.computedDeepComponents)

        elif self.computedDeepComponentsVariation:
            checkInside(self.computedDeepComponentsVariation)

    @property
    def atomicInstancesGlyphs(self):
        if self.computedDeepComponentsVariation:
            elements = self.computedDeepComponentsVariation
        elif self.computedDeepComponents:
            elements = self.computedDeepComponents

        for i, atomicInstanceGlyph in self._getAtomicInstanceGlyph(elements):
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
            self._glyphVariations[self.selectedSourceAxis][self.selectedElement[0]]['coord'][nameAxis] = value
        else:
            self._deepComponents[self.selectedElement[0]]['coord'][nameAxis]=value

    def removeVariationAxis(self, name):
        del self._glyphVariations[name]

    def addDeepComponentNamed(self, deepComponentName, items = False):
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
            for k in self.currentFont[deepComponentName]._glyphVariations.keys():
                d['coord'][k] = 0
        d["name"] = deepComponentName

        self._deepComponents.append(d)

        variation_d = {k:v for k, v in d.items() if k!='name'}
        for k, v in self._glyphVariations.items():
            v.append(variation_d)

    def removeDeepComponentAtIndex(self):
        if not self.selectedElement: return
        for i in self.selectedElement:
            self._deepComponents.pop(i)
            for k, v in self._glyphVariations.items():
                v.pop(i)
            self.selectedElement = []

    def addVariationAxisToDeepComponentNamed(self, axisName, deepComponentName):
        for d in self._deepComponents:
            if deepComponentName == d['name']:
                d['coord'][axisName] = 0

        for gvAxisName, l in self._glyphVariations.items():
            for i, d in enumerate(l):
                if deepComponentName == self._deepComponents[i]['name']:
                    d['coord'][axisName] = 0

    def removeVariationAxisToDeepComponentNamed(self, axisName, deepComponentName):
        for d in self._deepComponents:
            if deepComponentName == d['name']:
                del d['coord'][axisName]

        for gvAxisName, l in self._glyphVariations.items():
            for i, d in enumerate(l):
                if deepComponentName == self._deepComponents[i]['name']:
                    del d['coord'][axisName]

    def computeDeepComponents(self):
        self.computedDeepComponents = []
        self.computedDeepComponentsVariation = []
        if self.selectedSourceAxis is None:
            self.computedDeepComponents = self.generateCharacterGlyph(
                self, 
                preview=False
                )
        else:
            self.computedDeepComponentsVariation = self.generateCharacterGlyphVariation(
                self.selectedSourceAxis,
                preview=False
                )

    def computeDeepComponentsPreview(self):
        self.preview = []
        deepComponentsSelectedVariation = []

        characterGlyphAxisInfos = {}
        for UICharacterGlyphVariation in self.sourcesList:
            characterGlyphAxisInfos[UICharacterGlyphVariation['Axis']] = UICharacterGlyphVariation['PreviewValue']

        if not characterGlyphAxisInfos: return

        outputCG = interpolation.deepdeepdeepolation(
            self._deepComponents, 
            self._glyphVariations, 
            characterGlyphAxisInfos
            )

        for j, masterDeepComponentInstance in enumerate(outputCG):
            glyph = self.currentFont[masterDeepComponentInstance['name']]
            masterDeepComponent = glyph._atomicElements
            deepComponentVariations = glyph._glyphVariations
            deepComponentAxisInfos = masterDeepComponentInstance['coord']
        
            deepdeepolatedDeepComponent = interpolation.deepdeepolation(
                masterDeepComponent, 
                deepComponentVariations, 
                deepComponentAxisInfos
                )

            previewGlyph = deepComponent.DeepComponent("PreviewGlyph")
            previewGlyph._atomicElements = deepdeepolatedDeepComponent

            atomicInstancesPreview = self.generateDeepComponent(
                previewGlyph, 
                preview=True
                )

            for e in atomicInstancesPreview:
                for aeName, ae in e.items():
                    ae[0].scaleBy((masterDeepComponentInstance['scalex'], masterDeepComponentInstance['scaley']))
                    ae[0].moveBy((self._deepComponents[j]['x'], self._deepComponents[j]['y']))
                    ae[0].moveBy((masterDeepComponentInstance['x'], masterDeepComponentInstance['y']))
                    ae[0].rotateBy(masterDeepComponentInstance['rotation'])
                
            deepComponentsSelectedVariation.append({self._deepComponents[j]['name']: (masterDeepComponentInstance['coord'], atomicInstancesPreview)})                
        self.preview = deepComponentsSelectedVariation

    def generateCharacterGlyphVariation(self, selectedSourceAxis, preview=True):
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
                
                    masterDeepComponent = self.currentFont[cgdc[j]['name']]._atomicElements
                    deepComponentVariations = self.currentFont[cgdc[j]['name']]._glyphVariations
                    deepComponentAxisInfos = {}

                    deepComponentAxisInfos = dc['coord'] 

                    deepdeepolatedDeepComponent = interpolation.deepdeepolation(masterDeepComponent, deepComponentVariations, deepComponentAxisInfos)
                    previewGlyph = RGlyph()
                    previewGlyph._atomicElements = deepdeepolatedDeepComponent
            
                    atomicInstancesPreview = self.generateDeepComponent(previewGlyph, preview=True)
                    for e in atomicInstancesPreview:
                        for aeName, ae in e.items():
                            ae[0].scaleBy((dc['scalex'], dc['scaley']))
                            ae[0].moveBy((dc['x'], dc['y']))
                            ae[0].rotateBy(dc['rotation'])
                    deepComponentsSelectedVariation.append({cgdc[j]['name']: (dc['coord'], atomicInstancesPreview)})
                    
                    _lib[characterGlyphAxisName].append(dc)
                    
        self._glyphVariations = _lib
        return deepComponentsSelectedVariation

    def addCharacterGlyphNamedVariationToGlyph(self, name):
        if name in self._glyphVariations.keys(): return
        cggv = copy.deepcopy(self._deepComponents)
        for e in cggv:
            del e["name"]
        self._glyphVariations[name] = cggv

    def removeDeepComponentAtIndexToGlyph(self):
        if not self.selectedElement: return
        for index in self.selectedElement:
            self._deepComponents.pop(index)
            for dcList in self._glyphVariations.values():
                dcList.pop(index)

    def save(self):
        self.lib.clear()
        lib = RLib()
        lib[deepComponentsKey] = self._deepComponents
        lib[glyphVariationsKey] = self._glyphVariations
        self.lib.update(lib)