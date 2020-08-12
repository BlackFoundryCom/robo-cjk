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

from dataclasses import dataclass
from vanilla import *
from vanilla.dialogs import putFile
from drawBot.ui.drawView import DrawView
from AppKit import NumberFormatter, NSColor
from mojo.canvas import Canvas
from mojo.roboFont import RGlyph
import Cocoa
try:
    import drawBot as db
except:
    print("DrawBot for robofont is not installed. PDF proofer need it, please install:\nhttps://github.com/typemytype/drawBotRoboFontExtension")
    pass
import copy
from imp import reload
from utils import files
# reload(files)
numberFormatter = NumberFormatter()

class FontsList:

    _fonts = None

    @classmethod
    def get(cls) -> list:
        if cls._fonts is None:
            manager = Cocoa.NSFontManager.sharedFontManager()
            cls._fonts = list(manager.availableFontFamilies())
        return cls._fonts

    @classmethod
    def reload(cls):
        cls._fonts = None

@dataclass
class Textbox:

    index: int
    position: tuple #(x, y, w, h)
    fontSize: int = 72
    color: tuple = (0, 0, 0, 1)
    text: str = ""
    tracking: int = 0
    align: str = "left"
    lineHeight: int = 1200
    designFrame: bool = False
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "%s - %s"%(str(self.index), self.text)
    
