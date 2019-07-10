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
from mojo.drawingTools import *
from mojo.events import extractNSEvent
from Helpers import deepCompatible, deepolation
from mojo.UI import OpenGlyphWindow, UpdateCurrentGlyphView

class LayersCanvas():
    
    def __init__(self, interface, glyphLayerGroup):
        self.ui = interface
        self.gl = glyphLayerGroup
        self.scale = .12
        self.canvasHeight = 290
        self.canvasWidth = 395
        self.boxHeight = 1200
        self.boxWidth = 1000
        self.scroll = 0
        self.gl.StorageGlyphCurrentLayer = None
        
    def scrollWheel(self, info):
        alt = extractNSEvent(info)['optionDown']
        delta = info.deltaY()
        sensibility = .002
        if not alt:
            scroll = self.scroll
            scroll -= (delta / abs(delta) * 50) / self.scale
            if scroll < 0:
                scroll = 0
            self.scroll = scroll
        else:
            scale = self.scale
            scale += (delta / abs(delta) * sensibility) / self.scale
            minScale = .005
            if scale > minScale:
                self.scale = scale
        self.update()
        
    def mouseDown(self, info):
        pointX, pointY = info.locationInWindow()
        for loc in self.glyphLocation_in_Window:
            x, y, w, h = loc
            if x < (pointX-400)/self.scale < x+w and y < (pointY-224)/self.scale < y+h:
                self.gl.StorageGlyphCurrentLayer = self.glyphLocation_in_Window[loc]
                if info.clickCount() == 2:
                    OpenGlyphWindow(self.gl.StorageGlyphCurrentLayer)
        self.update()
        
    def update(self):
        self.gl.layersCanvas.update()
        
    def draw(self):
        save()
        self.glyphLocation_in_Window = {}
        try:            
            self.ui.glyph = self.gl.storageGlyph
            canvasHeight = (self.canvasHeight / self.scale - self.boxHeight) + self.scroll            
            scale(self.scale, self.scale)
            translate(0, canvasHeight)            
            columnWidth = self.boxWidth
            lineHeight = canvasHeight            
            if self.gl.storageGlyph is None: return            
            for i, layerName in enumerate(self.gl.storageGlyph.lib['deepComponentsLayer']):                
                g = self.gl.storageGlyph.getLayer(layerName)                
                fill(None)
                stroke(0)                
                rect(0, 0, self.boxWidth, self.boxHeight)                
                #### DRAW GLYPH ####
                save()
                stroke(None)
                fill(0,0,0,1)
                if not deepCompatible(self.gl.storageGlyph.getLayer("foreground"), [layerName]):
                    fill(.9,0,.3,1)                
                x = (self.boxWidth-g.width)*.5
                y = 200                
                translate(x, y)                
                drawGlyph(g)
                restore()                
                #### LAYERS NAMES ####
                save()
                fill(0,.4,1,1)
                stroke(None)                
                if g == self.gl.StorageGlyphCurrentLayer:
                    fill(.9,0,.3,1)                
                font('Menlo-Regular', fontSize=int(90))                
                text(str(layerName), (20, self.boxHeight-120))
                restore()                
                x, y, w, h = columnWidth-self.boxWidth, lineHeight, self.boxWidth, self.boxHeight
                self.glyphLocation_in_Window[(x, y, w, h)] = g                
                #### TRANSLATE ####
                if (columnWidth + self.boxWidth) * self.scale > self.canvasWidth:                    
                    lineHeight -= self.boxHeight
                    translate(-columnWidth + self.boxWidth, -self.boxHeight)                        
                    columnWidth = 0
                else:                    
                    translate(self.boxWidth, 0)                
                columnWidth += self.boxWidth     
                # print(self.glyphLocation_in_Window)       
        except Exception as e:
            print(e)
        restore()
        UpdateCurrentGlyphView()