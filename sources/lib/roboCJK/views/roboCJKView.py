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
import os
import json

from controllers import roboCJKController
reload(roboCJKController)


class RoboCJKWindow(BaseWindowController):
    def __init__(self, RCJKI):
        super(RoboCJKWindow, self).__init__()
        self.RCJKI = RCJKI
        self.w = Window((0, 0, 200, 100), 'Robo-CJK')
        self.w.userTextBox = TextBox((0,0, 200, 20), self.RCJKI.user,alignment='center')
        self.w.projectEditorButton = Button((0,20,200,20), 'Project Editor', callback=self.openProjectEditor)
        self.w.initialDesignEditorButton = Button((0,40,200,20), 'Initial Design', callback=self.openInitialDesignEditor)
        self.w.deepComponentEditorButton = Button((0,60,200,20), 'Deep Component Editor', callback=self.openDeepComponentEditor)
        self.w.settingsButton = Button((0,-20,200,20), 'Settings', callback=self.openSettings)
        self.w.initialDesignEditorButton.enable(False)
        self.w.deepComponentEditorButton.enable(False)
        self.w.bind('close', self.windowCloses)
        self.w.open()

    def openProjectEditor(self, sender):
    	self.RCJKI.projectEditorController.launchProjectEditorInterface()

    def openDeepComponentEditor(self, sender):
        print(self.RCJKI.characterSets[self.RCJKI.project.script]['DeepComponentKeys'])

    def openInitialDesignEditor(self, sender):
        print(self.RCJKI.characterSets[self.RCJKI.project.script]['Basic'])

    def openSettings(self, sender):
        pass

    def windowCloses(self, sender):
    	if self.RCJKI.projectEditorController.interface:
    		self.RCJKI.projectEditorController.interface.w.close()
