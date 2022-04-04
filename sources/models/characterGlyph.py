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
from models import glyph, component, glyphPreview
# reload(glyph)
# reload(component)
# reload(glyphPreview)
from utils import interpolation, decorators
# reload(interpolation)
Glyph = glyph.Glyph
glyphAddRemoveUndo = decorators.glyphAddRemoveUndo
from models import deepComponent
# reload(deepComponent)

DeepComponentNamed = component.DeepComponentNamed
DeepComponents = component.DeepComponents
Axes = component.Axes
VariationGlyphs = component.VariationGlyphs

import copy, time
from fontTools.varLib.models import VariationModel

# Deprecated keys
# deepComponentsKeyOld = 'robocjk.characterGlyph.deepComponents'
glyphVariationsKey = 'robocjk.fontVariationGlyphs'

# Actual keys
deepComponentsKey = 'robocjk.deepComponents'
axesKey = 'robocjk.axes'
variationGlyphsKey = 'robocjk.variationGlyphs'
statusKey = 'robocjk.status'

import cProfile, pstats, io
from pstats import SortKey


class CharacterGlyph(Glyph):

    
    def __init__(self, name):
        super().__init__()
        self._deepComponents = DeepComponents()
        self._axes = Axes()
        self._glyphVariations = VariationGlyphs()
        self.selectedSourceAxis = None
        self.computedDeepComponents = []
        self.computedDeepComponentsVariation = []
        self.selectedElement = []
        self.name = name
        self.type = "characterGlyph"
        self.outlinesPreview = None
        self.previewGlyph = []
        self.axisPreview = []
        
        # self.preview = glyphPreview
        # self.preview = glyphPreview.CharacterGlyphPreview(self)

        # lib = RLib()
        # lib[deepComponentsKey] = copy.deepcopy(self._deepComponents)
        # lib[glyphVariationsKey] = copy.deepcopy(self._glyphVariations)
        # self.stackUndo_lib = [lib]
        # self.indexStackUndo_lib = 0

        self._setStackUndo()
        self.save()


    def preview(self, position:dict={}, deltasStore:dict={}, font = None, forceRefresh=True, axisPreview = False):
        locationKey = ','.join([k+':'+str(v) for k,v in position.items()]) if position else ','.join([k+':'+str(v) for k,v in self.normalizedValueToMinMaxValue(self.getLocation(), self).items()])
        # print(locationKey)
        #### There is 3 possible condition for the drawing/preview if there is a selected element(s) ####
        #### fr: 3 CONDITIONS DE DESSIN POSSIBLE EN CAS D'ÉLEMENT SELECTIONNÉ ####
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


        #### If there is no selected element, we will have a look to the stored preview ####
        #### fr: S'IL N'Y A PAS DE SELECTION, RECHERCHE D'UN CACHE ####

        previewLocationsStore = self.previewLocationsStore.get(locationKey, False)
        # print("previewLocationsStore", previewLocationsStore, '\n')
        # print("redrawSelectedElementSource", self.redrawSelectedElementSource, '\n')
        if axisPreview:
            redrawSeletedElement = self.redrawSelectedElementSource
        else:
            redrawSeletedElement = self.redrawSelectedElementPreview
        if not redrawSeletedElement:
            if previewLocationsStore:
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

        #### if there is no selection and no redraw instruction, we will have a look to the stored preview ####
        #### fr: S'IL N'Y A UNE SELECTION MAIS PAS D'INSTRUCTION DE REDESSIN, RECHERCHE D'UN CACHE ####
        if not redrawAndTransformAll and not redrawAndTransformSelected and not onlyTransformSelected:
            if previewLocationsStore:
                for p in previewLocationsStore:
                    yield p
                return
            ############################################################
        else:
            #### there is no redraw instruction ####
            #### fr: IL Y A DES INSTRUCTION DE REDESSIN ####
            if axisPreview:
                preview = self.axisPreview
            else:
                preview = self.previewGlyph

            """ in this condition we don't look into the stored preview, we will recompute and redraw everything"""
            """ fr: Dans cette condition on ne ce soucis pas du cache, on redessine tout"""
            if redrawAndTransformAll:
                if axisPreview:
                    preview = self.axisPreview = []
                else:
                    preview = self.previewGlyph = []
            else:
                """In this contition we take the stored preview and we will work on it, to modify the transformation settings 
                of the selected element, or to recompute the element and its transformation settings. All the other elements 
                non selected from the stored preview will not be recomputed"""

                """fr: Dans cette condition on récupère ce qu'il y a dans le cache et on travaillera 
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

        position =self.normalizedValueToMinMaxValue(position, self)


        # pr = cProfile.Profile()
        # pr.enable()

        locations = [{}]
        locations.extend([self.normalizedValueToMinMaxValue(x["location"], self) for x in self._glyphVariations if x["on"]])
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
            if not set([name]) & (font.staticAtomicElementSet()|font.staticDeepComponentSet()|font.staticCharacterGlyphSet()): continue
            g = font[name]
            
            if onlyTransformSelected:
                preview[self.selectedElement[i]].transformation = dc.get("transform")
            else:
                resultGlyph = RGlyph()
                g = g.preview(position=dc.get('coord'), deltasStore=deltasList[i], font=font, forceRefresh=True)
                for c in g:
                    c = c.glyph
                    c.draw(resultGlyph.getPen())
                if redrawAndTransformSelected:
                    preview[self.selectedElement[i]].resultGlyph = resultGlyph   
                    preview[self.selectedElement[i]].transformation = dc.get("transform")
                else:
                    preview.append(self.ResultGlyph(resultGlyph, dc.get("transform")))

        if len(self._RGlyph) and not self.selectedElement:
            layerGlyphs = []
            layerNames = self._glyphVariations.axes
            for layerName in layerNames:
                try:
                    g = font._RFont.getLayer(layerName)[self.name]
                except Exception as e: 
                    print(e)
                    continue
                layerGlyphs.append(g)
            if len(layerGlyphs):
                resultGlyph = model.interpolateFromMasters(position, [self._RGlyph, *layerGlyphs])
                preview.append(self.ResultGlyph(resultGlyph))

        self.previewLocationsStore[','.join([k+':'+str(v) for k,v in position.items()])] = preview

        if axisPreview:
            self.redrawSelectedElementSource = False
        else:
            self.redrawSelectedElementPreview = False

        for resultGlyph in preview:
            yield resultGlyph

        # pr.disable()
        # s = io.StringIO()
        # sortby = SortKey.CUMULATIVE
        # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        # ps.print_stats()
        # print(s.getvalue())

    @property
    def foreground(self):
        return self._RFont[self.name].getLayer('foreground')

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
                    deepComponents = self._RGlyph.lib.get(deepComponentsKey, [])
                    variationGlyphs = self._RGlyph.lib[glyphVariationsKey]
                else:
                    deepComponents = self._RGlyph.lib.get(deepComponentsKey, [])
                    variationGlyphs = self._RGlyph.lib[variationGlyphsKey]
                hasAxisKey = axesKey in self._RGlyph.lib.keys()
                axes = self._RGlyph.lib.get(axesKey)
                status = self._RGlyph.lib.get(statusKey, 0)
            if hasAxisKey:
                self._deepComponents = DeepComponents(deepComponents)
                self._axes = Axes(axes)
                self._glyphVariations = VariationGlyphs(variationGlyphs, self._axes)
                self._status = status
            else:
                self._deepComponents = DeepComponents()
                self._deepComponents._init_with_old_format(deepComponents)
                self._axes = Axes()      
                self._axes._init_with_old_format(variationGlyphs)
                self._glyphVariations = VariationGlyphs()
                self._glyphVariations._init_with_old_format(variationGlyphs, self._axes)
            # self._temp_set_Status_value()
        except Exception as e:
            self._deepComponents = DeepComponents()
            self._axes = Axes()   
            self._glyphVariations = VariationGlyphs()

    def duplicateSelectedElements(self): # TODO
        # for selectedElement in self._getSelectedElement():
        element = self._getElements()
        if element is None: return
        for index in self.selectedElement:
            selectedElement = element[index]
            if selectedElement.get("name"):
                self.addDeepComponentNamed(selectedElement["name"], copy.deepcopy(selectedElement))
                # self.selectedElement = [len(self._deepComponents)-1]
        self.redrawSelectedElementSource = True
        self.redrawSelectedElementPreview = True
        self.selectedElement = []
            
    def updateDeepComponentCoord(self, nameAxis, value):
        if self.selectedSourceAxis:
            index = 0
            for i, x in enumerate(self._glyphVariations):
                if x.sourceName == self.selectedSourceAxis:
                    index = i
                    break
            self._glyphVariations[index].deepComponents[self.selectedElement[0]].coord[nameAxis] = value
            # self._glyphVariations[self.selectedSourceAxis][self.selectedElement[0]].coord[nameAxis] = value
        else:
            self._deepComponents[self.selectedElement[0]].coord[nameAxis]=value

    def removeVariationAxis(self, name):
        index = 0
        for i, x in enumerate(self._axes):
            if x.name == name:
                index = i
        self._glyphVariations.removeVariation(index)
        self._axes.removeAxis(index)

    @glyphAddRemoveUndo
    def addDeepComponentNamed(self, deepComponentName, items = False):
        if not items:
            d = DeepComponentNamed(deepComponentName)
            dcglyph = self.currentFont[deepComponentName]
            for i, axis in enumerate(dcglyph._axes):
                value = dcglyph._axes[i].defaultValue
                d.coord.add(axis.name, value)
        else:
            d = items
            d.name = deepComponentName

        self._deepComponents.addDeepComponent(d)
        if self._axes:
            self._glyphVariations.addDeepComponent(d)
        self.redrawSelectedElementSource = True
        self.redrawSelectedElementPreview = True
        self.selectedElement = []

        # self.preview.computeDeepComponentsPreview(update = False)
        # self.preview.computeDeepComponents(update = False)

        # font = self.getParent()
        # glyph = font[self.name]
        # font.writeGlif(glyph)


    def addCharacterGlyphNamedVariationToGlyph(self, name):
        if name in self._axes: return
        self._axes.addAxis({"name":name, "minValue":0, "maxValue":1})
        self._glyphVariations.addVariation({"deepComponents":self._deepComponents, "location":{name:1}}, self._axes)

    @glyphAddRemoveUndo
    def removeDeepComponentAtIndexToGlyph(self, indexes = []):
        if not self.selectedElement and not indexes: return
        if indexes:
            self.removeDeepComponents(indexes)
        else:
            self.removeDeepComponents(self.selectedElement)
        self.selectedElement = []
        self.redrawSelectedElementSource = True
        self.redrawSelectedElementPreview = True
        self.selectedElement = []

    def save(self):
        # color = self.markColor
        self.lib.clear()
        lib = RLib()

        # for axis, variations in self._glyphVariations.items():
        #     variations.layerName = axis
        #     try:
        #         axisGlyph = self._RFont.getLayer(variations.layerName)[self.name]
        #         variations.writeOutlines(axisGlyph)
        #         variations.setAxisWidth(axisGlyph.width)
        #     except:
        #         pass

        # lib[deepComponentsKeyOld] = self._deepComponents.getList()
        # lib[glyphVariationsKey] = self._glyphVariations.getList()

        lib[deepComponentsKey] = self._deepComponents.getList()
        lib[axesKey] = self._axes.getList()
        lib[variationGlyphsKey] = self._glyphVariations.getList()
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
        # self.markColor = color