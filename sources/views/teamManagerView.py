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

class TeamManagerUI:
    
    def __init__(self, TMC):
        self.TMC = TMC
        self.w = Window((1205, 600), "Team Manager")

        self.w.managersTitle = TextBox((10, 10, 70, 20), "Project managers")
        self.w.managersPopUpButton = PopUpButton((80, 10, 150, 20), ["Claire", "Jeremie"])
        self.w.managersEditButton = Button((240, 10, 70, 20), 'Edit')
        
        self.w.globalBacklogBox = Box((10, 65, 140, -10))
        self.w.groupsBox = Box((160, 50, 500, -10), 'Groups section, only editable by the project managers')
        self.w.usersBox = Box((670, 50, -10, -10), 'Users section, only editable by the group managers')      
        
        self.w.globalBacklogBox.backlogTitle = TextBox((5, 5, -5, 20), 'Global backlog')
        self.w.globalBacklogBox.backlogList = List((5, 30, -5, -50), [], drawFocusRing = False)
        self.w.globalBacklogBox.backlogUpdateButton = Button((5, -45, -5, 25), 'refresh')
        self.w.globalBacklogBox.backlogTotalTitle = TextBox((5, -15, -5, 20), "4376 glyphs", alignment = 'center', sizeStyle = "small")
        
        self.w.groupsBox.groupsTitle = TextBox((5, 10, 150, 20), 'Groups')
        self.w.groupsBox.groupsList = List((5, 35, 200, -30), ["ChenRong_team", "ZhanGuodong_team"], drawFocusRing = False)
        self.w.groupsBox.addGroupsButton = Button((5, -25, 100, 20), '+')
        self.w.groupsBox.removeGroupsButton = Button((105, -25, 100, 20), '-')
        
        self.w.groupsBox.groupsBacklogTitle = TextBox((210, 10, 100, 20), 'Backlog')
        self.w.groupsBox.groupsBacklogList = List((210, 35, 90, -30), [], drawFocusRing = False)
        self.w.groupsBox.backlogTotalTitle = TextBox((210, -20, 90, 20), "376 glyphs", alignment = 'center', sizeStyle = "small")
        
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
        
    def launchInterface(self):
        self.w.open()