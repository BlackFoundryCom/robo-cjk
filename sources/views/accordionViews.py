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
from vanilla.dialogs import askYesNo
from mojo.roboFont import *
from mojo.canvas import Canvas, CanvasGroup
import mojo.drawingTools as mjdt
from AppKit import NSColor, NSFont
from utils import decorators, files, interpolation, vanillaPlus
from views import sheets
import os, copy

import cProfile, pstats, io
from pstats import SortKey

SmartTextBox = vanillaPlus.SmartTextBox


lockedProtect = decorators.lockedProtect
refresh = decorators.refresh
EditButtonImagePath = os.path.join(os.getcwd(), "resources", "EditButton.pdf")
alignLeftButtonImagePath = os.path.join(os.getcwd(), "resources", "alignLeftButton.pdf")
alignTopButtonImagePath = os.path.join(os.getcwd(), "resources", "alignTopButton.pdf")
alignRightButtonImagePath = os.path.join(os.getcwd(), "resources", "alignRightButton.pdf")
alignBottomButtonImagePath = os.path.join(os.getcwd(), "resources", "alignBottomButton.pdf")



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
        # for c in self.glyph.previewGlyph:
        for c in self.glyph.preview({}, forceRefresh=False):
            mjdt.drawGlyph(c.glyph) 
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
        # self.glyph.preview.computeDeepComponents(update = False)
        self.canvas.update()
        self.setExistingInstances(self.deepComponentName)

    def setExistingInstances(self, deepComponentName):
        self.existingDeepComponentInstances = []
        f = self.RCJKI.currentFont

        dcdatabase = set(["uni%s"%hex(ord(x))[2:].upper() for x in self.RCJKI.currentFont.deepComponents2Chars.get(chr(int(deepComponentName.split("_")[1], 16)), set())])
        self.existingDeepComponentInstances = []
        for n in f.staticCharacterGlyphSet()&dcdatabase:
            try:
                self.existingDeepComponentInstances.append(chr(int(n[3:], 16)))
            except:
                self.existingDeepComponentInstances.append(n)
        self.existingInstancesList.set(self.existingDeepComponentInstances)

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
        self.deepComponentSettings, self.deepComponentVariationSettings = {},[]#self.existingDeepComponentInstances[char]

        f = self.RCJKI.currentFont
        try:
            g = f.get("uni%s"%hex(ord(char))[2:].upper())
        except:
            g = f.get(char)
        for i, x in enumerate(g._deepComponents):
            if x['name'] == self.deepComponentName:
                self.deepComponentVariationSettings = [copy.deepcopy(y.deepComponents[i]) for y in g._glyphVariations]
                self.deepComponentSettings = copy.deepcopy(g._deepComponents[i])
                break
        if not "name" in self.deepComponentSettings: 
            self.RCJKI.drawer.existingInstance = None
            self.RCJKI.drawer.existingInstancePos = [0, 0]
            self.deepComponentSettings = []
            self.deepComponentVariationSettings = []
            return
        dcname = self.deepComponentSettings['name']
        dcglyph = self.RCJKI.currentFont.get(dcname)
        dcglyphPreview = []
        for c in dcglyph.preview(self.deepComponentSettings['coord'], forceRefresh=True):
            dcglyphPreview.append(interpolation._transformGlyph(c.glyph, self.deepComponentSettings['transform']))
        self.RCJKI.drawer.existingInstance = dcglyphPreview

    def existingInstancesListDoubleClickCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        dcname = self.deepComponentSettings["name"]
        self.RCJKI.currentGlyph.addDeepComponentNamed(dcname, self.deepComponentSettings)

        if len(self.deepComponentVariationSettings) == len(self.RCJKI.currentGlyph._glyphVariations):
            for i, variation in enumerate(self.RCJKI.currentGlyph._glyphVariations):
                dc = copy.deepcopy(self.deepComponentVariationSettings[i])
                self.RCJKI.currentGlyph._glyphVariations[i].deepComponents[-1].set(dc._toDict())

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
        except: 
            char = self.RCJKI.currentGlyph.name
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
        self.drawOnlyInterpolationCheckBox = CheckBox(
            (125, -20, 140, 20), 
            "Draw only interpolation", 
            value = self.RCJKI.drawOnlyInterpolation, 
            sizeStyle = "small",
            callback = self.drawOnlyInterpolationCheckBoxCallback)

        self.glyphwidth = self.RCJKI.currentFont._RFont.lib.get('robocjk.defaultGlyphWidth', 1000)
        
    def roundToGridCheckBoxCallback(self, sender):
        self.RCJKI.roundToGrid = sender.get()
        self.RCJKI.updateDeepComponent(update = False)
    
    @refresh    
    def drawOnlyInterpolationCheckBoxCallback(self, sender):
        self.RCJKI.drawOnlyInterpolation = sender.get()
        
    def draw(self):
        try:
            mjdt.save()
            mjdt.fill(1, 1, 1, .7)
            mjdt.roundedRect(0, 0, 300, [525, 425][self.RCJKI.currentGlyph.type == "atomicElement"], 10)
            scale = .15
            mjdt.translate((self.glyphwidth*scale/2), 50)
            mjdt.fill(.15)
            mjdt.scale(scale, scale)
            mjdt.translate(0, abs(self.RCJKI.currentFont._RFont.info.descender))

            mjdt.save()
            mjdt.fill(0, 0, 0, 1)
            mjdt.stroke(0, 0, 0, 0)
            mjdt.strokeWidth(scale)
            loc = {}
            glyph = self.RCJKI.currentGlyph
            if glyph.sourcesList: 
                loc = {x["Axis"]:x["PreviewValue"] for x in glyph.sourcesList}
            # for g in glyph.glyphPreview:
            for g in glyph.preview(loc, forceRefresh=False):
                mjdt.drawGlyph(g.glyph)  
            mjdt.restore()
            mjdt.restore()
        except:pass

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
        for axis, variation in zip(self.RCJKI.currentGlyph._axes, self.RCJKI.currentGlyph._glyphVariations):
            glyphVariationsAxes.append({"Axis":axis.name, "Layer":variation.layerName, "PreviewValue":0, "MinValue":axis.minValue, "MaxValue":axis.maxValue})
        # for axisName, layer in self.RCJKI.currentGlyph._glyphVariations.items():
        #         glyphVariationsAxes.append({"Axis":axisName, "Layer":layer.layerName, "PreviewValue":0, "MinValue":layer.minValue, "MaxValue":layer.maxValue})
        self.view.glyphVariationAxesList.set(glyphVariationsAxes)        
        self.view.glyphVariationAxesList.setSelection([isel-1])
        self.RCJKI.updateDeepComponent(update = False)
        
    def closeSheet(self, sender):
        self.w.close()


from AppKit import NumberFormatter
numberFormatter = NumberFormatter()

