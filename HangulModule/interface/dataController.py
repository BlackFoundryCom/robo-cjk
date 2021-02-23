from vanilla import *
from vanilla.dialogs import putFile, getFile
import json
from imp import reload
from hm_resources import hangul
reload(hangul)

class UsersNames(Group):

    def __init__(self, hangulModule, interface):
        super().__init__((10, 100, -10, -10))
        self.hangulModule = hangulModule
        self.interface = interface

        self.initialTitle = TextBox((10, 10, 195, -10), "Initial")
        self.initialList = List((10, 30, 195, -10),
            self.hangulModule.userNames.initial,
            columnDescriptions = [dict(title = 'jamo', editable = False, width = 30),
                                dict(title = 'name', editable = True)],
            drawFocusRing = False,
            showColumnTitles = False,
            editCallback = self.initialListEditCallback
            )

        self.medialTitle = TextBox((200, 10, 195, -10), "Medial")
        self.medialList = List((200, 30, 195, -10),
            self.hangulModule.userNames.medial,
            columnDescriptions = [dict(title = 'jamo', editable = False, width = 30),
                                dict(title = 'name', editable = True)],
            drawFocusRing = False,
            showColumnTitles = False,
            editCallback = self.medialListEditCallback
            )

        self.finalTitle = TextBox((395, 10, 195, -10), "Final")
        self.finalList = List((395, 30, 195, -10),
            self.hangulModule.userNames.final,
            columnDescriptions = [dict(title = 'jamo', editable = False, width = 30),
                                dict(title = 'name', editable = True)],
            drawFocusRing = False,
            showColumnTitles = False,
            editCallback = self.finalListEditCallback
            )

    def initialListEditCallback(self, sender):
        self.hangulModule.userNames.initial = sender.get()

    def medialListEditCallback(self, sender):
        self.hangulModule.userNames.medial = sender.get()

    def finalListEditCallback(self, sender):
        self.hangulModule.userNames.final = sender.get()

    def setUI(self):
        self.initialList.set(self.hangulModule.userNames.initial)
        self.medialList.set(self.hangulModule.userNames.medial)
        self.finalList.set(self.hangulModule.userNames.final)


