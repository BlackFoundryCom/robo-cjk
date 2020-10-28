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

from mojo.UI import AccordionView, UpdateCurrentGlyphView
from vanilla import *
from mojo.roboFont import *
from mojo.canvas import Canvas, CanvasGroup
import mojo.drawingTools as mjdt
from AppKit import NSColor, NSFont
from utils import decorators, files
from views import sheets
import os, copy

lockedProtect = decorators.lockedProtect
refresh = decorators.refresh
EditButtonImagePath = os.path.join(os.getcwd(), "resources", "EditButton.pdf")
alignLeftButtonImagePath = os.path.join(os.getcwd(), "resources", "alignLeftButton.pdf")
alignTopButtonImagePath = os.path.join(os.getcwd(), "resources", "alignTopButton.pdf")
alignRightButtonImagePath = os.path.join(os.getcwd(), "resources", "alignRightButton.pdf")
alignBottomButtonImagePath = os.path.join(os.getcwd(), "resources", "alignBottomButton.pdf")

class SmartTextBox(TextBox):
    def __init__(self, posSize, text="", alignment="natural", 
        selectable=False, callback=None, sizeStyle=40.0,
        red=0,green=0,blue=0, alpha=1.0):
        super(SmartTextBox, self).__init__(posSize, text=text, alignment=alignment, 
            selectable=selectable, sizeStyle=sizeStyle)
        
    def _setSizeStyle(self, sizeStyle):
        value = sizeStyle
        self._nsObject.cell().setControlSize_(value)
        font = NSFont.systemFontOfSize_(value)
        self._nsObject.setFont_(font)

class EditingSheet():

    def __init__(self, controller, RCJKI):
        self.RCJKI = RCJKI
        self.c = controller
        self.w = Sheet((240, 80), self.c.controller.w)
        self.char =  self.c.char.get()
        self.w.char = SmartTextBox(
            (0, 0, 80, -0),
            self.char,
            sizeStyle = 65,
            alignment = "center"
            )
        self.w.editField = TextEditor(
            (80, 0, -0, -20),
            ""
            )
        self.w.closeButton = Button(
            (80, -20, -0, -0),
            "Close",
            sizeStyle = "small",
            callback = self.closeCallback
            )

        self.setUI()
        self.w.open()

    def setUI(self):
        unicode = str(hex(self.RCJKI.currentGlyph.unicode)[2:])
        self.w.editField.set(self.RCJKI.currentFont.selectDatabaseKey(unicode))

    def closeCallback(self, sender):
        components = list(self.w.editField.get())
        self.RCJKI.currentFont.updateDatabaseKey(str(hex(self.RCJKI.currentGlyph.unicode)[2:]), components)
        if not self.RCJKI.currentFont.mysqlFont:
            self.RCJKI.exportDataBase()
        self.c.componentsList.set(components)
        self.w.close()

