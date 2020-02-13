from vanilla import *
from mojo.canvas import CanvasGroup
from AppKit import NSColor, NSNoBorder
import mojo.drawingTools as mjdt
from imp import reload
from utils import decorators
reload(decorators)

from utils import files
reload(files)

from views import sheets, drawer
reload(sheets)
reload(drawer)

lockedProtect = decorators.lockedProtect
glyphUndo = decorators.glyphUndo
refresh = decorators.refresh

transparentColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 1, 0)

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

        self.AETextBox = TextBox(
            (0, -120, -0, 20), 
            "Atomic Element's Axis"
            )
        self.atomicElementsList = List(
            (0, -100, -0, -0), 
            [],
            columnDescriptions = [
                    {"title": "Axis", "editable": False, "width": 50},
                    {"title": "Layer", "editable": False, "width": 40},
                    {"title": "PreviewValue", "cell": slider}],
            showColumnTitles = False,
            editCallback = self.atomicElementsListEditCallback,
            allowsMultipleSelection = False
            )
        setListAesthetic(self.atomicElementsList)

    @refresh
    @lockedProtect
    def atomicElementsListEditCallback(self, sender):
        if not sender.getSelection(): return
        self.RCJKI.currentGlyph.sourcesList = sender.get()
        self.RCJKI.currentGlyph.computeDeepComponentsPreview()

class DCCG_View(CanvasGroup):

    def __init__(self, RCJKI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.RCJKI = RCJKI
        slider = SliderListCell(minValue = 0, maxValue = 1)
        
        self.sourcesTitle = TextBox(
            (0, -240, -0, 20), 
            ""
            )
        self.sourcesList = List(
            (0, -220, -0, -140), 
            [],
            columnDescriptions = [
                    {"title": "Axis", "editable": True, "width": 50},
                    {"title": "PreviewValue", "cell": slider}],
            showColumnTitles = False,
            selectionCallback = self.sourcesListSelectionCallback,
            doubleClickCallback = self.sourcesListDoubleClickCallback,
            editCallback = self.sourcesListEditCallback,
            allowsMultipleSelection = False
            )
        setListAesthetic(self.sourcesList)

        self.addVarAxis = Button(
            (0, -140, 100, 20),
            "+",
            sizeStyle = 'mini',
            callback = self.addVarAxisCallback
            )
        self.addVarAxis.getNSButton().setShowsBorderOnlyWhileMouseInside_(True)

        self.removeVarAxis = Button(
            (100, -140, -0, 20),
            "-",
            sizeStyle = 'mini',
            callback = self.removeVarAxisCallback
            )
        self.removeVarAxis.getNSButton().setShowsBorderOnlyWhileMouseInside_(True)

        self.sliderTitle = TextBox(
            (0, -120, -0, 20), 
            ""
            )
        self.slidersList = List(
            (0, -100, -0, -20), 
            [],
            columnDescriptions = [
                    {"title": "Axis", "editable": False, "width": 50},
                    {"title": "PreviewValue", "cell": slider}],
            showColumnTitles = False,
            editCallback = self.slidersListEditCallback,
            allowsMultipleSelection = False
            )
        setListAesthetic(self.slidersList)
        self.selectedSourceAxis = None

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
        else:
            self.selectedSourceAxis = self.sourcesList.get()[sel[0]]["Axis"]
        self.RCJKI.updateDeepComponent()

    @lockedProtect
    def sourcesListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        edited = sender.getEditedColumnAndRow()
        if edited[0] == 0:
            name =  sender.get()[edited[1]]['Axis']
            if name != self.selectedSourceAxis:
                self.RCJKI.currentGlyph.renameVariationAxis(self.selectedSourceAxis, name)
        self.RCJKI.currentGlyph.sourcesList = sender.get()
        self.RCJKI.updateDeepComponent()

    @lockedProtect
    @glyphUndo
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
            self.sourcesList.setSelection([isel])
            self.RCJKI.currentGlyph.selectedSourceAxis = source[isel-1]['Axis']
            self.RCJKI.updateDeepComponent()       
            
        elif self.RCJKI.isCharacterGlyph:
            sheets.SelectFontVariationSheet(self.RCJKI)

    @lockedProtect
    @glyphUndo
    def removeVarAxisCallback(self, sender):
        if self.sourcesList.getSelection():
            name = self.sourcesList.get()[self.sourcesList.getSelection()[0]]["Axis"]
            self.RCJKI.currentGlyph.removeVariationAxis(name)
            self.RCJKI.currentGlyph.selectedElement = []
            self.RCJKI.currentGlyph.selectedSourceAxis = None
            self.sourcesList.setSelection([0])
            self.slidersList.set([])
            self.RCJKI.sliderValue = None
            self.RCJKI.sliderName = None
            self.RCJKI.updateListInterface()
            self.RCJKI.updateDeepComponent()

    @lockedProtect
    @glyphUndo
    def slidersListEditCallback(self, sender):
        if not sender.getSelection(): return
        self.RCJKI.sliderValue = round(float(self.slidersList[sender.getSelection()[0]]['PreviewValue']), 3)
        self.RCJKI.sliderName = self.slidersList[sender.getSelection()[0]]['Axis']
        if self.RCJKI.isDeepComponent:
            self.RCJKI.currentGlyph.updateAtomicElementCoord(self.RCJKI.sliderName, self.RCJKI.sliderValue)
        elif self.RCJKI.isCharacterGlyph:
            self.RCJKI.currentGlyph.updateDeepComponentCoord(self.RCJKI.sliderName, self.RCJKI.sliderValue)
        self.RCJKI.updateDeepComponent()


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
            self.drawer.drawDeepComponentPreview(
                self.glyph, 
                scale, 
                color = (0, 0, 0, 1), 
                strokecolor = (0, 0, 0, 0)
                )

        elif self.glyphType == 'characterGlyph':
            self.drawer.drawCharacterGlyphPreview(
                self.glyph, 
                scale, 
                color = (0, 0, 0, 1), 
                strokecolor = (0, 0, 0, 0)
                )
