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
from mojo.events import addObserver, removeObserver
from mojo.UI import UpdateCurrentGlyphView
from imp import reload

from drawers.ReferenceViewerDrawer import ReferenceViewerDraw

class ReferenceViewer(Group):

    def __init__(self, posSize, interface):
        super(ReferenceViewer, self).__init__(posSize)
        self.ui = interface

        self.OnOff_referenceViewer = 1
        self.OnOff_referenceViewer_checkBox = CheckBox((10,5,-10,20),
                'On/Off',
                value = self.OnOff_referenceViewer,
                sizeStyle = "small",
                callback = self._OnOff_referenceViewer_callback)

        self.drawPreview_referenceViewer = 1
        self.drawPreview_referenceViewer_checkBox = CheckBox((150,5,-10,20),
                'Draw Preview',
                value = self.drawPreview_referenceViewer,
                sizeStyle = "small",
                callback = self._drawPreview_referenceViewer_callback)

        self.ui.w.bind('close', self.windowWillClose)
        self.observer()

    def _OnOff_referenceViewer_callback(self, sender):
        self.OnOff_referenceViewer = sender.get()
        UpdateCurrentGlyphView()

    def _drawPreview_referenceViewer_callback(self, sender):
        self.drawPreview_referenceViewer = sender.get()
        UpdateCurrentGlyphView()

    def windowWillClose(self, sender):
        self.observer(remove=True)
        
    def observer(self, remove = False):
        if not remove:
            addObserver(self, "draw", "draw")
            addObserver(self, "draw", "drawPreview")
            addObserver(self, "draw", "drawInactive")
            return
        removeObserver(self, "draw")
        removeObserver(self, "drawPreview")
        removeObserver(self, "drawInactive")

    def draw(self, info):
        self.glyph = self.ui.glyph
        if self.glyph is None: return
        if not self.OnOff_referenceViewer: return
        if info['notificationName'] == "drawPreview" and not self.drawPreview_referenceViewer: return

        if self.glyph.name.startswith("uni"):
            txt = chr(int(self.glyph.name[3:7],16))
        elif self.glyph.unicode: 
            txt = chr(self.glyph.unicode)
        else:
            txt=""
        ReferenceViewerDraw(self.ui, txt)