class Text(Textbox):
    
    def __init__(self, font, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.font = font
        self.type = self.__class__.__name__
        
    def __repr__(self):
        return super().__str__()

    def __str__(self):
        return super().__str__()   

class UfoText(Textbox):
    
    def __init__(self, RCJKI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.RCJKI = RCJKI
        self.type = self.__class__.__name__
        self.sourceList = []
        
    def __repr__(self):
        return super().__str__()

    def __str__(self):
        return super().__str__() 

    ###### RECURSIVITY TEST (FAIL) ######
    # @property
    # def glyphs(self):
    #     x = 0
    #     y = (self.position[3]-self.fontSize)*(1000/self.fontSize)
        
    #     for char in self.text:
    #         charName = files.unicodeName(char)
    #         try:
    #             def yieldAtomicInstanceGlyph(glyph):
    #                 glyph.preview.computeDeepComponents()
    #                 yield (x, y), glyph, glyph.atomicInstancesGlyphs
    #                 for c in glyph.flatComponents:
    #                     yield from yieldAtomicInstanceGlyph(self.RCJKI.currentFont[c.baseGlyph])

    #             rglyph = self.RCJKI.currentFont[charName] 
    #             # rglyph.preview.computeDeepComponents()
    #             yield from yieldAtomicInstanceGlyph(rglyph)
                
    #             x += rglyph.width + self.tracking * (1000 / self.fontSize)
    #             if (x + rglyph.width) // (1000/self.fontSize) > self.position[2]:
    #                 y -= self.lineHeight
    #                 x = 0
    #         except:
    #             continue    

    @property
    def glyphs(self):
        x = 0
        y = (self.position[3]-self.fontSize)*(1000/self.fontSize)
        
        for char in self.text:
            charName = files.unicodeName(char)
            try:
                rglyph = self.RCJKI.currentFont[charName] 
                glyph = RGlyph()
                if not self.sourceList:
                    rglyph.preview.computeDeepComponents(update = False)
                    for atomicInstance in rglyph.preview.axisPreview:
                        for c in atomicInstance.getTransformedGlyph():
                            glyph.appendContour(c)
                else:
                    rglyph.preview.computeDeepComponentsPreview(self.sourceList,update = False)
                    glyph = rglyph.preview.variationPreview

                yield (x, y), glyph
                
                for c in rglyph.flatComponents:
                    g = self.RCJKI.currentFont[c.baseGlyph]
                    glyph = RGlyph()
                    if not self.sourceList:
                        g.preview.computeDeepComponents(update = False)
                        for atomicInstance in g.preview.axisPreview:
                            for c in atomicInstance.getTransformedGlyph():
                                glyph.appendContour(c)
                    else:
                        g.preview.computeDeepComponentsPreview(self.sourceList,update = False)
                        glyph = g.preview.variationPreview

                    yield (x, y), glyph
                    
                
                x += rglyph.width + self.tracking * (1000 / self.fontSize)
                if (x + rglyph.width) // (1000/self.fontSize) > self.position[2]:
                    y -= self.lineHeight
                    x = 0
            except:# Exception as e:
                # raise e
                continue    

@dataclass            
class Page:
    
    RCJKI: object
    index: int
    size: tuple = (1800, 3000)
    columns: int = 1
    lines: int = 1
    margin: int = 40
    backgroundColor: tuple = (1, 1, 1, 1)
    
    def __post_init__(self):
        self.textBoxes = []
        self.update()

    def getPosFromIndex(self, i):
        pw, ph = self.size
        width = (pw - (self.margin*self.columns)-self.margin) / self.columns
        height = (ph - (self.margin*self.lines)-self.margin) / self.lines
        x = (i % self.columns) * width + self.margin * (i % self.columns) + self.margin
        # y = self.margin + (height + self.margin) * ((i) // self.columns)
        y = (ph-height) - self.margin - (height + self.margin) * ((i) // self.columns)
        return (x, y, width, height)
            
    def __repr__(self):
        return self.__str__()
        
    def __str__(self):
        return str(self.index)

    def update(self):
        textBoxes = []
        
        for index in range(self.columns*self.lines):
            d = {}
            if index < len(self.textBoxes):
                d = self.saveValueFromItem(self.textBoxes[index])
            textBoxes.append(
                UfoText(
                    self.RCJKI, 
                    index,
                    position = self.getPosFromIndex(index), 
                    **d
                    )
                )
        self.textBoxes = textBoxes

    def saveValueFromItem(self, item):
        return {
                "fontSize":item.fontSize,
                "color":item.color,
                "text":item.text,
                "tracking":item.tracking,
                "align":item.align,
                "lineHeight":item.lineHeight,
                "designFrame":item.designFrame,
                }

    def setBoxType(self, boxIndex: int, boxType: int):
        # boxes = [UfoText, Text]
        currentBox = self.textBoxes[boxIndex]
        boxInstance = [UfoText, Text][boxType](
            [self.RCJKI, "Arial"][boxType],
            boxIndex,
            position = self.getPosFromIndex(boxIndex), 
            **self.saveValueFromItem(currentBox),
            # text = currentBox.text
            )
        textBoxes = []
        for i, e in enumerate(self.textBoxes):
            if i != boxIndex:
                textBoxes.append(e)
            else:
                textBoxes.append(boxInstance)
        self.textBoxes = textBoxes

class PDFEngine:
    
    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.pages = []
        self.interface = Interface(self)
       
    def newPage(self, *args, **kwargs):
        page = Page(self.RCJKI, len(self.pages), *args, **kwargs)
        self.pages.append(page)
        self.interface.refresh()

    def removePage(self, index):
        self.pages.pop(index)
        self.interface.refresh()
       
class Interface:
    
    def __init__(self, pdf):
        self.pdf = pdf
        self.w = Window((600, 200),"PDF Proofer", minSize= (200, 200))    

        self.w.mainsegmentedButton = SegmentedButton(
            (10, 10, -10, 20), 
            [dict(title = "overlay"), dict(title = "custom")],
            callback = self.mainsegmentedButtonCallback
            )
        self.w.mainsegmentedButton.set(0)

        self.w.overlay = Group((10, 30, -10, -0))
        self.w.overlay.inputText = TextEditor((0, 0, -0, -20), '')
        self.w.overlay.generatePDFButton = Button((0, -20, -0, -0),
            "Generate PDF",
            callback = self.generatePDFButtonCallback
            )

        self.w.customPages = Group((0, 30, -0, -0))
        self.w.customPages.show(0)

        self.w.customPages.canvas = DrawView((400, 0, -0, -0))
        self.w.customPages.pageTitle = TextBox(
            (10, 10, 100, 20),
            "Pages",
            sizeStyle = 'small'
            )
        self.w.customPages.pagesList = List(
            (10, 30, 80, 180),
            self.pdf.pages,
            selectionCallback = self.pagesListSelectionCallback,
            drawFocusRing = False
            )
        self.w.customPages.newPage = Button(
            (10, 210, 40, 20),
            '+',
            callback = self.newPageCallback,
            sizeStyle = "small"
            )
        self.w.customPages.delPage = Button(
            (50, 210, 40, 20),
            '-',
            callback = self.delPageCallback,
            sizeStyle = "small"
            )

        self.w.customPages.page = Group((95, 0, 305, 300))
        self.w.customPages.page.show(False)
        self.w.customPages.page.widthTitle = TextBox(
            (0, 30, 45, 20),
            "Width",
            sizeStyle = 'small'
            )
        self.w.customPages.page.pageWidth = EditText(
            (40, 30, 50, 20),
            841,
            sizeStyle = 'small',
            formatter = numberFormatter, 
            callback = self.pageSizeCallback,
            continuous = False
            )
        self.w.customPages.page.heightTitle = TextBox(
            (98, 30, 45, 20),
            "Height",
            sizeStyle = 'small'
            )
        self.w.customPages.page.pageHeight = EditText(
            (145, 30, 50, 20),
            595,
            sizeStyle = 'small',
            formatter = numberFormatter, 
            callback = self.pageSizeCallback,
            continuous = False
            )
        self.w.customPages.page.columnsTitle = TextBox(
            (0, 60, 100, 20),
            "Columns",
            sizeStyle = 'small'
            )
        self.w.customPages.page.columsSlider = Slider(
            (0, 80, 195, 20),
            minValue = 1,
            maxValue = 10,
            value = 1,
            tickMarkCount = 9,
            stopOnTickMarks = True,
            callback = self.columsSliderCallback
            )

        self.w.customPages.page.linesTitle = TextBox(
            (0, 110, 100, 20),
            "Lines",
            sizeStyle = 'small'
            )
        self.w.customPages.page.linesSlider = Slider(
            (0, 130, 195, 20),
            minValue = 1,
            maxValue = 10,
            value = 1,
            tickMarkCount = 9,
            stopOnTickMarks = True,
            callback = self.linesSliderCallback
            )

        self.w.customPages.page.marginTitle = TextBox(
            (0, 160, 100, 20),
            "Margin",
            sizeStyle = 'small'
            )
        self.w.customPages.page.marginSlider = Slider(
            (0, 180, 195, 20),
            minValue = 10,
            maxValue = 100,
            value = 10,
            callback = self.marginSliderCallback
            )
        self.w.customPages.page.backgrounColorTitle = TextBox(
            (0, 210, 150, 20),
            "Background color",
            sizeStyle = 'small'
            )
        self.w.customPages.page.backgrounColorWell = ColorWell(
            (105, 210, 90, 20),
            callback = self.backgroundcolorBoxCallback,
            color = NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 1, 1)
            )

        self.w.customPages.page.textBoxTitle = TextBox(
            (205, 10, 80, 150),
            "Box",
            sizeStyle = 'small'
            )
        self.w.customPages.page.textBoxList = List(
            (205, 30, 80, 200),
            [],
            selectionCallback = self.textBoxListSelectionCallback,
            drawFocusRing = False
            )
        
        self.w.customPages.text = Group((0, 250, 400, 400))
        self.w.customPages.text.show(False)

        self.w.customPages.text.horizontalLine = HorizontalLine((10, 0, -10, 10))

        y = 30
        self.w.customPages.text.fontSizeTitle = TextBox(
            (210, y, 80, 20),
            'FontSize',
            sizeStyle = "small"
            )
        self.w.customPages.text.fontSize = EditText(
            (280, y, 100, 20),
            10,
            sizeStyle = "small",
            formatter = numberFormatter,
            callback = self.fontSizeCallback,
            continuous = False
            )

        y += 30
        self.w.customPages.text.colorTitle = TextBox(
            (210, y, 80, 20),
            'Color',
            sizeStyle = "small"
            )
        self.w.customPages.text.color = ColorWell(
            (280, y, 100, 20),
            callback = self.textcolorBoxCallback
            )

        y += 30
        self.w.customPages.text.trackingTitle = TextBox(
            (210, y, 80, 20),
            'Tracking',
            sizeStyle = "small"
            )
        self.w.customPages.text.tracking = Slider(
            (280, y, 100, 20),
            minValue = 0,
            maxValue = 100,
            value = 0,
            callback = self.trackingBoxCallback
            )
        y += 30
        self.w.customPages.text.lineHeightTitle = TextBox(
            (210, y, 80, 20),
            'LineHeight',
            sizeStyle = "small"
            )
        self.w.customPages.text.lineHeight = Slider(
            (280, y, 100, 20),
            minValue = 500,
            maxValue = 2500,
            value = 1200,
            callback = self.lineHeightBoxCallback
            )
        y += 30
        self.w.customPages.text.alignTitle = TextBox(
            (210, y, 80, 20),
            'Align',
            sizeStyle = "small"
            )
        self.w.customPages.text.align = PopUpButton(
            (280, y, 100, 20),
            ["left", "center", "right"],
            callback = self.alignBoxCallback
            )

        self.w.customPages.text.segmentedButton = SegmentedButton(
            (10, 30, 190, 20),
            segmentDescriptions = [
                                    dict(title = "UFO"),
                                    dict(title = "FontBook")
                                    ],
            callback = self.segmentedButtonCallback,
            sizeStyle = 'small'
            )
        self.w.customPages.text.segmentedButton.set(0)

        self.w.customPages.text.ufo = Group((10, 60, 190, 110))

        self.fontAxis = []
        if self.pdf.RCJKI.currentFont.fontVariations:
            self.fontAxis = [dict(Axis = x, PreviewValue = 0) for x in self.pdf.RCJKI.currentFont.fontVariations]
        slider = SliderListCell(minValue = 0, maxValue = 1)
        self.w.customPages.text.ufo.axis = List(
            (0, 0, -0,  -0),
            self.fontAxis,
            columnDescriptions = [
                    {"title": "Axis", "editable": False, "width": 60},
                    {"title": "PreviewValue", "cell": slider}],
            showColumnTitles = False,
            editCallback = self.ufoAxisListEditCallback,
            allowsMultipleSelection = False,
            drawFocusRing = False
            )

        self.w.customPages.text.fontManager = PopUpButton(
            (10, 60, 190, 20),
            FontsList.get(),
            callback = self.fontManagerCallback,
            sizeStyle = "small"
            )
        self.w.customPages.text.fontManager.show(0)

        self.w.customPages.text.textEditorTitle = TextBox(
            (10, 180, -10, -0),
            "Text",
            sizeStyle = "small"
            )
        self.w.customPages.text.textEditor = TextEditor(
            (10, 200, -10, -20),
            "",
            callback = self.textEditorCallback
            )
        self.w.customPages.text.setAllGlyphsDone = PopUpButton(
            (10, -20, -10, -0),
            [
                "", 
                "Set all character glyphs with deep components or contours",
                "Set all character glyphs with deep components and contours",
                "Set all character glyphs with deep components",
                "Set all character glyphs with contours",
            ],
            # "Set all character glyphs not empty",
            callback = self.setAllGlyphsDoneCallback
            )
        self.w.customPages.exportPDF = Button(
            (0, -20, 400, -0),
            "Export PDF",
            callback = self.exportPDFCallback
            )

        # self.w.customPages.exportPDFNew = Button(
        #     (0, -40, 400, -20),
        #     "Export PDF new",
        #     callback = self.exportPDFNewCallback
        #     )

    def mainsegmentedButtonCallback(self, sender):
        for i, group in enumerate([self.w.overlay, self.w.customPages]):
            group.show(i == sender.get())
        x, y, _, _ = self.w.getPosSize()
        if sender.get():
            self.w.setPosSize((x, y, 1200, 800))
        else:
            self.w.setPosSize((x, y, 600, 200))

    def generatePDFButtonCallback(self, sender):
        NewPDF(self.pdf.RCJKI, self, self.w.overlay.inputText.get())

    # def exportPDFNewCallback(self, sender):
    #     NewPDF(self.pdf.RCJKI, self)


    def backgroundcolorBoxCallback(self, sender):
        color = sender.get()
        bgcolor = (
            color.redComponent(),
            color.greenComponent(),
            color.blueComponent(),
            color.alphaComponent()
            )
        self.currentPage.backgroundColor = bgcolor
        self.draw([self.currentPage])

    def columsSliderCallback(self, sender):
        self.currentPage.columns = int(sender.get())
        self.currentPage.update()
        self.w.customPages.page.textBoxList.set(self.currentPage.textBoxes)
        self.draw([self.currentPage])

    def linesSliderCallback(self, sender):
        self.currentPage.lines = int(sender.get())
        self.currentPage.update()
        self.w.customPages.page.textBoxList.set(self.currentPage.textBoxes)
        self.draw([self.currentPage])

    def marginSliderCallback(self, sender):
        self.currentPage.margin = int(sender.get())
        self.currentPage.update()
        self.w.customPages.page.textBoxList.set(self.currentPage.textBoxes)
        self.draw([self.currentPage])

    def pagesListSelectionCallback(self, sender):
        sel = sender.getSelection()
        self.w.customPages.page.show(sel)
        if not sel:
            self.currentPage = None
            self.w.customPages.page.textBoxList.set([])
            return
        self.setCurrentPage(sel[0])
        self.draw([self.currentPage])

    def pageSizeCallback(self, sender):
        if self.currentPage is None:
            return
        size = (int(self.w.customPages.page.pageWidth.get()), int(self.w.customPages.page.pageHeight.get()))
        self.currentPage.size = size
        self.currentPage.update()
        self.draw([self.currentPage])

    def textBoxListSelectionCallback(self, sender):
        sel = sender.getSelection()
        self.w.customPages.text.show(sel)
        if not sel:
            self.currentTextBox = None
            self.w.customPages.text.textEditor.set("")
            return
        self.currentTextBox = self.currentPage.textBoxes[sel[0]]
        # self.w.customPages.text.textEditor.set(self.currentTextBox.text)
        if self.currentTextBox.sourceList:
            self.w.customPages.text.ufo.axis.set(self.currentTextBox.sourceList)
        self.setTextGroupUI()
        self.draw([self.currentPage])

    def textEditorCallback(self, sender):
        self.currentTextBox.text = sender.get()
        self.draw([self.currentPage])

    def setAllGlyphsDoneCallback(self, sender):
        option = sender.getItem()
        font = self.pdf.RCJKI.currentFont
        text = ""
        for name in font.characterGlyphSet:
            if option == "Set all character glyphs with deep components or contours":
                if font[name]._deepComponents or len(font[name]):
                    if font[name].unicode:
                        text += chr(font[name].unicode)
            if option == "Set all character glyphs with deep components and contours":
                if font[name]._deepComponents and len(font[name]):
                    if font[name].unicode:
                        text += chr(font[name].unicode)
            elif option == "Set all character glyphs with deep components":
                if font[name]._deepComponents and not len(font[name]):
                    if font[name].unicode:
                        text += chr(font[name].unicode)
            elif option == "Set all character glyphs with contours":
                if not font[name]._deepComponents and len(font[name]):
                    if font[name].unicode:
                        text += chr(font[name].unicode)
        self.currentTextBox.text = text 
        self.w.customPages.text.textEditor.set(text)
        self.draw([self.currentPage])

    def newPageCallback(self, sender):
        self.newPage()
        self.refresh()

    def delPageCallback(self, sender):
        sel = self.w.customPages.pagesList.getSelection()
        if not sel:
            return
        index = sel[0]
        self.pdf.removePage(index)
        self.refresh()

    def setPageGroupsUI(self):
        self.w.customPages.page.pageWidth.set(self.currentPage.size[0])
        self.w.customPages.page.pageHeight.set(self.currentPage.size[1])
        self.w.customPages.page.columsSlider.set(self.currentPage.columns)
        self.w.customPages.page.linesSlider.set(self.currentPage.lines)
        self.w.customPages.page.marginSlider.set(self.currentPage.margin)
        self.w.customPages.page.backgrounColorWell.set(NSColor.colorWithCalibratedRed_green_blue_alpha_(*self.currentPage.backgroundColor))
        self.w.customPages.page.textBoxList.set(self.currentPage.textBoxes)

    def setTextGroupUI(self):
        self.w.customPages.text.fontSize.set(self.currentTextBox.fontSize)
        self.w.customPages.text.textEditor.set(self.currentTextBox.text)
        self.w.customPages.text.color.set(NSColor.colorWithCalibratedRed_green_blue_alpha_(*self.currentTextBox.color))
        self.w.customPages.text.tracking.set(self.currentTextBox.tracking)
        self.w.customPages.text.lineHeight.set(self.currentTextBox.lineHeight)
        self.w.customPages.text.segmentedButton.set(self.currentTextBox.type == "Text")
            
    def exportPDFCallback(self, sender):
        path = putFile("pdf")
        self.draw(self.pdf.pages, export = True)
        outputPath = "%s.pdf"%path
        if path.endswith(".pdf"):
            outputPath = "%s.pdf"%path[:-4]
        db.saveImage(outputPath)

    def newPage(self):
        size = (int(self.w.customPages.page.pageWidth.get()), int(self.w.customPages.page.pageHeight.get()))
        _columns = int(self.w.customPages.page.columsSlider.get())
        _lines = int(self.w.customPages.page.linesSlider.get())
        _margin = self.w.customPages.page.marginSlider.get()
        nscolor = self.w.customPages.page.backgrounColorWell.get()
        _color = (
            nscolor.redComponent(),
            nscolor.greenComponent(),
            nscolor.blueComponent(),
            nscolor.alphaComponent()
            )
        self.pdf.newPage(
            size = size,
            columns = _columns, 
            lines = _lines,
            margin = _margin,
            backgroundColor = _color
            )
        index = len(self.w.customPages.pagesList.get())-1
        self.w.customPages.pagesList.setSelection([index])
        self.setCurrentPage(index)

    def setCurrentPage(self, index):
        self.currentPage = self.pdf.pages[index]
        self.setPageGroupsUI()

    def fontSizeCallback(self, sender):
        self.currentTextBox.fontSize = sender.get()
        self.draw([self.currentPage])

    def trackingBoxCallback(self, sender):
        self.currentTextBox.tracking = sender.get()
        self.draw([self.currentPage])       

    def lineHeightBoxCallback(self, sender):
        self.currentTextBox.lineHeight = sender.get()
        self.draw([self.currentPage])    

    def alignBoxCallback(self, sender):
        self.currentTextBox.align = sender.get()
        self.draw([self.currentPage])    

    def textcolorBoxCallback(self, sender):
        nscolor = sender.get()
        color = (
            nscolor.redComponent(),
            nscolor.greenComponent(),
            nscolor.blueComponent(),
            nscolor.alphaComponent()
            )
        self.currentTextBox.color = color
        self.draw([self.currentPage])

    def open(self):
        self.newPage()
        self.w.open()
        self.refresh()  
            
    def refresh(self):
        self.w.customPages.pagesList.set(self.pdf.pages)
        self.draw([self.currentPage])

    def ufoAxisListEditCallback(self, sender):
        self.currentTextBox.sourceList = [dict(x) for x in sender.get()]
        self.draw([self.currentPage]) 

    def fontManagerCallback(self, sender):
        fontName = FontsList.get()[sender.get()]
        self.currentTextBox.font = fontName
        self.draw([self.currentPage])        

    def segmentedButtonCallback(self, sender):
        self.w.customPages.text.ufo.show(not sender.get())
        self.w.customPages.text.fontManager.show(sender.get())
        boxIndex = self.w.customPages.page.textBoxList.getSelection()[0]
        boxType = sender.get()
        self.currentPage.setBoxType(boxIndex,boxType)
        self.currentTextBox = self.currentPage.textBoxes[self.w.customPages.page.textBoxList.getSelection()[0]]
        self.draw([self.currentPage])

    def draw(self, pages: list, export = False):
        if not pages: return
        tbs = self.w.customPages.page.textBoxList.getSelection()
        db.newDrawing()
        for page in pages:
            if page is None: continue
            db.newPage(*page.size)

            db.save()
            db.fill(*page.backgroundColor)
            db.rect(0, 0, *page.size)
            db.restore()

            for i, textbox in enumerate(page.textBoxes):
                db.save()
                db.translate(*textbox.position[:2])
                if not export:
                    db.save()
                    db.fill(None)
                    if i in tbs:
                        db.stroke(1, 0, 0, 1)
                    if not textbox.text:
                        db.fill(.5, .5, .5, .5)
                    db.rect(0, 0, *textbox.position[2:])
                    db.restore()

                if textbox.type == "Text":
                    db.save()
                    db.fill(*textbox.color)
                    db.tracking(textbox.tracking)
                    db.font(textbox.font, textbox.fontSize)
                    db.textBox(
                        textbox.text, 
                        (0, 0, *textbox.position[2:]), 
                        textbox.align
                        )
                    db.restore()
                    
                elif textbox.type == "UfoText":
                    db.save()
                    db.fill(*textbox.color)
                    
                    s = textbox.fontSize/1000
                    db.scale(s, s)
                    for pos, glyph in textbox.glyphs:
                        db.save()
                        db.translate(*pos)
                        if export:
                            glyph.round()
                        db.drawGlyph(glyph)
                        db.restore()
                    db.restore()
                db.restore()
                
        pdfData = db.pdfImage()
        self.w.customPages.canvas.setPDFDocument(pdfData)


from mojo.events                import addObserver, removeObserver
from AppKit                     import NSImage, NumberFormatter, NSColor
from mojo.extensions            import getExtensionDefault, setExtensionDefault
from lib.UI.toolbarGlyphTools   import ToolbarGlyphTools
from mojo.UI                    import UpdateCurrentGlyphView, CurrentGlyphWindow
from mojo.canvas                import CanvasGroup
from mojo.drawingTools          import *
from vanilla                    import *
from vanilla.dialogs            import putFile, getFile
import json
import os


import datetime

class DesignFrame:

    # __slots__ = "em_Dimension", "characterFace", "overshoot", \
    #             "horizontalLine", "verticalLine", "customsFrames"

    def __init__(self):
        self.em_Dimension = [1000, 1000]
        self.characterFace = 90
        self.overshoot = [20, 20]
        self.customsFrames = []

    def set(self, lib: dict):
        if not lib: return
        for k, v in lib.items():
            setattr(self, k, v)

    def get(self) -> dict:
        return vars(self)

    def __len__(self) -> int:
        return len(list(filter(lambda x: getattr(self, x), vars(self))))

    def __str__(self) -> str:
        str = ""
        for e in vars(self):
            str += f"{e}:{getattr(self, e)}, "
        return str

class HanDesignFrame(DesignFrame):

    def __init__(self):
        super().__init__()
        self.horizontalLine = 15
        self.verticalLine = 15
        self.type = 'han'

FRAMEX, FRAMEY = 595, 841

class NewPDF:

    def __init__(self, RCJKI, controller, text):
        self.RCJKI = RCJKI
        self.controller = controller
        self.designFrame = HanDesignFrame()
        self.designFrameViewer = DesignFrameDrawer(self)
        self.pages = [ ["uni%s"%hex(ord(x))[2:].upper() for x in text[i:i+20]] for i in range(0, len(text), 20) ]
        self.draw()

    def draw(self):
        user = self.RCJKI.gitUserName
        now = datetime.datetime.now()
        date = "%s%s%s_%s%s%s"%(now.year, str(now.month).zfill(2), str(now.day).zfill(2), str(now.hour).zfill(2), str(now.minute).zfill(2), str(now.second).zfill(2))

        def drawDesignFrame():
            for e in self.designFrameViewer.elements:
                glyph, color, type = e
                if type =='stroke':
                    db.stroke(*color)
                    db.fill(None)
                else:
                    db.stroke(None)
                    db.fill(*color)
                db.drawGlyph(glyph)


        for pageIndex, page in enumerate(self.pages):
            db.newDrawing()
            self.designFrameViewer.draw()

            glyphsVariations = {}
            # light = []
            db.newPage(FRAMEX, FRAMEY)

            db.textBox('%s-Overlay'%self.RCJKI.currentFont.fontName, (0, FRAMEY-105, FRAMEX, 55), align = 'center')
            s = .11
            tx, ty = (FRAMEX/s-1000*4)*.5, 1000 * 5.8
            db.save()
            db.scale(s, s)
            db.translate(tx, ty)
            db.fontSize(60)
            for i, name in enumerate(page):
                try:
                    for variation in self.RCJKI.currentFont.fontVariations:
                        glyph1 = self.RCJKI.currentFont[name]
                        glyph1.preview.computeDeepComponentsPreview([dict(Axis = variation, PreviewValue = 1)])
                        glyph1.preview.variationPreview.removeOverlap()
                        if variation not in glyphsVariations.keys():
                            glyphsVariations[variation] = []
                        glyphsVariations[variation].append(glyph1.preview.variationPreview)

                        drawDesignFrame()
                        db.fill(0, 0, 0, 1)
                        db.stroke(None)                    
                        db.textBox(name, (0, 900, 1000, 100), align = "center")

                        db.fill(1, 1, 1, 1)
                        db.stroke(0, 0, 0, 1)
                        db.strokeWidth(1)
                        
                        db.drawGlyph(glyph1.preview.variationPreview)
                        glyph1.preview.computeDeepComponentsPreview([dict(Axis = variation, PreviewValue = 0)])
                        glyph1.preview.variationPreview.removeOverlap()
                        variation = "normal"
                        if variation not in glyphsVariations.keys():
                            glyphsVariations[variation] = []
                        glyphsVariations[variation].append(glyph1.preview.variationPreview)
                        db.drawGlyph(glyph1.preview.variationPreview)

                        if (i+1)%4:
                            db.translate(1000, 0)
                        else:
                            db.translate(-1000*3, -1200)
                except Exception as e:
                    raise e
            db.restore()

            pdfData = db.pdfImage()            
            outputPath = os.path.join(self.RCJKI.currentFont.fontPath, "Proofing", user, '%s_%s_%s-%s.pdf'%(date, str(pageIndex).zfill(2), self.RCJKI.currentFont.fontName, "Overlay"))
            files.makepath(outputPath)
            db.saveImage(outputPath)

            def drawWeight(weight, text):

                db.newDrawing()
                self.designFrameViewer.draw()

                db.newPage(FRAMEX, FRAMEY)
                db.textBox(text, (0, FRAMEY-105, FRAMEX, 55), align = 'center')
                s = .11
                tx, ty = (FRAMEX/s-1000*4)*.5, 1000 * 5.8
                db.save()
                db.scale(s, s)
                db.translate(tx, ty)
                db.fontSize(60)

                for i, glyph in enumerate(weight):
                    drawDesignFrame()
                    db.fill(0, 0, 0, 1)
                    db.stroke(None)                    
                    db.textBox(glyph.name, (0, 900, 1000, 100), align = "center")

                    db.fill(0, 0, 0, 1)
                    db.stroke(None)
                    db.drawGlyph(glyph)
                    if (i+1)%4 :
                        db.translate(1000, 0)
                    else:
                        db.translate(-1000*3, -1200)

                db.restore()
                pdfData = db.pdfImage()
                now = datetime.datetime.now()
                outputPath = os.path.join(self.RCJKI.currentFont.fontPath, "Proofing", user, '%s_%s_%s.pdf'%(date, str(pageIndex).zfill(2), text))
                files.makepath(outputPath)
                db.saveImage(outputPath)

            for variations, weights in glyphsVariations.items():
                drawWeight(weights, '%s-%s'%(self.RCJKI.currentFont.fontName, variations))

            textPath = os.path.join(self.RCJKI.currentFont.fontPath, "Proofing", user, '%s_%s_text.txt'%(date, str(pageIndex).zfill(2)))
            files.makepath(textPath)
            with open(textPath, 'w', encoding = 'utf-8') as file:
                file.write("".join([chr(int(x[3:], 16)) for x in page]))

class DesignFrameDrawer:

    def __init__(self, controller):
        self.controller = controller
        self.drawPreview = False
        self.secondLines = True
        self.customsFrames = True
        self.elements = []
        self.draw()

    def _getFrame(self, x: int, y: int, w: int, h:int, ty) -> tuple:
        glyph = RGlyph()
        pen = glyph.getPen()
        pen.moveTo((x, y))
        pen.lineTo((w+x, y))
        pen.lineTo((w+x, h+y))
        pen.lineTo((x, h+y))
        pen.closePath()

        glyph.round()
        glyph.moveBy((0, ty))

        self.elements.append((glyph, (0, 0, 0, 1), 'stroke'))

    def _getEmRatioFrame(self, frame: int, w: int, h: int, ty) -> tuple:
        charfaceW = w * frame / 100
        charfaceH = h * frame / 100
        x = (w - charfaceW) * .5
        y = (h - charfaceH) * .5

        glyph = RGlyph()
        pen = glyph.getPen()
        pen.moveTo((x, y))
        pen.lineTo((charfaceW+x, y))
        pen.lineTo((charfaceW+x, charfaceH+y))
        pen.lineTo((x, charfaceH+y))
        pen.closePath()

        glyph.round()
        glyph.moveBy((0, ty))

        self.elements.append((glyph, (0, 0, 0, 1), 'stroke'))

        return x, y, charfaceW, charfaceH

    def _makeOvershoot(self, 
            glyph: RGlyph, 
            origin_x: int, 
            origin_y: int, 
            width: int, 
            height: int, 
            inside: int, 
            outside: int,
            ty):
        ox = origin_x - outside
        oy = origin_y - outside
        width += outside
        height += outside
        pen = glyph.getPen()
        pen.moveTo((ox, oy))
        pen.lineTo((ox + width + outside, oy))
        pen.lineTo((ox + width + outside, oy + height + outside))
        pen.lineTo((ox, oy + height + outside))
        pen.closePath()
        ox = origin_x + inside
        oy = origin_y + inside
        width -= outside + inside
        height -= outside + inside
        pen.moveTo((ox, oy))
        pen.lineTo((ox, oy + height - inside))
        pen.lineTo((ox + width - inside, oy + height - inside))
        pen.lineTo((ox + width - inside, oy))
        pen.closePath()
        glyph.round()
        glyph.moveBy((0, ty))

        self.elements.append((glyph, (0, .75, 1, .1), 'fill'))
        # db.drawGlyph(glyph)

    def _makeHorSecLine(self, 
            glyph: RGlyph, 
            origin_x: int, 
            origin_y: int, 
            width: int, 
            height: int,
            ty):
        pen = glyph.getPen()
        pen.moveTo((origin_x, origin_y))
        pen.lineTo((origin_x + width, origin_y))
        pen.closePath()
        pen.moveTo((origin_x, height))
        pen.lineTo((origin_x + width, height))
        pen.closePath()
        glyph.round()
        glyph.moveBy((0, ty))
        self.elements.append((glyph, (.65, 0.16, .39, 1), 'stroke'))
        # db.drawGlyph(glyph)

    def _makeVerSecLine(self, 
            glyph: RGlyph, 
            origin_x: int, 
            origin_y: int, 
            width: int, 
            height: int,
            ty):
        pen = glyph.getPen()
        pen.moveTo((origin_x, origin_y))
        pen.lineTo((origin_x, origin_y + height))
        pen.closePath()
        pen.moveTo((width, origin_y))
        pen.lineTo((width, origin_y + height))
        pen.closePath()
        glyph.round()
        glyph.moveBy((0, ty))
        self.elements.append((glyph, (.65, 0.16, .39, 1), 'stroke'))
        # db.drawGlyph(glyph)

    def _makeHorGrid(self,
                    glyph: RGlyph, 
                    x: int, 
                    y: int, 
                    w: int,
                    h: int,
                    ty: int,
                    step: int):
        pen = glyph.getPen()
        dist = y + h / step
        for i in range(step-1):
            pen.moveTo((x, dist))
            pen.lineTo((x+w, dist))
            pen.closePath()
            dist += h / step
        # db.drawGlyph(glyph)
        glyph.moveBy((0, ty))
        self.elements.append((glyph, (.65, 0.16, .39, 1), 'stroke'))

    def _makeVerGrid(self,
                    glyph: RGlyph, 
                    x: int, 
                    y: int, 
                    w: int,
                    h: int,
                    ty: int,
                    step: int):
        pen = glyph.getPen()
        dist = x + w / step
        for i in range(step-1):
            pen.moveTo((dist, y))
            pen.lineTo((dist, y+h))
            pen.closePath()
            dist += w / step
        # db.drawGlyph(glyph)
        glyph.moveBy((0, ty))
        self.elements.append((glyph, (.65, 0.16, .39, 1), 'stroke'))


    def _findProximity(self, 
            pos: list, 
            point: int, 
            left: int = 0, 
            right: int = 0) -> bool:
        for p in pos:
            if p + left < point < p + right:
                return True
        return False

    def draw(self, 
            glyph = None,
            notificationName: str = "",
            mainFrames: bool = True, 
            customsFrames: bool = True,
            proximityPoints: bool = False, 
            translate_secondLine_X: int = 0, 
            translate_secondLine_Y: int = 0,
            scale: int = 1):

        if notificationName == 'drawPreview' and not self.drawPreview: return
        if not self.controller.designFrame: return
        x, y = 0, 0
        w, h = self.controller.designFrame.em_Dimension
        translateY = -12 * h / 100

        if mainFrames:
            self._getFrame(x, y, w, h, translateY)

            frame = self._getEmRatioFrame(self.controller.designFrame.characterFace, w, h, translateY)
            outside, inside = self.controller.designFrame.overshoot
            self._makeOvershoot(RGlyph(), *frame, *self.controller.designFrame.overshoot, translateY)

        self._makeHorGrid(RGlyph(), *frame, translateY, step = 24)
        self._makeVerGrid(RGlyph(), *frame, translateY, step = 24)

        # if self.secondLines:
        #     if self.controller.designFrame.type == "han":
        #         ratio = (h * .5 * (self.controller.designFrame.horizontalLine / 50))
        #         y = h * .5 - ratio
        #         height = h * .5 + ratio
        #         self._makeHorSecLine(RGlyph(), 0, y + translate_secondLine_Y, w, height + translate_secondLine_Y, translateY)

        #         ratio = (w * .5 * (self.controller.designFrame.verticalLine / 50))
        #         x = w * .5 - ratio
        #         width = w * .5 + ratio
        #         self._makeVerSecLine(RGlyph(), x + translate_secondLine_X, 0, width + translate_secondLine_X, h, translateY)
        #     else:
        #         self._makeHorGrid(RGlyph(), *frame, step = int(self.controller.designFrame.horizontalLine))
        #         self._makeVerGrid(RGlyph(), *frame, step = int(self.controller.designFrame.verticalLine))
        
        if self.customsFrames:
            for frame in self.controller.designFrame.customsFrames:
                if not "Value" in frame: continue