class CompositionRulesGroup(Group):
    
    def __init__(self, posSize, RCJKI, controller):
        super().__init__(posSize)
        self.RCJKI = RCJKI
        self.controller = controller
        self.glyph = None
        self.char = SmartTextBox(
            (0, 0, 80, -0),
            "",
            sizeStyle = 65,
            alignment = "center"
            )
        self.editButton = ImageButton(
            (0, -15, 15, -0),
            EditButtonImagePath,
            bordered = False,
            callback = self.editButtonCallback
            )
        self.componentsList = List(
            (80, 0, 40, -0), [], 
            drawFocusRing = False,
            selectionCallback = self.componentsListSelectionCallback)
        
        self.variantList = List(
            (120, 0, 40, -0), [], 
            drawFocusRing = False,
            selectionCallback = self.variantListSelectionCallback,
            doubleClickCallback = self.variantListDoubleClickCallback)
        self.existingInstancesList = List(
            (-40, 0, 40, -20), [], 
            drawFocusRing = False,
            selectionCallback = self.existingInstancesListSelectionCallback,
            doubleClickCallback = self.existingInstancesListDoubleClickCallback
            )
        self.canvas = CanvasGroup((160, 0, -40, -0), delegate = self)
        self.deselectButton = Button(
            (-40, -20, -0, 20), "✖", 
            sizeStyle = 'small', 
            callback = self.deselectButtonCallback)
        
        self.setUI()

    def setUI(self):
        if not self.RCJKI.currentFont.dataBase or not self.RCJKI.currentGlyph.name.startswith("uni"): return
        if not self.RCJKI.currentGlyph.unicode and self.RCJKI.currentGlyph.name.startswith('uni'):
            try:
                self.RCJKI.currentGlyph.unicode = int(self.RCJKI.currentGlyph.name[3:], 16)
            except:
                print('this glyph has no Unicode')
                return
        char = chr(self.RCJKI.currentGlyph.unicode)
        d = self.RCJKI.currentFont.dataBase.get(char, [])
        if d is None:
            d = []
        self.componentsList.set(d)
        self.char.set(char)

    def editButtonCallback(self, sender):
        EditingSheet(self, self.RCJKI)
        
    def draw(self):
        if self.glyph is None: return
        mjdt.save()
        mjdt.translate(20, 25)
        mjdt.scale(.04)
        mjdt.fill(0, 0, 0, 1)
        for atomicInstance in self.glyph.preview.axisPreview:
            mjdt.drawGlyph(atomicInstance.getTransformedGlyph()) 
        mjdt.restore()

    def componentsListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            self.variantList.set([])
            return
        char = sender.get()[sel[0]]
        self.code = files.normalizeUnicode(hex(ord(char))[2:].upper())
        dcName = "DC_%s_00"%self.code
        deepComponentSet = self.RCJKI.currentFont.deepComponentSet
        if dcName not in deepComponentSet: 
            self.variantList.set([])
            return
        index = deepComponentSet.index(dcName)
        l = ["00"]
        i = 1
        while True:
            name = "DC_%s_%s"%(self.code, str(i).zfill(2))
            if not name in deepComponentSet:
                break
            l.append(str(i).zfill(2))
            i += 1
        self.variantList.set(l)

    def variantListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            try:
                self.existingInstancesList.setSelection([])
                self.existingInstancesList.set([])
            except:pass
            self.glyph = None
            self.RCJKI.drawer.existingInstance = None
            self.RCJKI.drawer.existingInstancePos = [0, 0]
            self.canvas.update()
            return
        index = sender.get()[sel[0]]
        self.deepComponentName = "DC_%s_%s"%(self.code, index)
        self.glyph = self.RCJKI.currentFont.get(self.deepComponentName)
        self.glyph.preview.computeDeepComponents(update = False)
        self.canvas.update()
        self.setExistingInstances(self.deepComponentName)

    def setExistingInstances(self, deepComponentName):
        self.existingDeepComponentInstances = {}
        f = self.RCJKI.currentFont
        for n in f.staticCharacterGlyphSet():
            g = f.get(n)
            for i, x in enumerate(g._deepComponents):
                if x.name == deepComponentName:
                    variations = {k:copy.deepcopy(y[i]) for k, y in g._glyphVariations.items()}
                    try:
                        self.existingDeepComponentInstances[chr(int(n[3:], 16))] = [copy.deepcopy(x), variations]
                    except:
                        self.existingDeepComponentInstances[n] = [copy.deepcopy(x), variations]
                    break
        self.existingInstancesList.set(list(self.existingDeepComponentInstances.keys()))

    def variantListDoubleClickCallback(self, sender):
        self.RCJKI.currentGlyph.addDeepComponentNamed(self.deepComponentName)
        self.RCJKI.updateDeepComponent(update = False)

    @refresh
    def existingInstancesListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            self.RCJKI.drawer.existingInstance = None
            self.RCJKI.drawer.existingInstancePos = [0, 0]
            self.deepComponentSettings = []
            self.deepComponentVariationSettings = []
            return
        char = sender.get()[sel[0]]
        self.deepComponentSettings, self.deepComponentVariationSettings = self.existingDeepComponentInstances[char]
        dcname = self.deepComponentSettings.name
        dcglyph = self.RCJKI.currentFont.get(dcname)
        axes = [{"Axis":axisName, "Layer":layer, "PreviewValue":self.deepComponentSettings['coord'][axisName]} for axisName, layer in dcglyph._glyphVariations.items()]
        dcglyph.preview.computeDeepComponentsPreview(axes)
        self.RCJKI.drawer.existingInstance = dcglyph.preview.variationPreview
        self.RCJKI.drawer.existingInstancePos = [self.deepComponentSettings.x, self.deepComponentSettings.y]

    def existingInstancesListDoubleClickCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        dcname = self.deepComponentSettings.name
        self.RCJKI.currentGlyph.addDeepComponentNamed(dcname, self.deepComponentSettings)

        for variation in self.RCJKI.currentGlyph._glyphVariations:
            if variation in self.deepComponentVariationSettings:
                dc = copy.deepcopy(self.deepComponentVariationSettings[variation])
                self.RCJKI.currentGlyph._glyphVariations[variation][-1].set(dc._toDict())

        self.deselectButtonCallback(None)

    @refresh
    def deselectButtonCallback(self, sender):
        self.RCJKI.drawer.existingInstance = None
        self.RCJKI.drawer.existingInstancePos = [0, 0]
        self.deepComponentSettings = []
        self.deepComponentVariationSettings = []
        self.existingInstancesList.setSelection([])
        