class GroupPosition(Group):

    def __init__(self, hangulModule, interface, position):
        super().__init__((0, 30, -0, -0))
        self.hangulModule = hangulModule
        self.interface = interface
        self.position = position

        self.currentGroup = None
        self.lock = False
        self.jamolock = False

        self.jamosTitles = TextBox(
            (410, 10, 200, -10), 
            'Jamos')
        self.jamos = []
        self.jamosList = List(
            (410, 30, 200, -80),
            self.jamos,
            columnDescriptions = [dict(title = 'sel', cell = CheckBoxListCell(), width = 30), 
                                dict(title = 'jamo', width = 50, editable = False), 
                                dict(title = 'groups', editable = False)],
            drawFocusRing = False,
            showColumnTitles = False,
            selectionCallback = self.jamosListSelectionCallback,
            # editCallback = self.jamosListEditCallback
            )
        
        self.jamoBelongsTo = TextEditor(
            (410, -80, 200, -00),
            ""
            )
        # self.groupContent = TextEditor(
        #     (380, 30, -0, -0),
        #     ""
        #     )
        self.setJamosList()

        self.groupsTitles = TextBox(
            (10, 10, 400, -10), 
            'Groups')
        self.groups = []
        self.groupsList = List(
            (10, 30, 400, -20),
            self.groups,
            columnDescriptions = [dict(title = 'groups', width = 160, editable = True), 
                                dict(title = 'jamos', editable = False)],
            drawFocusRing = False,
            showColumnTitles = False,
            selectionCallback = self.groupsListSelectionCallback,
            editCallback = self.groupsListEditCallback
            )
        self.addGroup = Button(
            (10, -20, 200, 20),
            "+",
            callback = self.addGroupCallback
            )
        self.removeGroup = Button(
            (210, -20, 200, 20),
            "-",
            callback = self.removeGroupCallback
            )
        self.setGroupsList()

    def setUI(self):
        self.setJamosList()
        self.setGroupsList()


    def lock(func):
        def wrapper(self, *args, **kwargs):
            try:
                print(self.lock)
                if self.lock: return
                # self.lock = True
                func(self, *args, **kwargs)
                # self.lock = False
            except Exception as e:
                raise e
            return wrapper

    def resetJamosList(func):
        def wrapper(self, *args, **kwargs):
            try:
                func(self, *args, **kwargs)
                self.setJamosList()
            except:pass
        return wrapper

    def resetGroupsList(func):
        def wrapper(self, *args, **kwargs):
            try:
                func(self, *args, **kwargs)
                self.setGroupsList()
            except:pass
        return wrapper

    
    # @resetGroupsList
    @resetJamosList
    # @lock
    def groupsListSelectionCallback(self, sender):
        if self.lock == True:
            return
        sel = self.groupsList.getSelection()
        if not sel:
            self.currentGroup = None
            # self.groupContent.set("")
            return
        self.currentGroup = self.groupsList.get()[sel[0]].get("groups")

        # groupContent = ''.join(self.hangulModule.groups[self.currentGroup].jamos)
        # self.groupContent.set(groupContent)
        # self.setGroupsList()

    def groupsListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            return
        oldName = self.currentGroup
        newName = sender.get()[sel[0]].get("groups")
        if newName == oldName: return
        self.hangulModule.groups.renameGroup(oldName, newName)
        self.currentGroup = newName
        # print(oldName, newName)
    
    @resetGroupsList
    @resetJamosList
    # @lock
    def addGroupCallback(self, sender):
        groups = self.hangulModule.getGroupsFor(self.position)
        index = 0
        while True:
            name = f"{self.position}Group_{str(index).zfill(2)}"
            if name not in self.hangulModule.groups.keys():
                break
            index += 1
        self.hangulModule.groups.newGroup(name, self.position)

    
    @resetGroupsList
    @resetJamosList
    # @lock
    def removeGroupCallback(self, sender):
        if self.currentGroup is None: return
        self.hangulModule.groups.removeGroup(self.currentGroup)
        self.currentGroup = None

    def setGroupsList(self):
        self.lock = True
        sel = self.groupsList.getSelection()
        self.groupsList.set([dict(groups = x, jamos = "".join(self.hangulModule.groups[x].jamos)) for x in self.hangulModule.getGroupsFor(self.position)])
        self.groupsList.setSelection(sel)
        self.lock = False

    def setJamosList(self):
        if self.currentGroup is not None:
            jamos2Groups = self.hangulModule.jamos2Groups(self.position)
            self.jamos = [dict(sel = self.currentGroup in v, jamo = k, groups = f"{len(v)} group") for k, v in jamos2Groups.items()]
        else:
            self.jamos = []
        self.jamosList.set(self.jamos)

    # @lock
    def jamosListSelectionCallback(self, sender):
        self.jamolock = True
        sel = sender.getSelection()
        if not sel:
            self.jamoBelongsTo.set("")
            return
        itemSel = sender.get()[sel[0]]
        jamo = itemSel.get("jamo")
        text = f"{jamo} belongs to:\n"
        for group in self.hangulModule.jamos2Groups(self.position)[jamo]:
            text += f"  • {group}\n"
        self.jamoBelongsTo.set(text)

        for item in sender.get():
            if not item.get("sel"):
                self.hangulModule.groups.removeJamo(self.currentGroup, item.get("jamo"))
            else:
                self.hangulModule.groups.addJamo(self.currentGroup, item.get("jamo"))

        self.setGroupsList()
        self.jamolock = False


class Groups(Group):

    def __init__(self, hangulModule, interface):
        super().__init__((0, 100, -0, -10))
        self.hangulModule = hangulModule
        self.interface = interface

        self.positionSegmentedButton = SegmentedButton(
            (10, 10, -10, 20),
            [dict(title = "Initial"),
            dict(title = "Medial"),
            dict(title = "Final")],
            callback = self.positionSegmentedButtonCallback
            )
        self.positionSegmentedButton.set(0)

        self.initial = GroupPosition(self.hangulModule, self.interface, "initial")
        self.medial = GroupPosition(self.hangulModule, self.interface, "medial")
        self.final = GroupPosition(self.hangulModule, self.interface, "final")

        self.medial.show(False)
        self.final.show(False)

    def positionSegmentedButtonCallback(self, sender):
        for i, x in enumerate([self.initial, self.medial, self.final]):
            x.show(i == sender.get())


