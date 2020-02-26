from mojo.roboFont import *
from imp import reload
from utils import interpolation
reload(interpolation)
from models import deepComponent
import copy
# reload(deepComponent)

def compute(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        self.computeDeepComponents()
        self.computeDeepComponentsPreview()
    return wrapper

class Glyph(RGlyph):

    def __init__(self):
        super().__init__()
        self.type = None
        self.preview = None
        self.sourcesList = []
        # self.transformationWithMouse = False

    def save(self):
        self.lib.clear()

    def getParent(self):
        return self.currentFont

    def setParent(self, currentFont):
        self.currentFont = currentFont

    @property
    def _RGlyph(self):
        return self.currentFont._RFont[self.name]

    def keyDown(self, keys):
        modifiers, inputKey, character = keys
        element = self._getElements()
        if modifiers[2]:
            if character == '∂':
                self.duplicateSelectedElements()
            else:
                rotation = (-10*modifiers[0]*modifiers[4]*inputKey[0] - 4*modifiers[0]*inputKey[0] - inputKey[0])*.5
                self.setRotationAngleToSelectedElements(rotation)
        elif modifiers[3]:
            x = round((9*modifiers[0]*inputKey[0] + inputKey[0])*.01, 3)
            y = round((9*modifiers[0]*inputKey[1] + inputKey[1])*.01, 3)
            self.setScaleToSelectedElements((x, y))
        else:
            x = 90*modifiers[0]*modifiers[4]*inputKey[0] + 9*modifiers[0]*inputKey[0] + inputKey[0] 
            y = 90*modifiers[0]*modifiers[4]*inputKey[1] + 9*modifiers[0]*inputKey[1] + inputKey[1]
            self.setPositionToSelectedElements((x, y))

    def _getSelectedElement(self):
        element = self._getElements()
        if element is None: return
        for index in self.selectedElement:
            yield element[index]

    @compute
    def setRotationAngleToSelectedElements(self, rotation: int, append: bool = True):
        for selectedElement in self._getSelectedElement():
            if append:
                selectedElement["rotation"] += int(rotation)
            else:
                selectedElement["rotation"] = -int(rotation)

    @compute
    def setPositionToSelectedElements(self, position: list):
        for selectedElement in self._getSelectedElement():
            selectedElement["x"] += position[0]
            selectedElement["y"] += position[1]

    @compute
    def setScaleToSelectedElements(self, scale: list):
        x, y = scale
        for selectedElement in self._getSelectedElement():
            rotation = selectedElement["rotation"]
            if -45 < rotation < 45:
                x, y = x, y
            elif -135 < rotation < -45 or 225 < rotation < 315:
                x, y = -y, x
            elif 45 < rotation < 135 or -315 < rotation < -225:
                x, y = y, -x
            elif -225 < rotation < -135 or 135 < rotation < 225:
                x, y = -x, -y
            elif -360 < rotation < -315 or 315 < rotation < 360:
                x, y = -x, -y
            selectedElement["scalex"] += x
            selectedElement["scaley"] += y

    def generateDeepComponent(self, g, preview=True):
        atomicInstances = []
        if not hasattr(g,"_atomicElements"): return
        for i, atomicElement in enumerate(g._atomicElements):
            layersInfos = {}
            
            # aeGlyph = self.getParent()[atomicElement['name']]
            atomicElementGlyph = self.currentFont[atomicElement['name']].foreground
            atomicVariations = self.currentFont[atomicElement['name']]._glyphVariations
            
            for axisName in atomicElement['coord'].keys():
                # if self.selected == (i, atomicElement['name']) and self.sliderName == axisName and preview == False and self.sliderValue:
                #     atomicElement['coord'][axisName] = float(self.sliderValue)
                layersInfos[atomicVariations[axisName]] = atomicElement['coord'][axisName]
                
            atomicInstanceGlyph = interpolation.deepolation(
                RGlyph(), 
                atomicElementGlyph, 
                layersInfos
                )
    
            atomicInstanceGlyph.scaleBy((atomicElement['scalex'], atomicElement['scaley']))
            atomicInstanceGlyph.rotateBy(atomicElement['rotation'])
            atomicInstanceGlyph.moveBy((atomicElement['x'], atomicElement['y']))                          
            atomicInstances.append({atomicElement['name']:(atomicInstanceGlyph, atomicVariations, atomicElement['coord'])})
        return atomicInstances


    def generateCharacterGlyph(self, g, preview=True):
        ### CLEANING TODO ###
        _lib = []

        deepComponents = []
        for j, dc in enumerate(g._deepComponents):
            # if self.selected == (j, dc['name']) and self.sliderValue and preview==False:
            #     dc['coord'][self.sliderName] = float(self.sliderValue)
                
            dcGlyph = self.getParent()[dc['name']]
            masterDeepComponent = dcGlyph._atomicElements
            deepComponentVariations = dcGlyph._glyphVariations
            deepComponentAxisInfos = {}

            deepComponentAxisInfos = dc['coord'] 

            deepdeepolatedDeepComponent = interpolation.deepdeepolation(
                masterDeepComponent, 
                deepComponentVariations, 
                deepComponentAxisInfos
                )
            previewGlyph = deepComponent.DeepComponent("PreviewGlyph")
            previewGlyph._atomicElements = deepdeepolatedDeepComponent
            
            atomicInstancesPreview = self.generateDeepComponent(previewGlyph, preview=True)
            for e in atomicInstancesPreview:
                for aeName, ae in e.items():
                    ae[0].scaleBy((dc['scalex'], dc['scaley']))
                    ae[0].moveBy((dc['x'], dc['y']))
                    ae[0].rotateBy(dc['rotation'])
            deepComponents.append({dc['name']: (dc['coord'], atomicInstancesPreview)})
            _lib.append(dc)
        g._deepComponents = _lib
        return deepComponents

    

    def transform(self, element, instance, keys):
        modifiers, inputKey, character = keys
        # index = self.selectedElement.get("index")
        for index in self.selectedElement:
            # if index is None: return
            d = element[index]
            if modifiers[2]:
                if character == "∂" and d.get("name"):
                    if self.type == "deepComponent":
                        self.addAtomicElementNamed(d["name"], copy.deepcopy(d))
                    elif self.type == "characterGlyph":
                        self.addDeepComponentNamed(d["name"], copy.deepcopy(d))
                    # self.selectedElement = []
                else:
                    d['rotation'] += (-10*modifiers[0]*modifiers[4]*inputKey[0] - 4*modifiers[0]*inputKey[0] - inputKey[0])*.5
            elif modifiers[1]:
                d['scalex'] = round(d['scalex'] + (9*modifiers[0]*inputKey[0] + inputKey[0])*.01, 3)
                d['scaley'] = round(d['scaley'] + (9*modifiers[0]*inputKey[1] + inputKey[1])*.01, 3)
                print(d['scalex'], d['scaley'])
            else:
                d['x'] += 90*modifiers[0]*modifiers[4]*inputKey[0] + 9*modifiers[0]*inputKey[0] + inputKey[0] 
                d['y'] += 90*modifiers[0]*modifiers[4]*inputKey[1] + 9*modifiers[0]*inputKey[1] + inputKey[1]
        self.computeDeepComponents()
        self.computeDeepComponentsPreview()