class RelatedGlyphsGroup(Group):

    filterRules = [
        "In font",
        "Not in font",
        "Can be designed with current deep components",
        "Can't be designed with current deep components",
        "All",
        "Have outlines", 
        "Custom list"
        ]
    
    def __init__(self, posSize, RCJKI, controller):
        super().__init__(posSize)
        self.RCJKI = RCJKI
        self.controller = controller

        self.backgroundCanvas = CanvasGroup((0, 0, -0, -0), delegate = self)
        self.filter = 0
        self.preview = 1
        self.title = TextBox((0, 5, -0, 20), "", sizeStyle = 'small', alignment = 'center')
        self.optionPopUpButton = PopUpButton(
            (0, 20, -0, 20), self.filterRules, 
            sizeStyle = "mini",
            callback = self.optionPopUpButtonCallback)
        self.customField = EditText((0, 37, -0, 20), "", callback = self.customFieldCallback)
        self.customField.show(False)
        self.charactersList = List(
            (80, 36, 40, -0), [],
            drawFocusRing = False, 
            selectionCallback = self.charactersListSelectionCallback)
        self.component = SmartTextBox(
            (0, 36, 80, -0),
            "",
            sizeStyle = 65,
            alignment = "center"
            )

        self.previewCheckBox = CheckBox(
            (125, 40, 120, 20), "Preview", 
            value = self.preview, 
            sizeStyle = "small",
            callback = self.previewCheckBoxCallback)

        self.sliders = Group((120, 65, -0, -0))
        self.sliders.show(False)
        
        self.sliders.sliderPositionX = Slider(
            (0, 0, -10, 20), 
            minValue = -1000,
            maxValue = 1000, 
            value = 0,
            callback = self.sliderPositionCallback)
        self.sliders.sliderPositionY = Slider(
            (0, 20, -10, 20), 
            minValue = -1000, 
            maxValue = 1000, 
            value = 0,
            callback = self.sliderPositionCallback)
        
        self.sliders.scaleXEditText = EditText(
            (0, 40, 50, 20), 1, 
            sizeStyle = "small",
            callback = self.scaleEditTextCallback)
        self.sliders.scaleYEditText = EditText(
            (50, 40, 50, 20), 1, 
            sizeStyle = "small",
            callback = self.scaleEditTextCallback)
        self.RCJKI.drawer.refGlyph = None
        self.RCJKI.drawer.refGlyphPos = [0, 0]
        self.char = ""
        self.setUI()
        
    def draw(self):
        pass

    def mouseDragged(self, point):
        x, y = self.RCJKI.drawer.refGlyphPos
        dx = point.deltaX()
        dy = point.deltaY()
        x += dx
        y -= dy
        sensibility = 1
        self.RCJKI.drawer.refGlyphPos = [x*sensibility, y*sensibility]  
        self.sliders.sliderPositionX.set(x)
        self.sliders.sliderPositionY.set(y)
        UpdateCurrentGlyphView()

    def optionPopUpButtonCallback(self, sender):
        self.filter = sender.get()
        self.filterCharacters()

    def filterCharacters(self):
        l = []
        characterGlyphSet = self.RCJKI.currentFont.staticCharacterGlyphSet()
        deepComponentSet = self.RCJKI.currentFont.staticDeepComponentSet()
        if self.filter == 4:
            l = list(self.relatedChars)
            title = "Related Characters"
        elif self.filter in [0, 1]:
            names = [files.unicodeName(c) for c in self.relatedChars]
            if self.filter == 0:
                result = set(names) & set(characterGlyphSet)
            else:
                result = set(names) - set(characterGlyphSet)
            title = self.filterRules[self.filter]
            l = [chr(int(n[3:], 16)) for n in result]

        elif self.filter in [2, 3]:
            DCSet = set([x for x in deepComponentSet if self.RCJKI.currentFont.get(x)._RGlyph.lib["robocjk.deepComponents"]])
            for c in self.relatedChars:
                compo = ["DC_%s_00"%files.normalizeUnicode(hex(ord(v))[2:].upper()) for v in self.RCJKI.currentFont.dataBase[c]]
                inside = len(set(compo) - DCSet) == 0
                if self.filter == 2 and inside:
                    l.append(c)
                elif self.filter == 3 and not inside:
                    l.append(c)
            title = " ".join(self.filterRules[self.filter].split(' ')[:3])

        elif self.filter == 5:
            names = [files.unicodeName(c) for c in self.relatedChars]
            l = []
            for name in names:
                try:
                    if len(self.RCJKI.currentFont.get(name)):
                        l.append(chr(int(name[3:], 16)))
                except:pass
            title = self.filterRules[self.filter]

        if self.filter == 6:
            self.charactersList.setPosSize((80, 56, 40, -0))
            self.component.setPosSize((0, 56, 80, -0))
            self.previewCheckBox.setPosSize((125, 60, 120, 20))
            self.sliders.setPosSize((120, 85, -0, -0))
            self.customField.show(True)
            title = "Custom List" 
        else:
            self.customField.show(False)
            self.charactersList.setPosSize((80, 36, 40, -0))
            self.component.setPosSize((0, 36, 80, -0))
            self.previewCheckBox.setPosSize((125, 40, 120, 20))
            self.sliders.setPosSize((120, 65, -0, -0))


        self.RCJKI.drawer.refGlyph = None
        self.RCJKI.drawer.refGlyphPos = [0, 0]   
        UpdateCurrentGlyphView()
        self.charactersList.set(l)
        self.title.set("%s %s"%(len(l), title))

    def customFieldCallback(self, sender):
        chars = sender.get()
        self.charactersList.set(chars)
        self.title.set("%s %s"%(len(chars), "Custom List"))

    def setRefGlyph(self, sender):
        sel = sender.getSelection()
        if not sel:
            self.RCJKI.drawer.refGlyph = None
            self.RCJKI.drawer.refGlyphPos = [0, 0]
            return
        char = sender.get()[sel[0]]
        if self.preview:
            try:
                glyph = self.RCJKI.currentFont.get(files.unicodeName(char))
            except:
                glyph = None
            self.RCJKI.drawer.refGlyph = glyph
            self.RCJKI.drawer.refGlyphPos = [self.sliders.sliderPositionX.get(), self.sliders.sliderPositionY.get()]  
            UpdateCurrentGlyphView()

    def setUI(self):
        if not self.RCJKI.currentGlyph.name.startswith("DC_"): return
        self.relatedChars = set()
        try:
            _, code, _ = self.RCJKI.currentGlyph.name.split("_") 
            char = chr(int(code, 16))
            for k, v in self.RCJKI.currentFont.dataBase.items():
                if char in v:
                    self.relatedChars.add(k)
        except: pass
        self.filterCharacters()
        self.component.set(char)

    def charactersListSelectionCallback(self, sender):
        self.previewCheckBox.show(self.filter in [0, 5, 6])
        self.sliders.show(self.filter in [0, 5, 6])
        if self.preview:
            self.setRefGlyph(sender)

        sel = sender.getSelection()
        if not sel:
            return
        char = sender.get()[sel[0]]
        if char != self.char:
            self.sliders.sliderPositionX.set(0)
            self.sliders.sliderPositionY.set(0)
            self.RCJKI.drawer.refGlyphPos = [0, 0]

            self.sliders.scaleXEditText.set(100)
            self.sliders.scaleYEditText.set(100)
            self.RCJKI.drawer.refGlyphScale = [1, 1]  
            self.char = char

        if self.filter in [0, 3]:
            if files.unicodeName(char) in self.RCJKI.currentFont.staticCharacterGlyphSet():
                self.previewCheckBox.show(True)
        UpdateCurrentGlyphView()

    def previewCheckBoxCallback(self, sender):
        self.preview = sender.get()
        self.sliders.show(self.preview)
        if self.preview:
            self.setRefGlyph(self.charactersList)
        else:
            self.RCJKI.drawer.refGlyph = None 
            self.RCJKI.drawer.refGlyphPos = [0, 0]
            UpdateCurrentGlyphView()

    def sliderPositionCallback(self, sender):
        self.RCJKI.drawer.refGlyphPos = [self.sliders.sliderPositionX.get(), self.sliders.sliderPositionY.get()]  
        UpdateCurrentGlyphView()

    def scaleEditTextCallback(self, sender):
        self.RCJKI.drawer.refGlyphScale = [int(self.sliders.scaleXEditText.get())/100, int(self.sliders.scaleYEditText.get())/100]  
        UpdateCurrentGlyphView()   
        
