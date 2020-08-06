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
from vanilla import *
from AppKit import NSDragOperationMove

globalBacklogListDragType = "globalBacklogListDragType"

def managerLocked(func):
    def wrapper(self, *args, **kwargs):
        if self.username not in self.TMC.team.managers:
            return
        func(self, *args, **kwargs)
    return wrapper

def lockUI(func):
    def wrapper(self, *args, **kwargs):
        if self._lock: return
        self._lock = True
        func(self, *args, **kwargs)
        self._lock = False
    return wrapper

class TeamManagerUI:
    
    def __init__(self, TMC):
        self.TMC = TMC
        self._lock = False
        self.username = self.TMC.RCJKI.mysql_userName
        self.w = Window((1205, 600), "Team Manager")

        self.w.managersTitle = TextBox(
            (10, 10, 150, 20), 
            "Project managers"
            )
        self.w.managersPopUpButton = PopUpButton(
            (130, 10, 150, 20), 
            []
            )
        self.w.managersEditButton = Button(
            (280, 10, 70, 20), 
            'Edit', 
            callback = self.managersEditButtonCallback
            )
        
        self.w.globalBacklogBox = Box((10, 65, 140, -10))
        self.w.groupsBox = Box(
            (160, 50, 500, -10), 
            'Groups section, only editable by the project managers'
            )
        self.w.usersBox = Box(
            (670, 50, -10, -10), 
            'Users section, only editable by the group managers'
            )      
        
        self.w.globalBacklogBox.backlogTitle = TextBox(
            (5, 5, -5, 20), 
            'Global backlog'
            )
        self.TMC.getglobalbacklog()
        self.w.globalBacklogBox.backlogList = List(
            (5, 30, -5, -70), 
            self.TMC.globalBacklog,
            drawFocusRing = False,
            selectionCallback = self.backlogListSelectionCallback,
            dragSettings=dict(type=globalBacklogListDragType, callback=self.globalBacklogListDragCallback),
            # selfWindowDropSettings=dict(type=globalBacklogListDragType, operation=NSDragOperationMove, callback=self.globalBacklogListDropCallback),
            )
        self.w.globalBacklogBox.backlogSelectionTitle = TextBox(
            (5, -65, -5, 20), '0 selected',
            sizeStyle = 'small',
            alignment = "center"
            )
        self.w.globalBacklogBox.backlogUpdateButton = Button(
            (5, -45, -5, 25), 
            'refresh', 
            callback = self.backlogUpdateButtonCallback
            )
        self.w.globalBacklogBox.backlogTotalTitle = TextBox(
            (5, -15, -5, 20), 
            "%s glyphs"%len(self.w.globalBacklogBox.backlogList.get()), 
            alignment = 'center',
            sizeStyle = "small"
            )
        
        self.selectedGroup = ''
        self.w.groupsBox.groupsTitle = TextBox(
            (5, 10, 150, 20), 
            'Groups'
            )
        self.w.groupsBox.groupsList = List(
            (5, 35, 200, -30), 
            self.TMC.groups, 
            drawFocusRing = False, 
            selectionCallback = self.groupsListSelectionCallback, 
            editCallback = self.groupsListEditCallback,
            )
        self.w.groupsBox.addGroupsButton = Button(
            (5, -25, 100, 20), 
            '+', 
            callback = self.addGroupsButtonCallback
            )
        self.w.groupsBox.removeGroupsButton = Button(
            (105, -25, 100, 20), 
            '-', 
            callback = self.removeGroupsButtonCallback
            )
        
        self.w.groupsBox.groupsBacklogTitle = TextBox(
            (210, 10, 100, 20), 'Backlog')
        self.w.groupsBox.groupsBacklogList = List(
            (210, 35, 90, -30), 
            [], 
            drawFocusRing = False,
            selfWindowDropSettings=dict(type=globalBacklogListDragType, operation=NSDragOperationMove, callback=self.globalBacklogListDropCallback),
            )
        self.w.groupsBox.backlogTotalTitle = TextBox(
            (210, -20, 90, 20), 
            "0 glyphs", 
            alignment = 'center', 
            sizeStyle = "small"
            )
        
        self.w.groupsBox.groupsWIPTitle = TextBox((300, 10, 100, 20), 'WIP')
        self.w.groupsBox.groupsWIPList = List((300, 35, 90, -30), [], drawFocusRing = False)
        self.w.groupsBox.WIPTotalTitle = TextBox((300, -20, 90, 20), "206 glyphs", alignment = 'center', sizeStyle = "small")
        
        self.w.groupsBox.groupsDoneTitle = TextBox((390, 10, 100, 20), 'Done')
        self.w.groupsBox.groupsDoneList = List((390, 35, 90, -30), [], drawFocusRing = False)
        self.w.groupsBox.doneTotalTitle = TextBox((390, -20, 90, 20), "106 glyphs", alignment = 'center', sizeStyle = "small")
        
        self.w.usersBox.usersTitle = TextBox((5, 10, 150, 20), 'Users')
        self.w.usersBox.usersList = List((5, 35, 200, -30), ["ChenRong"], drawFocusRing = False)
        self.w.usersBox.addusersButton = Button((5, -25, 100, 20), '+')
        self.w.usersBox.removeusersButton = Button((105, -25, 100, 20), '-')
        
        self.w.usersBox.usersBacklogTitle = TextBox((210, 10, -5, 20), 'Backlog')
        self.w.usersBox.usersBacklogList = List((210, 35, 100, -30), [], drawFocusRing = False)
        self.w.usersBox.backlogTotalTitle = TextBox((210, -20, 90, 20), "76 glyphs", alignment = 'center', sizeStyle = "small")
        
        self.w.usersBox.usersInProgressTitle = TextBox((310, 10, -5, 20), 'WIP')
        self.w.usersBox.usersInProgressList = List((310, 35, 100, -30), [], drawFocusRing = False)
        self.w.usersBox.WIPTotalTitle = TextBox((310, -20, 100, 20), "73 glyphs", alignment = 'center', sizeStyle = "small")        
        
        self.w.usersBox.usersDoneTitle = TextBox((410, 10, -5, 20), 'Done')
        self.w.usersBox.usersDoneList = List((410, 35, 100, -30), [], drawFocusRing = False)
        self.w.usersBox.doneTotalTitle = TextBox((410, -20, 100, 20), "47 glyphs", alignment = 'center', sizeStyle = "small")

        self.w.bind("close", self.windowWillClose)

    ####### WINDOW #######
    #----------------------
        
    def launchInterface(self):
        self.w.open()

    def setUI(self):
        self.w.managersPopUpButton.setItems(self.TMC.team.managers.managersList)
        self.setGroupList()

    def windowWillClose(self, sender):
        self.TMC.saveTeam()

    def managersEditButtonCallback(self, sender):
        if self.TMC.permissionToEditManagers():
            ProjectManagerEditSheet(self.TMC, self.w)

    ####### BACKLOG #######
    #----------------------

    def backlogListSelectionCallback(self, sender):
        sel = sender.getSelection()
        title = '%s selected'%len(sel)
        self.w.globalBacklogBox.backlogSelectionTitle.set(title)

    def backlogUpdateButtonCallback(self, sender):
        self.w.globalBacklogBox.backlogList.setSelection([])
        self.TMC.getglobalbacklog()
        self.w.globalBacklogBox.backlogList.set(self.TMC.globalBacklog)

    def globalBacklogListDragCallback(self, sender, indexes):
        self.globalBacklogListDragElements = [x for i, x in enumerate(sender.get()) if i in indexes]

    def globalBacklogListDropCallback(self, sender, dropInfos):
        isProposal = dropInfos["isProposal"]
        if not isProposal:
            if self.selectedGroup:
                glyphs = self.globalBacklogListDragElements
                self.TMC.team.get(self.selectedGroup)._addBackLogGlyphs(glyphs)
                self.TMC.team.backlog_glyphs.remove(glyphs)
                self.w.globalBacklogBox.backlogList.setSelection([])
                self.w.globalBacklogBox.backlogList.set(self.TMC.team.backlog_glyphs._glyphs)
                self.updateGroupsUI()
        return True

    ####### GROUPS #######
    #----------------------

    # @managerLocked
    @lockUI
    def groupsListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            self.selectedGroup = ""
            self.updateGroupsUI()
            return
        self.selectedGroup = sender.get()[sel[0]]
        self.updateGroupsUI()

    @managerLocked
    @lockUI
    def groupsListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            return
        groupName = sender.get()[sel[0]]
        if self.selectedGroup != groupName:
            self.TMC.renameGroup(self.selectedGroup, groupName)
            self.selectedGroup = groupName
        self.setGroupList()

    @managerLocked
    @lockUI
    def addGroupsButtonCallback(self, sender):
        i = 0
        while True:
            name = "newGroup%s"%str(i).zfill(2)
            if name not in self.TMC.groups:
                break
            i += 1
        self.TMC.addGroup(name)
        self.setGroupList()

    @managerLocked
    @lockUI
    def removeGroupsButtonCallback(self, sender):
        sel = self.w.groupsBox.groupsList.getSelection()
        if not sel:
            return
        name = self.w.groupsBox.groupsList.get()[sel[0]]
        self.TMC.removeGroup(name)
        self.setGroupList()

    def setGroupList(self):
        self.w.groupsBox.groupsList.set(self.TMC.groups)

    def updateGroupsUI(self):
        if self.selectedGroup:
            self.w.groupsBox.groupsBacklogList.set(list(self.TMC.team.get(self.selectedGroup).backlog_glyphs))
            self.w.groupsBox.backlogTotalTitle.set("%s glyphs"%len(self.w.groupsBox.groupsBacklogList.get()))
        else:
            self.w.groupsBox.groupsBacklogList.set([])
            self.w.groupsBox.backlogTotalTitle.set("0 glyphs")

