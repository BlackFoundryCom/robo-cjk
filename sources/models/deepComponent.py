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
# reload(component)
# reload(glyphPreview)
from utils import interpolation, decorators
from fontTools.varLib.models import VariationModel
# reload(interpolation)
# reload(decorators)
glyphUndo = decorators.glyphUndo
import copy
Glyph = glyph.Glyph
glyphAddRemoveUndo = decorators.glyphAddRemoveUndo

DeepComponentNamed = component.DeepComponentNamed
DeepComponents = component.DeepComponents
Axes = component.Axes
VariationGlyphs = component.VariationGlyphs
VariationGlyphsInfos = component.VariationGlyphsInfos

# Deprecated keys
# atomicElementsKey = 'robocjk.deepComponent.atomicElements'
glyphVariationsKey = 'robocjk.glyphVariationGlyphs'

# Actual keys
deepComponentsKey = 'robocjk.deepComponents'
axesKey = 'robocjk.axes'
variationGlyphsKey = 'robocjk.variationGlyphs'
statusKey = 'robocjk.status'


class DeepComponent(Glyph):
    def __init__(self, name):
        super().__init__()
        self._deepComponents = DeepComponents()
        self._axes = Axes()
        self._glyphVariations = VariationGlyphs()
        self.selectedSourceAxis = None
        self.computedAtomicSelectedSourceInstances = []
        self.computedAtomicInstances = []
        self.selectedElement = []
        self.name = name
        self.type = "deepComponent"
        self.previewGlyph = []
        self.axisPreview = []
        # self.preview = glyphPreview.DeepComponentPreview(self)
        self._setStackUndo()
        self.save()

    def preview(self, position:dict={}, deltasStore:dict={}, font = None, forceRefresh=True, axisPreview = False):
        
        locationKey = ','.join([k+':'+str(v) for k,v in position.items()]) if position else ','.join([k+':'+str(v) for k,v in self.normalizedValueToMinMaxValue(self.getLocation(), self).items()])

        #### 3 CONDITIONS DE DESSIN POSSIBLE EN CAS D'ÉLEMENT SELECTIONNÉ ####
        redrawAndTransformAll = False
        redrawAndTransformSelected = False
        onlyTransformSelected = False

        if self.selectedElement and not self.reinterpolate:
            onlyTransformSelected = True
        elif self.selectedElement and self.reinterpolate and not axisPreview:
            redrawAndTransformAll = True
        elif self.selectedElement:
            redrawAndTransformSelected = True
        else:
            redrawAndTransformAll = True
        ############################################################


        #### S'IL N'Y A PAS DE SELECTION, RECHERCHE D'UN CACHE ####
        previewLocationsStore = self.previewLocationsStore.get(locationKey, False)
        if axisPreview:
            redrawSeletedElement = self.redrawSelectedElementSource
        else:
            redrawSeletedElement = self.redrawSelectedElementPreview
        if not self.redrawSelectedElementSource:
            if previewLocationsStore:
                # print('I have cache', locationKey)
                for p in previewLocationsStore:
                    yield p
                return
            if axisPreview and self.axisPreview:
                # print('DC has axisPreview', self.axisPreview)
                for e in self.axisPreview: yield e
                return
            elif not forceRefresh and self.previewGlyph and not axisPreview: 
                # print('DC has previewGlyph', self.previewGlyph)
                for e in self.previewGlyph: yield e
                return
        ############################################################


        #### S'IL N'Y A UNE SELECTION MAIS PAS D'INSTRUCTION DE REDESSIN, RECHERCHE D'UN CACHE ####
        if not redrawAndTransformAll and not redrawAndTransformSelected and not onlyTransformSelected:
            if previewLocationsStore:
                # print('I have cache', locationKey)
                for p in previewLocationsStore:
                    yield p
                return
            ############################################################
        else:
            #### IL Y A DES INSTRUCTION DE REDESSIN ####
            if axisPreview:
                preview = self.axisPreview
            else:
                preview = self.previewGlyph

            """ Dans cette condition on ne ce soucis pas du cache, on redessine tout"""
            if redrawAndTransformAll:
                if axisPreview:
                    preview = self.axisPreview = []
                else:
                    preview = self.previewGlyph = []
            else:
                """Dans cette condition on récupère ce qu'il y a dans le cache et on travaillera 
                dessus après, soit pour modifier les instructions de transformation de l'element selectionné
                soit pour recalculer l'element et ses instructions de transformation. Les autres elements du cache ne seront
                pas recalculé"""
                if previewLocationsStore:
                    if axisPreview:
                        preview = self.axisPreview = previewLocationsStore
                    else:
                        preview = self.previewGlyph = previewLocationsStore 


        if not position:
            position = self.getLocation()

        position = self.normalizedValueToMinMaxValue(position, self)
        # print("position", position, "\n")

        locations = [{}]
        locations.extend([self.normalizedValueToMinMaxValue(x["location"], self) for x in self._glyphVariations if x["on"]])
        # print("location", locations, "\n\n")
        model = VariationModel(locations)
        
        if redrawAndTransformAll:
            masterDeepComponents = self._deepComponents
            axesDeepComponents = [variation.get("deepComponents") for variation in self._glyphVariations.getList() if variation.get("on")==1]
        else:
            masterDeepComponents = [x for i, x in enumerate(self._deepComponents) if i in self.selectedElement]
            axesDeepComponents = [[x for i, x in enumerate(variation.get("deepComponents")) if i in self.selectedElement] for variation in self._glyphVariations.getList() if variation.get("on")==1]
        
        result = []
        deltasList = []
        for i, deepComponent in enumerate(masterDeepComponents):
            variations = []
            for gv in axesDeepComponents:
                variations.append(gv[i])
            deltas = model.getDeltas([deepComponent, *variations])
            
            # result.append(model.interpolateFromMasters(position, [deepComponent, *variations]))
            result.append(model.interpolateFromDeltas(position, deltas))
            deltasList.append(deltas)

        if font is None:
            font = self.getParent()
        for i, dc in enumerate(result):
            name = dc.get("name")
            try: g = font[name]
            except: continue
            
            if onlyTransformSelected: 
                preview[self.selectedElement[i]].transformation = dc.get("transform")
            else:
                resultGlyph = RGlyph()
                pen = resultGlyph.getPen()
                pos = dc.get('coord')
                g = g.preview(pos, font, forceRefresh=True)

                for c in g:
                    c = c.glyph
                    c.draw(pen)

                if redrawAndTransformSelected: 
                    preview[self.selectedElement[i]].resultGlyph = resultGlyph   
                    preview[self.selectedElement[i]].transformation = dc.get("transform")
                else: 
                    preview.append(self.ResultGlyph(resultGlyph, dc.get("transform")))

        self.previewLocationsStore[','.join([k+':'+str(v) for k,v in position.items()])] = preview

        if axisPreview:
            self.redrawSelectedElementSource = False
        else:
            self.redrawSelectedElementPreview = False

        for resultGlyph in preview:
            yield resultGlyph


    @property
    def atomicElements(self):
        return self._deepComponents

    @property
    def glyphVariations(self):
        return self._glyphVariations
    
    def _initWithLib(self, lib=None):
        try:
            if lib:
                if variationGlyphsKey not in lib.keys():
                    deepComponents = lib[deepComponentsKey]
                    variationGlyphs = lib[glyphVariationsKey]
                else:
                    deepComponents = lib[deepComponentsKey]
                    variationGlyphs = lib[variationGlyphsKey]
                hasAxisKey = axesKey in lib.keys()
                axes = lib.get(axesKey)
                status = lib.get(statusKey, 0)
            else:
                if variationGlyphsKey not in self._RGlyph.lib.keys():
                    deepComponents = self._RGlyph.lib[deepComponentsKey]
                    variationGlyphs = self._RGlyph.lib[glyphVariationsKey]
                else:
                    deepComponents = self._RGlyph.lib[deepComponentsKey]
                    variationGlyphs = self._RGlyph.lib[variationGlyphsKey]
                hasAxisKey = axesKey in self._RGlyph.lib.keys()
                axes = self._RGlyph.lib.get(axesKey)
                status = self._RGlyph.lib.get(statusKey, 0)
            if hasAxisKey:
                self._deepComponents = DeepComponents(deepComponents)
                self._axes = Axes(axes, global_axes = self.currentFont.designspace["axes"])
                self._glyphVariations = VariationGlyphs(variationGlyphs, self._axes, defaultWidth = self._RGlyph.width)
                self._status = status
            else:
                self._deepComponents = DeepComponents()
                self._deepComponents._init_with_old_format(deepComponents)
                self._axes = Axes(global_axes = self.currentFont.designspace["axes"])      
                self._axes._init_with_old_format(variationGlyphs)
                self._glyphVariations = VariationGlyphs()
                self._glyphVariations._init_with_old_format(variationGlyphs, self._axes, defaultWidth = self._RGlyph.width)
            # self._temp_set_Status_value()
        except Exception as e:
            self._deepComponents = DeepComponents()
            self._axes = Axes(global_axes = self.currentFont.designspace["axes"])  
            self._glyphVariations = VariationGlyphs()

    def duplicateSelectedElements(self): # TODO
        element = self._getElements()
        if element is None: return
        for index in self.selectedElement:
            selectedElement = element[index]
            if selectedElement.get("name"):
                self.addAtomicElementNamed(selectedElement["name"], copy.deepcopy(selectedElement))
        #         self.selectedElement = [len(self._deepComponents)-1]
        self.redrawSelectedElementSource = True
        self.redrawSelectedElementPreview = True
        self.selectedElement = []

    def addGlyphVariation(self, newAxisName):
        self._axes.addAxis({"name":newAxisName, "minValue":0, "maxValue":1})
        self._glyphVariations.addVariation({"deepComponents":self._deepComponents, "location":{newAxisName:1}}, self.axes, defaultWidth = self._RGlyph.width)

    def removeGlyphVariation(self, axisName):
        index = 0
        for i, x in enumerate(self._axes):
            if x.name == axisName:
                index = i
        self._glyphVariations.removeVariation(index)
        self._axes.removeAxis(index)

    def updateAtomicElementCoord(self, axisName, value):
        if self.selectedSourceAxis:
            index = 0
            # print(self.selectedSourceAxis)
            for i, x in enumerate(self._glyphVariations):
                if x.sourceName == self.selectedSourceAxis:
                    index = i
            self._glyphVariations[index].deepComponents[self.selectedElement[0]].coord[axisName] = value
            # self._glyphVariations[self.selectedSourceAxis][self.selectedElement[0]].coord[axisName] = value
        else:
            self._deepComponents[self.selectedElement[0]].coord[axisName] = value

    @glyphAddRemoveUndo
    def addAtomicElementNamed(self, atomicElementName, items = False):
        if not items:
            d = DeepComponentNamed(atomicElementName)
            dcglyph = self.currentFont[atomicElementName]
            for i, axis in enumerate(dcglyph._axes):
                value = dcglyph._axes[i].defaultValue
                d.coord.add(axis.name, value)
        else:
            d = items
            d.name = atomicElementName

        self._deepComponents.addDeepComponent(d)
        if self._axes:
            self._glyphVariations.addDeepComponent(d)
        self.redrawSelectedElementSource = True
        self.redrawSelectedElementPreview = True
        self.selectedElement = []

        # self.preview.computeDeepComponentsPreview(update = False)
        # self.preview.computeDeepComponents(update = False)

    @glyphAddRemoveUndo
    def removeAtomicElementAtIndex(self, indexes = []):
        if not self.selectedElement and not indexes: return
        if indexes:
            self.removeDeepComponents(indexes)
        else:
            self.removeDeepComponents(self.selectedElement)
        self.redrawSelectedElementSource = True
        self.redrawSelectedElementPreview = True
        self.selectedElement = []
        
    def addVariationToGlyph(self, name):
        if name in self._axes.names: return
        # if name in self._glyphVariations.axes: return
        self.addGlyphVariation(name)


    def renameVariationAxis(self, oldName, newName):
        self._axes.renameAxis(oldName, newName)
        # for axis in self._axes:
        #     if axis.name == oldName:
        #         axis.name == newName
        self._glyphVariations.renameAxisInsideLocation(oldName, newName)


    def removeVariationAxis(self, name):
        self.removeGlyphVariation(name)
        # self._glyphVariations.removeAxis(name)

    def save(self):
        # color = self.markColor
        self.lib.clear()
        lib = RLib()

        # for variations in self._glyphVariations.values():
        #     variations.setAxisWidth(self.currentFont.defaultGlyphWidth)

        lib[deepComponentsKey] = self._deepComponents.getList()
        lib[axesKey] = self._axes.getList()
        lib[variationGlyphsKey] = self._glyphVariations.getList(exception=["layerName"])
        for i, v in enumerate(lib[variationGlyphsKey]):
            if v["width"] == self._RGlyph.width:
                del lib[variationGlyphsKey][i]["width"]
        if self._status:
            lib[statusKey] = self._status
        if 'public.markColor' in lib:
            del lib['public.markColor']
        self.lib.update(lib)
        if 'public.markColor' in self.lib:
            del self.lib['public.markColor']
        if not self.lib[axesKey]:
            del self.lib[axesKey]
        if not self.lib[deepComponentsKey]:
            del self.lib[deepComponentsKey]
        if not self.lib[variationGlyphsKey]:
            del self.lib[variationGlyphsKey]
        # self.markColor = color
