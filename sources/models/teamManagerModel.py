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

class User:

	"""
	{'backlog' : '# list of glyphs names', 'inProgress' : '', 'done' : } 
	"""

	__slots__ = 'manager', 'backlog', 'inProgress', 'done'

	def __init__(self, **kwargs):
		self.manager = False
		self.backlog = []
		self.inProgress = []
		self.done = []
		for k, v in kwargs.items():
			setattr(self, k, v)
		
	def __repr__(self):
		return str(self)

	def __str__(self):
		return f"<{self._asDict()}>"

	def _asDict(self):
		return {x:getattr(self, x) for x in self.__slots__}

	def export(self):
		return self._asDict()

	def _addGlyphs(self, glyphs:list = []):
		glyphs = set(self.backlog) | set(glyphs)
		self.backlog = sorted(list(glyphs))

	def _removeGlyphs(self, glyphs:list = []):
		def _recreateGlyphsList(glyphlist):
			backlog = set(glyphlist) - set(glyphs)
			glyphlist = sorted(list(backlog))
		for glyphlist in [self.backlog, self.inProgress, self.done]:
			_recreateGlyphsList(glyphlist)

	def moveGlyphsToInProgress(self, glyphs:list = []):
		"""
		Move a list of glyphs from backlog to inprogess
		"""
		glyphs = set(self.backlog) & set(glyphs)
		self.inProgress.extend(list(glyphs))
		self.backlog = list(set(self.backlog)-glyphs)

	def moveGlyphsToDone(self, glyphs:list = []):
		"""
		Move a list of glyphs from inprogress to done
		"""
		glyphs = set(self.inProgress) & set(glyphs)
		self.done.extend(list(glyphs))
		self.inProgress = list(set(self.inProgress)-glyphs)

	def moveBackGlyphsToBacklog(self, glyphs:list = []):
		pass

	@property
	def glyphs(self):
		return self.backlog + self.inProgress + self.done
	
class Group:

	def __init__(self, name):
		self._name = name
		self._users = set()
		self._backlog_glyphs = []

	def __iter__(self):
		for user in self.users:
			yield user

	def get(self, userName):
		"""
		return a user from its name

		>>> user = group.get("userName")
		"""
		if not hasattr(self, userName): return 
		return getattr(self, userName)

	# Properties
	# --------------------

	@property
	def name(self):
		return self._name

	@property
	def backlog_glyphs(self):
		return self._backlog_glyphs

	@property
	def users(self):
		return self._users

	@property
	def glyphs(self):
		glyphs = [x for user in self._users for x in getattr(self, user).glyphs]
		return glyphs

	@property
	def inProgress(self):
		return [x for user in self.users for x in getattr(self, user).backlog + getattr(self, user).inProgress]
	
	
	# Import / Export
	# --------------------

	def initGroup(self, data):
		self._backlog_glyphs = data.get("backlog_glyphs", [])
		for user in data.get("users", {}):
			self._addUser(user, data.get("users").get(user))

	def export(self):
		return self._asDict()
	
	def _asDict(self) -> dict:
		usersDict = {}
		for user in self._users:
			usersDict[user] = getattr(self, user).export()
		return {"backlog_glyphs": self._backlog_glyphs, 'users': usersDict}

	# Users
	# --------------------

	def _addUser(self, user, data:dict = {}):
		setattr(self, user, User(**data))
		self._users.add(user)

	def addUser(self, userName:str, data:dict = {}):
		if hasattr(self, userName): return
		self._addUser(userName, data)

	def removeUser(self, userName:str, appendUserGlyphsToBackLog:bool = False):
		"""
		Remove user from user name and return its glyphs

		appendUserGlyphsToBackLog allows to bring back in the backlog the user glyphs
		"""
		if not hasattr(self, userName): return
		userGlyphs = getattr(self, userName).export()
		delattr(self, userName)
		self._users.remove(userName)

		if appendUserGlyphsToBackLog:
			self._addBackLogGlyphs(userGlyphs.get("backlog", []))
		return userGlyphs

	def renameUser(self, oldname, newname):
		self.addUser(newname, self.removeUser(oldname))

	# Glyphs
	# --------------------

	def _addBackLogGlyphs(self, glyphs:list = []):
		glyphs = set(self._backlog_glyphs) | set(glyphs)
		self._backlog_glyphs = sorted(list(glyphs))

	def _removeBackLogGlyphs(self, glyphs:list = []):
		glyphs = set(self._backlog_glyphs) - set(glyphs)
		self._backlog_glyphs = sorted(list(glyphs))

	def addGlyphsToUser(self, userName:str, glyphs:list = []):
		if not hasattr(self, userName): return
		glyphsList = list(set(glyphs) & set(self._backlog_glyphs))
		getattr(self, userName)._addGlyphs(glyphsList)
		self._removeBackLogGlyphs(glyphsList)
		return getattr(self, userName).glyphs

	def removeGlyphsToUser(self, userName:str, glyphs:list = []):
		return NotImplemented

	def removeGlyphFromBacklog(self, glyphs: list):
		for glyph in glyphs:
			self.backlog_glyphs.remove(glyph)