class ProjectManagerEditSheet:

    def __init__(self, TMC, parentWindow):
        self.TMC = TMC
        self.w = Sheet((220, 200), parentWindow)
        self.oldname = ""
        self.w.managersList = List(
            (0, 0, -0, -40), 
            [], 
            selectionCallback = self.managersListSelectionCallback, 
            editCallback = self.managersListEditCallback
            )
        self.w.addManagerButton = Button(
            (0, -40, 110, 20), 
            '+', 
            callback = self.addManagerCallback
            )
        self.w.removeManagerButton = Button(
            (110, -40, 110, 20), 
            '-', 
            callback = self.removeManagerCallback
            )
        self.w.closeButton = Button(
            (0, -20, -0, 20), 
            'close', 
            callback = self.closeWindowCallback
            )
        self.setManagersList()
        self.w.open()

    def closeWindowCallback(self, sender):
        self.TMC.interface.setUI()
        self.w.close()

    def addManagerCallback(self, sender):
        managersList = self.w.managersList.get()
        i = 0
        while True:
            name = "unnamed_%s"%str(i).zfill(2)
            if name not in managersList:
                break
            i += 1
        self.TMC.addManager(name)
        self.setManagersList()

    def removeManagerCallback(self, sender):
        sel = self.w.managersList.getSelection()
        if not sel: return
        name = self.w.managersList.get()[sel[0]]
        self.TMC.removeManager(name)
        self.oldname = ""
        self.w.managersList.setSelection([])
        self.setManagersList()

    def setManagersList(self):
        if self.TMC.RCJKI.mysql_userName not in self.TMC.team.managers:
            self.TMC.addManager(self.TMC.RCJKI.mysql_userName)
        self.w.managersList.set(self.TMC.team.managers.managersList)

    def managersListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            return
        self.oldname = sender.get()[sel[0]]
        if self.oldname == self.TMC.RCJKI.mysql_userName:
            self.w.removeManagerButton.enable(False)
        else:
            self.w.removeManagerButton.enable(True)

    def managersListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            return
        name = sender.get()[sel[0]]
        if self.oldname != name:
            self.TMC.renameManager(self.oldname, name)
        self.oldname = name
