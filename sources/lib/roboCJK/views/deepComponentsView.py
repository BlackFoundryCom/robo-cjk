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
from imp import reload
from defconAppKit.windows.baseWindow import BaseWindowController
from vanilla import *

class DeepComponentsWindow(BaseWindowController):

    def __init__(self, controller):
        super(DeepComponentsWindow, self).__init__()
        self.controller = controller
        self.RCJKI = self.controller.RCJKI

        self.w = Window((0, 185, 200, 60), "Deep Components")

        self.w.keysAndExtremsGlyphButton = Button((0, 0, 200, 20), 
                'Keys & Extremes', 
                callback = self.keysAndExtremsGlyphButtonCallback)

        self.w.deepComponentEditionButton = Button((0, 20, 200, 20), 
                'DC Edition', 
                callback = self.deepComponentEditionButtonCallback)

        self.w.deepComponentInstantiationButton = Button((0, 40, 200, 20), 
                'DC Instantiation', 
                callback = self.deepComponentInstantiationButtonCallback)

        self.w.open()

    def keysAndExtremsGlyphButtonCallback(self, sender):
        self.RCJKI.closeDesignControllers()
        self.RCJKI.keysAndExtremsEditionController.launchkeysAndExtremsEditionInterface()

    def deepComponentEditionButtonCallback(self, sender):
        self.RCJKI.closeDesignControllers()
        self.RCJKI.deepComponentEditionController.launchDeepComponentEditionInterface()

    def deepComponentInstantiationButtonCallback(self, sender):
        pass