class AxisSheet:

    def __init__(self, parentWindow, RCJKI, controller, glyphType):
        self.RCJKI = RCJKI
        self.controller = controller
        self.glyphType = glyphType
        self.w = Sheet((300, 140), parentWindow)

        if glyphType != "characterGlyph":
            self.w.axisNameTitle = TextBox((10, 20, 90, 20), "Axis name", sizeStyle = 'small')
            self.w.axisName = EditText((100, 20, 150, 20), "", sizeStyle = 'small')
        else:
            self.fontVariations = [axis for axis in self.RCJKI.currentFont.fontVariations if axis not in self.RCJKI.currentGlyph._axes.names]
            self.w.axisNameTitle = TextBox((10, 20, 90, 20), "Axis name", sizeStyle = 'small')
            self.w.axisName = PopUpButton((100, 20, 150, 20), self.fontVariations, sizeStyle = 'small')
        # else:
        #     self.layers = [l.name for l in self.RCJKI.currentFont._RFont.layers]
        #     self.w.axisNameTitle = TextBox((10, 20, 90, 20), "Axis name", sizeStyle = 'small')
        #     self.w.axisName = PopUpButton((100, 20, 150, 20), self.layers, sizeStyle = 'small')

        self.w.minValueTitle = TextBox((10, 50, 90, 20), "Min value", sizeStyle = 'small')
        self.w.minValue = EditText((100, 50, 150, 20), 0, sizeStyle = 'small', formatter = numberFormatter)

        self.w.maxValueTitle = TextBox((10, 80, 90, 20), "Max Value", sizeStyle = 'small')
        self.w.maxValue = EditText((100, 80, 150, 20), 1, sizeStyle = 'small', formatter = numberFormatter)

        self.w.apply = Button((150, -20, -0, 20), "Add", sizeStyle = 'small',callback = self.applyCallback)
        self.w.cancel = Button((00, -20, 150, 20), "Cancel", sizeStyle = 'small',callback = self.cancelCallback)
        self.w.setDefaultButton(self.w.apply)
        self.w.open()

    def applyCallback(self, sender):
        if self.glyphType != "characterGlyph":
            axisName = self.w.axisName.get()
        else: 
            axisName = self.fontVariations[self.w.axisName.get()]
        minValue = int(self.w.minValue.get())
        maxValue = int(self.w.maxValue.get())
        if not all([x!="" for x in [axisName, minValue, maxValue]]): return
        self.RCJKI.currentGlyph.addAxis(axisName, minValue, maxValue)
        self.controller.setList()
        self.controller.controller.sourcesItem.setList()
        self.w.close()

    def cancelCallback(self, sender):
        self.w.close()  

def str_to_int_or_float(s):
    try:
        if isinstance(s, (float, int)):
            return s
        elif '.' in s or ',' in s:
            return float(s)
        else:
            return int(s)
    except ValueError as e:
        return None      

class ModifyAxisSheet:

    def __init__(self, parentWindow, RCJKI, controller, axisList, axisIndex):
        self.RCJKI = RCJKI
        self.controller = controller
        self.axisList = axisList
        self.axisIndex = axisIndex
        self.w = Sheet((300, 200), parentWindow)

        self.w.minValueTitle = TextBox((10, 10, 100, 20), "minValue", sizeStyle='small')
        self.w.minValue = EditText((110, 10, 100, 20), axisList["MinValue"], sizeStyle='small')

        self.w.maxValueTitle = TextBox((10, 40, 100, 20), "maxValue", sizeStyle='small')
        self.w.maxValue = EditText((110, 40, 100, 20), axisList["MaxValue"], sizeStyle='small')

        self.changeDesignSpace = 1
        self.w.changeDesignSpaceCheckBox = CheckBox((10, -50, -10, 20), 'Change design space values', value = self.changeDesignSpace, callback = self.changeDesignSpaceCallback, sizeStyle="small")

        self.w.cancel = Button((0, -20, 150, 20), "cancel", sizeStyle = "small", callback = self.cancelCallback)
        self.w.apply = Button((150, -20, 150, 20), "apply", sizeStyle = "small", callback = self.applyCallback)
        self.w.setDefaultButton(self.w.apply)
        self.w.open()

    def changeDesignSpaceCallback(self, sender):
        self.changeDesignSpace = sender.get()

    def applyCallback(self, sender):
        axisName = self.axisList["Axis"]
        oldMinValue = str_to_int_or_float(self.axisList["MinValue"])
        oldMaxValue = str_to_int_or_float(self.axisList["MaxValue"])

        newMinValue = self.w.minValue.get()
        newMaxVamue = self.w.maxValue.get()

        try:
            newMinValue = str_to_int_or_float(newMinValue)
            newMaxVamue = str_to_int_or_float(newMaxVamue)
        except: return

        self.RCJKI.currentGlyph._axes[self.axisIndex].minValue = newMinValue
        self.RCJKI.currentGlyph._axes[self.axisIndex].maxValue = newMaxVamue
        if self.changeDesignSpace:
            for variation in self.RCJKI.currentGlyph._glyphVariations:
                if axisName in variation.location:
                    systemValue = self.RCJKI.systemValue(variation.location[axisName], oldMinValue, oldMaxValue)
                    newValue = self.RCJKI.userValue(systemValue, newMinValue, newMaxVamue)
                    variation.location[axisName] = newValue

        self.controller.setList()
        self.controller.controller.sourcesItem.setList()

        self.w.close()

    def cancelCallback(self, sender):
        self.w.close()

