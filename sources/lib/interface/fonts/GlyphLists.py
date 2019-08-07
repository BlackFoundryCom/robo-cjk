"""
Copyright 2019 Black Foundry.

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
from mojo.roboFont import *
from mojo.UI import OpenGlyphWindow, CurrentGlyphWindow
from mojo.canvas import Canvas
from AppKit import NSAppearance, NSColor
# from drawers.MainCanvas import MainCanvas
from lib.cells.colorCell import RFColorCell
from Helpers import normalizeUnicode

class GlyphLists(Group):

    def __init__(self, posSize, interface):
        super(GlyphLists, self).__init__(posSize)
        self.ui = interface

        self.displayGlyphset_settingList = ['find Char/Name', "Sort by key"]
        self.displaySettings = 'find Char/Name'
        self.displayGlyphset_setting = PopUpButton((0, 0, -0, 20),
            self.displayGlyphset_settingList,
            sizeStyle = "small",
            callback = self._displayGlyphset_setting_callback)

        self.jumpTo = SearchBox((0,30,-0,20),
            placeholder = "Char/Name",
            sizeStyle = "small", 
            callback = self._jumpTo_callback,
            # continuous = False,
            )

        self.glyphset_List = List((0,50,-0,-0),
            [],
            columnDescriptions = [
                                {"title": "Char", "width" : 30},
                                {"title": "Name", "width" : 105},                  
                                ],
            drawFocusRing=False, 
            selectionCallback = self._glyphset_List_selectionCallback,
            doubleClickCallback = self._glyphset_List_doubleClickCallback)

        self.set_glyphset_List()

    def _displayGlyphset_setting_callback(self, sender):
        self.displaySettings = self.displayGlyphset_settingList[sender.get()]
        if self.displaySettings == 'find Char/Name':
            self.ui.glyphset = self.ui.font.lib['public.glyphOrder']
            glyphset = self.ui.glyphsSetDict[self.ui.font]
            self.glyphset_List.set(glyphset)

    def set_glyphset_List(self):
        if self.ui.font in self.ui.glyphsSetDict:
            self.ui.glyphset = self.ui.font.lib['public.glyphOrder']
            glyphset = self.ui.glyphsSetDict[self.ui.font]
            self.glyphset_List.set(glyphset)

    def _glyphset_List_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        # if self.ui.glyphset:
        name = self.ui.glyphset[sel[0]]
        self.ui.glyph = self.ui.font[name]
    
        self.ui.getCompositionGlyph()
        
        self.ui.selectedVariantName = ""
        self.ui.currentGlyph_DeepComponents = {
                                            'CurrentDeepComponents':{}, 
                                            'Existing':{}, 
                                            'NewDeepComponents':{},
                                            }
        self.ui.getDeepComponents_FromCurrentGlyph()                   
        self.ui.newDeepComponent_active = False
        self.ui.updateViews()

    def _glyphset_List_doubleClickCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        if self.ui.glyph is None: return
        OpenGlyphWindow(self.ui.glyph)
        gw = CurrentGlyphWindow()
        appearance = NSAppearance.appearanceNamed_('NSAppearanceNameVibrantDark')
        gw.window().getNSWindow().setAppearance_(appearance)

    def _jumpTo_callback(self, sender):
        string = sender.get()
        if not string:
            glyphset = self.ui.glyphsSetDict[self.ui.font]
            self.glyphset_List.setSelection([])
            self.glyphset_List.set(glyphset)
            self.ui.glyphset = self.ui.font.lib['public.glyphOrder']
            return
        try:
            if self.displaySettings == 'find Char/Name':
                # self.ui.glyphset = self.ui.glyphsSetDict[self.ui.font]
                if string.startswith("uni"):
                    index = self.ui.glyphset.index(string)
                elif len(string) == 1:
                    code = "uni"+normalizeUnicode(hex(ord(string))[2:].upper())
                    index = self.ui.glyphset.index(code)
                self.glyphset_List.setSelection([index])

            elif self.displaySettings == 'Sort by key':
                name = string
                if string.startswith("uni"):
                    name = string[3:]
                elif len(string) == 1:
                    name = normalizeUnicode(hex(ord(string))[2:].upper())
                    
                self.ui.glyphset = self.ui.key2Glyph[name]
                self.glyphset_List.set([dict(Name = name, Char = chr(int(name[3:],16)) if name.startswith('uni') else "") for name in self.ui.glyphset])
        except:
            pass
