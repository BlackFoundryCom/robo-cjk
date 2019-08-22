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

from controllers import initialDesignController
reload(initialDesignController)


class RoboCJKWindow(BaseWindowController):
    def __init__(self, RCJKI):
        super(RoboCJKWindow, self).__init__()
        self.RCJKI = RCJKI
        self.w = Window((0, 0, 200, 140), 'Robo-CJK')
        self.w.userTextBox = TextBox((0,0, 200, 20), self.RCJKI.user,alignment='center')
        self.w.projectEditorButton = Button((0,20,200,20), 'Project', callback=self.openProjectEditor)
        self.w.initialDesignEditorButton = Button((0,40,200,20), 'Initial Design', callback=self.openInitialDesignEditor)
        self.w.deepComponentEditorButton = Button((0,60,200,20), 'Deep Component Editor', callback=self.openDeepComponentEditor)
        self.w.textCenterButton = Button((0,80,200,20), 'Text Center', callback=self.openTextCenter)
        self.w.toolsBoxButton = Button((0,100,200,20), 'Tools Box', callback=self.openToolsBox)
        self.w.settingsButton = Button((0,-20,200,20), 'Settings', callback=self.openSettings)
        self.RCJKI.toggleObservers()
        self.w.bind('close', self.windowCloses)
        self.w.open()

    def openTextCenter(self, sender):
        if self.RCJKI.currentFont:
            self.RCJKI.launchTextCenterInterface()

    def openProjectEditor(self, sender):
        self.RCJKI.projectEditorController.launchProjectEditorInterface()

    def openInitialDesignEditor(self, sender):
        self.RCJKI.initialDesignController.launchInitialDesignInterface()

    def openDeepComponentEditor(self, sender):
        print(self.RCJKI.characterSets[self.RCJKI.project.script]['DeepComponentKeys'])

    def openSettings(self, sender):
        pass

    def openToolsBox(self, sender):
        self.RCJKI.toolsBoxController.launchToolsBoxInterface()

    def windowCloses(self, sender):
        self.RCJKI.toggleObservers(forceKill=True)

        if self.RCJKI.projectEditorController.interface:
            self.RCJKI.projectEditorController.interface.w.close()

        if self.RCJKI.initialDesignController.interface:
            self.RCJKI.initialDesignController.interface.w.close()

        if self.RCJKI.textCenterInterface:
            self.RCJKI.textCenterInterface.w.close()

        if self.RCJKI.toolsBoxController:
            self.RCJKI.toolsBoxController.interface.w.close()