class AxesGroup(Group):

    def __init__(self, posSize, RCJKI, controller, glyphtype, axes = []):
        super().__init__(posSize)
        self.RCJKI = RCJKI
        self.controller = controller
        self.glyphtype = glyphtype
        self.axes = axes

        self.resetSliderToZero = Button((5, 3, 100, 20), 'Reset sliders', sizeStyle = "small", callback = self.resetSliderToZeroCallback)

        self.sliderValueTitle = TextBox((-160, 3, -100, 20), "Axis value:", sizeStyle = 'small')
        self.sliderValueEditText = EditText((-100, 0, -0, 20), '', callback = self.sliderValueEditTextCallback)

        self.selectedSourceAxis = None
        # slider = SliderListCell(minValue = 0, maxValue = 1)
        # self.axesList = List((0, 20, -0, -20),
        #     [],
        #     columnDescriptions = [
        #             {"title": "Axis", "editable": True, "width": 100},
        #             {"title": "MinValue", "editable": True, "width": 40},
        #             {"title": "PreviewValue", "cell": slider},
        #             {"title": "MaxValue", "editable": True, "width": 40}
        #             ],
        #     selectionCallback = self.axesListSelectionCallback,
        #     editCallback = self.axesListEditCallback,
        #     allowsMultipleSelection = False,
        #     drawFocusRing = False,
        #     showColumnTitles = False
        #             )

        self.setList()

        self.modifyAxisButton = Button((0, -40, 80, 20), "Modify axis", sizeStyle="small", callback = self.modifyAxisCallback)

        if glyphtype in ["deepComponent", "atomicElement"]:
            self.editSelectedAxisExtremeValueButton = Button(
                (80, -40, 200, 20), 
                "Edit selected axis extreme value", 
                sizeStyle = "small",
                callback = self.editSelectedAxisExtremeValueButtonCallback)
            self.setLocationTo1Button = Button(
                (280, -40, 100, 20), 
                "Set location to 1", 
                sizeStyle = "small",
                callback = self.setLocationTo1ButtonCallback)
            self.setLocationTo1Button.show(False)

        self.addAxisButton = Button((0, -20, 150, 20), "+", sizeStyle = "small", callback = self.addAxisButtonCallback)
        self.removeAxisButton = Button((150, -20, 150, 20), "-", sizeStyle = "small", callback = self.removeAxisButtonCallback)


    def editSelectedAxisExtremeValueButtonCallback(self, sender):
        sel = self.axesList.getSelection()
        if not sel:
            return
        selectedAxisName = self.axesList.get()[sel[0]]["Axis"]
        f = self.RCJKI.currentFont
        f._RFont.newLayer("backup_axis", color = (.2, 0, .2, 1))
        backuplayer = f._RFont.getLayer("backup_axis")
        backuplayer.newGlyph(self.RCJKI.currentGlyph.name)
        backupGlyph = backuplayer[self.RCJKI.currentGlyph.name]
        backupGlyph.clear()
        pen = backupGlyph.getPen()
        self.setLocationTo1Button.show(True)

        # loc = {}
        # if self.RCJKI.currentGlyph.selectedSourceAxis:
        #     loc = {self.RCJKI.currentGlyph.selectedSourceAxis:1}
        for atomicInstance in self.RCJKI.currentGlyph.preview():
            g = atomicInstance.glyph
            g.draw(pen)

    def setLocationTo1ButtonCallback(self, sender):
        self.setLocationTo1Button.show(False)
        sel = self.axesList.getSelection()
        if not sel:
            return
        selectedAxisName = self.axesList.get()[sel[0]]["Axis"]
        location1value = self.axesList.get()[sel[0]]["PreviewValue"]

        minValue = self.axesList.get()[sel[0]]["MinValue"]
        maxValue = self.axesList.get()[sel[0]]["MaxValue"]

        newMaxValue = maxValue / location1value

        self.RCJKI.currentGlyph._axes.get(selectedAxisName).maxValue = newMaxValue#self.RCJKI.userValue(round(location1value, 3), minValue, maxValue)

        for variation in self.RCJKI.currentGlyph._glyphVariations:
            if selectedAxisName in variation.location:
                systemValue = self.RCJKI.systemValue(variation.location[selectedAxisName], minValue, maxValue)
                newValue = self.RCJKI.userValue(systemValue, minValue, newMaxValue)
                variation.location[selectedAxisName] = newValue

        f = self.RCJKI.currentFont
        f._RFont.removeLayer("backup_axis")

        self.setList()
        self.controller.sourcesItem.setList()

    def modifyAxisCallback(self, sender):
        sel = self.axesList.getSelection()
        if not sel: return
        ModifyAxisSheet(self.controller.w, self.RCJKI, self, self.axesList[sel[0]], sel[0])

    @lockedProtect
    def resetSliderToZeroCallback(self, sender):
        sel = self.axesList.getSelection()
        newList = []
        for i, e in enumerate(self.axesList.get()):
            minValue = float(e["MinValue"])
            maxValue = float(e["MaxValue"])
            newList.append({
                "Axis":e["Axis"],
                "MinValue":e["MinValue"],
                "PreviewValue":0,#self.RCJKI.systemValue(0, minValue, maxValue),
                "MaxValue":e["MaxValue"],
                })
            self.axesList.set(newList)

        self.RCJKI.currentGlyph.sourcesList = [{"Axis":x["Axis"], "MinValue":x["MinValue"], "MaxValue":x["MaxValue"], "PreviewValue":self.RCJKI.userValue(float(x["PreviewValue"]), float(x["MinValue"]), float(x["MaxValue"]))} for x in newList]
        self.RCJKI.currentGlyph.redrawSelectedElementSource = True
        self.RCJKI.currentGlyph.redrawSelectedElementPreview = True
        self.RCJKI.currentGlyph.reinterpolate = True
        self.RCJKI.updateDeepComponent(update = False)
        self.axesList.setSelection(sel)
        self.controller.updatePreview()

    def setList(self):
        self.axes = [dict(Axis=x.name, MinValue=x.minValue, PreviewValue=0, MaxValue=x.maxValue) for x in self.RCJKI.currentGlyph._axes]
        # self.axesList.set(self.axes)

        if hasattr(self, "axesList"):
            delattr(self, "axesList")

        slider = SliderListCell(minValue = 0, maxValue = 1)
        self.axesList = List((0, 20, -0, -40),
            self.axes,
            columnDescriptions = [
                    {"title": "Axis", "editable": True, "width": 100},
                    {"title": "MinValue", "editable": True, "width": 40},
                    {"title": "PreviewValue", "cell": slider},
                    {"title": "MaxValue", "editable": True, "width": 40}
                    ],
            selectionCallback = self.axesListSelectionCallback,
            editCallback = self.axesListEditCallback,
            allowsMultipleSelection = False,
            drawFocusRing = False,
            showColumnTitles = False
                    )

        self.RCJKI.currentGlyph.sourcesList = []

    @lockedProtect
    def sliderValueEditTextCallback(self, sender):
        sel = self.axesList.getSelection()
        if not sel:
            sender.set("")
            return
        value = sender.get()
        try: 
            value = float(value.replace(",", "."))
        except:
            return
        newList = []
        for i, e in enumerate(self.axesList.get()):
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
            self.axesList.set(newList)

        self.RCJKI.currentGlyph.sourcesList = self.axesList.get()
        self.RCJKI.updateDeepComponent(update = False)
        self.axesList.setSelection(sel)
        self.controller.updatePreview()

    @lockedProtect
    def axesListSelectionCallback(self, sender):
        sel = sender.getSelection()
        senderGet = sender.get()
        if not sel:
            self.selectedSourceAxis = None
            self.sliderValueEditText.set('')
        else:
            self.selectedSourceAxis = sender.get()[sel[0]]["Axis"]
            sliderValue = round(sender.get()[sel[0]]["PreviewValue"], 3)
            axis = sender.get()[sel[0]]["Axis"]
            self.sliderValueEditText.set(self.RCJKI.userValue(sliderValue, self.RCJKI.currentGlyph._axes.get(axis).minValue, self.RCJKI.currentGlyph._axes.get(axis).maxValue))
        self.RCJKI.updateDeepComponent(update = False)
        self.controller.updatePreview()

    @lockedProtect
    # @refreshPreview
    def axesListEditCallback(self, sender):
        # pr = cProfile.Profile()
        # pr.enable()

        sel = sender.getSelection()
        if not sel: 
            return
        edited = sender.getEditedColumnAndRow()
        senderGet = sender.get()
        if not senderGet: return
        
        sliderValue = round(senderGet[sel[0]]['PreviewValue'], 3)
        if edited[0] in [0, 1, 3]:

            l = []
            for axis in self.RCJKI.currentGlyph._axes:
                l.append({'Axis':axis.name, 'PreviewValue':0, "MinValue":axis.minValue, "MaxValue":axis.maxValue})
            sender.set(l)
            sender.setSelection(sel)

        axis = sender.get()[sel[0]]["Axis"]
        self.sliderValueEditText.set(self.RCJKI.userValue(sliderValue, self.RCJKI.currentGlyph._axes.get(axis).minValue, self.RCJKI.currentGlyph._axes.get(axis).maxValue))
        self.RCJKI.currentGlyph.sourcesList = [{"Axis":x["Axis"], "MinValue":x["MinValue"], "MaxValue":x["MaxValue"], "PreviewValue":self.RCJKI.userValue(float(x["PreviewValue"]), float(x["MinValue"]), float(x["MaxValue"]))} for x in senderGet]
        self.RCJKI.updateDeepComponent(update = False)
        self.controller.updatePreview()
        self.RCJKI.currentGlyph.redrawSelectedElementSource = True
        self.RCJKI.currentGlyph.redrawSelectedElementPreview = True
        self.RCJKI.currentGlyph.reinterpolate = True

        # pr.disable()
        # s = io.StringIO()
        # sortby = SortKey.CUMULATIVE
        # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        # ps.print_stats()
        # print('axesListEditCallback (AccordionViews.py)', s.getvalue())

    def addAxisButtonCallback(self, sender):
        AxisSheet(self.controller.w, self.RCJKI, self, self.glyphtype)

    def removeAxisButtonCallback(self, sender):
        answer = askYesNo("Are you sure you want to delete this axis?")
        if not answer: return
        sel = self.axesList.getSelection()
        if not sel: return
        selectedAxisIndex = sel[0]
        self.RCJKI.currentGlyph.removeAxis(selectedAxisIndex)
        self.setList()
        self.controller.sourcesItem.setList()
        self.RCJKI.currentGlyph.selectedSourceAxis = None
        self.RCJKI.updateDeepComponent(update = False)
        self.controller.updatePreview()

