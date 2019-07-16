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
from mojo.roboFont import *
# from Helpers import deepolation

class DeepComponentDrawer():

    def __init__(self, interface, glyph, storageFont):
        self.ui = interface
        self.glyph = glyph
        self.font = storageFont
        self.draw()

    def draw(self):
        g = self.glyph
        f = self.font
        if "deepComponentsGlyph" in g.lib: 
            save()
            for desc in self.ui.currentGlyph_DeepComponents["CurrentDeepComponents"].values():
                save()
                glyph = desc['Glyph']
                ID = desc['ID']
                offset_X, offset_Y = desc['Offsets']
                stroke(None)
                if glyph == self.ui.current_DeepComponent_selection:
                    translate(self.ui.deepCompo_DeltaX, self.ui.deepCompo_DeltaY)
                    stroke(1, 0, 0, 1)
                drawGlyph(glyph)
                restore()
            restore()

        ##### TEMP DEEP COMP #####
    
        save()
        for name in self.ui.currentGlyph_DeepComponents['Existing']:
            for desc in self.ui.currentGlyph_DeepComponents['Existing'][name]:
                # for desc in desc:
                if not "Glyph" in desc: continue
                save()
                glyph = desc["Glyph"]
                offset_X, offset_Y = desc['Offsets']
                
                # offset_X, offset_Y = self.ui.temp_DeepComponents[self.ui.selectedVariantName]['Offset']
                fill(1, .8, .3, .7)
                stroke(None)
                if glyph == self.ui.current_DeepComponent_selection:
                    translate(self.ui.deepCompo_DeltaX, self.ui.deepCompo_DeltaY)
                    stroke(0, 0, 1, 1)
                # translate(offset_X, offset_Y)
                drawGlyph(glyph)
                restore()
        restore()
        
        save()
        for desc in self.ui.currentGlyph_DeepComponents['NewDeepComponents'].values():
            if not "Glyph" in desc: continue
            save()
            glyph = desc["Glyph"]
            offset_X, offset_Y = desc['Offsets']
            
            # offset_X, offset_Y = self.ui.temp_DeepComponents[self.ui.selectedVariantName]['Offset']
            fill(1, 0, .3, .8)
            stroke(None)
            if glyph == self.ui.current_DeepComponent_selection:
                translate(self.ui.deepCompo_DeltaX, self.ui.deepCompo_DeltaY)
                stroke(0, 0, 1, 1)
            # translate(offset_X, offset_Y)
            drawGlyph(glyph)
            restore()
        restore()