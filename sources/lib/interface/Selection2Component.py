from vanilla import *
from vanilla.dialogs import message
from mojo.roboFont import *
from mojo.UI import AccordionView, UpdateCurrentGlyphView
from imp import reload
import Helpers

reload(Helpers)
from Helpers import SmartTextBox

class Selection2Component(Group):

    def __init__(self, posSize, interface):
        super(Selection2Component, self).__init__(posSize)
        self.ui = interface

        self.suggestComponent_list = List((10,10,140,-30),
                self.ui.suggestComponent,
                allowsMultipleSelection=False, 
                selectionCallback = self._selection2Compo_suggestComponent_list_selectionCallback,
                drawFocusRing = False)

        self.previewChar = ""
        self.previewChar_textBox = SmartTextBox((150,10,-10,-30),
            self.previewChar,
            sizeStyle = 50,
            alignment = "center",
            red = .1,
            green = .4,
            blue = .9)

        self.selectionToComponent_button = Button((10,-25,-10,-5),
                "Selection to Component",
                sizeStyle = "small",
                callback = self._selectionToComponent_button_callback)

    def _selection2Compo_suggestComponent_list_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            self.previewChar = ""
            self.components2suggestComponent = []
        else:
            name = self.ui.suggestComponent[sel[0]].split("_")[0]
            self.previewChar = chr(int(name,16))
            self.components2suggestComponent = list(filter(lambda x: self.ui.suggestComponent[sel[0]] in x, self.ui.font.keys()))
        self.previewChar_textBox.set(self.previewChar)

    def _selectionToComponent_button_callback(self, sender):
        sel = self.suggestComponent_list.getSelection()
        if not sel:
            message('Warning there is no selected name')
            return
        i=0
        while True:
            index = "_%s"%str(i).zfill(2)
            name = self.ui.suggestComponent[sel[0]]+index
            if name not in self.components2suggestComponent: 
                break
            i+=1

        seletedContours = [c for c in self.ui.glyph if c.selected or [p for p in c.points if p.selected]]

        if not seletedContours: 
            message("Warning, there are not selected contours")
            return

        if name not in self.ui.font.keys():
            self.ui.font.newGlyph(name)

        newG = self.ui.font[name]
        newG.clear()
        newG.width = self.ui.glyph.width
        for c in seletedContours:
            newG.appendContour(c)
            self.ui.glyph.removeContour(c)
        newG.update()
        self.ui.glyph.appendComponent(name)
        self.ui.glyph.update()
        UpdateCurrentGlyphView()