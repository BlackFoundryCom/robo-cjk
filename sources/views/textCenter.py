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
from mojo.UI import MultiLineView, AccordionView
from mojo.events import addObserver, removeObserver
from utils import files
import mojo.drawingTools as mjdt

class displayModeGroup(Group):

    def __init__(self, posSize, controller):
        super().__init__(posSize)
        self.c = controller

        self.linesMode = ["Multi Line", 'Single Line', "Water Fall"]
        self.displaymodeRadioGroup = RadioGroup(
            (10, 5, -10, 50),
            self.linesMode,
            callback = self.displaymodeRadioGroupCallback,
            sizeStyle = 'small'
            )
        self.displaymodeRadioGroup.set(0)

        self.lineHeightTitle = TextBox(
            (10, 60, -10, 20),
            'LineHeight',
            sizeStyle='small'
            )
        self.lineHeightSlider = Slider(
            (10, 75, -10, 20),
            minValue = 20,
            maxValue = 1000,
            value = 200,
            callback = self.lineHeightSliderCallback
            )

    def displaymodeRadioGroupCallback(self, sender):
        mode = self.linesMode[sender.get()]
        for m in self.linesMode:
            if m != mode:
                self.c.displayOptions[m] = False
            if m == mode:
                self.c.displayOptions[m] = True
        self.c.displayOptions['displayMode'] = mode
        self.c.w.multiLineView.setDisplayStates(self.c.displayOptions)

    def lineHeightSliderCallback(self, sender):
        self.c.w.multiLineView.setLineHeight(sender.get())

class GlyphUsingDC(Group):

    def __init__(self, posSize, controller):
        super().__init__(posSize)
        self.c = controller
        self.char = ""
        self.charactersNamesList = []
        self.deepComponent = set()
        for dcname in self.c.RCJKI.currentFont.staticDeepComponentSet():
            if len(dcname.split('_')) > 1:
                try:
                    self.deepComponent.add(chr(int(dcname.split("_")[1], 16)))
                except:continue

        self.search = SearchBox((0, 5, 100, 20),
            callback = self.searchCallback)

        self.deepComponent = list(self.deepComponent)
        self.deepComponentList = List(
            (0, 25, 50, -0),
            self.deepComponent,
            selectionCallback = self.deepComponentListSelectionCallback
            )
        self.variantList = List(
            (50, 25, 50, -0),
            [],
            selectionCallback = self.variantListSelectionCallback
            )
        self.charactersField = TextEditor(
            (100, 5, 100, -0),
            readOnly = True
            )

    def searchCallback(self, sender):
        char = sender.get()
        if char not in self.deepComponent: return
        self.char = char
        self.deepComponentList.setSelection([self.deepComponent.index(self.char)])

    def getCodeVariants(self, char):
        if not char: return []
        var = []
        code = files.normalizeUnicode(hex(ord(char))[2:].upper())
        for name in self.c.RCJKI.currentFont.staticDeepComponentSet():
            if code in name.split("_"):
                var.append("_".join(name.split("_")[2:]))
        return var

    def deepComponentListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            return
        self.char = sender.get()[sel[0]]
        self.variantList.set(self.getCodeVariants(self.char))

    def variantListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            return
        index = sender.get()[sel[0]]
        code = files.normalizeUnicode(hex(ord(self.char))[2:].upper())
        self.charactersNamesList = self.characterGlyphUsing("%s_%s"%(code, index))
        self.characters = ""
        for name in self.charactersNamesList:
            try:
                self.characters+=chr(int(name.split(".")[0][3:], 16))
            except:
                pass
        self.charactersField.set(self.characters)
        # self.c.input(" ".join(self.charactersNamesList))

    def characterGlyphUsing(self, code):
        characters = []
        if not self.c.RCJKI.currentFont.mysql:
            for name in self.c.RCJKI.currentFont.staticCharacterGlyphSet():
                glyph = self.c.RCJKI.currentFont.get(name)
                for dc in glyph._deepComponents:
                    if code in dc.name:
                        characters.append(name)
                        break
        else:
            code = "DC_%s"%code
            response = self.c.RCJKI.currentFont.client.deep_component_get(self.c.RCJKI.currentFont.uid, code)
            return [x["name"] for x in response["data"]["used_by"]]
            # print(code)
        return characters

