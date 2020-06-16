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
from vanilla.dialogs import getFile, getFolder
from mojo.canvas import Canvas
import mojo.drawingTools as mjdt
from mojo.UI import CurrentGlyphWindow
from utils import files
from AppKit import NumberFormatter, NSColor
from mojo.UI import PostBannerNotification
from mojo.extensions import getExtensionDefault, setExtensionDefault

import json, os
blackrobocjk_locker = "com.black-foundry.blackrobocjk_locker"

transparentColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 1, 0)

class SelectLayerSheet():
    def __init__(self, RCJKI, availableLayers):
        self.RCJKI = RCJKI
        self.availableLayers = availableLayers
        self.parent = CurrentGlyphWindow()
        self.parent.sheet = Sheet((300, 420), self.parent.w)
        
        self.previewGlyph = None
        
        self.aegv =  self.RCJKI.currentGlyph.lib.get('robocjk.atomicElement.glyphVariations',{})
        self.parent.sheet.layerList = List(
            (0, 0, -0, 80),
            [l.layer.name for l in self.availableLayers if l.layer.name not in self.aegv.values()],
            allowsMultipleSelection = False,
            selectionCallback = self.updatePreview
            )
        
        self.parent.sheet.newAxisNameTextBox = TextBox(
            (0, 80, 100, 20), 
            'Axis Name:'
            )
        layerName = files.normalizeCode(str(len(self.aegv)), 4)
        self.parent.sheet.newAxisNameEditText = EditText(
            (100, 80, -0, 20), 
            layerName
            )
    
        self.parent.sheet.canvasPreview = Canvas(
            (0, 100, -0, -20), 
            canvasSize=(300, 300), 
            delegate=self
            )

        self.updatePreview(None)
        
        self.parent.sheet.addButton = Button(
            (-150,-20, 150, 20), 
            'Add', 
            callback=self.addLayer
            )

        self.parent.sheet.closeButton = Button(
            (-300,-20, 150, 20), 
            'Close', 
            callback=self.closeSheet
            )

        self.parent.sheet.setDefaultButton(self.parent.sheet.addButton)
        self.parent.sheet.open()
        
    def addLayer(self, sender):
        newAxisName = self.parent.sheet.newAxisNameEditText.get()
        newLayerName = self.parent.sheet.layerList.get()[self.parent.sheet.layerList.getSelection()[0]]
        if newAxisName in self.RCJKI.currentGlyph._glyphVariations.axes:
            PostBannerNotification('Impossible', "Layer name already exist")
            return
        self.RCJKI.currentGlyph.addGlyphVariation(newAxisName, newLayerName)
        self.RCJKI.updateListInterface()
        self.RCJKI.updateDeepComponent(update = False)
        
    def closeSheet(self, sender):
        self.parent.sheet.close()
    
    def updatePreview(self, sender):
        if not self.parent.sheet.layerList.getSelection() : return
        self.previewGlyph = None
        for l in self.availableLayers:
            if l.layer.name == self.parent.sheet.layerList.get()[self.parent.sheet.layerList.getSelection()[0]]:
                self.previewGlyph = l
        self.parent.sheet.canvasPreview.update()
                
    def draw(self):
        if not self.previewGlyph: return
        mjdt.save()
        mjdt.translate(75, 95)
        mjdt.scale(.15)
        mjdt.fill(0, 0, 0, 1)
        mjdt.drawGlyph(self.previewGlyph)  
        mjdt.restore()

