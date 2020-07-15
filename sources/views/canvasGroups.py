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
# reload(decorators)
from utils import files
# reload(files)

from views import sheets, drawer
# reload(sheets)
# reload(drawer)

import copy

lockedProtect = decorators.lockedProtect
refresh = decorators.refresh

transparentColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 1, 0)
numberFormatter = NumberFormatter()

INPROGRESS = (1, 0, 0, 1)
CHECKING1 = (1, .5, 0, 1)
CHECKING2 = (1, 1, 0, 1)
CHECKING3 = (0, 0, 1, 1)
VALIDATE = (0, 1, .5, 1)
STATE_COLORS = (INPROGRESS, CHECKING1, CHECKING2, CHECKING3, VALIDATE)

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
                    {"title": "Axis", "editable": False, "width": 80},
                    {"title": "Layer", "editable": False, "width": 80},
                    {"title": "MinValue", "editable": True, "width": 40},
                    {"title": "PreviewValue", "cell": slider},
                    {"title": "MaxValue", "editable": True, "width": 40},
                    ],
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
        print(availableLayers)
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
            minValue = round(sender.get()[sel[0]]['MinValue'], 3)
            maxValue = round(sender.get()[sel[0]]['MaxValue'], 3)
            sliderValue = round(sender.get()[sel[0]]['PreviewValue'], 3)
            self.atomicElementsSliderValue.set(self.RCJKI.userValue(sliderValue, minValue, maxValue))
            # self.atomicElementsSliderValue.set(round(self.atomicElementsList.get()[sel[0]]['PreviewValue'], 3))

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
                minValue = float(e["MinValue"])
                maxValue = float(e["MaxValue"])
                newList.append({
                    "Axis":e["Axis"],
                    "Layer":e["Layer"],
                    "MinValue":e["MinValue"],
                    "PreviewValue":self.RCJKI.systemValue(value, minValue, maxValue),
                    "MaxValue":e["MaxValue"],
                    })
            self.atomicElementsList.set(newList)

        self.atomicElementsList.setSelection(sel)
        self.computeCurrentGlyph(self.atomicElementsList)

    @refresh
    @lockedProtect
    def atomicElementsListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        
        values = sender.get()[sel[0]]
        axis = values["Axis"]
        minValue = float(values["MinValue"])
        maxValue = float(values["MaxValue"])

        sliderValue = round(sender.get()[sel[0]]['PreviewValue'], 3)
        # UIValue = minValue + (maxValue-minValue)*sliderValue
        self.atomicElementsSliderValue.set(self.RCJKI.userValue(sliderValue, minValue, maxValue))


        self.RCJKI.currentGlyph._glyphVariations[axis].minValue = minValue
        self.RCJKI.currentGlyph._glyphVariations[axis].maxValue = maxValue
        self.computeCurrentGlyph(sender)

    def computeCurrentGlyph(self, sender):
        self.RCJKI.currentGlyph.sourcesList = sender.get()
        self.RCJKI.currentGlyph.preview.computeDeepComponentsPreview(sender.get())