class SourcesSheet:

    def __init__(self, parentWindow, RCJKI, controller, glyphType):
        self.RCJKI = RCJKI
        self.controller = controller
        self.glyphType = glyphType
        if glyphType != "atomicElement":
            height = 80 + 30*len(self.RCJKI.currentGlyph._axes)
        else:
            height = 60 + 30*len(self.RCJKI.currentGlyph._axes)
        self.w = Sheet((300, height), parentWindow)

        y = 10
        if glyphType != "atomicElement":
            self.w.sourceNameTitle = TextBox((10, y, 90, 20), 'Source name', sizeStyle = 'small')
            self.w.sourceName = EditText((100, y, -0, 20), "", sizeStyle = "small")
        else:
            layers = []
            for l in self.RCJKI.currentFont._RFont.layers:
                fl = self.RCJKI.currentFont._RFont.getLayer(l.name)
                if self.RCJKI.currentGlyph.name in fl.keys():
                    if len(fl[self.RCJKI.currentGlyph.name]):
                        layers.append(l)
            self.layers = [l.name for l in layers if l.name != 'foreground' and l.name not in self.RCJKI.currentGlyph._glyphVariations.layerNames()]
            self.w.sourceNameTitle = TextBox((10, y, 90, 20), "Axis name", sizeStyle = 'small')
            self.w.sourceName = PopUpButton((100, y, 150, 20), self.layers, sizeStyle = 'small')
        y += 25

        self.axes = {}
        for i, axis in enumerate(self.RCJKI.currentGlyph._axes):
            textbox = TextBox((10, y, 90, 20), axis.name, sizeStyle = 'small')
            minValue = TextBox((100, y+5, 50, 20), axis.minValue, sizeStyle = 'small', alignment="right")
            editText = EditText((150, y, -50, 20), [axis.minValue, axis.maxValue][i + 1 == len(self.RCJKI.currentGlyph._axes)], sizeStyle = "small", 
                # formatter = numberFormatter, 
                continuous = False,
                callback = self.valuesCallback)
            maxValue = TextBox((-50, y+5, 50, 20), axis.maxValue, sizeStyle = 'small', alignment="left")
            setattr(self.w, "%sName"%axis.name, textbox)
            setattr(self.w, "%sminValue"%axis.name, minValue)
            setattr(self.w, axis.name, editText)
            setattr(self.w, "%smaxValue"%axis.name, maxValue)
            self.axes[editText] = axis
            y += 25

        if glyphType != "atomicElement":
            self.w.copyfromTitle = TextBox((10, y, 90, 20), "copy from", sizeStyle = 'small')
            self.sources = ["master"]+self.RCJKI.currentGlyph._glyphVariations.sourceNames
            self.w.copyfromPopupButton = PopUpButton((100, y, -10, 20), self.sources, sizeStyle = 'small')

        self.w.cancel = Button((0, -20, 150, 20), 'Cancel', sizeStyle = 'small', callback = self.cancelCallback)
        self.w.apply = Button((150, -20, 150, 20), 'Apply', sizeStyle = 'small', callback = self.applyCallback)
        self.w.setDefaultButton(self.w.apply)
        self.w.open()

    def valuesCallback(self, sender):
        axis = self.axes[sender]
        minValue = axis.minValue
        maxValue = axis.maxValue
        value = sender.get()
        if value == "":
            sender.set(minValue)
            return
        value = str_to_int_or_float(value)
        if not isinstance(value, (int, float)): return
        if value > max(minValue, maxValue):
            value = max(minValue, maxValue)
        elif value < min(minValue, maxValue):
            value = min(minValue, maxValue)
        sender.set(value)

    def applyCallback(self, sender):
        sourceName = ""
        layerName = ""
        if self.glyphType != "atomicElement":
            sourceName = self.w.sourceName.get()
        else:
            if not self.layers: return
            layerName = self.layers[self.w.sourceName.get()]
        if not sourceName and not layerName: return
        location = {}
        for axis in self.RCJKI.currentGlyph._axes.names:
            try:
                value = float(getattr(self.w, axis).get())
                if value != "":
                    location[axis] = value
            except:
                continue
        if self.glyphType != "atomicElement":
            copyFrom = self.w.copyfromPopupButton.getItem()
        else:
            copyFrom = ""
        self.RCJKI.currentGlyph.addSource(sourceName=sourceName, location=location, layerName=layerName, copyFrom = copyFrom)
        self.RCJKI.currentGlyph.selectedSourceAxis = sourceName
        self.RCJKI.currentGlyph.redrawSelectedElementSource = True
        self.RCJKI.currentGlyph.redrawSelectedElementPreview = True
        self.controller.setList()
        self.controller.sourcesList.setSelection([len(self.controller.sourcesList)-1])
        self.RCJKI.glyphView.setSelectedSource()
        self.w.close()

    def cancelCallback(self, sender):
        self.w.close()


