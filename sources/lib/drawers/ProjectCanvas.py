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
from mojo.drawingTools import *
from mojo.events import extractNSEvent
from mojo.UI import UpdateCurrentGlyphView
from mojo.roboFont import *

from drawers.ReferenceViewerDrawer import ReferenceViewerDraw
from drawers.DesignFrameDrawer import DesignFrameDrawer

class ProjectCanvas():

    def __init__(self, sheet, canvasName, group=False):
        self.ui = sheet
        self.s = group
        self.name = canvasName
        self.scale = .2
        self.translateX = 0
        self.translateY = 0

        canvasWidth = 285
        canvasHeight = 270
        
        if self.name == "ReferenceViewer":
            self.scale = .15
            self.translateX = 600
            self.translateY = 300

        elif self.ui.glyph is not None and len(self.ui.glyph):
            self.translateX = ((canvasWidth/self.scale-self.ui.glyph.width)*.5 )
            self.translateY = ((canvasHeight/self.scale-(self.ui.glyph.box[3]-self.ui.glyph.box[1]))*.5 )

    def update(self):
        if self.name == "ReferenceViewer":
            self.s.canvas.update()
        else:
            self.s.canvas.update()

    def mouseDragged(self, info):
        command = extractNSEvent(info)['commandDown']
        deltaX = info.deltaX()/self.scale
        deltaY = info.deltaY()/self.scale
        if not command:
            self.translateX += deltaX
            self.translateY -= deltaY
        elif self.ui.reference_list_selection and self.name == "ReferenceViewer":
            currentSetting = self.ui.referenceViewerSettings[self.ui.reference_list_selection[0]]
            currentSetting["x"] += deltaX
            currentSetting["y"] -= deltaY
        self.ui.updateViews()
        self.update()

    def scrollWheel(self, info):
        alt = extractNSEvent(info)['optionDown']
        if not alt: return
        scale = self.scale
        delta = info.deltaY()
        sensibility = .009
        scale += (delta / abs(delta) * sensibility) / self.scale
        minScale = .005
        if scale > minScale:
            self.scale = scale
        self.update()

    def draw(self):
        try:
            scale(self.scale, self.scale)
            translate(self.translateX,self.translateY)
            strokeWidth(.4/self.scale)

            if self.name == "ReferenceViewer":
                save()
                stroke(0)
                fill(None)
                w, h = self.ui.EM_Dimension_X, self.ui.EM_Dimension_Y
                translateY = -12 * h / 100
                translate(0,translateY)
                rect(0,0,w, h)
                restore()

                txt = "a"
                if self.ui.glyph:
                    if self.ui.glyph.name.startswith("uni"):
                        txt = chr(int(self.ui.glyph.name[3:7],16))
                    elif g.unicode: 
                        txt = chr(self.ui.glyph.unicode)
                ReferenceViewerDraw(self.ui, txt)

            else:
                fill(0)
                if self.ui.glyph:
                    drawGlyph(self.ui.glyph)
                
                DesignFrameDrawer(self.ui).draw(glyph = self.ui.glyph, scale = self.scale)

        except Exception as e:
            print(e)