class DCUsingAE(Group):

    def __init__(self, posSize, controller):
        super().__init__(posSize)
        self.c = controller

        self.search = SearchBox((0, 5, 100, 20),
            callback = self.searchCallback)

        self.atomicElement = self.c.RCJKI.currentFont.staticAtomicElementSet()
        self.atomicElementList = List(
            (0, 25, 100, -0),
            self.atomicElement,
            selectionCallback = self.atomicElementListSelectionCallback
            )
        self.atomicElementList.setSelection([])
        self.deepComponentField = TextEditor(
            (100, 5, 100, -0),
            readOnly = True
            )

    def searchCallback(self, sender):
        name = sender.get()
        for i, e in enumerate(self.atomicElementList.get()):
            if name in e:
                self.atomicElementList.setSelection([i])
                break

    def atomicElementListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            return
        name = sender.get()[sel[0]]
        self.deepComponentField.set(" ".join(self.deepComponentGlyphUsing(name)))

    def deepComponentGlyphUsing(self, aename):
        deepComponents = []
        for name in self.c.RCJKI.currentFont.staticDeepComponentSet():
            glyph = self.c.RCJKI.currentFont.get(name)
            for dc in glyph._deepComponents:
                if aename == dc.name:
                    deepComponents.append(name)
                    break
        return deepComponents