class SelectAtomicElementSheet():

    def __init__(self, RCJKI, atomicElementsNames):
        self.RCJKI = RCJKI
        self.atomicElementsNames = atomicElementsNames
        self.atomicElementName = None
        self.previewGlyph = None
        self.parent = CurrentGlyphWindow()
        self.parent.sheet = Sheet((300, 400), self.parent.w)
        
        self.parent.sheet.searchBox = SearchBox(
            (0, 0, -0, 20),
            callback = self.searchBoxCallback
            )
        self.parent.sheet.atomicElementList = List(
            (0, 20, -0, -220),
            self.atomicElementsNames,
            allowsMultipleSelection = False,
            selectionCallback = self.atomicElementListSelectionCallback
            )
        self.parent.sheet.atomicElementList.setSelection([])

        self.parent.sheet.canvasPreview = Canvas(
            (0, -220, -0, -20), 
            canvasSize=(300, 200), 
            delegate=self
            )
        
        self.parent.sheet.addButton = Button(
            (-150,-20, 150, 20), 
            'Add', 
            callback=self.addAtomicElement
            )
        self.parent.sheet.closeButton = Button(
            (-300,-20, 150, 20), 
            'Close', 
            callback=self.closeSheet
            )
        self.parent.sheet.setDefaultButton(self.parent.sheet.addButton)
        self.parent.sheet.open()

    def searchBoxCallback(self, sender):
        name = sender.get()
        l = files._getFilteredListFromName(self.atomicElementsNames, name)
        if not l:
            l = self.atomicElementsNamest
        self.parent.sheet.atomicElementList.set(l)
    
    def closeSheet(self, sender):
        self.parent.sheet.close()

    def atomicElementListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        self.atomicElementName = sender.get()[sel[0]]
        self.previewGlyph = self.RCJKI.currentFont._RFont[self.atomicElementName]
        self.parent.sheet.canvasPreview.update()
    
    def addAtomicElement(self, sender):
        if self.atomicElementName is None: return
        self.RCJKI.currentGlyph.addAtomicElementNamed(self.atomicElementName)
        self.RCJKI.updateDeepComponent(update = False)

    def draw(self):
        if self.previewGlyph is None: return
        glyphs = self.previewGlyph.layers
        mjdt.save()
        mjdt.translate(75, 95)
        mjdt.scale(.15)
        mjdt.fill(0, 0, 0, 1/(len(glyphs)+1e-10))
        for glyph in glyphs:
            mjdt.drawGlyph(glyph)  
        mjdt.restore()

class SelectFontVariationSheet():
    def __init__(self, RCJKI, view):
        self.RCJKI = RCJKI
        self.view = view
        self.parent = CurrentGlyphWindow()
        self.parent.sheet = Sheet((300, 40), self.parent.w)
        l = [axis for axis in self.RCJKI.currentFont._RFont.lib.get('robocjk.fontVariations', []) if axis not in self.RCJKI.currentGlyph._glyphVariations.axes]
        if not l: l=[""]
        popupbuttonlist = PopUpButtonListCell(l)
        self.parent.sheet.fontVariationsList = List((0, 0, -0, 20), 
            [{'AxisName':l[0]}],
            columnDescriptions = [{"title":"AxisName", "cell":popupbuttonlist, "binding": "selectedValue", "editable":True, "width":290}],
            showColumnTitles = False,
            allowsMultipleSelection = False
            )
        self.parent.sheet.addButton = Button(
            (-150,-20, 150, 20), 
            'Add', 
            callback=self.addCharacterGlyphFontVariation
            )
        self.parent.sheet.closeButton = Button(
            (-300,-20, 150, 20), 
            'Close', 
            callback=self.closeSheet
            )
        self.parent.sheet.setDefaultButton(self.parent.sheet.addButton)
        self.parent.sheet.open()
        
    def addCharacterGlyphFontVariation(self, sender):
        name = self.parent.sheet.fontVariationsList.get()[self.parent.sheet.fontVariationsList.getSelection()[0]]['AxisName']
        self.RCJKI.currentGlyph.addCharacterGlyphNamedVariationToGlyph(name)
        self.RCJKI.updateListInterface()

        source = []
        if self.RCJKI.currentGlyph._glyphVariations:
            source = [{'Axis':axis, 'PreviewValue':0} for axis in self.RCJKI.currentGlyph._glyphVariations]
        isel = len(source)
        self.RCJKI.currentGlyph.selectedSourceAxis = source[isel-1]['Axis']
        self.view.sourcesList.setSelection([isel-1])
        self.RCJKI.updateDeepComponent(update = False)
        
    def closeSheet(self, sender):
        self.parent.sheet.close()

