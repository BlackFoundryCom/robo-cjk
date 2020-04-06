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
import Cocoa
import drawBot as db
from imp import reload
from utils import files
reload(files)
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
    #                 glyph.computeDeepComponents()
    #                 yield (x, y), glyph, glyph.atomicInstancesGlyphs
    #                 for c in glyph.flatComponents:
    #                     yield from yieldAtomicInstanceGlyph(self.RCJKI.currentFont[c.baseGlyph])

    #             rglyph = self.RCJKI.currentFont[charName] 
    #             # rglyph.computeDeepComponents()
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
                rglyph.computeDeepComponents()
                yield (x, y), rglyph, rglyph.atomicInstancesGlyphs
                for c in rglyph.flatComponents:
                    g = self.RCJKI.currentFont[c.baseGlyph]
                    g.computeDeepComponents()
                    yield (x, y), g, g.atomicInstancesGlyphs
                
                x += rglyph.width + self.tracking * (1000 / self.fontSize)
                if (x + rglyph.width) // (1000/self.fontSize) > self.position[2]:
                    y -= self.lineHeight
                    x = 0
            except:
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
        self.w = Window((1200, 800),"PDF Proofer", minSize= (200, 200))    
        self.w.canvas = DrawView((400, 0, -0, -0))
        self.w.pageTitle = TextBox(
            (10, 10, 100, 20),
            "Pages",
            sizeStyle = 'small'
            )
        self.w.pagesList = List(
            (10, 30, 80, 180),
            self.pdf.pages,
            selectionCallback = self.pagesListSelectionCallback,
            drawFocusRing = False
            )
        self.w.newPage = Button(
            (10, 210, 40, 20),
            '+',
            callback = self.newPageCallback,
            sizeStyle = "small"
            )
        self.w.delPage = Button(
            (50, 210, 40, 20),
            '-',
            callback = self.delPageCallback,
            sizeStyle = "small"
            )

        self.w.page = Group((95, 0, 305, 300))
        self.w.page.show(False)
        self.w.page.widthTitle = TextBox(
            (0, 30, 45, 20),
            "Width",
            sizeStyle = 'small'
            )
        self.w.page.pageWidth = EditText(
            (40, 30, 50, 20),
            841,
            sizeStyle = 'small',
            formatter = numberFormatter, 
            callback = self.pageSizeCallback
            )
        self.w.page.heightTitle = TextBox(
            (98, 30, 45, 20),
            "Height",
            sizeStyle = 'small'
            )
        self.w.page.pageHeight = EditText(
            (145, 30, 50, 20),
            595,
            sizeStyle = 'small',
            formatter = numberFormatter, 
            callback = self.pageSizeCallback
            )
        self.w.page.columnsTitle = TextBox(
            (0, 60, 100, 20),
            "Columns",
            sizeStyle = 'small'
            )
        self.w.page.columsSlider = Slider(
            (0, 80, 195, 20),
            minValue = 1,
            maxValue = 10,
            value = 1,
            tickMarkCount = 9,
            stopOnTickMarks = True,
            callback = self.columsSliderCallback
            )

        self.w.page.linesTitle = TextBox(
            (0, 110, 100, 20),
            "Lines",
            sizeStyle = 'small'
            )
        self.w.page.linesSlider = Slider(
            (0, 130, 195, 20),
            minValue = 1,
            maxValue = 10,
            value = 1,
            tickMarkCount = 9,
            stopOnTickMarks = True,
            callback = self.linesSliderCallback
            )

        self.w.page.marginTitle = TextBox(
            (0, 160, 100, 20),
            "Margin",
            sizeStyle = 'small'
            )
        self.w.page.marginSlider = Slider(
            (0, 180, 195, 20),
            minValue = 10,
            maxValue = 100,
            value = 10,
            callback = self.marginSliderCallback
            )
        self.w.page.backgrounColorTitle = TextBox(
            (0, 210, 150, 20),
            "Background color",
            sizeStyle = 'small'
            )
        self.w.page.backgrounColorWell = ColorWell(
            (105, 210, 90, 20),
            callback = self.backgroundcolorBoxCallback,
            color = NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 1, 1)
            )

        self.w.page.textBoxTitle = TextBox(
            (205, 10, 80, 150),
            "Box",
            sizeStyle = 'small'
            )
        self.w.page.textBoxList = List(
            (205, 30, 80, 200),
            [],
            selectionCallback = self.textBoxListSelectionCallback,
            drawFocusRing = False
            )
        
        self.w.text = Group((0, 250, 400, 400))
        self.w.text.show(False)

        self.w.text.horizontalLine = HorizontalLine((10, 0, -10, 10))

        y = 30
        self.w.text.fontSizeTitle = TextBox(
            (210, y, 80, 20),
            'FontSize',
            sizeStyle = "small"
            )
        self.w.text.fontSize = EditText(
            (280, y, 100, 20),
            10,
            sizeStyle = "small",
            formatter = numberFormatter,
            callback = self.fontSizeCallback
            )

        y += 30
        self.w.text.colorTitle = TextBox(
            (210, y, 80, 20),
            'Color',
            sizeStyle = "small"
            )
        self.w.text.color = ColorWell(
            (280, y, 100, 20),
            callback = self.textcolorBoxCallback
            )

        y += 30
        self.w.text.trackingTitle = TextBox(
            (210, y, 80, 20),
            'Tracking',
            sizeStyle = "small"
            )
        self.w.text.tracking = Slider(
            (280, y, 100, 20),
            minValue = 0,
            maxValue = 100,
            value = 0,
            callback = self.trackingBoxCallback
            )
        y += 30
        self.w.text.lineHeightTitle = TextBox(
            (210, y, 80, 20),
            'LineHeight',
            sizeStyle = "small"
            )
        self.w.text.lineHeight = Slider(
            (280, y, 100, 20),
            minValue = 500,
            maxValue = 2500,
            value = 1200,
            callback = self.lineHeightBoxCallback
            )
        y += 30
        self.w.text.alignTitle = TextBox(
            (210, y, 80, 20),
            'Align',
            sizeStyle = "small"
            )
        self.w.text.align = PopUpButton(
            (280, y, 100, 20),
            ["left", "center", "right"],
            callback = self.alignBoxCallback
            )

        self.w.text.segmentedButton = SegmentedButton(
            (10, 30, 190, 20),
            segmentDescriptions = [
                                    dict(title = "UFO"),
                                    dict(title = "FontBook")
                                    ],
            callback = self.segmentedButtonCallback,
            sizeStyle = 'small'
            )
        self.w.text.segmentedButton.set(0)

        self.w.text.fontManager = PopUpButton(
            (10, 60, 190, 20),
            FontsList.get(),
            callback = self.fontManagerCallback,
            sizeStyle = "small"
            )
        self.w.text.fontManager.show(0)

        self.w.text.textEditorTitle = TextBox(
            (10, 180, -10, -0),
            "Text",
            sizeStyle = "small"
            )
        self.w.text.textEditor = TextEditor(
            (10, 200, -10, -0),
            "",
            callback = self.textEditorCallback
            )
        self.w.exportPDF = Button(
            (0, -20, 400, -0),
            "Export PDF",
            callback = self.exportPDFCallback
            )

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
        self.w.page.textBoxList.set(self.currentPage.textBoxes)
        self.draw([self.currentPage])

    def linesSliderCallback(self, sender):
        self.currentPage.lines = int(sender.get())
        self.currentPage.update()
        self.w.page.textBoxList.set(self.currentPage.textBoxes)
        self.draw([self.currentPage])

    def marginSliderCallback(self, sender):
        self.currentPage.margin = int(sender.get())
        self.currentPage.update()
        self.w.page.textBoxList.set(self.currentPage.textBoxes)
        self.draw([self.currentPage])

    def pagesListSelectionCallback(self, sender):
        sel = sender.getSelection()
        self.w.page.show(sel)
        if not sel:
            self.currentPage = None
            self.w.page.textBoxList.set([])
            return
        self.setCurrentPage(sel[0])
        self.draw([self.currentPage])

    def pageSizeCallback(self, sender):
        if self.currentPage is None:
            return
        size = (int(self.w.page.pageWidth.get()), int(self.w.page.pageHeight.get()))
        self.currentPage.size = size
        self.currentPage.update()
        self.draw([self.currentPage])

    def textBoxListSelectionCallback(self, sender):
        sel = sender.getSelection()
        self.w.text.show(sel)
        if not sel:
            self.currentTextBox = None
            self.w.text.textEditor.set("")
            return
        self.currentTextBox = self.currentPage.textBoxes[sel[0]]
        # self.w.text.textEditor.set(self.currentTextBox.text)
        self.setTextGroupUI()
        self.draw([self.currentPage])

    def textEditorCallback(self, sender):
        self.currentTextBox.text = sender.get()
        self.draw([self.currentPage])

    def newPageCallback(self, sender):
        self.newPage()
        self.refresh()

    def delPageCallback(self, sender):
        sel = self.w.pagesList.getSelection()
        if not sel:
            return
        index = sel[0]
        self.pdf.removePage(index)
        self.refresh()

    def setPageGroupsUI(self):
        self.w.page.pageWidth.set(self.currentPage.size[0])
        self.w.page.pageHeight.set(self.currentPage.size[1])
        self.w.page.columsSlider.set(self.currentPage.columns)
        self.w.page.linesSlider.set(self.currentPage.lines)
        self.w.page.marginSlider.set(self.currentPage.margin)
        self.w.page.backgrounColorWell.set(NSColor.colorWithCalibratedRed_green_blue_alpha_(*self.currentPage.backgroundColor))
        self.w.page.textBoxList.set(self.currentPage.textBoxes)

    def setTextGroupUI(self):
        self.w.text.fontSize.set(self.currentTextBox.fontSize)
        self.w.text.textEditor.set(self.currentTextBox.text)
        self.w.text.color.set(NSColor.colorWithCalibratedRed_green_blue_alpha_(*self.currentTextBox.color))
        self.w.text.tracking.set(self.currentTextBox.tracking)
        self.w.text.lineHeight.set(self.currentTextBox.lineHeight)
        self.w.text.segmentedButton.set(self.currentTextBox.type == "Text")
            
    def exportPDFCallback(self, sender):
        path = putFile("pdf")
        self.draw(self.pdf.pages, export = True)
        db.saveImage("%s.pdf"%path)

    def newPage(self):
        size = (int(self.w.page.pageWidth.get()), int(self.w.page.pageHeight.get()))
        _columns = int(self.w.page.columsSlider.get())
        _lines = int(self.w.page.linesSlider.get())
        _margin = self.w.page.marginSlider.get()
        nscolor = self.w.page.backgrounColorWell.get()
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
        index = len(self.w.pagesList.get())-1
        self.w.pagesList.setSelection([index])
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
        self.w.pagesList.set(self.pdf.pages)
        self.draw([self.currentPage])

    def fontManagerCallback(self, sender):
        fontName = FontsList.get()[sender.get()]
        self.currentTextBox.font = fontName
        self.draw([self.currentPage])        

    def segmentedButtonCallback(self, sender):
        self.w.text.fontManager.show(sender.get())
        boxIndex = self.w.page.textBoxList.getSelection()[0]
        boxType = sender.get()
        self.currentPage.setBoxType(boxIndex,boxType)
        self.currentTextBox = self.currentPage.textBoxes[self.w.page.textBoxList.getSelection()[0]]
        self.draw([self.currentPage])

    def draw(self, pages: list, export = False):
        if not pages: return
        tbs = self.w.page.textBoxList.getSelection()
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
                    for pos, glyph, atomicInstanceGlyph in textbox.glyphs:
                        db.save()
                        db.translate(*pos)
                        for _, instanceGlyph in atomicInstanceGlyph:
                            db.drawGlyph(instanceGlyph)
                        db.drawGlyph(glyph)
                        db.restore()
                    db.restore()
                db.restore()
                
        pdfData = db.pdfImage()
        self.w.canvas.setPDFDocument(pdfData)
        
        