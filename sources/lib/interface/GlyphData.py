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

class GlyphData(Box):

    def __init__(self, posSize, interface):
        super(GlyphData, self).__init__(posSize)
        self.ui = interface


        self.glyphCompositionRules_TextBox = TextBox((0, 0, -0, 20),
            "Glyph composition rules",
            sizeStyle = "small")

        self.glyphCompositionRules_List = List((0, 20, -0, 100),
            self.ui.suggestComponent,
            drawFocusRing=False, )

        self.variants_TextBox = TextBox((0, 130, -0, 20),
            "Variants",
            sizeStyle = "small")

        self.variants_List = List((0, 150, -0, 100),
            [],
            drawFocusRing=False, )