class SelectDeepComponentSheet():

    def __init__(self, RCJKI, deepComponentsNames):
        self.RCJKI = RCJKI
        self.deepComponentsNames = deepComponentsNames
        self.parent = CurrentGlyphWindow()
        self.parent.sheet = Sheet((300, 400), self.parent.w)
        self.glyph = None

        self.parent.sheet.canvasPreview = Canvas(
            (0, -220, -0, -20), 
            canvasSize=(300, 300), 
            delegate=self
            )

        self.parent.sheet.searchBox = SearchBox(
            (0, 0, -0, 20),
            callback = self.searchBoxCallback
            )
        self.parent.sheet.deepComponentList = List(
            (0, 20, -0, -220),
            self.deepComponentsNames,
            selectionCallback = self.deepComponentListSelectionCallback,
            allowsMultipleSelection = False
            )
        if self.deepComponentsNames:
            self.getDeepComponentPreview(self.deepComponentsNames[0])
            self.deepComponentName = self.deepComponentsNames[0]
        
        self.parent.sheet.addButton = Button(
            (-150,-20, 150, 20), 
            'Add', 
            callback=self.addDeepComponentList
            )
        self.parent.sheet.closeButton = Button(
            (-300,-20, 150, 20), 
            'Close', 
            callback=self.closeSheet
            )
        self.parent.sheet.setDefaultButton(self.parent.sheet.addButton)
        self.parent.sheet.open()

    def searchBoxCallback(self, sender):
        name = sender.get()
        l = files._getFilteredListFromName(self.deepComponentsNames, name)
        if not l:
            l = self.deepComponentsNames
        self.parent.sheet.deepComponentList.set(l)

    def deepComponentListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        self.deepComponentName = sender.get()[sel[0]]
        self.getDeepComponentPreview(self.deepComponentName)

    def getDeepComponentPreview(self, deepComponentName):
        self.glyph = self.RCJKI.currentFont[deepComponentName]
        self.glyph.preview.computeDeepComponents(update = False)
        self.parent.sheet.canvasPreview.update()
    
    def closeSheet(self, sender):
        self.parent.sheet.close()
    
    def addDeepComponentList(self, sender):
        self.RCJKI.currentGlyph.addDeepComponentNamed(self.deepComponentName)
        self.RCJKI.updateDeepComponent(update = False)

    def draw(self):
        if self.glyph is None: return
        mjdt.save()
        mjdt.translate(75, 35)
        mjdt.scale(.15)
        mjdt.fill(0, 0, 0, 1)
        for atomicinstance in self.glyph.preview.axisPreview:
            mjdt.drawGlyph(atomicinstance.getTransformedGlyph()) 
        mjdt.restore()

numberFormatter = NumberFormatter()