class DCCG_View(CanvasGroup):

    def __init__(self, RCJKI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.RCJKI = RCJKI
        slider = SliderListCell(minValue = 0, maxValue = 1)
        self.horizontalLine = HorizontalLine((0, -275, -0, 1))
        # self.verticalLine = VerticalLine((-1, -275, -0, -0))

        self.roundToGrid = CheckBox(
            (5, -285, -0, 20),
            'Round to grid',
            value = self.RCJKI.roundToGrid,
            callback = self.roundToGridCallback,
            sizeStyle = "small"
            )
        
        self.drawOnlyDeepolation = CheckBox(
            (150, -285, -0, 20),
            'Draw only deepolation',
            value = self.RCJKI.drawOnlyDeepolation,
            callback = self.drawOnlyDeepolationCallback,
            sizeStyle = "small"
            )

        self.glyphState = PopUpButton(
            (5, -265, -100, 20),
            ["In Progress", "Checking round 1", "Checking round 2", "Checking round 3", "Validate"],
            callback = self.glyphStateCallback
            )
        # self.setglyphState()

        self.glyphStateColor = ColorWell(
            (-100, -265, -5, 20)
            )
        self.glyphStateColor.getNSColorWell().setBordered_(False)

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
                    {"title": "MinValue", "editable": True, "width": 40},
                    {"title": "PreviewValue", "cell": slider},
                    {"title": "MaxValue", "editable": True, "width": 40}],
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
                    {"title": "MinValue", "editable": False, "width": 40},
                    {"title": "PreviewValue", "cell": slider},
                    {"title": "MaxValue", "editable": False, "width": 40}],
            showColumnTitles = False,
            editCallback = self.slidersListEditCallback,
            selectionCallback = self.slidersListSelectiontCallback,
            allowsMultipleSelection = False
            )
        setListAesthetic(self.slidersList)
        self.selectedSourceAxis = None

    def setglyphState(self):
        color = self.RCJKI.currentGlyph.stateColor
        state = self.glyphState
        if color is None:
            state.set(0)
            self.glyphStateCallback(state)
        elif color == INPROGRESS:
            state.set(0)
        elif color == CHECKING1:
            state.set(1)
        elif color == CHECKING2:
            state.set(2)
        elif color == CHECKING3:
            state.set(3)
        elif color == VALIDATE:
            state.set(4)

    def glyphStateCallback(self, sender):
        state = sender.get()
        self.RCJKI.currentGlyph.stateColor = STATE_COLORS[state]
        self.glyphStateColor.set(NSColor.colorWithCalibratedRed_green_blue_alpha_(*STATE_COLORS[state]))

    def roundToGridCallback(self, sender):
        self.RCJKI.roundToGrid = sender.get()
        self.RCJKI.updateDeepComponent(update = False)

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
        self.setglyphState()

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

        self.RCJKI.updateDeepComponent(update = False)
        
    @lockedProtect
    def sourcesListSelectionCallback(self, sender):
        sel = self.sourcesList.getSelection()
        if not sel:
            self.selectedSourceAxis = None
            self.sourcesSliderValue.set('')
        else:
            self.selectedSourceAxis = self.sourcesList.get()[sel[0]]["Axis"]
            self.sourcesSliderValue.set(round(self.sourcesList.get()[sel[0]]["PreviewValue"], 3))
        self.RCJKI.updateDeepComponent(update = False)

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
                minValue = float(e["MinValue"])
                maxValue = float(e["MaxValue"])
                newList.append({
                    "Axis":e["Axis"],
                    "MinValue":e["MinValue"],
                    "PreviewValue":self.RCJKI.systemValue(value, minValue, maxValue),
                    "MaxValue":e["MaxValue"],
                    })
            self.sourcesList.set(newList)

        self.RCJKI.currentGlyph.sourcesList = self.sourcesList.get()
        self.RCJKI.updateDeepComponent(update = False)
        self.sourcesList.setSelection(sel)

    @lockedProtect
    def sourcesListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            return
        edited = sender.getEditedColumnAndRow()
        values = sender.get()[sel[0]]
        axis = values["Axis"]
        minValue = float(values["MinValue"])
        maxValue = float(values["MaxValue"])

        sliderValue = round(sender.get()[sel[0]]['PreviewValue'], 3)

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
            glyphVariations = self.RCJKI.currentGlyph._glyphVariations.axes
            # l = [{'Axis':axis, 'PreviewValue':0, "MinValue":axis.minValue, "MaxValue":axis.maxValue} for axis in glyphVariations]
            l = [{'Axis':axis, 'PreviewValue':0, "MinValue":value.minValue, "MaxValue":value.maxValue} for axis, value in self.RCJKI.currentGlyph._glyphVariations.items()]
            sender.set(l)
            sender.setSelection(sel)
        elif edited[0] in [1, 3]:
            self.RCJKI.currentGlyph._glyphVariations[axis].minValue = minValue
            self.RCJKI.currentGlyph._glyphVariations[axis].maxValue = maxValue
        self.sourcesSliderValue.set(self.RCJKI.userValue(sliderValue, minValue, maxValue))

        # self.sourcesSliderValue.set(round(sender.get()[sel[0]]['PreviewValue'], 3))
        self.RCJKI.currentGlyph.sourcesList = sender.get()
        self.RCJKI.updateDeepComponent(update = False)

    @lockedProtect
    def addVarAxisCallback(self, sender):
        if self.RCJKI.isDeepComponent:
            l = 0
            name = files.normalizeCode(files.int_to_column_id(l), 4)
            while name in self.RCJKI.currentGlyph._glyphVariations.axes:
                l += 1
                name = files.normalizeCode(files.int_to_column_id(l), 4)

            self.RCJKI.currentGlyph.addVariationToGlyph(name)

            if self.RCJKI.currentGlyph._glyphVariations:
                source = [{'Axis':axis, 'PreviewValue':0, "MinValue":value.minValue, "MaxValue":value.maxValue} for axis, value in self.RCJKI.currentGlyph._glyphVariations.items()]
            self.sourcesList.set(source)
            self.RCJKI.currentGlyph.sourcesList = source
            isel = len(source)
            self.sourcesList.setSelection([isel-1])
            self.selectedSourceAxis = source[isel-1]['Axis']
            self.RCJKI.currentGlyph.selectedSourceAxis = source[isel-1]['Axis']
            self.RCJKI.updateDeepComponent(update = False)       
            
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
            glyphVariations = self.RCJKI.currentGlyph._glyphVariations.axes
            l = [{'Axis':axis, 'PreviewValue':0, "MinValue":value.minValue, "MaxValue":value.maxValue} for axis, value in self.RCJKI.currentGlyph._glyphVariations.items()]
            self.RCJKI.currentGlyph.sourcesList = l
            self.sourcesList.set(l)
            self.slidersList.set([])
            self.RCJKI.sliderValue = None
            self.RCJKI.sliderName = None
            self.RCJKI.updateDeepComponent(update = False)

    @lockedProtect
    def slidersListSelectiontCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            self.sliderSliderValue.set('')
            return
        else:
            values = sender.get()[sel[0]]
            minValue, maxValue = self.RCJKI.currentGlyph.getDeepComponentMinMaxValue(self.slidersList[sel[0]]['Axis'])
            sliderValue = round(sender.get()[sel[0]]['PreviewValue'], 3)
            self.sliderSliderValue.set(self.RCJKI.userValue(sliderValue, minValue, maxValue))

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
        # if self.RCJKI.currentGlyph.type == "deepComponent":
        minValue, maxValue = self.RCJKI.currentGlyph.getDeepComponentMinMaxValue(self.slidersList[sel[0]]['Axis'])
        for i, e in enumerate(self.slidersList.get()):
            if i != sel[0]:
                newList.append(e)
            else:
                # if self.RCJKI.currentGlyph.type == "deepComponent":
                newList.append({
                    "Axis":e["Axis"],
                    "MinValue": minValue,
                    "PreviewValue":self.RCJKI.systemValue(value, minValue, maxValue),
                    "MaxValue": maxValue,
                    })
                # else:
                #     newList.append({
                #         "Axis":e["Axis"],
                #         "PreviewValue":value
                #         })
            self.slidersList.set(newList)

        self.slidersList.setSelection(sel)
        self.setSliderValue2Glyph(self.slidersList)
        self.RCJKI.updateDeepComponent(update = False)
        
    @lockedProtect
    def slidersListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return         
        self.setSliderValue2Glyph(sender)
        # self.sliderSliderValue.set(round(sender.get()[sel[0]]["PreviewValue"], 3))
        # if self.RCJKI.currentGlyph.type == "deepComponent":
        minValue, maxValue = self.RCJKI.currentGlyph.getDeepComponentMinMaxValue(self.slidersList[sender.getSelection()[0]]['Axis'])
        self.sliderSliderValue.set(self.RCJKI.userValue(round(sender.get()[sel[0]]["PreviewValue"], 3), minValue, maxValue))
        # else:
        #     self.sliderSliderValue.set(round(sender.get()[sel[0]]["PreviewValue"], 3))
        self.RCJKI.updateDeepComponent(update = False)

    def setSliderValue2Glyph(self, sender):
        def _getKeys(glyph):
            if glyph.type == "characterGlyph":
                return 'robocjk.deepComponents', 'robocjk.fontVariationGlyphs'
            else:
                return 'robocjk.deepComponents', 'robocjk.glyphVariationGlyphs'

        if self.RCJKI.currentGlyph.type in ['characterGlyph', 'deepComponent']:
            lib = RLib()
            deepComponentsKey, glyphVariationsKey = _getKeys(self.RCJKI.currentGlyph)
            # glyphVariationsKey = 'robocjk.characterGlyph.glyphVariations'
            lib[deepComponentsKey] = copy.deepcopy(self.RCJKI.currentGlyph._deepComponents.getList())
            lib[glyphVariationsKey] = copy.deepcopy(self.RCJKI.currentGlyph._glyphVariations.getDict())
            self.RCJKI.currentGlyph.stackUndo_lib = self.RCJKI.currentGlyph.stackUndo_lib[:self.RCJKI.currentGlyph.indexStackUndo_lib]
            self.RCJKI.currentGlyph.stackUndo_lib.append(lib)
            self.RCJKI.currentGlyph.indexStackUndo_lib += 1
            
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
        if self.glyph.type ==  "atomicElement":
            self.glyph.sourcesList = [
                {"Axis":axisName, "Layer":layer, "PreviewValue":0} for axisName, layer in  d.items()
                ]
        else:
            self.glyph.sourcesList = [
                {"Axis":axisName, "Layer":layerName, "PreviewValue":0} for axisName, layerName in  d.items()
                ]
        try:
            # print(type(self.glyph.color), self.glyph.color)
            if self.glyph._RGlyph.markColor is not None:
                print("here")
                # print('here', self.glyph._RGlyph.markColor)
            #     mjdt.fill(*(1, 0, 0, 1))
            mjdt.rect(0, 0, 200, 20)
            mjdt.fill(None)
        except:
            pass
        scale = .15
        mjdt.scale(scale, scale)
        mjdt.translate(((200-(self.glyph.width*scale))/scale)*.5, 450)
        self.glyph.preview.computeDeepComponentsPreview(update = False)
        if self.glyph.preview.variationPreview is not None:
            self.drawer.drawVariationPreview(
                    self.glyph, 
                    scale, 
                    color = (0, 0, 0, 1), 
                    strokecolor = (0, 0, 0, 0)
                    )
        else:
            self.glyph.preview.computeDeepComponents(update = False)
            self.drawer.drawAxisPreview(
                self.glyph, 
                (0, 0, 0, 1), 
                scale, 
                (0, 0, 0, 1), flatComponentColor = (0, 0, 0, 1)
                )

