from imp import reload
from interface import dataController
from hm_resources import hangul
import copy
reload(dataController)
reload(hangul)

class Repr:

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(vars(self))

class JamoGroup(Repr):

    def __init__(self, name, position, jamos):
        self.name = name
        self.position = position
        self.jamos = jamos

    def add(self, jamo):
        self.jamos.add(jamo)

    def remove(self, jamo):
        self.jamos.remove(jamo)

    def __sub__(self, other):
        return set(other) - self.jamos

    def todict(self):
        return {"name":self.name,
        "position":self.position,
        "jamos":list(self.jamos)}
        # return {x:getattr(self, x) for x in vars(self)}


class GroupRelation(Repr):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __iter__(self):
        for x in vars(self):
            yield x, getattr(self, x)

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)

    def get(self, item):
        return self[item]

    def toDict(self):
        return {x:getattr(self, x).toDict() for x in vars(self)}

class GroupsVariants(Repr):

    def __init__(self, group, variant):
        self.group = group
        self.variant = variant

    def toDict(self):
        return {x:getattr(self, x) for x in vars(self)}

class GroupController:

    initial = hangul.Jamos.initial
    medial = hangul.Jamos.medial
    final = hangul.Jamos.final

    def __iter__(self):
        for x in vars(self):
            yield getattr(self, x)

    def keys(self):
        for x in vars(self):
            yield x

    def __getitem__(self, item):
        if not hasattr(self, item):
            return
        return getattr(self, item)

    def newGroup(self, name:str, position:str, jamos=None):
        if hasattr(self, name):
            return None
        if jamos is None:
            jamos = set()
        else:
            jamos = set(jamos)
        setattr(self, name, JamoGroup(name, position, jamos))

    def removeGroup(self, name:str):
        if not hasattr(self, name):
            return
        delattr(self, name)

    def renameGroup(self, oldName, newName):
        if not hasattr(self, oldName):
            return
        jamos = copy.deepcopy(getattr(self, oldName).jamos)
        position = getattr(self, oldName).position
        delattr(self, oldName)
        self.newGroup(newName, position)
        getattr(self, newName).jamos = jamos

    def addJamo(self, groupName:str, jamo:str):
        groupPosition = getattr(self, groupName).position
        if jamo in getattr(self, groupPosition):
            return
        getattr(self, groupName).add(jamo)

    def removeJamo(self, groupName:str, jamo:str):
        if not hasattr(self, groupName): 
            return
        if getattr(self, groupName) - jamo:
            return
        getattr(self, groupName).remove(jamo)

    def _getGroupsFromPosition(self, position):
        return [x for x in vars(self) if getattr(self, x).position == position]

    @property
    def initial(self):
        return self._getGroupsFromPosition("initial")

    @property
    def medial(self):
        return self._getGroupsFromPosition("medial")

    @property
    def final(self):
        return self._getGroupsFromPosition("final")

    def export(self):
        groups = {}
        for position in ["initial", "medial", "final"]:
            groups[position] = {}
            for groupname in getattr(self, position):
                groups[position][groupname] = getattr(self, groupname).todict()
        return groups

    def initWithDict(self, groupsdict:dict = {}):
        for position, groups in groupsdict.items():
            for group, desc in groups.items():
                self.newGroup(desc["name"], position, desc["jamos"])

class Combinations(Repr):

    _indexes = {}

    def index(self, group):
        if group not in self._indexes:
            self._indexes[group] = 1
        else:
            self._indexes[group] += 1
        return "var%s"%(str(self._indexes[group]).zfill(2))

    def add(self, name, initial, medial, final = None):
        if final is None:
            setattr(self, name, GroupRelation(
                initial = GroupsVariants(list(initial)[0], list(initial)[1]),
                medial = GroupsVariants(list(medial)[0], list(medial)[1]),
                ))
        else:
            setattr(self, name, GroupRelation(
                initial = GroupsVariants(list(initial)[0], list(initial)[1]),
                medial = GroupsVariants(list(medial)[0], list(medial)[1]),
                final = GroupsVariants(list(final)[0], list(final)[1]),
                ))

    def names(self):
        return list(vars(self))

    def rename(self, oldname, newname):
        pass

    def remove(self, item):
        delattr(self, item)

    def __getitem__(self, item):
        return getattr(self, item)

    def get(self, item):
        return self[item]

    def export(self):
        return {k: getattr(self, k).toDict() for k in vars(self)}

    def initWithDict(self, combinationsDict:dict = {}):
        # return a dict for each position in a combo.
        # The dict has 2 values, one for the group name, one for the variant name
        for k, v in combinationsDict.items():
            if 'final' in v:
                self.add(k, v['initial'].values(),
                    v['medial'].values(), v['final'].values())
            else:
                self.add(k, v['initial'].values(), v['medial'].values())