class FontInfosSheet():

    def __init__(self, RCJKI, parentWindow, posSize):
        self.RCJKI = RCJKI
        if not self.RCJKI.get("currentFont"): return
        fontvariations = self.RCJKI.currentFont._RFont.lib.get('robocjk.fontVariations', [])
        if 'robocjk.defaultGlyphWidth' not in self.RCJKI.currentFont._RFont.lib:
            self.RCJKI.currentFont._RFont.lib['robocjk.defaultGlyphWidth'] = 1000
        defaultGlyphWidth = self.RCJKI.currentFont._RFont.lib['robocjk.defaultGlyphWidth']

        self.s = Sheet(posSize, parentWindow)
        self.s.fontVariationAxisList = List(
            (10, 10, 200, 100), 
            fontvariations, 
            editCallback = self.fontVariationAxisListEditCallback
            )
        self.s.addVariation = Button(
            (10, 110, 100, 20), 
            "+",
            callback = self.addVariationCallback,
            sizeStyle = 'small'
            )
        self.s.removeVariation = Button(
            (110, 110, 100, 20), 
            "-",
            callback = self.removeVariationCallback,
            sizeStyle = 'small'
            )

        self.s.defaultGlyphWidthTitle = TextBox(
            (10, 142, 150, 20),
            'Default Glyph Width',
            sizeStyle = "small"
            ) 

        self.s.defaultGlyphWidth = EditText(
            (125, 140, 85, 20),
            defaultGlyphWidth,
            sizeStyle = 'small',
            formatter = numberFormatter,
            callback = self.defaultGlyphWidthCallback
            )

        self.s.loadDataBase = Button(
            (10, 170, 200, 20),
            'Load Data Base',
            callback = self.loadDataBaseCallback,
            sizeStyle = 'small'
            )

        # self.s.exportDataBase = Button(
        #     (10, 190, 200, 20),
        #     'Export Data Base',
        #     callback = self.exportDataBaseCallback,
        #     sizeStyle = 'small'
        #     )

        self.s.closeButton = Button(
            (10, -30, -10, 20), 
            'close', 
            self.closeCallback,
            sizeStyle = 'small'
            )
        self.s.open()

    def fontVariationAxisListEditCallback(self, sender):
        self.RCJKI.currentFont._RFont.lib['robocjk.fontVariations'] = sender.get()

    def addVariationCallback(self, sender):
        l = 0
        name = files.normalizeCode(files.int_to_column_id(l), 4)
        while name in self.s.fontVariationAxisList.get():
            l += 1
            name = files.normalizeCode(files.int_to_column_id(l), 4)
        self.s.fontVariationAxisList.append(name)
        self.RCJKI.currentFont._RFont.lib['robocjk.fontVariations'].append(name)

    def defaultGlyphWidthCallback(self, sender):
        try:
            self.RCJKI.currentFont._RFont.lib['robocjk.defaultGlyphWidth'] = sender.get()
            self.RCJKI.currentFont.defaultGlyphWidth = sender.get()
        except: pass

    def removeVariationCallback(self, sender):
        sel = self.s.fontVariationAxisList.getSelection()
        if not sel: return
        l = self.s.fontVariationAxisList.get()
        l.pop(sel[0])
        self.s.fontVariationAxisList.set(l)
        self.RCJKI.currentFont._RFont.lib['robocjk.fontVariations'] = self.s.fontVariationAxisList.get()

    def loadDataBaseCallback(self, sender):
        path = getFile()[0]
        if path.endswith("txt"):
            with open(path, 'r', encoding = 'utf-8') as file:
                txt = file.readlines()
            self.RCJKI.dataBase = {}
            for line in txt:
                k, v = line.strip('\n').split(':')
                self.RCJKI.dataBase[k] = v
        elif path.endswith("json"):
            with open(path, 'r', encoding = 'utf-8') as file:
                self.RCJKI.dataBase = json.load(file)
        self.RCJKI.exportDataBase()

    # def exportDataBaseCallback(self, sender):
    #     self.RCJKI.exportDataBase()
        
    def closeCallback(self, sender):
        self.RCJKI.currentFont.createLayersFromVariationAxis()
        self.s.close()