class PreviewGroup(Group):
    
    def __init__(self, posSize, RCJKI):
        super().__init__(posSize)
        self.RCJKI = RCJKI
        
        self.canvas = CanvasGroup((0, 0, -0, -25), delegate = self)
        self.roundToGridCheckBox = CheckBox(
            (5, -20, 120, 20), 
            "Round to grid", 
            value = self.RCJKI.roundToGrid, 
            sizeStyle = "small",
            callback = self.roundToGridCheckBoxCallback
            )
        self.drawOnlyDeepolationCheckBox = CheckBox(
            (125, -20, 140, 20), 
            "Draw only deepolation", 
            value = self.RCJKI.drawOnlyDeepolation, 
            sizeStyle = "small",
            callback = self.drawOnlyDeepolationCheckBoxCallback)

        self.glyphwidth = self.RCJKI.currentFont._RFont.lib.get('robocjk.defaultGlyphWidth', 1000)
        
    def roundToGridCheckBoxCallback(self, sender):
        self.RCJKI.roundToGrid = sender.get()
        self.RCJKI.updateDeepComponent(update = False)
    
    @refresh    
    def drawOnlyDeepolationCheckBoxCallback(self, sender):
        self.RCJKI.drawOnlyDeepolation = sender.get()
        
    def draw(self):
        mjdt.save()
        mjdt.fill(1, 1, 1, .7)
        mjdt.roundedRect(0, 0, 300, [525, 425][self.RCJKI.currentGlyph.type == "atomicElement"], 10)
        scale = .15
        mjdt.translate((self.glyphwidth*scale/2), 50)
        mjdt.fill(.15)
        mjdt.scale(scale, scale)
        mjdt.translate(0, abs(self.RCJKI.currentFont._RFont.info.descender))
        self.RCJKI.drawer.drawGlyph(
            self.RCJKI.currentGlyph,
            scale,
            (0, 0, 0, 1),
            (0, 0, 0, 0),
            (0, 0, 0, 1),
            drawSelectedElements = False
            )
        mjdt.restore()

    def update(self):
        self.canvas.update()

class SelectFontVariationSheet():
    def __init__(self, RCJKI, view):
        self.RCJKI = RCJKI
        self.view = view
        self.w = Sheet((300, 140), self.view.controller.w)
        l = [axis for axis in self.RCJKI.currentFont.fontVariations if axis not in self.RCJKI.currentGlyph._glyphVariations.axes]
        self.w.fontVariationsTitle = TextBox((0, 5, -0, 20), "Font variations available:", alignment = 'center', sizeStyle = 'small')
        self.w.fontVariationsList = List((0, 20, -0, -20), 
            l,
            showColumnTitles = False,
            allowsMultipleSelection = False,
            drawFocusRing = False
            )
        self.w.addButton = Button(
            (-150,-20, 150, 20), 
            'Add', 
            callback=self.addCharacterGlyphFontVariation
            )
        self.w.closeButton = Button(
            (-300,-20, 150, 20), 
            'Close', 
            callback=self.closeSheet
            )
        self.w.setDefaultButton(self.w.addButton)
        self.w.open()
        
    def addCharacterGlyphFontVariation(self, sender):
        fontVariationsListSel = self.w.fontVariationsList.getSelection()
        if not fontVariationsListSel: return
        name = self.w.fontVariationsList.get()[fontVariationsListSel[0]]
        self.RCJKI.currentGlyph.addCharacterGlyphNamedVariationToGlyph(name)
        self.RCJKI.updateListInterface()

        source = []
        if self.RCJKI.currentGlyph._glyphVariations:
            source = [{'Axis':axis, 'PreviewValue':0} for axis in self.RCJKI.currentGlyph._glyphVariations]
        isel = len(source)
        self.RCJKI.currentGlyph.selectedSourceAxis = source[isel-1]['Axis']
        glyphVariationsAxes = []
        for axisName, layer in self.RCJKI.currentGlyph._glyphVariations.items():
                glyphVariationsAxes.append({"Axis":axisName, "Layer":layer.layerName, "PreviewValue":0, "MinValue":layer.minValue, "MaxValue":layer.maxValue})
        self.view.glyphVariationAxesList.set(glyphVariationsAxes)        
        self.view.glyphVariationAxesList.setSelection([isel-1])
        self.RCJKI.updateDeepComponent(update = False)
        
    def closeSheet(self, sender):
        self.w.close()
        
