from vanilla import *
from vanilla.dialogs import getFile
from mojo.canvas import Canvas
import mojo.drawingTools as mjdt
from mojo.UI import CurrentGlyphWindow
from utils import files
from AppKit import NumberFormatter
import json, os

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
        self.RCJKI.currentGlyph.addGlyphVariation(newAxisName, newLayerName)
        self.RCJKI.updateListInterface()
        self.RCJKI.updateDeepComponent()
        
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
        self.RCJKI.updateDeepComponent()

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
    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.parent = CurrentGlyphWindow()
        self.parent.sheet = Sheet((300, 40), self.parent.w)
        l = [axis for axis in self.RCJKI.currentFont._RFont.lib.get('robocjk.fontVariations', []) if axis not in self.RCJKI.currentGlyph.lib['robocjk.characterGlyph.glyphVariations'].keys()]
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
        self.RCJKI.updateDeepComponent()
        
    def closeSheet(self, sender):
        self.parent.sheet.close()

class SelectDeepComponentSheet():

    def __init__(self, RCJKI, deepComponentsNames):
        self.RCJKI = RCJKI
        self.deepComponentsNames = deepComponentsNames
        self.parent = CurrentGlyphWindow()
        self.parent.sheet = Sheet((300, 400), self.parent.w)
        self.previewGlyph = None

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
        glyph = self.RCJKI.currentFont[deepComponentName]
        self.previewGlyph = glyph.generateDeepComponent(
                glyph, 
                preview=False,
                )
        self.parent.sheet.canvasPreview.update()
    
    def closeSheet(self, sender):
        self.parent.sheet.close()
    
    def addDeepComponentList(self, sender):
        self.RCJKI.currentGlyph.addDeepComponentNamed(self.deepComponentName)
        self.RCJKI.updateDeepComponent()

    def draw(self):
        if self.previewGlyph is None: return
        mjdt.save()
        mjdt.translate(75, 35)
        mjdt.scale(.15)
        mjdt.fill(0, 0, 0, 1)
        for i, d in enumerate(self.previewGlyph):
            for atomicInstanceGlyph in d.values():
                mjdt.drawGlyph(atomicInstanceGlyph[0]) 
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
        self.s.close()

