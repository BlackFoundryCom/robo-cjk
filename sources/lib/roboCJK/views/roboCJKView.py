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
from mojo.UI import PostBannerNotification, setMaxAmountOfVisibleTools
from mojo.events import uninstallTool

from controllers import initialDesignController
from controllers import deepComponentsController
from controllers import textCenterController

from tools.externalTools import shapeTool
from tools.externalTools import scalingEditTool

reload(initialDesignController)
reload(deepComponentsController)
reload(textCenterController)
reload(shapeTool)
reload(scalingEditTool)


class RoboCJKWindow(BaseWindowController):
    def __init__(self, RCJKI):
        super(RoboCJKWindow, self).__init__()
        self.RCJKI = RCJKI
        self.w = Window((0, 0, 200, 140), 'Robo-CJK')
        self.w.userTextBox = TextBox((0,0, 200, 20), self.RCJKI.user,alignment='center')
        self.w.projectEditorButton = Button((0,20,200,20), 'Project', callback=self.openProjectEditor)
        self.w.initialDesignEditorButton = Button((0,40,200,20), 'Initial Design', callback=self.openInitialDesignEditor)
        self.w.deepComponentButton = Button((0,60,200,20), 'Deep Components', callback=self.openDeepComponent)
        self.w.textCenterButton = Button((0,80,200,20), 'Text Center', callback=self.openTextCenter)
        self.w.inspectorButton = Button((0,100,200,20), 'Inspector', callback=self.openInspector)
        self.w.settingsButton = Button((0,-20,200,20), 'Settings', callback=self.openSettings)
        self.RCJKI.toggleObservers()
        self.w.bind('close', self.windowCloses)
        self.w.open()

    def openTextCenter(self, sender):
        if self.RCJKI.currentFont is None:
            PostBannerNotification("Warning", "There is no current font")
            return
        self.RCJKI.textCenterController.launchTextCenterInterface()

    def openProjectEditor(self, sender):
        self.RCJKI.projectEditorController.launchProjectEditorInterface()

    def openInitialDesignEditor(self, sender):
        self.RCJKI.closeDesignControllers()
        self.RCJKI.initialDesignController.launchInitialDesignInterface()

    def openDeepComponent(self, sender):
        self.RCJKI.deepComponentsController.launchDeepComponentsInterface()

    def openSettings(self, sender):
        pass

    def openInspector(self, sender):
        self.RCJKI.inspectorController.launchInspectorInterface()

    def windowCloses(self, sender):
        self.RCJKI.windowCloses()


