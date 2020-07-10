
"""
List de glyph backlog

Team -> Groups -> Users -> List of glpyhs
			   \> List Glyphs

Créer des groupes
ajouter des utilisateur au group
assigner des glyph a un group
assigner des glyphs du group a un de ses users

"""


class User:

	def __init__(self, username, groupname, glyphs = []):
		self._name = username
		self._group = groupname
		self._glyphs = set(glyphs)

	@property
	def name(self):
		return self._name

	@name.setter
	def name(self, name:str):
		self._name = name
	
	@property
	def group(self):
		return self._group

	@group.setter
	def group(self, groupname:str):
		self._group = groupname

	@property
	def glyphs(self):
		return self._glyphs
	
	@glyphs.setter
	def glyphs(self, value):
		self._glyphs = self._glyphs.union(set(value))

	def __bool__(self):
		return bool(self.glyphs)

class Group:

	def __init__(self, groupname, glyphs = [], usersnames:list = []):
		self._groupname = groupname
		self._glyphs = set(glyphs)
		for name in set(usersnames):
			self.addUser(name)

	@property
	def groupname(self):
		return self._groupname

	@groupname.setter
	def groupname(self, value):
		self._groupname = value

	@property
	def glyphs(self):
		return self._glyphs
	
	@glyphs.setter
	def glyphs(self, value):
		if isinstance(value, str):
			self._glyphs.add(value)
		elif isinstance(value, list):
			self._glyphs = self._glyphs.union(set(value))

	def addUser(self, name, glyphs = []):
		setattr(self, name, User(name, self.groupname, glyphs))

	def removeUser(self, name):
		glyphs = getattr(self, name).glyphs
		delattr(self, name)
		return glyphs

class Groups:

	def addGroup(self, groupname, glyphs):
		setattr(self, groupname, Group(groupname, glyphs))

class Team:

	def __init__(self, groups, backlog_glyphs):
		self._backlog_glyphs = set(backlog_glyphs)
		self._groups = Groups()
		for group in groups:
			self.addGroup(group)

	@property
	def backlog_glyphs(self):
		return self._backlog_glyphs
	
	@backlog_glyphs.setter
	def backlog_glyphs(self, value):
		if isinstance(value, str):
			self._backlog_glyphs.add(value)
		elif isinstance(value, list):
			self._backlog_glyphs = self._backlog_glyphs.union(set(value))

	def addGroup(self, groupname, glyphs = []):
		self._groups.addGroup(groupname, glyphs)

	def removeGroup(self, groupname):
		pass

	def initFromJSON(self, data):
		self.backlog_glyphs = data.get()


if __name__ == '__main__':

	teamjson = {
		"backlog_glyphs" : 'abcdefhj',
		"groups": {
					"group1": {
								"glyphs": "klmnop",
								"users": { 
											"user1": {
														'glyphs': 'qrst'
													},
											"user2": {	
														'glyphs': 'uvwx'
													},
										},
								},
					},
		}

	team = Team()

	team.initFromJSON(teamjson)
















