class Combinations(Group):

    def __init__(self, hangulModule, interface):
        super().__init__((10, 100, -10, -10))
        self.hangulModule = hangulModule
        self.interface = interface

        self.generateCombinationsButton = Button(
            (10, 10,-10,20),
            "Generate Combinations",
            callback = self.generateCombinationsButtonCallback
            )

        self.combinationsList = List(
            (10, 40, 150, -10),
            [],
            selectionCallback = self.combinationsListSelectionCallback
            )

        i = 40

        self.initialTitle = TextBox(
            (170, i, 200, 20),
            "Initial"
            )
        i += 20
        self.initialGroup = PopUpButton(
            (170, i, 150, 20),
            []
            )
        self.initialVariant = EditText(
            (330, i, 100, 20),
            ''
            )
        i += 40


        self.medialTitle = TextBox(
            (170, i, 200, 20),
            "Medial"
            )
        i += 20
        self.medialGroup = PopUpButton(
            (170, i, 150, 20),
            []
            )
        self.medialVariant = EditText(
            (330, i, 100, 20),
            ''
            )
        i += 40


        self.finalTitle = TextBox(
            (170, i, 200, 20),
            "Final"
            )
        i += 20
        self.finalGroup = PopUpButton(
            (170, i, 150, 20),
            []
            )
        self.finalVariant = EditText(
            (330, i, 100, 20),
            ''
            )
        i += 40

    def generateCombinationsButtonCallback(self, sender):
        self.hangulModule.generateSyllableCombination()
        self.setUI()
        print(self.hangulModule.combinations)

    def combinationsListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            return
        combinationName = sender.get()[sel[0]]
        combination = self.hangulModule.combinations.get(combinationName)
        print("\n", combinationName, "\n")
        print(combination)
        self.initialGroup.setItem(combination.initial.group)
        self.initialVariant.set(combination.initial.variant)
        self.medialGroup.setItem(combination.medial.group)
        self.medialVariant.set(combination.medial.variant)
        if combination.get('final'):
            self.finalGroup.setItem(combination.final.group)
            self.finalVariant.set(combination.final.variant)
        else:
            self.finalVariant.set("None")

    def setUI(self):
        self.combinationsList.set(self.hangulModule.combinations.names())
        # set the list of possible versions
        self.initialGroup.setItems(list(self.hangulModule.groups.initial))
        self.medialGroup.setItems(list(self.hangulModule.groups.medial))
        self.finalGroup.setItems(list(self.hangulModule.groups.final))


class DataController:

    def __init__(self, hangulModule):
        self.hangulModule = hangulModule
        self.w = Window((620, 600), 'Hangul Module - data controller')

        self.w.loadHangulModuleData = Button(
            (10, 10, 300, 20), 
            'Load',
            sizeStyle = "regular",
            callback = self.loadHangulModuleDataCallback
            )

        self.w.saveHangulModuleData = Button(
            (310, 10, 300, 20), 
            'Save',
            sizeStyle = "regular",
            callback = self.saveHangulModuleDataCallback
            )

        self.w.loadCharactersComposition = Button(
            (10, 40, 300, 20), 
            'Load characters composition',
            sizeStyle = "regular"
            )

        self.w.saveCharactersComposition = Button(
            (310, 40, 300, 20), 
            'Save characters composition',
            sizeStyle = "regular"
            )

        self.w.stepsSegmentedButton = SegmentedButton(
            (10, 70, -10, 20),
            [dict(title = "User names"),
            dict(title = "Groups"),
            dict(title = "Combinations")],
            callback = self.stepsSegmentedButtonCallback
            )

        self.w.stepsSegmentedButton.set(0)

        self.w.userNames = UsersNames(self.hangulModule, self)
        self.w.groups = Groups(self.hangulModule, self)
        self.w.combinations = Combinations(self.hangulModule, self)

        self.w.groups.show(False)
        self.w.combinations.show(False)

    def launch(self):
        self.w.open()

    def stepsSegmentedButtonCallback(self, sender):
        for i, x in enumerate([self.w.userNames, self.w.groups, self.w.combinations]):
            x.show(i == sender.get())

    def saveHangulModuleDataCallback(self, sender):
        data = self.hangulModule.concatenateData()
        path = putFile()
        if not path.endswith(".json"):
            path += ".json"
        with open(path, 'w', encoding = 'utf-8') as file:
            file.write(json.dumps(data))

    def loadHangulModuleDataCallback(self, sender):
        paths = getFile()
        path = paths[0]
        with open(path, 'r', encoding = 'utf-8') as file:
            data = json.load(file)
        self.hangulModule.initializeWithExternalData(data)
        for e in ['userNames', 'combinations']:
            getattr(self.w, e).setUI()
        for pos in ['initial', 'medial', 'final']:
            getattr(self.w.groups, pos).setUI()

