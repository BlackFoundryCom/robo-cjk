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
from mojo.UI import PostBannerNotification, AllGlyphWindows, CurrentGlyphWindow
import json
import os

from models import roboCJKProject
from models import roboCJKCollab
from views import projectEditorView
from utils import files
from utils import git
reload(roboCJKProject)
reload(roboCJKCollab)
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
        gitEngine.createGitignore()
        gitEngine.pull()

        self.RCJKI.project.usersLockers = self.RCJKI.collab._toDict

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

        self.RCJKI.collab = roboCJKCollab.RoboCJKCollab()
        self.RCJKI.collab._addLocker(gitEngine.user())
        d = self.RCJKI.project.usersLockers
        for lck in d['lockers']:
            self.RCJKI.collab._addLocker(lck['user'])
        for lck in d['lockers']:
            locker = self.RCJKI.collab._userLocker(lck['user'])
            locker._addGlyphs(lck['glyphs'])

        if self.RCJKI.collab._userLocker(self.RCJKI.user):
            self.RCJKI.reservedGlyphs = self.RCJKI.collab._userLocker(self.RCJKI.user).glyphs
            self.RCJKI.lockedGlyphs = self.RCJKI.collab._userLocker(self.RCJKI.user)._allOtherLockedGlyphs


        stamp = "Project '%s' Saved" % self.RCJKI.project.name
        gitEngine.commit(stamp)
        gitEngine.push()
        PostBannerNotification('Git Push', stamp)
        self.updateUI()

    def loadProject(self, path):
        # for i in range(len(AllGlyphWindows())):
        #     CurrentGlyphWindow().close()
        self.RCJKI.projectFileLocalPath = path[0]
        rootfolder = os.path.split(self.RCJKI.projectFileLocalPath)[0]
        gitEngine = git.GitEngine(rootfolder)
        if not gitEngine.isInGitRepository():
            PostBannerNotification('Impossible', "Project is not is GIT repository")
            return
        
        rootfolder = os.path.split(self.RCJKI.projectFileLocalPath)[0]
        gitEngine = git.GitEngine(rootfolder)
        gitEngine.createGitignore()
        gitEngine.pull()

        projectFile = open(self.RCJKI.projectFileLocalPath, 'r')
        d = json.load(projectFile)
        self.RCJKI.project = roboCJKProject.RoboCJKProject(d['name'], d['admin'])
        self.RCJKI.project._initWithDict(d)

        self.RCJKI.projectFonts = {}
        for path in self.RCJKI.project.masterFontsPaths.values():
            f = Font(os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Masters', path))
            k = f.info.familyName+'-'+f.info.styleName
            self.RCJKI.projectFonts[k] = f

        self.RCJKI.collab = roboCJKCollab.RoboCJKCollab()
        self.RCJKI.collab._addLocker(gitEngine.user())
        d = self.RCJKI.project.usersLockers
        for lck in d['lockers']:
            self.RCJKI.collab._addLocker(lck['user'])
        for lck in d['lockers']:
            locker = self.RCJKI.collab._userLocker(lck['user'])
            locker._addGlyphs(lck['glyphs'])

        if self.RCJKI.collab._userLocker(self.RCJKI.user):
            self.RCJKI.reservedGlyphs = self.RCJKI.collab._userLocker(self.RCJKI.user).glyphs
            self.RCJKI.lockedGlyphs = self.RCJKI.collab._userLocker(self.RCJKI.user)._allOtherLockedGlyphs

        self.updateProject()

        self.updateUI()

        if self.RCJKI.initialDesignController.interface:
            self.RCJKI.initialDesignController.loadProjectFonts()

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

    # def saveCollabToFile(self):
    #     head, tail = os.path.split(self.RCJKI.projectFileLocalPath)
    #     title, ext = tail.split('.')
    #     tail = title + '.roboCJKCollab'
    #     path = os.path.join(head, tail)
    #     self.RCJKI.collabFileLocalPath = path
    #     collabFile = open(path, 'w')
    #     d = json.dumps(self.RCJKI.collab._toDict, indent=4, separators=(',', ':'))
    #     collabFile.write(d)
    #     collabFile.close()
        
    # def saveAndCommitProjectAndCollab(self):
    #     rootfolder = os.path.split(self.RCJKI.projectFileLocalPath)[0]
    #     gitEngine = git.GitEngine(rootfolder)
    #     gitEngine.pull()
    #     stamp = "Project and Collab '%s' Saved" % self.RCJKI.project.name
    #     gitEngine.commit(stamp)
    #     gitEngine.push()
    #     PostBannerNotification('Git Push', stamp)

    # def pushRefresh(self):

    #     rootfolder = os.path.split(self.RCJKI.projectFileLocalPath)[0]
    #     gitEngine = git.GitEngine(rootfolder)

    #     head, tail = os.path.split(self.RCJKI.projectFileLocalPath)
    #     title, ext = tail.split('.')
    #     tail = title + '.roboCJKCollab'
    #     collabFilePath = os.path.join(head, tail)

    #     collabFile = open(collabFilePath, 'r')
    #     d = json.load(collabFile)
    #     self.RCJKI.collab = roboCJKCollab.RoboCJKCollab()
    #     self.RCJKI.collab._addLocker(self.RCJKI.user)
    #     for lck in d['lockers']:
    #         self.RCJKI.collab._addLocker(lck['user'])
    #     for lck in d['lockers']:
    #         locker = self.RCJKI.collab._userLocker(lck['user'])
    #         locker._addGlyphs(lck['glyphs'])
    #     if self.RCJKI.collab._userLocker(self.RCJKI.user):
    #         self.RCJKI.lockedGlyphs = self.RCJKI.collab._userLocker(self.RCJKI.user)._allOtherLockedGlyphs
    #         self.RCJKI.reservedGlyphs = self.RCJKI.collab._userLocker(self.RCJKI.user).glyphs

    #     message = 'Pull Push Refresh %s'% self.RCJKI.project.name
    #     PostBannerNotification('Refresh', message)

    #     stamp = "Project and Collab '%s' Refreshed" % self.RCJKI.project.name
    #     gitEngine.commit(stamp)
    #     gitEngine.push()

    def launchProjectEditorInterface(self):
        if not self.interface:
            # for i in range(len(AllGlyphWindows())):
            #     CurrentGlyphWindow().close()
            self.interface = projectEditorView.ProjectEditorWindow(self.RCJKI)

    def updateUI(self):
        self.interface.w.projectNameTextBox.set(self.RCJKI.project.name)
        self.interface.w.editProjectButton.enable((self.RCJKI.project!=None and self.RCJKI.project.admin==self.RCJKI.user))
        self.RCJKI.interface.w.initialDesignEditorButton.enable(self.RCJKI.project!=None)
        self.RCJKI.interface.w.deepComponentEditorButton.enable(self.RCJKI.project!=None)
        
    def updateSheetUI(self):
        l = [{'FamilyName':e.split('-')[0], 'StyleName':e.split('-')[1]} for e in list(self.RCJKI.project.masterFontsPaths.keys())]
        self.interface.sheet.masterGroup.mastersList.set(l)