class GlyphVariationAxesGroup(Group):
    
    def __init__(self, posSize, RCJKI, controller, glyphtype, glyphVariationsAxes):
        super().__init__(posSize)
        self.RCJKI = RCJKI
        self.controller = controller
        self.glyphVariationsAxes = glyphVariationsAxes
        
        slider = SliderListCell(minValue = 0, maxValue = 1)

        self.resetSliderToZero = Button((5, 3, 100, 20), 'Reset sliders', sizeStyle = "small", callback = self.resetSliderToZeroCallback)
        
        self.sliderValueTitle = TextBox((-160, 3, -100, 20), "Axis value:", sizeStyle = 'small')
        self.sliderValueEditText = EditText((-100, 0, -0, 20), '', callback = self.sliderValueEditTextCallback)
        
        y = -20
        if glyphtype in ["deepComponent", "atomicElement"]:
            y = -40
        
        self.selectedSourceAxis = None
        listDescription = [
                    {"title": "Axis", "editable": True, "width": 100},
                    {"title": "MinValue", "editable": True, "width": 40},
                    {"title": "PreviewValue", "cell": slider},
                    {"title": "MaxValue", "editable": True, "width": 40}
                    ]
        if self.RCJKI.currentGlyph.type == "atomicElement":
            listDescription = [
                    {"title": "Axis", "editable": True, "width": 80},
                    {"title": "Layer", "editable": False, "width": 80},
                    {"title": "MinValue", "editable": True, "width": 40},
                    {"title": "PreviewValue", "cell": slider},
                    {"title": "MaxValue", "editable": True, "width": 40}
                    ]

        self.glyphVariationAxesList = List(
            (0, 25, -0, y), 
            self.glyphVariationsAxes, 
            columnDescriptions = listDescription,
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
            self.setLocationTo1Button.show(False)

    @lockedProtect
    def resetSliderToZeroCallback(self, sender):
        sel = self.glyphVariationAxesList.getSelection()
        newList = []
        for i, e in enumerate(self.glyphVariationAxesList.get()):
            minValue = float(e["MinValue"])
            maxValue = float(e["MaxValue"])
            newList.append({
                "Axis":e["Axis"],
                "MinValue":e["MinValue"],
                "PreviewValue":self.RCJKI.systemValue(0, minValue, maxValue),
                "MaxValue":e["MaxValue"],
                })
            self.glyphVariationAxesList.set(newList)

        self.RCJKI.currentGlyph.sourcesList = self.glyphVariationAxesList.get()
        self.RCJKI.updateDeepComponent(update = False)
        self.glyphVariationAxesList.setSelection(sel)
        self.controller.updatePreview()
        
    @lockedProtect
    def sliderValueEditTextCallback(self, sender):
        sel = self.glyphVariationAxesList.getSelection()
        if not sel:
            sender.set("")
            return
        value = sender.get()
        try: 
            value = float(value.replace(",", "."))
        except:
            return
        newList = []
        for i, e in enumerate(self.glyphVariationAxesList.get()):
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
            self.glyphVariationAxesList.set(newList)

        self.RCJKI.currentGlyph.sourcesList = self.glyphVariationAxesList.get()
        self.RCJKI.updateDeepComponent(update = False)
        self.glyphVariationAxesList.setSelection(sel)
        self.controller.updatePreview()
        
    @lockedProtect
    def glyphVariationAxesListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            self.selectedSourceAxis = None
            self.sliderValueEditText.set('')
        else:
            self.selectedSourceAxis = sender.get()[sel[0]]["Axis"]
            self.sliderValueEditText.set(round(sender.get()[sel[0]]["PreviewValue"], 3))
        self.RCJKI.updateDeepComponent(update = False)
        self.controller.updatePreview()
        
    @lockedProtect
    def glyphVariationAxesListEditCallback(self, sender):
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
            l = [{'Axis':axis, 'PreviewValue':0, "MinValue":value.minValue, "MaxValue":value.maxValue} for axis, value in self.RCJKI.currentGlyph._glyphVariations.items()]
            sender.set(l)
            sender.setSelection(sel)
        elif edited[0] in [1, 3]:
            self.RCJKI.currentGlyph._glyphVariations[axis].minValue = minValue
            self.RCJKI.currentGlyph._glyphVariations[axis].maxValue = maxValue
        self.sliderValueEditText.set(self.RCJKI.userValue(sliderValue, minValue, maxValue))
        self.RCJKI.currentGlyph.sourcesList = [{"Axis":x["Axis"], "MinValue":x["MinValue"], "MaxValue":x["MaxValue"], "PreviewValue":self.RCJKI.userValue(x["PreviewValue"], x["MinValue"], x["MaxValue"])} for x in sender.get()]
        # self.RCJKI.currentGlyph.sourcesList = sender.get()
        self.RCJKI.updateDeepComponent(update = False)
        self.controller.updatePreview()
        
    @lockedProtect
    def glyphVariationAxesListDoubleClickCallback(self, sender):
        if not sender.getSelection(): 
            self.RCJKI.currentGlyph.selectedSourceAxis = None
        else:
            isel = sender.getSelection()[0]
            self.RCJKI.currentGlyph.selectedSourceAxis = {sender.get()[isel]['Axis']:1}

        self.RCJKI.currentGlyph.selectedElement = []
        self.controller.deepComponentAxesItem.deepComponentAxesList.set([])
        self.RCJKI.sliderValue = None
        self.RCJKI.sliderName = None
        self.RCJKI.updateDeepComponent(update = False)
        self.controller.updatePreview()
        
    @lockedProtect
    def addGlyphVariationButtonCallback(self, sender):
        if self.RCJKI.currentGlyph.type == "deepComponent":
            l = 0
            name = files.normalizeCode(files.int_to_column_id(l), 4)
            while name in self.RCJKI.currentGlyph._glyphVariations.axes:
                l += 1
                name = files.normalizeCode(files.int_to_column_id(l), 4)
            self.RCJKI.currentGlyph.addVariationToGlyph(name)
            if self.RCJKI.currentGlyph._glyphVariations:
                source = [{'Axis':axis, 'PreviewValue':0, "MinValue":value.minValue, "MaxValue":value.maxValue} for axis, value in self.RCJKI.currentGlyph._glyphVariations.items()]
            self.glyphVariationAxesList.set(source)
            self.RCJKI.currentGlyph.sourcesList = source
            isel = len(source)
            self.glyphVariationAxesList.setSelection([isel-1])
            self.selectedSourceAxis = source[isel-1]['Axis']
            self.RCJKI.currentGlyph.selectedSourceAxis = source[isel-1]['Axis']
            self.RCJKI.updateDeepComponent(update = False)   
            self.controller.updatePreview()    
            
        elif self.RCJKI.currentGlyph.type == "characterGlyph":
            SelectFontVariationSheet(self.RCJKI, self)

        elif self.RCJKI.currentGlyph.type == "atomicElement":
            availableLayers = [l for l in self.RCJKI.currentGlyph._RGlyph.layers if l.layer.name!='foreground']
            print(availableLayers)
            if [l for l in self.RCJKI.currentGlyph._RGlyph.layers if l.name != 'foreground']:
                sheets.SelectLayerSheet(self.RCJKI, self, availableLayers)
        
    @lockedProtect
    def removeGlyphVariationButtonCallback(self, sender):
        if self.glyphVariationAxesList.getSelection():
            if self.RCJKI.currentGlyph.type != "atomicElement":
                name = self.glyphVariationAxesList.get()[self.glyphVariationAxesList.getSelection()[0]]["Axis"]
                self.RCJKI.currentGlyph.removeVariationAxis(name)
                self.RCJKI.currentGlyph.selectedElement = []
                self.RCJKI.currentGlyph.selectedSourceAxis = None
                self.glyphVariationAxesList.setSelection([0])
                glyphVariations = self.RCJKI.currentGlyph._glyphVariations.axes
                l = [{'Axis':axis, 'PreviewValue':0, "MinValue":value.minValue, "MaxValue":value.maxValue} for axis, value in self.RCJKI.currentGlyph._glyphVariations.items()]
                self.RCJKI.currentGlyph.sourcesList = l
                self.glyphVariationAxesList.set(l)
                self.controller.deepComponentAxesItem.deepComponentAxesList.set([])
                self.RCJKI.sliderValue = None
                self.RCJKI.sliderName = None
                self.RCJKI.updateDeepComponent(update = False)
                self.controller.updatePreview()
            else:
                sel = self.glyphVariationAxesList.getSelection()
                layers = self.glyphVariationAxesList.get()
                layerName = layers[sel[0]]["Axis"]
                self.RCJKI.currentGlyph.removeGlyphVariation(layerName)
                layers.pop(sel[0])
                self.glyphVariationAxesList.set(layers)
                self.computeCurrentGlyph(self.glyphVariationAxesList)

    def computeCurrentGlyph(self, sender):
        self.RCJKI.currentGlyph.sourcesList = sender.get()
        self.RCJKI.currentGlyph.preview.computeDeepComponentsPreview(sender.get())
        
    def editSelectedAxisExtremeValueButtonCallback(self, sender):
        sel = self.glyphVariationAxesList.getSelection()
        if not sel:
            return
        selectedAxisName = self.glyphVariationAxesList.get()[sel[0]]["Axis"]
        f = self.RCJKI.currentFont
        f._RFont.newLayer("backup_axis", color = (.2, 0, .2, 1))
        backuplayer = f._RFont.getLayer("backup_axis")
        backuplayer.newGlyph(self.RCJKI.currentGlyph.name)
        backupGlyph = backuplayer[self.RCJKI.currentGlyph.name]
        backupGlyph.clear()
        pen = backupGlyph.getPen()
        self.setLocationTo1Button.show(True)

        for atomicInstance in self.RCJKI.currentGlyph.preview.axisPreview:
            g = atomicInstance.getTransformedGlyph()
            g.draw(pen)

    def setLocationTo1ButtonCallback(self, sender):
        self.setLocationTo1Button.show(False)
        sel = self.glyphVariationAxesList.getSelection()
        if not sel:
            return
        selectedAxisName = self.glyphVariationAxesList.get()[sel[0]]["Axis"]
        location1value = self.glyphVariationAxesList.get()[sel[0]]["PreviewValue"]
        for deepComponent in self.RCJKI.currentGlyph._glyphVariations[selectedAxisName].content.deepComponents:
            minValue = deepComponent.minValue
            maxValue = deepComponent.maxValue
            
        minValue = self.RCJKI.currentGlyph._glyphVariations[selectedAxisName].minValue
        maxValue = self.RCJKI.currentGlyph._glyphVariations[selectedAxisName].maxValue

        # self.RCJKI.currentGlyph._glyphVariations[selectedAxisName].maxValue = maxValue / location1value
        # print(minValue, maxValue, location1value, self.RCJKI.userValue(round(location1value, 3), minValue, maxValue))
        self.RCJKI.currentGlyph._glyphVariations[selectedAxisName].maxValue = maxValue / location1value#self.RCJKI.userValue(round(location1value, 3), minValue, maxValue)

        f = self.RCJKI.currentFont
        f._RFont.removeLayer("backup_axis")

        if self.RCJKI.currentGlyph._glyphVariations:
            source = [{'Axis':axis, 'PreviewValue':0, "MinValue":value.minValue, "MaxValue":value.maxValue} for axis, value in self.RCJKI.currentGlyph._glyphVariations.items()]
        self.glyphVariationAxesList.set(source)

        # print(self.RCJKI.currentGlyph._glyphVariations[selectedAxisName])
        # f = self.RCJKI.currentFont
        # f._RFont.removeLayer("backup_axis")

class DeepComponentAxesGroup(Group):
    
    def __init__(self, posSize, RCJKI, deepComponentAxes):
        super().__init__(posSize)
        self.RCJKI = RCJKI
        self.deepComponentAxes = deepComponentAxes
        
        slider = SliderListCell(minValue = 0, maxValue = 1)

        self.deepComponentName = TextBox((5, 5, 150, 20), "", sizeStyle = 'small')
        
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
            drawFocusRing = False,
            showColumnTitles = False
            )
        
    @lockedProtect
    def sliderValueEditTextCallback(self, sender):
        sel = self.deepComponentAxesList.getSelection()
        if not sel:
            sender.set("")
            return
        value = sender.get()
        try: 
            value = float(value.replace(",", "."))
        except:
            return
        newList = []
        minValue, maxValue = self.RCJKI.currentGlyph.getDeepComponentMinMaxValue(self.deepComponentAxesList[sel[0]]['Axis'])
        for i, e in enumerate(self.deepComponentAxesList.get()):
            if i != sel[0]:
                newList.append(e)
            else:
                newList.append({
                    "Axis":e["Axis"],
                    "MinValue": minValue,
                    "PreviewValue":self.RCJKI.systemValue(value, minValue, maxValue),
                    "MaxValue": maxValue,
                    })
            self.deepComponentAxesList.set(newList)

        self.deepComponentAxesList.setSelection(sel)
        self.setSliderValue2Glyph(self.deepComponentAxesList, minValue, maxValue)
        self.RCJKI.updateDeepComponent(update = False)
    
    @lockedProtect    
    def deepComponentAxesListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            self.sliderValueEditText.set('')
            return
        else:
            values = sender.get()[sel[0]]
            minValue, maxValue = self.RCJKI.currentGlyph.getDeepComponentMinMaxValue(self.deepComponentAxesList[sel[0]]['Axis'])
            sliderValue = round(sender.get()[sel[0]]['PreviewValue'], 3)
            self.sliderValueEditText.set(self.RCJKI.userValue(sliderValue, minValue, maxValue))
        
    @lockedProtect
    def deepComponentAxesListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return         
        
        minValue, maxValue = self.RCJKI.currentGlyph.getDeepComponentMinMaxValue(self.deepComponentAxesList[sender.getSelection()[0]]['Axis'])
        self.setSliderValue2Glyph(sender, minValue, maxValue)
        self.sliderValueEditText.set(self.RCJKI.userValue(round(sender.get()[sel[0]]["PreviewValue"], 3), minValue, maxValue))
        self.RCJKI.updateDeepComponent(update = False)

    def setSliderValue2Glyph(self, sender, minValue, maxValue):
        def _getKeys(glyph):
            if glyph.type == "characterGlyph":
                return 'robocjk.deepComponents', 'robocjk.fontVariationGlyphs'
            else:
                return 'robocjk.deepComponents', 'robocjk.glyphVariationGlyphs'
        if self.RCJKI.currentGlyph.type in ['characterGlyph', 'deepComponent']:
            lib = RLib()
            deepComponentsKey, glyphVariationsKey = _getKeys(self.RCJKI.currentGlyph)
            lib[deepComponentsKey] = copy.deepcopy(self.RCJKI.currentGlyph._deepComponents.getList())
            lib[glyphVariationsKey] = copy.deepcopy(self.RCJKI.currentGlyph._glyphVariations.getList())
            self.RCJKI.currentGlyph.stackUndo_lib = self.RCJKI.currentGlyph.stackUndo_lib[:self.RCJKI.currentGlyph.indexStackUndo_lib]
            self.RCJKI.currentGlyph.stackUndo_lib.append(lib)
            self.RCJKI.currentGlyph.indexStackUndo_lib += 1
            
        # self.RCJKI.sliderValue = round(float(self.deepComponentAxesList[sender.getSelection()[0]]['PreviewValue']), 3)
        self.RCJKI.sliderValue = self.RCJKI.userValue(round(sender.get()[sender.getSelection()[0]]["PreviewValue"], 3), minValue, maxValue)
        sliderName = self.deepComponentAxesList[sender.getSelection()[0]]['Axis']
        self.RCJKI.sliderName = sliderName
        if self.RCJKI.isDeepComponent:
            self.RCJKI.currentGlyph.updateAtomicElementCoord(self.RCJKI.sliderName, self.RCJKI.sliderValue)
        elif self.RCJKI.isCharacterGlyph:
            self.RCJKI.currentGlyph.updateDeepComponentCoord(self.RCJKI.sliderName, self.RCJKI.sliderValue)

