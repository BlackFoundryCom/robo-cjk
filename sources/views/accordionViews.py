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

from mojo.UI import AccordionView
from vanilla import *
from mojo.canvas import Canvas

from utils import decorators
lockedProtect = decorators.lockedProtect

class CompositionRulesGroup(Group):
    
    def __init__(self, posSize, RCJKI):
        super().__init__(posSize)
        self.RCJKI = RCJKI
        
        self.componentsList = List(
            (80, 0, 40, -0), [], 
            drawFocusRing = False,
            selectionCallback = self.componentsListSelectionCallback)
        self.variantList = List(
            (120, 0, 40, -0), [], 
            drawFocusRing = False,
            selectionCallback = self.variantListSelectionCallback)
        self.canvas = Canvas((160, 0, -40, -0), delegate = self)
        self.existingInstancesList = List(
            (-40, 0, 40, -0), [], 
            drawFocusRing = False,
            selectionCallback = self.existingInstancesListSelectionCallback
            )
        
    def draw(self):
        pass

    def componentsListSelectionCallback(self, sender):
        pass

    def variantListSelectionCallback(self, sender):
        pass

    def existingInstancesListSelectionCallback(self, sender):
        pass
        
class RelatedGlyphsGroup(Group):
    
    def __init__(self, posSize, RCJKI):
        super().__init__(posSize)
        self.RCJKI = RCJKI
        
        self.optionPopUpButton = PopUpButton(
            (0, 0, -0, 20), [], 
            sizeStyle = "mini",
            callback = self.optionPopUpButtonCallback)
        self.variantList = List(
            (80, 16, 40, -0), [],
            drawFocusRing = False, 
            selectionCallback = self.variantListSelectionCallback)
        
        self.previewValue = 1
        self.previewCheckBox = CheckBox(
            (125, 20, 120, 20), "Preview", 
            value = self.previewValue, 
            sizeStyle = "small",
            callback = self.previewCheckBoxCallback)
        
        self.sliderPositionX = Slider(
            (125, 40, -10, 20), 
            minValue = -1000,
            maxValue = 1000, 
            value = 0,
            callback = self.sliderPositionXCallback)
        self.sliderPositionY = Slider(
            (125, 60, -10, 20), 
            minValue = -1000, 
            maxValue = 1000, 
            value = 0,
            callback = self.sliderPositionYCallback)
        
        self.scaleXEditText = EditText(
            (125, 80, 50, 20), 1, 
            sizeStyle = "small",
            callback = self.scaleXEditTextCallback)
        self.scaleYEditText = EditText(
            (175, 80, 50, 20), 1, 
            sizeStyle = "small",
            callback = self.scaleYEditTextCallback)
        
    def draw(self):
        pass

    def optionPopUpButtonCallback(self, sender):
        pass

    def variantListSelectionCallback(self, sender):
        pass

    def previewCheckBoxCallback(self, sender):
        pass

    def sliderPositionXCallback(self, sender):
        pass

    def sliderPositionYCallback(self, sender):
        pass

    def scaleXEditTextCallback(self, sender):
        pass

    def scaleYEditTextCallback(self, sender):
        pass
        
class PreviewGroup(Group):
    
    def __init__(self, posSize, RCJKI):
        super().__init__(posSize)
        self.RCJKI = RCJKI
        
        self.canvas = Canvas((0, 0, -0, -25), delegate = self)
        self.roundToGrid = 0
        self.roundToGridCheckBox = CheckBox(
            (5, -20, 120, 20), 
            "Round to grid", 
            value = self.roundToGrid, 
            sizeStyle = "small",
            callback = self.roundToGridCheckBoxCallback
            )
        self.drawOnlyDeepolation = 0
        self.drawOnlyDeepolationCheckBox = CheckBox(
            (125, -20, 140, 20), 
            "Draw only deepolation", 
            value = self.drawOnlyDeepolation, 
            sizeStyle = "small",
            callback = self.drawOnlyDeepolationCheckBoxCallback)
        
    def roundToGridCheckBoxCallback(self, sender):
        pass
        
    def drawOnlyDeepolationCheckBoxCallback(self, sender):
        pass
        
    def draw(self):
        pass
        
