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
from defcon import *
from mojo.roboFont import *
from mojo.UI import PostBannerNotification
import json
import os

from models import roboCJKProject
from views import projectEditorView
from utils import files
from utils import git
reload(roboCJKProject)
reload(projectEditorView)
reload(files)
reload(git)

class ProjectEditorController(object):
    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.interface = None

    def updateProject(self):
        rootfolder = os.path.split(self.RCJKI.projectFileLocalPath)[0]
        gitEngine = git.GitEngine(rootfolder)
        if not gitEngine.isInGitRepository():
            PostBannerNotification('Impossible', "Project is not is GIT repository")
            return
        gitEngine.pull()
        projectFile = open(self.RCJKI.projectFileLocalPath, 'w')
        d = json.dumps(self.RCJKI.project._toDict, indent=4, separators=(',', ':'))
        projectFile.write(d)
        projectFile.close()
        PostBannerNotification("Project '%s' Saved" % self.RCJKI.project.name, self.RCJKI.projectFileLocalPath)
        stamp = "Project '%s' Saved" % self.RCJKI.project.name
        gitEngine.commit(stamp)
        gitEngine.push()
        PostBannerNotification('Git Push', stamp)
        self.updateUI()

    def saveProject(self, path):
        name = os.path.split(path)[1].split('.')[0]
        rootfolder = os.path.split(path)[0]
        gitEngine = git.GitEngine(rootfolder)
        if not gitEngine.isInGitRepository():
            PostBannerNotification('Impossible', "Project is not is GIT repository")
            return
        gitEngine.pull()
        self.RCJKI.project = roboCJKProject.RoboCJKProject(name, gitEngine.user())
        self.RCJKI.projectFileLocalPath = path
        
        projectFile = open(path, 'w')
        d = json.dumps(self.RCJKI.project._toDict, indent=4, separators=(',', ':'))
        projectFile.write(d)
        projectFile.close()
        PostBannerNotification("Project '%s' Saved" % self.RCJKI.project.name, self.RCJKI.projectFileLocalPath)
        stamp = "Project '%s' Saved" % self.RCJKI.project.name
        gitEngine.commit(stamp)
        gitEngine.push()
        PostBannerNotification('Git Push', stamp)
        self.updateUI()

    def loadProject(self, path):
        self.RCJKI.projectFileLocalPath = path[0]
        rootfolder = os.path.split(self.RCJKI.projectFileLocalPath)[0]
        gitEngine = git.GitEngine(rootfolder)
        if not gitEngine.isInGitRepository():
            PostBannerNotification('Impossible', "Project is not is GIT repository")
            return

        rootfolder = os.path.split(self.RCJKI.projectFileLocalPath)[0]
        gitEngine = git.GitEngine(rootfolder)
        gitEngine.pull()

        projectFile = open(path[0], 'r')
        d = json.load(projectFile)
        self.RCJKI.project = roboCJKProject.RoboCJKProject(d['name'], d['admin'])
        self.RCJKI.project._initWithDict(d)

        self.RCJKI.projectFonts = {}
        for path in self.RCJKI.project.masterFontsPaths.values():
            f = Font(os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Masters', path))
            k = f.info.familyName+'-'+f.info.styleName
            self.RCJKI.projectFonts[k] = f

        self.updateUI()

    def importFontToProject(self, path):
        rootfolder = os.path.split(self.RCJKI.projectFileLocalPath)[0]
        gitEngine = git.GitEngine(rootfolder)
        gitEngine.pull()
        f = Font(path)
        k = f.info.familyName+'-'+f.info.styleName
        if k not in self.RCJKI.project.masterFontsPaths:
            UFOName = os.path.split(path)[1]
            savePath = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Masters', UFOName)
            files.makepath(savePath)
            f.save(savePath)
            self.RCJKI.project.masterFontsPaths[k] = UFOName
            self.RCJKI.projectFonts[k] = f
        self.updateSheetUI()
        self.updateProject()

    def launchProjectEditorInterface(self):
        if not self.interface:
            self.interface = projectEditorView.ProjectEditorWindow(self.RCJKI)

    def updateUI(self):
        # rootfolder = os.path.split(self.RCJKI.projectFileLocalPath)[0]
        # gitEngine = git.GitEngine(rootfolder)
        self.interface.w.projectNameTextBox.set(self.RCJKI.project.name)
        self.interface.w.editProjectButton.enable((self.RCJKI.project!=None and self.RCJKI.project.admin==self.RCJKI.user))
        self.RCJKI.interface.w.initialDesignEditorButton.enable(self.RCJKI.project!=None)
        self.RCJKI.interface.w.deepComponentEditorButton.enable(self.RCJKI.project!=None)
        
    def updateSheetUI(self):
        l = [{'FamilyName':e.split('-')[0], 'StyleName':e.split('-')[1]} for e in list(self.RCJKI.project.masterFontsPaths.keys())]
        self.interface.sheet.masterGroup.mastersList.set(l)