class NewCharacterGlyph:

    def __init__(self, RCJKI, parentWindow):
        self.RCJKI = RCJKI
        self.window = parentWindow
        self.w = Sheet((400, 300), self.window)
        self.w.segmentedButton = SegmentedButton(
            (10, 10, -10, 20),
            [dict(title = "Custom"), dict(title = "Related to deep components")],
            callback = self.segmentedButtonCallback
            )
        self.w.segmentedButton.set(0)

        self.w.custom = Group((0, 25, -0, -0))
        self.w.custom.show(True)
        self.w.related = Group((0, 25, -0, -0))
        self.w.related.show(False)
        self.groups = [self.w.custom, self.w.related]

        self.DCSet = set(self.RCJKI.currentFont.deepComponentSet)

        self.w.custom.remind = TextBox(
            (10, 10, -10, 20),
            "Glyphs names (separate with space) or characters",
            sizeStyle = 'small'
            )
        self.w.custom.characterField = TextEditor(
            (10, 30, -10, -50),
            ""
            )
        self.w.custom.relatedDeepComponents = CheckBox(
            (10, -60, -10, -10),
            "Create related deep components",
            value = True,
            sizeStyle = "small"
            )
        self.lockNewGlyph = True
        self.w.custom.lockNewGlyphs = CheckBox(
            (10, -25, -10, -10),
            "Lock new glyphs",
            value = self.lockNewGlyph,
            sizeStyle = "small",
            callback = self.lockNewGlyphsCallback
            )
        self.w.custom.addButton = Button(
            (-195, -30, -30, -10),
            "Add",
            callback = self.addButtonCallback,
            )

        self.w.related.deepComponentsTitle = TextBox(
            (10, 10, -10, 20),
            "Deep Components",
            sizeStyle = 'small'
            )
        checkBoxList = CheckBoxListCell()
        self.deepComponentList = []
        for n in self.RCJKI.currentFont.deepComponentSet:
            if not n.startswith("DC"): continue
            cell = dict(sel = 0, char = chr(int(n.split('_')[1], 16)))
            if cell not in self.deepComponentList:
                self.deepComponentList.append(cell)

        self.w.related.searchBox = SearchBox(
            (10, 30, 100, 20),
            "",
            callback = self.relatedDCSearchBox
            )

        self.w.related.deepComponentsList = List(
            (10, 50, 100, -40),
            self.deepComponentList,
            columnDescriptions = [
                {"title":"sel", "cell":checkBoxList, "width":20}, 
                {"title":"char"}
                ],
            drawFocusRing = False,
            showColumnTitles = False,
            editCallback = self.deepComponentsListEditCallback
            )
        self.w.related.characterField = TextEditor(
            (110, 30, -10, -60),
            "",
            readOnly = True
            )
        self.w.related.addfromField = Button(
            (110, -60, -10, -40),
            "Add",
            callback = self.addfromFieldCallback
            )
        self.w.related.lockNewGlyphs = CheckBox(
            (10, -25, -10, -10),
            "Lock new glyphs",
            value = self.lockNewGlyph,
            sizeStyle = "small",
            callback = self.lockNewGlyphsCallback
            )
        self.w.related.addAllPossibleButton = Button(
            (-225, -30, -30, -10),
            "Add all possible characters",
            callback = self.addAllPossibleCallback
            )
        self.w.closeButton = SquareButton(
            (-30, -30, -10, -10),
            "x",
            callback = self.closeCallback,
            sizeStyle = "small"
            )
        self.w.closeButton.getNSButton().setFocusRingType_(1)
        self.w.closeButton.getNSButton().setBackgroundColor_(transparentColor)
        self.w.closeButton.getNSButton().setBordered_(False)

        self.w.open()

    def lockNewGlyphsCallback(self, sender):
        self.lockNewGlyph = sender.get()

    def addGlyph(self, name, addRelatedDC=False):
        added = set()
        try:
            self.RCJKI.currentFont[name]
            return [name]
        except:
            self.RCJKI.currentFont.newGlyph("characterGlyph", name)
            added.add(name)
            if addRelatedDC and self.RCJKI.dataBase:
                dcChars = self.RCJKI.dataBase[chr(int(name[3:], 16))]
                DC = set(["DC_%s_00"%hex(ord(c))[2:].upper() for c in dcChars])
                # for name in DC:
                #     added.add(name)
                for name in DC-self.DCSet:
                    try:
                        self.RCJKI.currentFont[name]
                    except:
                        added.add(name)
                        self.RCJKI.currentFont.newGlyph("deepComponent", name)
            return list(added)

    def addButtonCallback(self, sender):
        addRelatedDC = self.w.custom.relatedDeepComponents.get()
        txt = self.w.custom.characterField.get().split(" ")
        glyphs = []
        for e in txt:
            if e.startswith("uni"):
                for dcname in self.addGlyph(e, addRelatedDC):
                    glyphs.append(self.RCJKI.currentFont[dcname])
            else:
                for c in e:
                    name = files.unicodeName(c)
                    for dcname in self.addGlyph(name, addRelatedDC):
                        glyphs.append(self.RCJKI.currentFont[dcname])
        self.lockGlyphs(glyphs)
        self.window.deepComponent.set(self.RCJKI.currentFont.deepComponentSet)
        charSet = [dict(char = files.unicodeName2Char(x), name = x) for x in self.RCJKI.currentFont.characterGlyphSet]
        self.window.characterGlyph.set(charSet)
        self.w.close()

    def lockGlyphs(self, glyphs):
        if self.lockNewGlyph:
            lock = self.RCJKI.currentFont.locker.batchLock(glyphs)
            PostBannerNotification("Lock %s"%["failed", "succeeded"][lock], "")

    def relatedDCSearchBox(self, sender):
        char = sender.get()
        for i, item in enumerate(self.deepComponentList):   
            if item["char"] == char:
                self.w.related.deepComponentsList.setSelection([i])
                break

    def deepComponentsListEditCallback(self, sender):
        deepComponents = []
        for i, e in enumerate(sender.get()):
            if e["sel"]:
                deepComponents.append(self.deepComponentList[i]["char"])
        characters = self.getRelatedCharacterToSelected(deepComponents) 
        self.w.related.characterField.set(characters)

    def addfromFieldCallback(self, sender):
        characters = self.w.related.characterField.get()
        glyphs = []
        for character in characters:
            name = files.unicodeName(character)
            for dcname in self.addGlyph(name):
                glyphs.append(self.RCJKI.currentFont[dcname])
        self.lockGlyphs(glyphs)
        print("-----------------")
        print("ADDED CHARACTERS: \n%s"%characters)
        print("-----------------")
        self.w.close()

    def addAllPossibleCallback(self, sender):
        deepComponents = [e["char"] for e in self.deepComponentList]
        characters = self.getRelatedCharacterToSelected(deepComponents)
        glyphs = []
        for character in characters:
            name = files.unicodeName(character)
            for dcname in self.addGlyph(name):
                glyphs.append(self.RCJKI.currentFont[dcname])
        self.lockGlyphs(glyphs)
        print("-----------------")
        print("ADDED CHARACTERS: \n%s"%characters)
        print("-----------------")
        self.w.close()

    def getRelatedCharacterToSelected(self, deepComponents):
        relatedChars = set()
        deepComponentsSet = set(deepComponents)
        for k, v in self.RCJKI.dataBase.items():
            setv = set(v)
            if setv & deepComponentsSet:
                if not setv - deepComponentsSet:
                    relatedChars.add(k)
        return "".join(sorted(list(relatedChars)))

    def closeCallback(self, sender):
        self.w.close()

    def segmentedButtonCallback(self, sender):
        for i, g in enumerate(self.groups):
            g.show(i == sender.get())

