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
from vanilla import *
from mojo.canvas import CanvasGroup
from mojo.UI import UpdateCurrentGlyphView
from mojo.roboFont import *
from AppKit import NSColor, NSNoBorder, NumberFormatter
import mojo.drawingTools as mjdt
from imp import reload
from utils import decorators
reload(decorators)
from utils import files
reload(files)

from views import sheets, drawer
reload(sheets)
reload(drawer)

import copy

lockedProtect = decorators.lockedProtect
refresh = decorators.refresh

transparentColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 1, 0)
numberFormatter = NumberFormatter()

def setListAesthetic(element):
    element.getNSTableView().setUsesAlternatingRowBackgroundColors_(False)
    element.getNSTableView().setBackgroundColor_(transparentColor)
    element.getNSScrollView().setDrawsBackground_(False)
    element.getNSScrollView().setBorderType_(NSNoBorder)

class AtomicView(CanvasGroup):

    def __init__(self, RCJKI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.RCJKI = RCJKI
        slider = SliderListCell(minValue = 0, maxValue = 1)

        self.horizontalLine = HorizontalLine((0, -175, -0, 1))
        # self.verticaleLine = VerticalLine((-1, -175, -0, -0))
        self.roundToGrid = CheckBox(
            (5, -165, -0, 20),
            'Round to grid',
            value = self.RCJKI.roundToGrid,
            callback = self.roundToGridCallback,
            sizeStyle = "small"
            )
        self.drawOnlyDeepolation = CheckBox(
            (150, -165, -0, 20),
            'Draw only deepolation',
            value = self.RCJKI.drawOnlyDeepolation,
            callback = self.drawOnlyDeepolationCallback,
            sizeStyle = "small"
            )

        self.AETextBox = TextBox(
            (0, -140, -0, 20), 
            "Atomic Element's Axis"
            )
        self.atomicElementsSliderValue = EditText(
            (-60, -140, -0, 20),
            "",
            callback=self.atomicElementsSliderValueCallback
            )
        self.atomicElementsList = List(
            (0, -120, -0, -20), 
            [],
            columnDescriptions = [
                    {"title": "Axis", "editable": False, "width": 100},
                    {"title": "Layer", "editable": False, "width": 100},
                    {"title": "PreviewValue", "cell": slider}],
            showColumnTitles = False,
            editCallback = self.atomicElementsListEditCallback,
            selectionCallback = self.atomicElementsListSelectionCallback,
            allowsMultipleSelection = False
            )
        setListAesthetic(self.atomicElementsList)

        self.addLayerToAtomicElement = Button(
            (0, -20, 150, 20),
            "+",
            sizeStyle = 'mini',
            callback = self.addLayerToAtomicElementCallback
            )
        # self.addLayerToAtomicElement.getNSButton().setShowsBorderOnlyWhileMouseInside_(True)

        self.removeLayerToAtomicElement = Button(
            (150, -20, -0, 20),
            "-",
            sizeStyle = 'mini',
            callback = self.removeLayerToAtomicElementCallback
            )
        # self.removeLayerToAtomicElement.getNSButton().setShowsBorderOnlyWhileMouseInside_(True)

    @refresh
    def roundToGridCallback(self, sender):
        self.RCJKI.roundToGrid = sender.get()
        self.computeCurrentGlyph(self.atomicElementsList)

    @refresh
    def drawOnlyDeepolationCallback(self, sender):
        self.RCJKI.drawOnlyDeepolation = sender.get()

    @lockedProtect
    def addLayerToAtomicElementCallback(self, sender):
        availableLayers = [l for l in self.RCJKI.currentGlyph._RGlyph.layers if l.layer.name!='foreground']
        if [l for l in self.RCJKI.currentGlyph._RGlyph.layers if l.name != 'foreground']:
            sheets.SelectLayerSheet(self.RCJKI, availableLayers)

    @refresh
    @lockedProtect
    def removeLayerToAtomicElementCallback(self, sender):
        sel = self.atomicElementsList.getSelection()
        if not sel:
            return
        layers = self.atomicElementsList.get()
        layerName = layers[sel[0]]["Axis"]
        self.RCJKI.currentGlyph.removeGlyphVariation(layerName)
        layers.pop(sel[0])
        self.atomicElementsList.set(layers)
        self.computeCurrentGlyph(self.atomicElementsList)

    @refresh
    @lockedProtect
    def atomicElementsListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            self.atomicElementsSliderValue.set("")
            return
        else:
            self.atomicElementsSliderValue.set(round(self.atomicElementsList.get()[sel[0]]['PreviewValue'], 3))

    @refresh
    @lockedProtect
    def atomicElementsSliderValueCallback(self, sender):
        sel = self.atomicElementsList.getSelection()
        if not sel:
            sender.set("")
            return
        value = sender.get()
        try: 
            value = float(value.replace(",", "."))
        except:
            return
        newList = []
        for i, e in enumerate(self.atomicElementsList.get()):
            if i != sel[0]:
                newList.append(e)
            else:
                newList.append({
                    "Axis":e["Axis"],
                    "Layer":e["Layer"],
                    "PreviewValue":value
                    })
            self.atomicElementsList.set(newList)

        self.atomicElementsList.setSelection(sel)
        self.computeCurrentGlyph(self.atomicElementsList)

    @refresh
    @lockedProtect
    def atomicElementsListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        self.atomicElementsSliderValue.set(round(sender.get()[sel[0]]['PreviewValue'], 3))
        self.computeCurrentGlyph(sender)

    def computeCurrentGlyph(self, sender):
        self.RCJKI.currentGlyph.sourcesList = sender.get()
        self.RCJKI.currentGlyph.computeDeepComponentsPreview()

class DCCG_View(CanvasGroup):

    def __init__(self, RCJKI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.RCJKI = RCJKI
        slider = SliderListCell(minValue = 0, maxValue = 1)
        self.horizontalLine = HorizontalLine((0, -275, -0, 1))
        # self.verticalLine = VerticalLine((-1, -275, -0, -0))

        self.roundToGrid = CheckBox(
            (5, -265, -0, 20),
            'Round to grid',
            value = self.RCJKI.roundToGrid,
            callback = self.roundToGridCallback,
            sizeStyle = "small"
            )
        
        self.drawOnlyDeepolation = CheckBox(
            (150, -265, -0, 20),
            'Draw only deepolation',
            value = self.RCJKI.drawOnlyDeepolation,
            callback = self.drawOnlyDeepolationCallback,
            sizeStyle = "small"
            )

        self.sourcesTitle = TextBox(
            (0, -240, -0, 20), 
            ""
            )
        self.sourcesSliderValue = EditText(
            (-60, -240, -0, 20),
            "",
            callback=self.sourcesSliderValueCallback
            )
        self.sourcesList = List(
            (0, -220, -0, -140), 
            [],
            columnDescriptions = [
                    {"title": "Axis", "editable": True, "width": 100},
                    {"title": "PreviewValue", "cell": slider}],
            showColumnTitles = False,
            selectionCallback = self.sourcesListSelectionCallback,
            doubleClickCallback = self.sourcesListDoubleClickCallback,
            editCallback = self.sourcesListEditCallback,
            allowsMultipleSelection = False
            )
        setListAesthetic(self.sourcesList)

        self.addVarAxis = Button(
            (0, -140, 150, 20),
            "+",
            sizeStyle = 'mini',
            callback = self.addVarAxisCallback
            )
        # self.addVarAxis.getNSButton().setShowsBorderOnlyWhileMouseInside_(True)

        self.removeVarAxis = Button(
            (150, -140, -0, 20),
            "-",
            sizeStyle = 'mini',
            callback = self.removeVarAxisCallback
            )
        # self.removeVarAxis.getNSButton().setShowsBorderOnlyWhileMouseInside_(True)

        self.sliderTitle = TextBox(
            (0, -120, -0, 20), 
            ""
            )
        self.sliderSliderValue = EditText(
            (-60, -120, -0, 20),
            "",
            callback=self.sliderSliderValueCallback
            )
        self.slidersList = List(
            (0, -100, -0, -20), 
            [],
            columnDescriptions = [
                    {"title": "Axis", "editable": False, "width": 100},
                    {"title": "PreviewValue", "cell": slider}],
            showColumnTitles = False,
            editCallback = self.slidersListEditCallback,
            selectionCallback = self.slidersListSelectiontCallback,
            allowsMultipleSelection = False
            )
        setListAesthetic(self.slidersList)
        self.selectedSourceAxis = None

    def roundToGridCallback(self, sender):
        self.RCJKI.roundToGrid = sender.get()
        self.RCJKI.updateDeepComponent()

    @refresh
    def drawOnlyDeepolationCallback(self, sender):
        self.RCJKI.drawOnlyDeepolation = sender.get()

    def setUI(self):
        if self.RCJKI.isDeepComponent:
            self.sourcesTitle.set("Deep Component's Axis")
            self.sliderTitle.set("Atomic Element's Axis")
        elif self.RCJKI.isCharacterGlyph:
            self.sourcesTitle.set("Font Variation's Axis")
            self.sliderTitle.set("Deep Component's Axis")

    @lockedProtect
    def sourcesListDoubleClickCallback(self, sender):
        if not sender.getSelection(): 
            self.RCJKI.currentGlyph.selectedSourceAxis = None
        else:
            isel = sender.getSelection()[0]
            self.RCJKI.currentGlyph.selectedSourceAxis = sender.get()[isel]['Axis']

        self.RCJKI.currentGlyph.selectedElement = []
        self.slidersList.set([])
        self.RCJKI.sliderValue = None
        self.RCJKI.sliderName = None

        self.RCJKI.updateDeepComponent()

    @lockedProtect
    def sourcesListSelectionCallback(self, sender):
        sel = self.sourcesList.getSelection()
        if not sel:
            self.selectedSourceAxis = None
            self.sourcesSliderValue.set('')
        else:
            self.selectedSourceAxis = self.sourcesList.get()[sel[0]]["Axis"]
            self.sourcesSliderValue.set(round(self.sourcesList.get()[sel[0]]["PreviewValue"], 3))
        self.RCJKI.updateDeepComponent()

    @lockedProtect
    def sourcesSliderValueCallback(self, sender):
        sel = self.sourcesList.getSelection()
        if not sel:
            sender.set("")
            return
        value = sender.get()
        try: 
            value = float(value.replace(",", "."))
        except:
            return
        newList = []
        for i, e in enumerate(self.sourcesList.get()):
            if i != sel[0]:
                newList.append(e)
            else:
                newList.append({
                    "Axis":e["Axis"],
                    "PreviewValue":value
                    })
            self.sourcesList.set(newList)

        self.RCJKI.currentGlyph.sourcesList = self.sourcesList.get()
        self.RCJKI.updateDeepComponent()
        self.sourcesList.setSelection(sel)

    @lockedProtect
    def sourcesListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            return
        edited = sender.getEditedColumnAndRow()
        if edited[0] == 0:
            name =  sender.get()[edited[1]]['Axis']
            if len([x for x in sender.get() if x['Axis'] == name]) > 1:
                i = 0
                while True:
                    name = sender.get()[edited[1]]['Axis'] + "_" + str(i).zfill(2)
                    if name not in [x["Axis"] for x in sender.get()]:
                        print(name)
                        break
                    i += 1

            if name != self.selectedSourceAxis:
                if self.RCJKI.currentGlyph.type != 'characterGlyph':
                    
                    self.RCJKI.currentGlyph.renameVariationAxis(self.selectedSourceAxis, name)
                    self.RCJKI.currentGlyph.selectedSourceAxis = name
            glyphVariations = self.RCJKI.currentGlyph._glyphVariations.keys()
            l = [{'Axis':axis, 'PreviewValue':0.5} for axis in glyphVariations]
            sender.set(l)
            sender.setSelection(sel)

        self.sourcesSliderValue.set(round(sender.get()[sel[0]]['PreviewValue'], 3))
        self.RCJKI.currentGlyph.sourcesList = sender.get()
        self.RCJKI.updateDeepComponent()

    @lockedProtect
    def addVarAxisCallback(self, sender):
        if self.RCJKI.isDeepComponent:
            l = 0
            name = files.normalizeCode(files.int_to_column_id(l), 4)
            while name in self.RCJKI.currentGlyph._glyphVariations.keys():
                l += 1
                name = files.normalizeCode(files.int_to_column_id(l), 4)

            self.RCJKI.currentGlyph.addVariationToGlyph(name)

            if self.RCJKI.currentGlyph._glyphVariations:
                source = [{'Axis':axis, 'PreviewValue':0.5} for axis in self.RCJKI.currentGlyph._glyphVariations]
            self.sourcesList.set(source)
            self.RCJKI.currentGlyph.sourcesList = source
            isel = len(source)
            self.sourcesList.setSelection([isel-1])
            self.selectedSourceAxis = source[isel-1]['Axis']
            self.RCJKI.currentGlyph.selectedSourceAxis = source[isel-1]['Axis']
            self.RCJKI.updateDeepComponent()       
            
        elif self.RCJKI.isCharacterGlyph:
            sheets.SelectFontVariationSheet(self.RCJKI, self)

    @lockedProtect
    def removeVarAxisCallback(self, sender):
        if self.sourcesList.getSelection():
            name = self.sourcesList.get()[self.sourcesList.getSelection()[0]]["Axis"]
            self.RCJKI.currentGlyph.removeVariationAxis(name)
            self.RCJKI.currentGlyph.selectedElement = []
            self.RCJKI.currentGlyph.selectedSourceAxis = None
            self.sourcesList.setSelection([0])
            glyphVariations = self.RCJKI.currentGlyph._glyphVariations.keys()
            l = [{'Axis':axis, 'PreviewValue':0.5} for axis in glyphVariations]
            self.RCJKI.currentGlyph.sourcesList = l
            self.sourcesList.set(l)
            self.slidersList.set([])
            self.RCJKI.sliderValue = None
            self.RCJKI.sliderName = None
            self.RCJKI.updateDeepComponent()

    @lockedProtect
    def slidersListSelectiontCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            self.sliderSliderValue.set('')
            return
        else:
            self.sliderSliderValue.set(round(sender.get()[sel[0]]["PreviewValue"], 3))

    @lockedProtect
    def sliderSliderValueCallback(self, sender):
        sel = self.slidersList.getSelection()
        if not sel:
            sender.set("")
            return
        value = sender.get()
        try: 
            value = float(value.replace(",", "."))
        except:
            return
        newList = []
        for i, e in enumerate(self.slidersList.get()):
            if i != sel[0]:
                newList.append(e)
            else:
                newList.append({
                    "Axis":e["Axis"],
                    "PreviewValue":value
                    })
            self.slidersList.set(newList)

        self.slidersList.setSelection(sel)
        self.setSliderValue2Glyph(self.slidersList)
        self.RCJKI.updateDeepComponent()
        

    @lockedProtect
    def slidersListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        if self.RCJKI.currentGlyph.type == 'characterGlyph':
            lib = RLib()
            deepComponentsKey = 'robocjk.characterGlyph.deepComponents'
            glyphVariationsKey = 'robocjk.characterGlyph.glyphVariations'
            lib[deepComponentsKey] = copy.deepcopy(self.RCJKI.currentGlyph._deepComponents)
            lib[glyphVariationsKey] = copy.deepcopy(self.RCJKI.currentGlyph._glyphVariations)
            self.RCJKI.currentGlyph.stackUndo_lib = self.RCJKI.currentGlyph.stackUndo_lib[:self.RCJKI.currentGlyph.indexStackUndo_lib]
            self.RCJKI.currentGlyph.stackUndo_lib.append(lib)
            self.RCJKI.currentGlyph.indexStackUndo_lib += 1

        self.setSliderValue2Glyph(sender)
        self.sliderSliderValue.set(round(sender.get()[sel[0]]["PreviewValue"], 3))
        self.RCJKI.updateDeepComponent()

    def setSliderValue2Glyph(self, sender):
        self.RCJKI.sliderValue = round(float(self.slidersList[sender.getSelection()[0]]['PreviewValue']), 3)
        sliderName = self.slidersList[sender.getSelection()[0]]['Axis']
        self.RCJKI.sliderName = sliderName
        if self.RCJKI.isDeepComponent:
            self.RCJKI.currentGlyph.updateAtomicElementCoord(self.RCJKI.sliderName, self.RCJKI.sliderValue)
        elif self.RCJKI.isCharacterGlyph:
            self.RCJKI.currentGlyph.updateDeepComponentCoord(self.RCJKI.sliderName, self.RCJKI.sliderValue)


class GlyphPreviewCanvas(CanvasGroup):

    def __init__(self, posSize, RCJKI, glyphType):
        super().__init__(posSize, delegate = self)
        self.RCJKI = RCJKI
        self.glyphType = glyphType
        self.glyphName = ''
        self.drawer = drawer.Drawer(RCJKI)

    def draw(self):
        if not self.RCJKI.get("currentFont"): return
        if not self.glyphName: return
        self.glyph = self.RCJKI.currentFont[self.glyphName]
        d = self.glyph._glyphVariations
        self.glyph.sourcesList = [
            {"Axis":axisName, "Layer":layerName, "PreviewValue":0.5} for axisName, layerName in  d.items()
            ]
        scale = .15
        mjdt.scale(scale, scale)
        mjdt.translate(((200-(self.glyph.width*scale))/scale)*.5, 450)
        self.glyph.computeDeepComponentsPreview()
        if self.glyphType == 'atomicElement':
            self.drawer.drawAtomicElementPreview(
                self.glyph, 
                scale, 
                color = (0, 0, 0, 1), 
                strokecolor = (0, 0, 0, 0)
                )

        elif self.glyphType == 'deepComponent':
            if self.glyph.preview:
                self.drawer.drawDeepComponentPreview(
                    self.glyph, 
                    scale, 
                    color = (0, 0, 0, 1), 
                    strokecolor = (0, 0, 0, 0)
                    )
            else:
                self.glyph.computeDeepComponents()
                self.drawer.drawGlyphAtomicInstance(
                    self.glyph, 
                    (0, 0, 0, 1), 
                    scale, 
                    (0, 0, 0, 1), flatComponentColor = (0, 0, 0, 1)
                    )

        elif self.glyphType == 'characterGlyph':
            if self.glyph.preview:
                self.drawer.drawCharacterGlyphPreview(
                    self.glyph, 
                    scale, 
                    color = (0, 0, 0, 1), 
                    strokecolor = (0, 0, 0, 0)
                    )
            else:
                self.glyph.computeDeepComponents()
                self.drawer.drawGlyphAtomicInstance(
                    self.glyph, 
                    (0, 0, 0, 1), 
                    scale, 
                    (0, 0, 0, 1), flatComponentColor = (0, 0, 0, 1)
                    )