class GlyphVariationAxesGroup(Group):
    
    def __init__(self, posSize, RCJKI, glyphtype, glyphVariationsAxes):
        super().__init__(posSize)
        self.RCJKI = RCJKI
        self.glyphVariationsAxes = glyphVariationsAxes
        
        slider = SliderListCell(minValue = 0, maxValue = 1)
        
        self.sliderValueTitle = TextBox((-160, 3, -100, 20), "Axis value:", sizeStyle = 'small')
        self.sliderValueEditText = EditText((-100, 0, -0, 20), '', callback = self.sliderValueEditTextCallback)
        
        y = -20
        if glyphtype in ["deepComponent", "atomicElement"]:
            y = -40
        
        self.glyphVariationAxesList = List(
            (0, 25, -0, y), 
            self.glyphVariationsAxes, 
            columnDescriptions = [
                    {"title": "Axis", "editable": True, "width": 100},
                    {"title": "MinValue", "editable": True, "width": 40},
                    {"title": "PreviewValue", "cell": slider},
                    {"title": "MaxValue", "editable": True, "width": 40}],
            selectionCallback = self.glyphVariationAxesListSelectionCallback,
            editCallback = self.glyphVariationAxesListEditCallback,
            doubleClickCallback = self.glyphVariationAxesListDoubleClickCallback,
            drawFocusRing = False,
            showColumnTitles = False
            )
        if glyphtype in ["deepComponent", "atomicElement"]:
            y = -20
        
        self.addGlyphVariationButton = Button(
            (0, y, 150, 20), '+', 
            sizeStyle = 'small', 
            callback = self.addGlyphVariationButtonCallback
            )
        self.removeGlyphVariationButton = Button(
            (150, y, 150, 20), '-', 
            sizeStyle = 'small',
            callback = self.removeGlyphVariationButtonCallback)
            
        if glyphtype in ["deepComponent", "atomicElement"]:
            self.editSelectedAxisExtremeValueButton = Button(
                (0, y-20, 200, 20), 
                "Edit selected axis extreme value", 
                sizeStyle = "small",
                callback = self.editSelectedAxisExtremeValueButtonCallback)
            self.setLocationTo1Button = Button(
                (200, y-20, 100, 20), 
                "Set location to 1", 
                sizeStyle = "small",
                callback = self.setLocationTo1ButtonCallback)
        
    @lockedProtect
    def sliderValueEditTextCallback(self, sender):
        pass
        
    @lockedProtect
    def glyphVariationAxesListSelectionCallback(self, sender):
        pass
        
    @lockedProtect
    def glyphVariationAxesListEditCallback(self, sender):
        pass
        
    @lockedProtect
    def glyphVariationAxesListDoubleClickCallback(self, sender):
        pass
        
    @lockedProtect
    def addGlyphVariationButtonCallback(self, sender):
        pass
        
    @lockedProtect
    def removeGlyphVariationButtonCallback(self, sender):
        pass
        
    def editSelectedAxisExtremeValueButtonCallback(self, sender):
        pass
        
    def setLocationTo1ButtonCallback(self, sender):
        pass
        
class DeepComponentAxesGroup(Group):
    
    def __init__(self, posSize, RCJKI, deepComponentAxes):
        super().__init__(posSize)
        self.RCJKI = RCJKI
        self.deepComponentAxes = deepComponentAxes
        
        slider = SliderListCell(minValue = 0, maxValue = 1)
        
        self.sliderValueTitle = TextBox((-160, 3, -100, 20), "Axis value:", sizeStyle = 'small')
        self.sliderValueEditText = EditText((-100, 0, -0, 20), '', callback = self.sliderValueEditTextCallback)
        
        self.deepComponentAxesList = List(
            (0, 25, -0, -0), 
            self.deepComponentAxes, 
            columnDescriptions = [
                    {"title": "Axis", "editable": False, "width": 100},
                    {"title": "MinValue", "editable": False, "width": 40},
                    {"title": "PreviewValue", "cell": slider},
                    {"title": "MaxValue", "editable": False, "width": 40}],
            selectionCallback = self.deepComponentAxesListSelectionCallback,
            editCallback = self.deepComponentAxesListEditCallback,
            doubleClickCallback = self.deepComponentAxesListDoubleClickCallback,
            drawFocusRing = False,
            showColumnTitles = False
            )
        
    @lockedProtect
    def sliderValueEditTextCallback(self, sender):
        pass
    
    @lockedProtect    
    def deepComponentAxesListSelectionCallback(self, sender):
        pass
        
    @lockedProtect
    def deepComponentAxesListEditCallback(self, sender):
        pass
        
    @lockedProtect
    def deepComponentAxesListDoubleClickCallback(self, sender):
        pass
        
class PropertiesGroup(Group):
    
    def __init__(self, posSize, RCJKI):
        super().__init__(posSize)
        self.RCJKI = RCJKI
        
        self.glyphState = PopUpButton(
            (5, 5, -100, 20),
            ["In Progress", "Checking round 1", "Checking round 2", "Checking round 3", "Done"],
            callback = self.glyphStateCallback
            )

        self.glyphStateColor = ColorWell(
            (-100, 5, -5, 20)
            )
        self.glyphStateColor.getNSColorWell().setBordered_(False)

    def glyphStateCallback(self, sender):
        pass