class TextCenter:
    
    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.w = Window((800, 300), "Text Center", minSize = (400, 320))
        self.w.leftInput = EditText(
            (0, 0, 60, 20),
            "",
            callback = self.inputCallback
            )
        self.w.input = EditText(
            (60, 0, -60, 20),
            "",
            callback = self.inputCallback
            )
        self.pointsSize = [9, 10, 11, 12, 14, 16, 18, 20, 24, 30, 36, 48, 60, 72, 96, 144, 256, 512, 1024],
        self.w.pointSize = ComboBox(
            (-60, 0, -0, 20),
            *self.pointsSize,
            callback = self.pointSizeCallback
            )
        self.w.pointSize.set(72)
        self.displayOptions = {
                'displayMode': 'Multi Line', #
                'Show Kerning': True, 
                'Multi Line': True, #
                'xHeight Cut': False, 
                'Water Fall': False, #
                'Single Line': True, #
                'Inverse': False, 
                'Show Metrics': False, 
                'Left to Right': True, 
                'Right to Left': False, 
                'Center': False, # 
                'Upside Down': False, 
                'Stroke': False, 
                'Fill': False, 
                'Beam': False, 
                'Guides': False, 
                'Blues': False, 
                'Family Blues': False, 
                'Show Control glyphs': True, 
                'Show Space Matrix': True, 
                'Show Template Glyphs': True, 
                'showLayers': []
                }
        self.w.multiLineView = MultiLineView(
            (200, 20, -0, -0),
            pointSize=72,
            displayOptions = self.displayOptions
            )
        self.w.multiLineView.setFont(self.RCJKI.currentFont._fullRFont)
        self.w.multiLineView.setLineHeight(200)

        self.sourcesList = []
        if self.RCJKI.currentFont.fontVariations:
            self.sourcesList = [dict(Axis = x, PreviewValue = 0) for x in self.RCJKI.currentFont.fontVariations]

        slider = SliderListCell(minValue = 0, maxValue = 1)
        self.w.sourcesList = List(
            (0, 20, 200, 90),
            self.sourcesList, 
            columnDescriptions = [
                    {"title": "Axis", "editable": False, "width": 60},
                    {"title": "PreviewValue", "cell": slider}],
            showColumnTitles = False,
            editCallback = self.sourcesListEditCallback,
            allowsMultipleSelection = False
            )

        self.accordionViewDescriptions = [

                        dict(label="Display options", 
                            view=displayModeGroup((0, 0, -0, -0), self), 
                            size=100, 
                            collapsed=True, 
                            canResize=0),

                        dict(label="Glyphs that use:", 
                            view=GlyphUsingDC((0, 0, -0, -0), self), 
                            size=180, 
                            collapsed=True, 
                            canResize=1),

                        dict(label="Deep components that use:", 
                            view=DCUsingAE((0, 0, -0, -0), self), 
                            size=180, 
                            collapsed=True, 
                            canResize=1),
                       ]

        self.w.accordionView = AccordionView((0, 120, 200, -0),
            self.accordionViewDescriptions,
            )

        self.observer()
        self.w.open()
        self.w.bind("close", self.windowWillClose)

    def close(self):
        self.w.close()

    def pointSizeCallback(self, sender):
        try:
            value = int(sender.get())
            self.w.multiLineView.setPointSize(value)
        except: return

    def sourcesListEditCallback(self, sender):
        self.sourcesList = sender.get()
        self.w.multiLineView.update()
        
    def inputCallback(self, sender):
        self.input(self.w.leftInput.get(), self.w.input.get())

    def input(self, l, t):
        l = l.replace("/", " ")
        t = t.replace("/", " ")
        txt = t.split()
        glyphs = []
        rfont = self.RCJKI.currentFont._RFont
        for e in txt:
            try:
                for c in l:
                    glyphs.append(self.RCJKI.currentFont.get(c, rfont))    
                glyphs.append(self.RCJKI.currentFont.get(e, rfont))
            except:
                for c in e:
                    try:
                        for x in l: 
                            glyphs.append(self.RCJKI.currentFont.get(files.unicodeName(x), rfont))
                        glyphs.append(self.RCJKI.currentFont.get(files.unicodeName(c), rfont))
                    except: continue
        self.w.multiLineView.set(glyphs)

    def observer(self, remove = False):
        if not remove:
            addObserver(self, "draw", "spaceCenterDraw")
            return
        removeObserver(self, "spaceCenterDraw")

    def draw(self, info):
        self.w.pointSize.set(self.w.multiLineView.getPointSize())
        glyph = self.RCJKI.currentFont[info["glyph"].name]#, self.RCJKI.currentFont._RFont)
        scale = info["scale"]
        sourcesList = {x["Axis"]:x["PreviewValue"] for x in self.sourcesList}

        mjdt.save()
        mjdt.fill(0, 0, 0, 1)
        mjdt.stroke(0, 0, 0, 0)
        mjdt.strokeWidth(scale)
        for c in glyph.preview(sourcesList, forceRefresh=True):
            mjdt.drawGlyph(c.glyph)
        mjdt.restore()

        # def drawVariation(glyph, sourcelist, drawer):
        #     glyph.preview.computeDeepComponentsPreview(sourcelist, update = False)
        #     drawer.drawVariationPreview(
        #             glyph,
        #             scale,
        #             (0, 0, 0, 1),
        #             (0, 0, 0, 0)
        #                 )

        # def drawPreview(glyph, drawer):
        #     glyph.preview.computeDeepComponents(update = False)
        #     drawer.drawAxisPreview(
        #             glyph,
        #             (0, 0, 0, 1),
        #             scale,
        #             (0, 0, 0, 1)
        #             )

        # if glyph.type in ['deepComponent', 'characterGlyph']:
        #     if self.sourcesList:# and glyph.glyphVariations:
        #         try:
        #             drawVariation(glyph, self.sourcesList, self.RCJKI.drawer)
        #         except:
        #             drawPreview(glyph, self.RCJKI.drawer)
        #         # glyph.preview.computeDeepComponentsPreview(self.sourcesList, update = False)
        #         # self.RCJKI.drawer.drawVariationPreview(
        #         #         glyph,
        #         #         scale,
        #         #         (0, 0, 0, 1),
        #         #         (0, 0, 0, 0)
        #         #         )
        #     else:
        #         drawPreview(glyph, self.RCJKI.drawer)
        #         # glyph.preview.computeDeepComponents(update = False)
        #         # self.RCJKI.drawer.drawAxisPreview(
        #         #     glyph,
        #         #     (0, 0, 0, 1),
        #         #     scale,
        #         #     (0, 0, 0, 1)
        #         #     )

    def windowWillClose(self, sender):
        self.RCJKI.textCenterWindows.pop(self.RCJKI.textCenterWindows.index(self))
        self.observer(remove = True)