class SourcesGroup(Group):

    def __init__(self, posSize, RCJKI, controller, glyphtype, sources):
        super().__init__(posSize)
        self.RCJKI = RCJKI
        self.controller = controller
        self.glyphtype = glyphtype

        self.activateAllSource = Button((0, 0, 150, 20), "Activate all sources", sizeStyle = "small", callback = self.activateAllSourceCallback)

        self.setList()
        
        self.addSourceButton = Button((0, -20, 150, 20), "+", sizeStyle = "small", callback = self.addSourceButtonCallback)
        self.removeSourceButton = Button((150, -20, 150, 20), "-", sizeStyle = "small", callback = self.removeSourceButtonCallback)

    def setList(self):
        if self.RCJKI.currentGlyph.type == "atomicElement":
            self.sources = [{"On/Off":x.on, "layerName":x.layerName, **{y.name:y.minValue for y in self.RCJKI.currentGlyph._axes}} for x in self.RCJKI.currentGlyph._glyphVariations]
        else:    
            self.sources = [{"On/Off":x.on, "name":x.sourceName, **{y.name:y.minValue for y in self.RCJKI.currentGlyph._axes}} for x in self.RCJKI.currentGlyph._glyphVariations]
        for i, source in enumerate(self.sources):
            source.update(self.RCJKI.currentGlyph._glyphVariations[i].location)

        checkbox = CheckBoxListCell()
        self.listDescription = [
                    {"title": "On/Off", "editable": True, "width": 40, "cell":checkbox},
                    {"title": "name", "editable": True, "width": 120},
                    *[dict(title=x.name, editable = True, width = 60) for x in self.RCJKI.currentGlyph._axes]
                    ]
        if self.RCJKI.currentGlyph.type == "atomicElement":
            self.listDescription = [
                    {"title": "On/Off", "editable": True, "width": 40, "cell":checkbox},
                    {"title": "layerName", "editable": True, "width": 120},
                    *[dict(title=x.name, editable = True, width = 60) for x in self.RCJKI.currentGlyph._axes]
                    ]

        if hasattr(self, "sourcesList"):
            delattr(self, "sourcesList")

        self.sourcesList = List((0, 20, -0, -20),
            self.sources,
            columnDescriptions = self.listDescription,
            editCallback = self.sourcesListEditCallback,
            doubleClickCallback = self.sourcesListDoubleClickCallback,
            drawFocusRing = False,
            showColumnTitles = True
            )

    def activateAllSourceCallback(self, sender):
        for i, _ in enumerate(self.RCJKI.currentGlyph._glyphVariations):
            self.RCJKI.currentGlyph._glyphVariations.activateSource(i, True, self.RCJKI.currentGlyph._axes)
        self.setList()

    @lockedProtect
    def sourcesListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            return
        edited = sender.getEditedColumnAndRow()
        values = sender.get()
        index = sel[0]
        variation = self.RCJKI.currentGlyph._glyphVariations[index]
        if edited[0] == -1: #On off
            value = values[sel[0]]["On/Off"]
            v = self.RCJKI.currentGlyph._glyphVariations.activateSource(index, value, self.RCJKI.currentGlyph._axes)

            empty = True
            loc = self.RCJKI.currentGlyph._glyphVariations[index].location
            for k, x in loc.items():
                if x != self.RCJKI.currentGlyph._axes.get(k).minValue:
                    empty = False
                    break
            if empty:
                v = False

            l = sender.get()
            l[index]["On/Off"] = v
            sender.set(l)
        elif edited[0] == 1: #name
            if self.RCJKI.currentGlyph.type == "atomicElement":
                name = values[edited[1]]['layerName']
                variation.layerName = name
            else:
                name = values[edited[1]]['name']
                variation.sourceName = name
        else:
            locations = {}
            for axis in self.listDescription[2:]:
                axisName = axis["title"]
                value = values[edited[1]][axisName]
                locations[axisName] = str_to_int_or_float(value)
            self.RCJKI.currentGlyph._glyphVariations.setLocationToIndex(locations, index, self.RCJKI.currentGlyph._axes)
            self.setList()
        self.RCJKI.updateDeepComponent(update = False)
        self.controller.updatePreview()

    @lockedProtect
    # @refreshPreview
    def sourcesListDoubleClickCallback(self, sender):
        if not sender.getSelection(): 
            self.RCJKI.currentGlyph.selectedSourceAxis = None
        else:
            isel = sender.getSelection()[0]
            if self.glyphtype != "atomicElement":
                self.RCJKI.currentGlyph.selectedSourceAxis = sender.get()[isel]['name']
            else:
                self.RCJKI.currentGlyph.selectedSourceAxis = sender.get()[isel]['layerName']

        self.RCJKI.currentGlyph.selectedElement = []
        if self.glyphtype != "atomicElement":
            self.controller.deepComponentAxesItem.deepComponentAxesList.set([])
        self.RCJKI.sliderValue = None
        self.RCJKI.sliderName = None
        self.RCJKI.axisPreview = []
        self.RCJKI.currentGlyph.redrawSelectedElementSource = True
        self.RCJKI.currentGlyph.redrawSelectedElementPreview = True
        self.RCJKI.updateDeepComponent(update = False)
        self.controller.updatePreview()
        self.RCJKI.glyphView.setSelectedSource()


    def addSourceButtonCallback(self, sender):
        SourcesSheet(self.controller.w, self.RCJKI, self, self.glyphtype)
        
    def removeSourceButtonCallback(self, sender):
        answer = askYesNo("Are you sure you want to delete this source?")
        if not answer: return
        sel = self.sourcesList.getSelection()
        if not sel: return
        selectedAxisIndex = sel[0]
        self.RCJKI.currentGlyph.removeSource(selectedAxisIndex)
        self.setList()
        self.RCJKI.currentGlyph.selectedSourceAxis = None
        self.RCJKI.updateDeepComponent()
        self.controller.updatePreview()
        self.sourcesList.setSelection([])
        self.controller.axesItem.axesList.setSelection([])
        

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
        selectedAtomicElementName = self.RCJKI.currentGlyph._deepComponents[self.RCJKI.currentGlyph.selectedElement[0]].name
        atomicElement = self.RCJKI.currentFont[selectedAtomicElementName]
        for x in atomicElement._axes:
            if self.deepComponentAxesList[sel[0]]['Axis'] == x.name:
                minValue = x.minValue
                maxValue = x.maxValue
                if value > max(minValue, maxValue) or value < min(minValue, maxValue):
                    return
        # minValue, maxValue = self.RCJKI.currentGlyph.getDeepComponentMinMaxValue(self.deepComponentAxesList[sel[0]]['Axis'])
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
        self.setEditTextValue2Glyph(value)
        self.RCJKI.updateDeepComponent(update = False)
        self.RCJKI.currentGlyph.redrawSelectedElementSource = True
        self.RCJKI.currentGlyph.redrawSelectedElementPreview = True
        self.RCJKI.currentGlyph.reinterpolate = True

    def setEditTextValue2Glyph(self, value):
        def _getKeys(glyph):
            return 'robocjk.deepComponents', 'robocjk.variationGlyphs', 'robocjk.axes'

        if self.RCJKI.currentGlyph.type in ['characterGlyph', 'deepComponent']:
            lib = RLib()
            deepComponentsKey, glyphVariationsKey, axesKey = _getKeys(self.RCJKI.currentGlyph)
            lib[deepComponentsKey] = copy.deepcopy(self.RCJKI.currentGlyph._deepComponents.getList())
            lib[glyphVariationsKey] = copy.deepcopy(self.RCJKI.currentGlyph._glyphVariations.getList())
            lib[axesKey] = copy.deepcopy(self.RCJKI.currentGlyph._axes.getList())
            self.RCJKI.currentGlyph.stackUndo_lib = self.RCJKI.currentGlyph.stackUndo_lib[:self.RCJKI.currentGlyph.indexStackUndo_lib]
            self.RCJKI.currentGlyph.stackUndo_lib.append(lib)
            self.RCJKI.currentGlyph.indexStackUndo_lib += 1
            
        # self.RCJKI.sliderValue = round(float(self.deepComponentAxesList[sender.getSelection()[0]]['PreviewValue']), 3)
        self.RCJKI.sliderValue = value
        sliderName = self.deepComponentAxesList[self.deepComponentAxesList.getSelection()[0]]['Axis']
        self.RCJKI.sliderName = sliderName
        if self.RCJKI.isDeepComponent:
            self.RCJKI.currentGlyph.updateAtomicElementCoord(self.RCJKI.sliderName, value)
        elif self.RCJKI.isCharacterGlyph:
            self.RCJKI.currentGlyph.updateDeepComponentCoord(self.RCJKI.sliderName, value)
    
    @lockedProtect    
    def deepComponentAxesListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            self.sliderValueEditText.set('')
            return
        else:
            values = sender.get()[sel[0]]
            selectedAtomicElementName = self.RCJKI.currentGlyph._deepComponents[self.RCJKI.currentGlyph.selectedElement[0]].name
            atomicElement = self.RCJKI.currentFont[selectedAtomicElementName]

            for x in atomicElement._axes:
                if self.deepComponentAxesList[sel[0]]['Axis'] == x.name:
                    minValue = x.minValue
                    maxValue = x.maxValue
            # minValue, maxValue = self.RCJKI.currentGlyph.getDeepComponentMinMaxValue(self.deepComponentAxesList[sel[0]]['Axis'])
            sliderValue = round(sender.get()[sel[0]]['PreviewValue'], 3)
            if not self.RCJKI.currentGlyph.selectedSourceAxis:
                self.sliderValueEditText.set(self.RCJKI.currentGlyph._deepComponents[self.RCJKI.currentGlyph.selectedElement[0]].coord[self.deepComponentAxesList[sel[0]]['Axis']] )
            else:
                self.sliderValueEditText.set(self.RCJKI.currentGlyph._glyphVariations.getFromSourceName(self.RCJKI.currentGlyph.selectedSourceAxis).deepComponents[self.RCJKI.currentGlyph.selectedElement[0]].coord[self.deepComponentAxesList[sel[0]]['Axis']] )
            # self.sliderValueEditText.set(self.RCJKI.userValue(sliderValue, minValue, maxValue))
        
    @lockedProtect
    # @refreshPreview
    def deepComponentAxesListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            return         
        # minValue = self.RCJKI.currentGlyph._axes[]

        selectedAtomicElementName = self.RCJKI.currentGlyph._deepComponents[self.RCJKI.currentGlyph.selectedElement[0]].name
        atomicElement = self.RCJKI.currentFont[selectedAtomicElementName]

        for x in atomicElement._axes:
            if self.deepComponentAxesList[sender.getSelection()[0]]['Axis'] == x.name:
                minValue = x.minValue
                maxValue = x.maxValue

        # minValue, maxValue = self.RCJKI.currentGlyph.getDeepComponentMinMaxValue(self.deepComponentAxesList[sender.getSelection()[0]]['Axis'])
        self.setSliderValue2Glyph(sender, minValue, maxValue)
        if not self.RCJKI.currentGlyph.selectedSourceAxis:
            self.sliderValueEditText.set(self.RCJKI.currentGlyph._deepComponents[self.RCJKI.currentGlyph.selectedElement[0]].coord[self.deepComponentAxesList[sel[0]]['Axis']] )
        else:
            self.sliderValueEditText.set(self.RCJKI.currentGlyph._glyphVariations.getFromSourceName(self.RCJKI.currentGlyph.selectedSourceAxis).deepComponents[self.RCJKI.currentGlyph.selectedElement[0]].coord[self.deepComponentAxesList[sel[0]]['Axis']] )
        self.RCJKI.updateDeepComponent(update = False)
        self.RCJKI.currentGlyph.redrawSelectedElementSource = True
        self.RCJKI.currentGlyph.redrawSelectedElementPreview = True
        self.RCJKI.currentGlyph.reinterpolate = True
        # location = {}
        # for v in self.RCJKI.currentGlyph._glyphVariations:
        #     if v.sourceName == self.RCJKI.currentGlyph.selectedSourceAxis:
        #         location = v.location
        # self.RCJKI.currentGlyph.updatePreviewLocationStore(location)

    def setSliderValue2Glyph(self, sender, minValue, maxValue):
        def _getKeys(glyph):
            return 'robocjk.deepComponents', 'robocjk.variationGlyphs', 'robocjk.axes'

        if self.RCJKI.currentGlyph.type in ['characterGlyph', 'deepComponent']:
            lib = RLib()
            deepComponentsKey, glyphVariationsKey, axesKey = _getKeys(self.RCJKI.currentGlyph)
            lib[deepComponentsKey] = copy.deepcopy(self.RCJKI.currentGlyph._deepComponents.getList())
            lib[glyphVariationsKey] = copy.deepcopy(self.RCJKI.currentGlyph._glyphVariations.getList())
            lib[axesKey] = copy.deepcopy(self.RCJKI.currentGlyph._axes.getList())
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