from utils import colors
INPROGRESS = colors.INPROGRESS
CHECKING1 = colors.CHECKING1
CHECKING2 = colors.CHECKING2
CHECKING3 = colors.CHECKING3
DONE = colors.DONE
STATE_COLORS = colors.STATE_COLORS
        
class PropertiesGroup(Group):
    
    def __init__(self, posSize, RCJKI, controller):
        super().__init__(posSize)
        self.RCJKI = RCJKI
        self.controller = controller
        self.glyphState = PopUpButton(
            (5, 5, -100, 20),
            [
            "In Progress", 
            "Checking round 1", 
            "Checking round 2", 
            "Checking round 3", 
            "Done"
            ],
            callback = self.glyphStateCallback
            )

        self.glyphStateColor = ColorWell(
            (-100, 5, -5, 20)
            )
        self.glyphStateColor.getNSColorWell().setBordered_(False)

    def setglyphState(self):
        color = self.RCJKI.currentGlyph.markColor
        state = self.glyphState
        if color is None:
            state.set(0)
        elif color == INPROGRESS:
            state.set(0)
        elif color == CHECKING1:
            state.set(1)
        elif color == CHECKING2:
            state.set(2)
        elif color == CHECKING3:
            state.set(3)
        elif color == DONE:
            state.set(4)
        else:
            state.set(0)
        self.glyphStateCallback(state)

    def glyphStateCallback(self, sender):
        state = sender.get()
        self.RCJKI.currentGlyph.markColor = STATE_COLORS[state]
        if STATE_COLORS[state] == DONE and self.RCJKI.currentGlyph.type == "characterGlyph":
            self.RCJKI.decomposeGlyphToBackupLayer(self.RCJKI.currentGlyph)
        self.glyphStateColor.set(NSColor.colorWithCalibratedRed_green_blue_alpha_(*STATE_COLORS[state]))