class HangulModule:

    def __init__(self):
        self.userNames = UserNames()
        self.groups = GroupController()
        self.dataControllerInterface = dataController.DataController(self)
        self.characterComposition = hangul.Composition()
        self.combinations = Combinations()

    def launchDataControllerInterface(self):
        self.dataControllerInterface.launch()

    def _jamos2Groups(self, jamos):
        ij2g = {}
        for jamo in jamos:
            if jamo not in ij2g:
                ij2g[jamo] = set()
            for group in self.groups:
                if jamo in group.jamos:
                    ij2g[jamo].add(group.name)
        return ij2g

    def jamos2Groups(self, position):
        if position == "initial":
            return self._jamos2Groups(hangul.Jamos.initial)
        elif position == "medial":
            return self._jamos2Groups(hangul.Jamos.medial)
        else:
            return self._jamos2Groups(hangul.Jamos.final)

    def getGroupsFor(self, position):
        if position == 'initial':
            return self.groups.initial
        elif position == 'medial':
            return self.groups.medial
        else:
            return self.groups.final

        

    def concatenateData(self):
        usernames = self.userNames.export()
        groups = self.groups.export()

        combinations = self.combinations.export()
        print("---")
        print(combinations)
        print("---")
        data = {"userNames":usernames,
                "groups": groups,
                "combinations": combinations
                }
        return data

    def initializeWithExternalData(self, data):
        for k, value in data.items():
            # if k == "groups":continue
            getattr(self, k).initWithDict(value)
            # if k == "userNames":
            #     self.userNames.initWithDict(value)
            # elif k == "groups":
            #     self.groups.initWithDict(value)

    # @property
    # def initialJamos2Groups(self):
    #   return self.jamos2Groups(hangul.Jamos.initial, self.groups.initial)

    # @property
    # def medialJamos2Groups(self):
    #   return self.jamos2Groups(hangul.Jamos.medial, self.groups.medial)

    # @property
    # def finalJamos2Groups(self):
    #   return self.jamos2Groups(hangul.Jamos.final, self.groups.final)

    def generateSyllableCombination(self):
        initialGroups = self.groups.initial
        medialGroups = self.groups.medial
        finalGroups = self.groups.final
        combinations = []

        combinationsIndex = 0
        for init_index, initial in enumerate(initialGroups):
            for medi_index, medial in enumerate(medialGroups):
                self.combinations.add(
                    "combo%s"%str(combinationsIndex).zfill(2),
                    initial,
                    medial
                    )
                combinationsIndex+=1

                for fina_index, final in enumerate(finalGroups):
                    self.combinations.add(
                        "combo%s"%str(combinationsIndex).zfill(2),
                        initial,
                        medial,
                        final
                        )
                    combinationsIndex+=1

    # def jamosDefinitions(self):
    #   jamos = JamosDefinition()
    #   for group in self.groups:
    #       groupName, groupItems = group
    #       groupPosition = groupItems.position

    #       for jamo in groupItems.jamos:
    #           jamos.add(jamo, self.userNames[jamo], groupName)
                
    #           for combination in self.combinations:
    #               for position, relation in combination:
    #                   if relation.group == groupName:
    #                       jamos[jamo].addVariant(position)
    #   return jamos

class UserNames:

    def __init__(self):
        self.initial, self.medial, self.final = [], [], []

        def fillPositionJamos(jamos, position):
            for jamo in jamos:
                code = hex(ord(jamo))[2:].upper()
                position.append(dict(jamo = jamo, name = f"DC_{code}_00"))

        fillPositionJamos(hangul.Jamos.initial, self.initial)
        fillPositionJamos(hangul.Jamos.medial, self.medial)
        fillPositionJamos(hangul.Jamos.final, self.final)

    def initWithDict(self, usernames:dict = {}):
        print(usernames)
        for k, v in usernames.items():
            desc = [dict(jamo = x, name = y) for x, y in v.items()]
            setattr(self, k, desc)

    def export(self):
        usernames = {}
        for x in vars(self):
            usernames[x] = {y["jamo"]:y["name"] for y in getattr(self, x)}
        return usernames