class Groups:

	def add(self, name, data:dict = {}):
		"""
		Add group from its name and possibly initialized with its data as dict
	
		>>> data = {
				"backlog_glyphs": "abcdefgh",
				"users": { 
							"userName_1": {
										'backlog': 'ijkl',
										'inProgress': '',
										'done': '',
									},
							"userName_2": {	
										'backlog': 'mnop',
										'inProgress': '',
										'done': '',
									},
						},
				},
		>>> groups.add('groupName', data)
		"""
		setattr(self, name, Group(name))
		getattr(self, name).initGroup(data)

	def remove(self, name) -> dict:
		"""
		Remove group by its name

		>>> groups.remove('groupName')
		"""
		if not hasattr(self, name): return
		groupData =  getattr(self, name).export()
		delattr(self, name)
		return groupData

	def rename(self, oldName: str, newName: str):
		"""
		Rename group with old name and new name

		>>> groups.rename(oldName, newName)
		"""
		if not hasattr(self, oldName): return
		data = getattr(self, oldName).export()
		delattr(self, oldName)
		self.add(newName, data)

	def get(self, name:str) -> Group:
		"""
		return a group from its name

		>>> group = groups.get("groupName")
		"""
		if not hasattr(self, name): return
		return getattr(self, name)

	@property
	def list(self):
		return list(vars(self))

	def _asDict(self):
		groups = {}
		for x in vars(self):
			groups[x] = getattr(self, x).export()
		return groups

	def export(self):
		return self._asDict()
	
	def __iter__(self):
		for x in vars(self):
			yield getattr(self, x)

class BackLogGlyph:

	def __init__(self, glyphs:list = []):
		self._glyphs = list(set(glyphs))

	def add(self, other):
		self.__iadd__(other)

	def remove(self, other):
		self._glyphs = list(set(self._glyphs)-set(other))

	def __iadd__(self, other):
		self._glyphs += list(set(other)-set(self._glyphs))	

	def __repr__(self):
		return ' '.join(sorted(self._glyphs))

	def __str__(self):
		return repr(self)

	def __iter__(self):
		for x in self._glyphs:
			yield x

	def export(self):
		return self._glyphs

class Managers:

	def __init__(self, managers = []):
		self._managers = set(managers)

	def add(self, user):
		self._managers.add(user)

	def remove(self, user):
		self._managers.remove(user)

	def rename(self, oldname, newname):
		self._managers.remove(oldname)
		self._managers.add(newname)

	def export(self):
		return list(self._managers)

	def __contains__(self, value):
		return value in self._managers

	def __iter__(self):
		for x in self._managers:
			yield x

	def __bool__(self):
		return bool(self.managersList)

	@property
	def managersList(self):
		return sorted(list(self._managers))
	
class Team:

	__slots__ = '_backlog_glyphs', '_groups', '_managers'

	def __init__(self):
		self._backlog_glyphs = BackLogGlyph()
		self._groups = Groups()
		self._managers = Managers()

	# Properties
	# --------------------

	@property
	def backlog_glyphs(self):
		return self._backlog_glyphs

	@backlog_glyphs.setter
	def backlog_glyphs(self, value):
		self._backlog_glyphs = BackLogGlyph(list(value))

	@property
	def managers(self):
		return self._managers

	@managers.setter
	def managers(self, value):
		self._managers = Managers(value)

	@property
	def groups(self):
		return self._groups

	@property
	def allTeamsGlyphs(self):
		glyphs = [x for group in self._groups for x in group.glyphs]
		return glyphs

	# Import / Export
	# --------------------
	
	def initFromJSON(self, data:dict):
		"""
		Initialize team with dict

		>>> {
			"backlog_glyphs" : 'abcdefhj',
			"groups": {"group1": {"backlog_glyphs": "klmnop", "users": {"user1": {'backlog': 'qrst', 'inProgress': '', 'done': ''},"user2": {'backlog': 'uvwx', 'inProgress': '', 'done': ''}}},
					"group2": {"backlog_glyphs": "AZERTYU", "users": {"user3": {'backlog': 'WXCV', 'inProgress': '', 'done': ''}, "user4": {'backlog': 'QSDF', 'inProgress': '', 'done': ''}}}},
			}
		"""
		# if not data: return
		print("----")
		print(data)
		print("----")
		self._backlog_glyphs = BackLogGlyph(data.get("backlog_glyphs", []))
		self._managers = Managers(data.get("managers", []))
		for groupname in data.get("groups", []):
			groupData = data.get("groups")[groupname]
			self._groups.add(groupname, groupData)

	def _asDict(self):
		return {'backlog_glyphs': self.backlog_glyphs.export(),
		'groups' : self._groups.export(),
		'managers': self._managers.export()
		}

	def export(self):
		"""
		Return all team data as dict

		>>> {
			"backlog_glyphs" : 'abcdefhj',
			"groups": {"group1": {"backlog_glyphs": "klmnop", "users": {"user1": {'backlog': 'qrst', 'inProgress': '', 'done': ''},"user2": {'backlog': 'uvwx', 'inProgress': '', 'done': ''}}},
					"group2": {"backlog_glyphs": "AZERTYU", "users": {"user3": {'backlog': 'WXCV', 'inProgress': '', 'done': ''}, "user4": {'backlog': 'QSDF', 'inProgress': '', 'done': ''}}}},
			}
		"""
		return self._asDict()

	# Users
	# --------------------

	def getUserGlyphs(self, userName: str):
		"""
		return the user's glyphs from a user name
		"""
		for group in self.groups:
			if userName in group.users:
				return group.get(userName).glyphs

	def getUserGroup(self, userName: str):
		"""
		return the user's group from a user name
		"""
		for group in self.groups:
			if userName in group.users:
				return group.name

	# Groups
	# --------------------

	def addGlyphsToGroup(self, glyphs:list, group:str):
		glyphs = list(set(self._backlog_glyphs) & set(glyphs))
		self.groups.get(group)._addBackLogGlyphs(glyphs)
		self._backlog_glyphs.remove(glyphs)

	def get(self, name):
		"""
		return a group from its name

		>>> group = groups.get("groupName")
		"""
		return self.groups.get(name)

