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
from views import teamManagerView
from models import teamManagerModel
from utils import files

class TeamManagerController:

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.team = teamManagerModel.Team()
        self.interface = teamManagerView.TeamManagerUI(self)

    def launchInterface(self):
        self.loadTeam()
        self.interface.launchInterface()
        self.interface.setUI()
        self.getglobalbacklog()

    def saveTeam(self):
        teamDict = self.team.export()
        self.RCJKI.currentFont.saveTeam(teamDict)
        self.RCJKI.currentFont.save()

    def loadTeam(self):
        teamDict = self.RCJKI.currentFont.loadTeam()
        self.team.initFromJSON(teamDict)

    def getglobalbacklog(self):
        f = self.RCJKI.currentFont
        DCDone = set()
        for n in f.deepComponentSet:
            g = f[n]
            if g.designState == "DONE":
                if n.split("_") and len(n.split("_")) > 1:
                    DCDone.add(chr(int(n.split("_")[1], 16)))

        backlog = []
        for k, v in self.RCJKI.currentFont.dataBase.items():
            # v = v.strip("\n")
            dcuse = set(v)
            if not len(dcuse-DCDone):
                n = files.unicodeName(k)
                backlog.append(n)

        print('backlog', backlog)
        print('self.team.allTeamsGlyphs', self.team.allTeamsGlyphs)
        backlog = list(set(backlog)-set(self.team.allTeamsGlyphs))
        print('backlog', backlog)
        # print("backlog", backlog)
        # print("allTeamsGlyphs", self.team.allTeamsGlyphs)

        # print("self.team.allTeamsGlyphs", self.team.allTeamsGlyphs)
        self.team.backlog_glyphs = backlog
        print('backlog', self.team.backlog_glyphs)
        # return list(backlog)

    @property
    def globalBacklog(self):
        return [files.unicodeName2Char(x) for x in self.team.backlog_glyphs]

    def charListFromUnicodeNames(self, glyphs:list = []):
        return [files.unicodeName(x) for x in glyphs]

    def unicodeNamesFromCharList(self, glyphs:list = []):
        return [files.unicodeName2Char(x) for x in glyphs]
    

    ####### MANAGERS #######
    #----------------------

    def addManager(self, name):
        self.team.managers.add(name)

    def removeManager(self, name):
        self.team.managers.remove(name)

    def renameManager(self, oldname, newname):
        self.team.managers.rename(oldname, newname)

    def permissionToEditManagers(self):
        if not self.team.managers:
            return True
        elif self.RCJKI.mysql_userName in self.team.managers: 
            return True
        return False

    ####### GROUPS #######
    #----------------------

    @property
    def groups(self):
        return self.team.groups.list

    def addGroup(self, name):
        self.team.groups.add(name)

    def removeGroup(self, name):
        self.team.groups.remove(name)

    def renameGroup(self, oldname, newname):
        self.team.groups.rename(oldname, newname)

    def addGroupUser(self, groupname, username):
        self.team.get(groupname).addUser(username)

    def removeGroupUser(self, groupname, username):
        self.team.get(groupname).removeUser(username, appendUserGlyphsToBackLog = True)

    def renameUserFromGroup(self, oldname, newname, groupname):
        self.team.get(groupname).renameUser(oldname, newname)