class TransformationGroup(Group):

    def __init__(self, posSize, RCJKI, controller):
        super().__init__(posSize)
        self.RCJKI = RCJKI
        self.controller = controller

        self.alignLeft = ImageButton(
            (5, 5, 40, 40),
            alignLeftButtonImagePath,
            bordered = False,
            callback = self.alignLeftButtonCallback
            )
        self.alignTop = ImageButton(
            (45, 5, 40, 40),
            alignTopButtonImagePath,
            bordered = False,
            callback = self.alignTopButtonCallback
            )
        self.alignRight = ImageButton(
            (85, 5, 40, 40),
            alignRightButtonImagePath,
            bordered = False,
            callback = self.alignRightButtonCallback
            )
        self.alignBottom = ImageButton(
            (125, 5, 40, 40),
            alignBottomButtonImagePath,
            bordered = False,
            callback = self.alignBottomButtonCallback
            )

    def alignLeftButtonCallback(self, sender):
        self.alignSelectedElements(self.RCJKI.currentGlyph, "left")
        self.RCJKI.updateDeepComponent(update = False)
        self.controller.updatePreview()

    def alignTopButtonCallback(self, sender):
        self.alignSelectedElements(self.RCJKI.currentGlyph, "top")
        self.RCJKI.updateDeepComponent(update = False)
        self.controller.updatePreview()

    def alignRightButtonCallback(self, sender):
        self.alignSelectedElements(self.RCJKI.currentGlyph, "right")
        self.RCJKI.updateDeepComponent(update = False)
        self.controller.updatePreview()

    def alignBottomButtonCallback(self, sender):
        self.alignSelectedElements(self.RCJKI.currentGlyph, "bottom")
        self.RCJKI.updateDeepComponent(update = False)
        self.controller.updatePreview()

    def alignSelectedElements(self, glyph, align = "left"):

        class SelectedElements:
        
            def __init__(self, settings, glyph):
                self.settings = settings
                self.glyph = glyph
                
            def __repr__(self):
                return f"< settings:{self.settings}, glyph:{self.glyph} >"

        selection = glyph.selectedElement
        elements = []
        for i, x in zip(selection, glyph._getSelectedElement()):
            elements.append(SelectedElements(x, glyph.preview.axisPreview[i].getTransformedGlyph()))
        alignments = ["left", "bottom", "right", "top"]
        pos = alignments.index(align)
        target = []
        for element in elements:
            target.append(element.glyph.box[pos])
        target = [max(target), min(target)][pos < 2]
        for element in elements:
            diffx = [target - element.glyph.box[pos], 0][pos%2]
            diffy = [0, target - element.glyph.box[pos]][pos%2]
            element.settings.x += diffx
            element.settings.y += diffy