class Login:

    def __init__(self, RCJKI, parentWindow):
        self.RCJKI = RCJKI
        self.w = Sheet((400, 200), parentWindow)

        self.w.segmentedButton = SegmentedButton(
            (10, 10, -10, 20),
            [dict(title = "Git"), dict(title = "mySQL")],
            callback = self.segmentedButtonCallback
            )
        self.w.segmentedButton.set(0)
        self.w.git = Group((0, 30, -0, -0))
        self.w.git.show(not self.RCJKI.mysql)
        self.w.mysql = Group((0, 30, -0, -0))
        self.w.mysql.show(self.RCJKI.mysql)

        self.w.git.userNameTitle = TextBox(
            (10, 10, 100, 20),
            "UserName"
            )
        self.w.git.userName = EditText(
            (90, 10, -10, 20),
            getExtensionDefault(blackrobocjk_locker+"username", "")
            )
        self.w.git.passwordTitle = TextBox(
            (10, 40, 100, 20),
            "Password"
            )
        self.w.git.password = SecureEditText(
            (90, 40, -10, 20),
            getExtensionDefault(blackrobocjk_locker+"password", "")
            )
        self.w.git.hostlockerTitle = TextBox(
            (10, 70, 100, 20),
            "HostLocker"
            )
        self.w.git.hostlocker = EditText(
            (90, 70, -10, 20),
            getExtensionDefault(blackrobocjk_locker+"hostlocker", "")
            )
        self.w.git.hostLockerPasswordTitle = TextBox(
            (10, 100, 200, 20),
            "HostLocker password optional"
            )
        self.w.git.hostLockerPassword = SecureEditText(
            (200, 100, -10, 20),
            getExtensionDefault(blackrobocjk_locker+"hostlockerpassword", "")
            )
        self.w.cancelButton = Button(
            (10, -30, 100, -10),
            "Cancel",
            callback = self.cancelCallback
            )
        self.w.closeButton = Button(
            (110, -30, -10, -10),
            "Login",
            callback = self.closeCallback
            )

        self.w.mysql.userNameTitle = TextBox(
            (10, 10, 100, 20),
            "UserName"
            )
        self.w.mysql.userName = EditText(
            (90, 10, -10, 20),
            getExtensionDefault(blackrobocjk_locker+"mysql_username", "")
            )
        self.w.mysql.passwordTitle = TextBox(
            (10, 40, 100, 20),
            "Password"
            )
        self.w.mysql.password = SecureEditText(
            (90, 40, -10, 20),
            getExtensionDefault(blackrobocjk_locker+"mysql_password", "")
            )

        self.w.setDefaultButton(self.w.closeButton)
        self.w.open()

    def cancelCallback(self, sender):
        self.w.close()

    def closeCallback(self, sender):
        if not self.w.git.userName.get() or not self.w.git.password.get() or not self.w.git.hostlocker.get(): return

        self.RCJKI.gitUserName = self.w.git.userName.get()
        self.RCJKI.gitPassword = self.w.git.password.get()
        self.RCJKI.gitHostLocker = self.w.git.hostlocker.get()
        self.RCJKI.gitHostLockerPassword = self.w.git.hostLockerPassword.get()

        setExtensionDefault(blackrobocjk_locker+"username", self.RCJKI.gitUserName)
        setExtensionDefault(blackrobocjk_locker+"password", self.RCJKI.gitPassword)
        setExtensionDefault(blackrobocjk_locker+"hostlocker", self.RCJKI.gitHostLocker)
        setExtensionDefault(blackrobocjk_locker+"hostlockerpassword", self.RCJKI.gitHostLockerPassword)

        
        self.w.close()
        if not self.RCJKI.mysql:
            folder = getFolder()
            if not folder: return
            self.RCJKI.projectRoot = folder[0]
            self.RCJKI.setGitEngine()
            self.RCJKI.roboCJKView.setrcjkFiles()
        else:
            self.RCJKI.mysql_userName = self.w.mysql.userName.get()
            self.RCJKI.mysql_password = self.w.mysql.password.get()
            setExtensionDefault(blackrobocjk_locker+"mysql_username", self.RCJKI.mysql_userName)
            setExtensionDefault(blackrobocjk_locker+"mysql_password", self.RCJKI.mysql_password)
            self.RCJKI.getmySQLParams()
            self.RCJKI.connect2mysql()
            self.RCJKI.roboCJKView.setmySQLRCJKFiles()

    def segmentedButtonCallback(self, sender):
        for i, x in enumerate([self.w.git, self.w.mysql]):
            x.show(i == sender.get())
        self.RCJKI.mysql = sender.get()


