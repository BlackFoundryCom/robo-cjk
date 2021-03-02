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
from vanilla import TextBox
from AppKit import NSColor, NSFont

class SmartTextBox(TextBox):
    def __init__(self, posSize, text="", alignment="natural", 
        selectable=False, callback=None, sizeStyle=40.0,
        red=0,green=0,blue=0, alpha=1.0):
        self.color = NSColor.colorWithCalibratedRed_green_blue_alpha_(red, green, blue, alpha)
        super().__init__(posSize, text=text, alignment=alignment, 
            selectable=selectable, sizeStyle=sizeStyle)
        
    def _setSizeStyle(self, sizeStyle):
        value = sizeStyle
        self._nsObject.cell().setControlSize_(value)
        font = NSFont.systemFontOfSize_(value)
        self._nsObject.setFont_(font)
        self._nsObject.setTextColor_(self.color)

    def setColor(self, red, green, blue, alpha=1):
    	self._nsObject.setTextColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(red, green, blue, alpha))