class DeepComponentListGroup(Group):

    def __init__(self, posSize, RCJKI):
        super().__init__(posSize)
        self.RCJKI = RCJKI

        checkbox = CheckBoxListCell()
        self.deepComponentList = List(
            (0, 25, -0, -20), 
            [], 
            columnDescriptions = [
                    {"title": "select", "editable": True, "width": 40, "cell":checkbox},
                    {"title": "name", "editable": False}],
            editCallback = self.deepComponentListEditCallback,
            drawFocusRing = False,
            showColumnTitles = False
            )
        self.setList()

        self.addDeepComponentButton = Button((0, -20, 150, 20), "+", sizeStyle = "small", callback = self.addDeepComponentButtonCallback)
        self.removeDeepComponentButton = Button((150, -20, 150, 20), "-", sizeStyle = "small", callback = self.removeDeepComponentButtonCallback)

    def setList(self):
        self.deepComponentsNames = [dict(name=x.get("name"), select = i in self.RCJKI.currentGlyph.selectedElement) for i, x in enumerate(self.RCJKI.currentGlyph._deepComponents)]
        self.deepComponentList.set(self.deepComponentsNames)

    def deepComponentListEditCallback(self, sender):
        self.RCJKI.currentGlyph.selectedElement = [i for i, x in enumerate(sender.get()) if x["select"]]
        self.RCJKI.updateDeepComponent()

    def addDeepComponentButtonCallback(self, sender):
        if self.RCJKI.isDeepComponent:
            self.RCJKI.addAtomicElement(None)
        elif self.RCJKI.isCharacterGlyph:
            self.RCJKI.addDeepComponent(None)

    def removeDeepComponentButtonCallback(self, sender):
        if self.RCJKI.isDeepComponent:
            self.RCJKI.removeAtomicElement(None)
        elif self.RCJKI.isCharacterGlyph:
            self.RCJKI.removeDeepComponent(None)


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

        self.xTitle = TextBox(
            (5, 55, 50, 20),
            "x", 
            sizeStyle = 'small')
        self.xInput = EditText(
            (55, 55, 50, 20),
            '', 
            sizeStyle='small', 
            callback = self.setTransformCallback, 
            formatter = numberFormatter)

        self.yTitle = TextBox(
            (110, 55, 50, 20),
            "y", 
            sizeStyle = 'small')
        self.yInput = EditText(
            (160, 55, 50, 20),
            '', 
            sizeStyle='small', 
            callback = self.setTransformCallback, 
            formatter = numberFormatter)

        self.scalexTitle = TextBox(
            (5, 80, 50, 20),
            "scalex", 
            sizeStyle = 'small')
        self.scalexInput = EditText(
            (55, 80, 50, 20),
            '', 
            sizeStyle='small', 
            callback = self.setTransformCallback, 
            formatter = numberFormatter)

        self.scaleyTitle = TextBox(
            (110, 80, 50, 20),
            "scaley", 
            sizeStyle = 'small')
        self.scaleyInput = EditText(
            (160, 80, 50, 20),
            '', 
            sizeStyle='small', 
            callback = self.setTransformCallback, 
            formatter = numberFormatter)

        self.rotationTitle = TextBox(
            (5, 105, 50, 20),
            "rotation", 
            sizeStyle = 'small')
        self.rotationInput = EditText(
            (55, 105, 50, 20),
            '', 
            sizeStyle='small', 
            callback = self.setTransformCallback, 
            formatter = numberFormatter)

        self.tcenterxTitle = TextBox(
            (5, 130, 50, 20),
            "tcenterx", 
            sizeStyle = 'small')
        self.tcenterxInput = EditText(
            (55, 130, 50, 20),
            '', 
            sizeStyle='small', 
            callback = self.setTransformCallback, 
            formatter = numberFormatter)

        self.tcenteryTitle = TextBox(
            (110, 130, 50, 20),
            "tcentery", 
            sizeStyle = 'small')
        self.tcenteryInput = EditText(
            (160, 130, 50, 20),
            '', 
            sizeStyle='small', 
            callback = self.setTransformCallback, 
            formatter = numberFormatter)

        self.selectedDeepComponentTransform = None

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

    def setTransformationsField(self):
        sel = self.RCJKI.currentGlyph.selectedElement
        if not self.RCJKI.currentGlyph.selectedElement: 
            self.xInput.set("")
            self.yInput.set("")
            self.scalexInput.set("")
            self.scaleyInput.set("")
            self.rotationInput.set("")
            self.tcenterxInput.set("")
            self.tcenteryInput.set("")
            self.selectedDeepComponentTransform = None
            return

        self.selectedDeepComponentTransform = self.RCJKI.currentGlyph._deepComponents[sel[0]].transform
        if self.RCJKI.currentGlyph.selectedSourceAxis:
            for dcs in self.RCJKI.currentGlyph._glyphVariations:
                if dcs.sourceName == self.RCJKI.currentGlyph.selectedSourceAxis:
                    self.selectedDeepComponentTransform = dcs.deepComponents[sel[0]].transform

        x = self.selectedDeepComponentTransform["x"]
        y = self.selectedDeepComponentTransform["y"]
        scalex = self.selectedDeepComponentTransform["scalex"]
        scaley = self.selectedDeepComponentTransform["scaley"]
        rotation = self.selectedDeepComponentTransform["rotation"]
        tcenterx = self.selectedDeepComponentTransform["tcenterx"]
        tcentery = self.selectedDeepComponentTransform["tcentery"]

        self.xInput.set(x)
        self.yInput.set(y)
        self.scalexInput.set(scalex*1000)
        self.scaleyInput.set(scaley*1000)
        self.rotationInput.set(rotation)
        self.tcenterxInput.set(tcenterx)
        self.tcenteryInput.set(tcentery)

    def setTransformCallback(self, sender):
        if not self.selectedDeepComponentTransform:
            self.setTransformationsField()
        fields = [self.xInput, self.yInput, self.scalexInput, self.scaleyInput, self.rotationInput, self.tcenterxInput, self.tcenteryInput]
        transform = ["x", "y", "scalex", "scaley", "rotation", "tcenterx", "tcentery"]
        for f, t in zip(fields, transform):
            if f.get() == "":
                if t not in ["scalex", "scaley"]:
                    self.selectedDeepComponentTransform[t] = 0
                else:
                    self.selectedDeepComponentTransform[t] = 1000
                f.set(self.selectedDeepComponentTransform[t])
                self.RCJKI.currentGlyph.redrawSelectedElementSource = True
                self.RCJKI.currentGlyph.redrawSelectedElementPreview = True
            else:
                if t not in ["scalex", "scaley"]:
                    self.selectedDeepComponentTransform[t] = f.get()
                else:
                    self.selectedDeepComponentTransform[t] = f.get()/1000
                self.RCJKI.currentGlyph.redrawSelectedElementSource = True
                self.RCJKI.currentGlyph.redrawSelectedElementPreview = True
        self.RCJKI.updateDeepComponent(update = False)

    def alignSelectedElements(self, glyph, align = "left"):

        class SelectedElements:
        
            def __init__(self, settings, glyph):
                self.settings = settings
                self.glyph = glyph
                
            def __repr__(self):
                return f"< settings:{self.settings}, glyph:{self.glyph} >"

        selection = glyph.selectedElement
        elements = []
        # loc = {}
        # if glyph.selectedSourceAxis:
        #     loc = {glyph.selectedSourceAxis:1}
        preview = [g.glyph for x in glyph.preview(forceRefresh=False)]
        # preview = [g.glyph for g in glyph.previewGlyph]
        for i, x in zip(selection, glyph._getSelectedElement()):
            elements.append(SelectedElements(x, preview[i]))
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

    def __init__(self, RCJKI, glyphVariationsAxes = [], deepComponentAxes = [], axes = []):
        self.RCJKI = RCJKI
        self.glyphVariationsAxes = glyphVariationsAxes
        self.deepComponentAxes = deepComponentAxes
        self.w = Window((0, 0, 400, 850), self.RCJKI.currentGlyph.name, minSize = (100, 200), closable = False)

        self.type = "characterGlyph"
        
        self.compositionRulesItem = CompositionRulesGroup((10, 0, -10, -0), self.RCJKI, self)
        self.previewItem = PreviewGroup((10, 0, -10, -0), self.RCJKI)

        self.axesItem = AxesGroup((10, 0, -10, -0), self.RCJKI, self, self.type, axes)
        self.sourcesItem = SourcesGroup((10, 0, -10, -0), self.RCJKI, self, self.type, glyphVariationsAxes)

        # self.glyphVariationAxesItem = GlyphVariationAxesGroup((0, 0, -0, -0), self.RCJKI, self, "characterGlyph", glyphVariationsAxes)
        self.deepComponentAxesItem = DeepComponentAxesGroup((10, 0, -10, -0), self.RCJKI, deepComponentAxes)
        self.deepComponentListItem = DeepComponentListGroup((10, 0, -10, -0), self.RCJKI)
        self.propertiesItem = PropertiesGroup((10, 0, -10, -0), self.RCJKI, self)
        self.transformationItem = TransformationGroup((10, 0, -10, -0), self.RCJKI, self)

        descriptions = [
                       dict(label="Composition Rules", view=self.compositionRulesItem, size=100, collapsed=False, canResize=True),
                       dict(label="Preview", view=self.previewItem, minSize=100, size=300, collapsed=False, canResize=True),

                       dict(label="Font axes", view=self.axesItem, minSize=80, size=100, collapsed=False, canResize=True),
                       dict(label="Glyph Sources", view=self.sourcesItem, minSize=80, size=100, collapsed=False, canResize=True),

                       # dict(label="Font variation axes", view=self.glyphVariationAxesItem, minSize=80, size=150, collapsed=False, canResize=True),
                       dict(label="Deep component axes", view=self.deepComponentAxesItem, minSize=100, size=150, collapsed=False, canResize=True),
                       dict(label="Deep component list", view=self.deepComponentListItem, minSize=100, size=150, collapsed=False, canResize=True),
                       dict(label="Transformation", view=self.transformationItem, minSize = 80, size=160, collapsed=False, canResize=True),
                       dict(label="Properties", view=self.propertiesItem, minSize = 80, size=80, collapsed=False, canResize=True),
                       
                       ]

        self.w.accordionView = AccordionView((0, 0, -0, -0), descriptions)
        self.previewItem.update()
        self.propertiesItem.setglyphState()
        self.w.open()
        