class LockController:

    def __init__(self, RCJKI, parentWindow):
        self.RCJKI = RCJKI
        self.w = Sheet((340, 230), parentWindow)
        self.w.unlock = Group((0, 30, -0, -0))
        self.w.unlock.show(False)
        self.w.lock = Group((0, 30, -0, -0))
        self.locksGroup = [self.w.lock, self.w.unlock]
        self.w.segmentedButton = SegmentedButton(
            (10, 10, -10, 20),
            [dict(title = "Lock"), dict(title = "Unlock")],
            callback = self.segmentedButtonCallback
            )
        self.w.segmentedButton.set(0)
        self.w.lock.remind = TextBox(
            (10, 10, -10, 20),
            "Glyphs names (separate with space) or characters",
            sizeStyle = 'small'
            )
        self.w.lock.field = TextEditor(
            (10, 30, -10, -40),
            ""
            )
        self.w.lock.lockButton = Button(
            (10, -30, -30, 20),
            'lock',
            callback = self.lockButtonCallback
            )
        self.w.unlock.searchBox = SearchBox(
            (10, 10, 150, 20),
            callback = self.filterListCallback
            )
        self.currentGlyphName = None
        self.lockedList = [dict(sel = 0, name = x) for x in self.RCJKI.currentFont.locker.myLockedGlyphs]
        self.w.unlock.lockedGlyphsList = List(
            (10, 30, 150, -40),
            self.lockedList,
            columnDescriptions = [dict(title = "sel", cell = CheckBoxListCell(), width = 20), dict(title = "name")],
            showColumnTitles = False,
            allowsMultipleSelection = False,
            drawFocusRing = False,
            selectionCallback = self.lockedGlyphsListSelectionCallback
            )
        self.w.unlock.canvas = Canvas(
            (160, 10, -10, -40),
            delegate = self
            )
        self.w.unlock.unlockSelectedButton = Button(
            (10, -30, 150, -10),
            "Unlock selected",
            callback = self.unlockSelectedButtonCallback
            )
        self.w.unlock.unlockAllButton = Button(
            (160, -30, 150, -10),
            "Unlock all",
            callback = self.unlockAllButtonCallback
            )
        self.w.closeButton = SquareButton(
            (-30, -30, -0, -10),
            "x",
            callback = self.closeCallback
            )
        self.w.closeButton.getNSButton().setFocusRingType_(1)
        self.w.closeButton.getNSButton().setBackgroundColor_(transparentColor)
        self.w.closeButton.getNSButton().setBordered_(False)

        if self.lockedList:
            self.w.unlock.lockedGlyphsList.setSelection([0])
            self.lockedGlyphsListSelectionCallback(self.w.unlock.lockedGlyphsList)
        else:
            self.w.unlock.lockedGlyphsList.setSelection([])

    def segmentedButtonCallback(self, sender):
        for i, group in enumerate(self.locksGroup):
            group.show(i == sender.get())
        self.resetList()

    def lockedGlyphsListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            self.currentGlyphName = None
            return
        self.currentGlyphName = sender.get()[sel[0]]["name"]
        self.w.unlock.canvas.update()

    def lockGlyphs(self, glyphs):
        lock = self.RCJKI.currentFont.locker.batchLock(glyphs)
        PostBannerNotification("Lock %s"%["failed", "succeeded"][lock], "")

    def lockButtonCallback(self, sender):
        txt = self.w.lock.field.get().split()
        glyphs = []
        for e in txt:
            try:
                glyphs.append(self.RCJKI.currentFont[e])
            except:
                for c in e:
                    try: glyphs.append(self.RCJKI.currentFont[files.unicodeName(c)])
                    except: continue
        self.lockGlyphs(glyphs)

    def unlockSelectedButtonCallback(self, sender):
        f = self.RCJKI.currentFont
        glyphs = []
        filesToRemove = []
        for x in self.w.unlock.lockedGlyphsList.get():
            if x["sel"]:
                try:    
                    glyphs.append(f[x["name"]])
                except:
                    filesToRemove.append(x["name"])
        self.RCJKI.currentFont.locker.removeFiles(filesToRemove)
        if glyphs:
            self.unlockGlyphs(glyphs)
        self.resetList()

    def resetList(self):
        self.lockedList = [dict(sel = 0, name = x) for x in self.RCJKI.currentFont.locker.myLockedGlyphs]
        self.w.unlock.lockedGlyphsList.set(self.lockedList)
        self.w.unlock.lockedGlyphsList.setSelection([])
        self.currentGlyphName = None
        self.w.unlock.canvas.update()

    def unlockGlyphs(self, glyphs):
        unlock = self.RCJKI.currentFont.locker.batchUnlock(glyphs)
        PostBannerNotification("Unlock %s"%["failed", "succeeded"][unlock], "")

    def unlockAllButtonCallback(self, sender):
        f = self.RCJKI.currentFont
        glyphs = []
        filesToRemove = []
        for x in self.w.unlock.lockedGlyphsList.get():
            try: glyphs.append(f[x["name"]])
            except: 
                filesToRemove.append(x["name"])
        self.RCJKI.currentFont.locker.removeFiles(filesToRemove)
        self.unlockGlyphs(glyphs)
        self.resetList()        

    def filterListCallback(self, sender):
        if not sender.get():
            l = self.lockedList
        else:
            try:
                name = files.unicodeName(sender.get())
            except:
                name = str(sender.get())
            lockedNames = [x["name"] for x in self.lockedList]
            l = [dict(sel = 0, name = x) for x in files._getFilteredListFromName(lockedNames, name)]
        if not l:
            l = self.lockedList

        self.w.unlock.lockedGlyphsList.set(l)
        self.w.unlock.lockedGlyphsList.setSelection([])

    def draw(self):
        if self.currentGlyphName is None: return
        glyph = self.RCJKI.currentFont[self.currentGlyphName]
        mjdt.save()
        s = .1
        mjdt.scale(s, s)
        mjdt.translate(350, 350)
        if glyph.type != "atomicElement":
            glyph.preview.computeDeepComponents(update = False)
            self.RCJKI.drawer.drawAxisPreview(
                glyph,
                (0, 0, 0, 1),
                s,
                (0, 0, 0, 1)
                )
        mjdt.drawGlyph(glyph)
        mjdt.restore()

    def open(self):
        self.w.open()

    def closeCallback(self, sender):
        self.w.close()