if __name__ == '__main__':

	teamjson = {
		"backlog_glyphs" : ['a', 'b', 'c', 'd', 'e', 'f', 'h', 'j'],
		"managerS": ['claire'],
		"groups": {
					"group1": {
								"backlog_glyphs": ['k', 'l', 'm', 'n', 'o', 'p'],
								"users": { 
											"ruosi": {	
														'manager': False,
														'backlog': ['q', 'r', 's', 't']
													},
											"Jeremie": {	
														'manager': True,
														'backlog': ['u', 'v', 'x'],
														'done': ['w']
													},
										},
								},
					"group2": {
								"backlog_glyphs": ["A", "Z", "E", "R", "T", "Y", "U"],
								"users": { 
											"claire": {
														'manager': True,
														'backlog': ['W', 'X', 'C', 'V']
													},
											"Robin": {	
														'manager': False,
														'backlog': ['Q', 'S', 'D', 'F']
													},
										},
								},
					},
		}

	team = Team()

	team.initFromJSON(teamjson)
	print(team.backlog_glyphs)

	####### BACKLOG #######
	#----------------------

	print("\n ---- BACKLOG ----")

	team.backlog_glyphs.add(['z'])
	print("add", team.backlog_glyphs)

	team.backlog_glyphs.remove(['d', 'f'])
	print("remove", team.backlog_glyphs)

	# team.backlog_glyphs = 'helloworld'
	# print("equal", team.backlog_glyphs)

	####### GROUPS #######
	#---------------------

	print("\n ---- GROUPS ----")

	team.groups.add("china")
	print("\nadd Group: ", team.export())

	team.groups.rename('group1', 'chenRongTeam')
	print("\nrename Group: ", team.export())

	groupData = team.groups.remove('group2')
	print("data from the removed group ->", groupData)
	print("\nremove Group: ", team.export())	

	team.addGlyphsToGroup(["a", "b", "c"], "china")

	####### GROUP #######	
	#--------------------

	print("\n ---- GROUP ----")

	for group in team.groups:
		print(group.backlog_glyphs)

	backlogChina = team.get('china').backlog_glyphs
	print("backlogChina ->", backlogChina)

	print("add user")
	team.get("chenRongTeam").addUser("Gaetan", {"backlog":["x", "y", "z"]})
	print("add User Gaetan", team.export())

	print("removeUser")
	ruosisGlyphs = team.get("chenRongTeam").removeUser("ruosi")
	print("remove User Ruosi", team.export())
	print("Ruosi's glyphs", ruosisGlyphs)

	print("add glyphs to user")
	team.get("chenRongTeam").addGlyphsToUser("Jeremie", ["n", "o", "p"])
	print("add glyphs to Jeremie", team.export())

	print("remove glyphs to user")
	print(team.get("chenRongTeam").removeGlyphsToUser("ruosi"))


	####### TEAM #######
	#-------------------

	print("\n ---- TEAM ----")

	glyphs = team.getUserGlyphs("Jeremie")	
	print("JeremieGlyphs ->", glyphs)

	totoGlyphs = team.getUserGlyphs("toto")	
	print("totoGlyphs ->", totoGlyphs)

	group = team.getUserGroup("Jeremie")	
	print("Jeremie's group is ->", group)

	allglyphs = team.allTeamsGlyphs
	print("All team glyphs are -> ", allglyphs)

	# help(team)

	####### USERS #######
	#--------------------

	print("\n ---- USER ----")

	team.get("chenRongTeam").get("Gaetan").moveGlyphsToInProgress(["z", "e"])
	print("move glyphs to in progress ->", team.export())

	team.get("chenRongTeam").get("Jeremie").moveGlyphsToInProgress(["o", "p"])
	print("move glyphs to in progress ->", team.export())

	team.get("chenRongTeam").get("Jeremie").moveGlyphsToDone(["o"])
	print("move glyphs to in progress ->", team.export())