class DeepComponentInspector(Inspector):

    def __init__(self, RCJKI, glyphVariationsAxes = [], atomicElementAxes = [], axes = []):
        self.RCJKI = RCJKI
        self.w = Window((0, 0, 400, 870), self.RCJKI.currentGlyph.name, minSize = (100, 200), closable = False)

        self.type = "deepComponent"
        
        self.relatedGlyphsItem = RelatedGlyphsGroup((10, 0, -10, -0), self.RCJKI, self)
        self.previewItem = PreviewGroup((10, 0, -10, -0), self.RCJKI)

        self.axesItem = AxesGroup((10, 0, -10, -0), self.RCJKI, self, self.type, axes)
        self.sourcesItem = SourcesGroup((10, 0, -10, -0), self.RCJKI, self, self.type, glyphVariationsAxes)

        # self.glyphVariationAxesItem = GlyphVariationAxesGroup((0, 0, -0, -0), self.RCJKI, self, "deepComponent", glyphVariationsAxes)
        self.deepComponentAxesItem = DeepComponentAxesGroup((10, 0, -10, -0), self.RCJKI, atomicElementAxes)
        self.deepComponentListItem = DeepComponentListGroup((10, 0, -10, -0), self.RCJKI)
        self.propertiesItem = PropertiesGroup((10, 0, -10, -0), self.RCJKI, self)
        self.transformationItem = TransformationGroup((10, 0, -10, -0), self.RCJKI, self)

        descriptions = [
                       dict(label="Related glyphs", view=self.relatedGlyphsItem, size=140, collapsed=False, canResize=True),
                       dict(label="Preview", view=self.previewItem, minSize=100, size=300, collapsed=False, canResize=True),

                       dict(label="Glyph axes", view=self.axesItem, minSize=80, size=150, collapsed=False, canResize=True),
                       dict(label="Glyph Sources", view=self.sourcesItem, minSize=80, size=150, collapsed=False, canResize=True),

                       # dict(label="Deep component axes", view=self.glyphVariationAxesItem, minSize=100, size=170, collapsed=False, canResize=True),
                       dict(label="Atomic element axes", view=self.deepComponentAxesItem, minSize=100, size=150, collapsed=False, canResize=True),
                       dict(label="Atomic element list", view=self.deepComponentListItem, minSize=100, size=150, collapsed=False, canResize=True),
                       dict(label="Transformation", view=self.transformationItem, minSize = 80, size=160, collapsed=False, canResize=True),
                       dict(label="Properties", view=self.propertiesItem, minSize = 80, size=80, collapsed=False, canResize=True),
                       
                       ]

        self.w.accordionView = AccordionView((0, 0, -0, -0), descriptions)
        self.previewItem.update()
        self.propertiesItem.setglyphState()
        self.w.open()
        
