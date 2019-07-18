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
from mojo.roboFont import *
import os
from Helpers import makepath, deepolation

class testInstall():

    def __init__(self, interface):
        self.ui = interface
        self.testinstall()

    def testinstall(self):

        for fontName, font in self.ui.fonts.items():
            
            familyName, styleName = fontName.split('-')

            storageFont = self.ui.font2Storage[font]

            ####################################################
            #  / \                                             #
            # / ! \ Find a way to do a proper copy of the font #
            # -----                                            #
            ####################################################

            tempFont = font

            path = os.path.join(self.ui.projectPath, "TEMP/temp_%s.ufo"%fontName)
            makepath(path)
            
            for glyph in tempFont:

                if "deepComponentsGlyph" in glyph.lib:

                    for deepComp_Name, value in glyph.lib["deepComponentsGlyph"].items():

                        ID = value[0]
                        offset_x, offset_Y = value[1]

                        layersInfo = storageFont.lib["deepComponentsGlyph"][deepComp_Name][ID]

                        newGlyph = deepolation(RGlyph(), storageFont[deepComp_Name].getLayer("foreground"), layersInfo)

                        if newGlyph:
                            newGlyph.moveBy((offset_x, offset_Y))

                            for c in newGlyph:
                                glyph.appendContour(c)

            tempFont.save(path)
            tempFont.testInstall()
            tempFont.close()
