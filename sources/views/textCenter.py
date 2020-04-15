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
from mojo.UI import MultiLineView
from mojo.events import addObserver, removeObserver
from utils import files

class TextCenter:
    
    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.w = Window((800, 300), "Text Center", minSize = (400, 320))
        self.w.input = EditText(
            (0, 0, -0, 20),
            "",
            callback = self.inputCallback
            )
        self.w.multiLineView = MultiLineView(
            (200, 20, -0, -0),
            pointSize=120
            )
        self.w.multiLineView.setFont(self.RCJKI.currentFont._RFont)

        self.sourcesList = []
        if self.RCJKI.currentFont._RFont.lib.get('robocjk.fontVariations', ''):
            self.sourcesList = [dict(Axis = x, PreviewValue = 0) for x in self.RCJKI.currentFont._RFont.lib['robocjk.fontVariations']]

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

        self.char = ""
        self.charactersNamesList = []
        self.deepComponentList = set()
        for dcname in self.RCJKI.currentFont.deepComponentSet:
            if len(dcname.split('_')) > 1:
                self.deepComponentList.add(chr(int(dcname.split("_")[1], 16)))

        self.w.glyphUsingDCTitle = TextBox(
            (0, 120, 200, 20),
            "Glyphs that use:"
            )
        self.w.search = SearchBox((0, 140, 100, 20),
            callback = self.searchCallback)

        self.deepComponentList = list(self.deepComponentList)
        self.w.deepComponentList = List(
            (0, 160, 50, 140),
            self.deepComponentList,
            selectionCallback = self.deepComponentListSelectionCallback
            )
        self.w.variantList = List(
            (50, 160, 50, 140),
            [],
            selectionCallback = self.variantListSelectionCallback
            )
        self.w.characters = TextEditor(
            (100, 140, 100, 160),
            readOnly = True
            )

        self.observer()
        self.w.open()
        self.w.bind("close", self.windowWillClose)

    def characterGlyphUsing(self, code):
        characters = []
        for name in self.RCJKI.currentFont.characterGlyphSet:
            glyph = self.RCJKI.currentFont[name]
            for dc in glyph._deepComponents:
                if code in dc["name"]:
                    characters.append(name)
                    break
        return characters

    def getCodeVariants(self, char):
        if not char: return []
        var = []
        code = files.normalizeUnicode(hex(ord(char))[2:].upper())
        for name in self.RCJKI.currentFont.deepComponentSet:
            if code in name.split("_"):
                var.append(name.split("_")[2])
        return var

    def searchCallback(self, sender):
        char = sender.get()
        if char not in self.deepComponentList: return
        self.char = char
        self.w.deepComponentList.setSelection([self.deepComponentList.index(self.char)])

    def deepComponentListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            return
        self.char = sender.get()[sel[0]]
        self.w.variantList.set(self.getCodeVariants(self.char))

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
        self.w.characters.set(self.characters)
        self.input(" ".join(self.charactersNamesList))

    def sourcesListEditCallback(self, sender):
        self.sourcesList = sender.get()
        self.w.multiLineView.update()
        
    def inputCallback(self, sender):
        self.input(sender.get())

    def input(self, t):
        t = t.replace("/", " ")
        txt = t.split()
        glyphs = []
        for e in txt:
            try:
                glyphs.append(self.RCJKI.currentFont[e])
            except:
                for c in e:
                    try: glyphs.append(self.RCJKI.currentFont[files.unicodeName(c)])
                    except: continue
        self.w.multiLineView.set(glyphs)

    def observer(self, remove = False):
        if not remove:
            addObserver(self, "draw", "spaceCenterDraw")
            return
        removeObserver(self, "spaceCenterDraw")

    def draw(self, info):
        glyph = self.RCJKI.currentFont[info["glyph"].name]
        scale = info["scale"]

        if self.sourcesList and glyph.glyphVariations:
            glyph.computeDeepComponentsPreview(self.sourcesList)
            self.RCJKI.drawer.drawCharacterGlyphPreview(
                glyph,
                scale,
                (0, 0, 0, 1),
                (0, 0, 0, 0)
                )
        else:
            if glyph.type in ['deepComponent', 'characterGlyph']:
                glyph.computeDeepComponents()
                self.RCJKI.drawer.drawGlyphAtomicInstance(
                    glyph,
                    (0, 0, 0, 1),
                    scale,
                    (0, 0, 0, 1)
                    )

    def windowWillClose(self, sender):
        self.observer(remove = True)