class AtomicElementInspector(Inspector):

    def __init__(self, RCJKI, glyphVariationsAxes = [], axes = []):
        self.RCJKI = RCJKI
        self.w = Window((0, 0, 400, 780), self.RCJKI.currentGlyph.name, minSize = (100, 200), closable = False)

        self.type = "atomicElement"
        
        self.previewItem = PreviewGroup((10, 0, -10, -0), self.RCJKI)

        self.axesItem = AxesGroup((10, 0, -10, -0), self.RCJKI, self, self.type, axes)
        self.sourcesItem = SourcesGroup((10, 0, -10, -0), self.RCJKI, self, self.type, glyphVariationsAxes)

        # self.glyphVariationAxesItem = GlyphVariationAxesGroup((0, 0, -0, -0), self.RCJKI, self, "atomicElement", glyphVariationsAxes)
        self.propertiesItem = PropertiesGroup((10, 0, -10, -0), self.RCJKI, self)

        descriptions = [
                       dict(label="Preview", view=self.previewItem, minSize=100, size=300, collapsed=False, canResize=True),

                       dict(label="Glyph axes", view=self.axesItem, minSize=80, size=150, collapsed=False, canResize=True),
                       dict(label="Glyph Sources", view=self.sourcesItem, minSize=80, size=150, collapsed=False, canResize=True),

                       # dict(label="Atomic element axes", view=self.glyphVariationAxesItem, minSize=100, size=170, collapsed=False, canResize=True),
                       dict(label="Properties", view=self.propertiesItem, minSize = 80, size=80, collapsed=False, canResize=True)
                       ]

        self.w.accordionView = AccordionView((0, 0, -0, -0), descriptions)
        self.previewItem.update()
        self.propertiesItem.setglyphState()
        self.w.open()