class CharacterGlyphInspector:

    def __init__(self, RCJKI, glyphVariationsAxes = [], deepComponentAxes = []):
        self.RCJKI = RCJKI
        self.glyphVariationsAxes = glyphVariationsAxes
        self.deepComponentAxes = deepComponentAxes
        
        self.w = Window((300, 850), "Character glyph", minSize = (100, 200))
        
        self.compositionRulesItem = CompositionRulesGroup((0, 0, -0, -0), self.RCJKI)
        self.previewItem = PreviewGroup((0, 0, -0, -0), self.RCJKI)
        self.fontVariationAxesItem = GlyphVariationAxesGroup((0, 0, -0, -0), self.RCJKI, "characterGlyph", glyphVariationsAxes)
        self.deepComponentAxesItem = DeepComponentAxesGroup((0, 0, -0, -0), self.RCJKI, deepComponentAxes)
        self.propertiesItem = PropertiesGroup((0, 0, -0, -0), self.RCJKI)

        descriptions = [
                       dict(label="Composition Rules", view=self.compositionRulesItem, size=100, collapsed=False, canResize=True),
                       dict(label="Preview", view=self.previewItem, minSize=100, size=300, collapsed=False, canResize=True),
                       dict(label="Font variation axes", view=self.fontVariationAxesItem, minSize=80, size=150, collapsed=False, canResize=True),
                       dict(label="Deep component axes", view=self.deepComponentAxesItem, minSize=100, size=150, collapsed=False, canResize=True),
                       dict(label="Properties", view=self.propertiesItem, minSize = 80, size=80, collapsed=False, canResize=True)
                       ]

        self.w.accordionView = AccordionView((0, 0, -0, -0), descriptions)
        self.w.open()
        
class DeepComponentInspector:

    def __init__(self, RCJKI, glyphVariationsAxes = [], atomicElementAxes = []):
        self.RCJKI = RCJKI
        self.w = Window((300, 870), "Deep Component", minSize = (100, 200))
        
        self.relatedGlyphsItem = RelatedGlyphsGroup((0, 0, -0, -0), self.RCJKI)
        self.previewItem = PreviewGroup((0, 0, -0, -0), self.RCJKI)
        self.deepComponentAxesItem = GlyphVariationAxesGroup((0, 0, -0, -0), self.RCJKI, "deepComponent", glyphVariationsAxes)
        self.atomicElementAxesItem = DeepComponentAxesGroup((0, 0, -0, -0), self.RCJKI, atomicElementAxes)
        self.propertiesItem = PropertiesGroup((0, 0, -0, -0), self.RCJKI)

        descriptions = [
                       dict(label="Related glyphs", view=self.relatedGlyphsItem, size=100, collapsed=False, canResize=True),
                       dict(label="Preview", view=self.previewItem, minSize=100, size=300, collapsed=False, canResize=True),
                       dict(label="Deep component axes", view=self.deepComponentAxesItem, minSize=100, size=170, collapsed=False, canResize=True),
                       dict(label="Atomic element axes", view=self.atomicElementAxesItem, minSize=100, size=150, collapsed=False, canResize=True),
                       dict(label="Properties", view=self.propertiesItem, minSize = 80, size=80, collapsed=False, canResize=True)
                       ]

        self.w.accordionView = AccordionView((0, 0, -0, -0), descriptions)
        self.w.open()
        
class AtomicElementInspector:

    def __init__(self, RCJKI, glyphVariationsAxes = []):
        self.RCJKI = RCJKI
        self.w = Window((300, 600), "Atomic element", minSize = (100, 200))
        
        self.previewItem = PreviewGroup((0, 0, -0, -0), self.RCJKI)
        self.atomicElementAxesItem = GlyphVariationAxesGroup((0, 0, -0, -0), self.RCJKI, "atomicElement", glyphVariationsAxes)
        self.propertiesItem = PropertiesGroup((0, 0, -0, -0), self.RCJKI)

        descriptions = [
                       dict(label="Preview", view=self.previewItem, minSize=100, size=300, collapsed=False, canResize=True),
                       dict(label="Atomic element axes", view=self.atomicElementAxesItem, minSize=100, size=170, collapsed=False, canResize=True),
                       dict(label="Properties", view=self.propertiesItem, minSize = 80, size=80, collapsed=False, canResize=True)
                       ]

        self.w.accordionView = AccordionView((0, 0, -0, -0), descriptions)
        self.w.open()

# CharacterGlyphInspector("RCJKI", glyphVariationsAxes = [], deepComponentAxes = [])
# DeepComponentInspector("RCJKI", glyphVariationsAxes = [], atomicElementAxes = [])
# AtomicElementInspector("RCJKI", glyphVariationsAxes = [])
