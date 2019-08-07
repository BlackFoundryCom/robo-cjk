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
from imp import reload
import Helpers
reload(Helpers)

class Settings():

    def __init__(self, interface):
        self.ui = interface
        self.w = Sheet((600,550), self.ui.w)
        self.w.close_button = Button((-100,-30,-10,-10),
                'close',
                callback = self._close_button_callback)

        Helpers.setDarkMode(self.w, self.ui.darkMode)
        self.w.open()

    def _close_button_callback(self, sender):
        self.w.close()