class Inspector:

    def closeWindow(self):
        self.w.close()

    def updatePreview(self):
        self.previewItem.update()

class CharacterGlyphInspector(Inspector):

    def __init__(self, RCJKI, glyphVariationsAxes = [], deepComponentAxes = []):
        self.RCJKI = RCJKI
        self.glyphVariationsAxes = glyphVariationsAxes
        self.deepComponentAxes = deepComponentAxes
        self.w = Window((0, 0, 300, 850), self.RCJKI.currentGlyph.name, minSize = (100, 200), closable = False)

        self.type = "characterGlyph"
        
        self.compositionRulesItem = CompositionRulesGroup((0, 0, -0, -0), self.RCJKI, self)
        self.previewItem = PreviewGroup((0, 0, -0, -0), self.RCJKI)
        self.glyphVariationAxesItem = GlyphVariationAxesGroup((0, 0, -0, -0), self.RCJKI, self, "characterGlyph", glyphVariationsAxes)
        self.deepComponentAxesItem = DeepComponentAxesGroup((0, 0, -0, -0), self.RCJKI, deepComponentAxes)
        self.propertiesItem = PropertiesGroup((0, 0, -0, -0), self.RCJKI, self)

        descriptions = [
                       dict(label="Composition Rules", view=self.compositionRulesItem, size=100, collapsed=False, canResize=True),
                       dict(label="Preview", view=self.previewItem, minSize=100, size=300, collapsed=False, canResize=True),
                       dict(label="Font variation axes", view=self.glyphVariationAxesItem, minSize=80, size=150, collapsed=False, canResize=True),
                       dict(label="Deep component axes", view=self.deepComponentAxesItem, minSize=100, size=150, collapsed=False, canResize=True),
                       dict(label="Properties", view=self.propertiesItem, minSize = 80, size=80, collapsed=False, canResize=True)
                       ]

        self.w.accordionView = AccordionView((0, 0, -0, -0), descriptions)
        self.previewItem.update()
        self.propertiesItem.setglyphState()
        self.w.open()
        
class DeepComponentInspector(Inspector):

    def __init__(self, RCJKI, glyphVariationsAxes = [], atomicElementAxes = []):
        self.RCJKI = RCJKI
        self.w = Window((0, 0, 300, 870), self.RCJKI.currentGlyph.name, minSize = (100, 200), closable = False)

        self.type = "deepComponent"
        
        self.relatedGlyphsItem = RelatedGlyphsGroup((0, 0, -0, -0), self.RCJKI, self)
        self.previewItem = PreviewGroup((0, 0, -0, -0), self.RCJKI)
        self.glyphVariationAxesItem = GlyphVariationAxesGroup((0, 0, -0, -0), self.RCJKI, self, "deepComponent", glyphVariationsAxes)
        self.deepComponentAxesItem = DeepComponentAxesGroup((0, 0, -0, -0), self.RCJKI, atomicElementAxes)
        self.propertiesItem = PropertiesGroup((0, 0, -0, -0), self.RCJKI, self)
        self.transformationItem = TransformationGroup((0, 0, -0, -0), self.RCJKI, self)

        descriptions = [
                       dict(label="Related glyphs", view=self.relatedGlyphsItem, size=140, collapsed=False, canResize=True),
                       dict(label="Preview", view=self.previewItem, minSize=100, size=300, collapsed=False, canResize=True),
                       dict(label="Deep component axes", view=self.glyphVariationAxesItem, minSize=100, size=170, collapsed=False, canResize=True),
                       dict(label="Atomic element axes", view=self.deepComponentAxesItem, minSize=100, size=150, collapsed=False, canResize=True),
                       dict(label="Properties", view=self.propertiesItem, minSize = 80, size=80, collapsed=False, canResize=True),
                       dict(label="Transformation", view=self.transformationItem, minSize = 80, size=80, collapsed=False, canResize=True)
                       ]

        self.w.accordionView = AccordionView((0, 0, -0, -0), descriptions)
        self.previewItem.update()
        self.propertiesItem.setglyphState()
        self.w.open()
        
class AtomicElementInspector(Inspector):

    def __init__(self, RCJKI, glyphVariationsAxes = []):
        self.RCJKI = RCJKI
        self.w = Window((0, 0, 300, 600), self.RCJKI.currentGlyph.name, minSize = (100, 200), closable = False)

        self.type = "atomicElement"
        
        self.previewItem = PreviewGroup((0, 0, -0, -0), self.RCJKI)
        self.glyphVariationAxesItem = GlyphVariationAxesGroup((0, 0, -0, -0), self.RCJKI, self, "atomicElement", glyphVariationsAxes)
        self.propertiesItem = PropertiesGroup((0, 0, -0, -0), self.RCJKI, self)

        descriptions = [
                       dict(label="Preview", view=self.previewItem, minSize=100, size=300, collapsed=False, canResize=True),
                       dict(label="Atomic element axes", view=self.glyphVariationAxesItem, minSize=100, size=170, collapsed=False, canResize=True),
                       dict(label="Properties", view=self.propertiesItem, minSize = 80, size=80, collapsed=False, canResize=True)
                       ]

        self.w.accordionView = AccordionView((0, 0, -0, -0), descriptions)
        self.previewItem.update()
        self.propertiesItem.setglyphState()
        self.w.open()

