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

class TeamManagerController:

	def __init__(self, RCJKI):
		self.RCJKI = RCJKI
		self.team = teamManagerModel.Team()
		self.interface = teamManagerView.TeamManagerUI(self)

	def launchInterface(self):
		self.interface.launchInterface()