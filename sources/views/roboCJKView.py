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
from vanilla.dialogs import getFolder, putFile
from mojo.UI import OpenGlyphWindow, AllWindows
from defconAppKit.windows.baseWindow import BaseWindowController
from views import canvasGroups
from mojo.canvas import CanvasGroup
import mojo.drawingTools as mjdt
# from lib.doodleDocument import DoodleDocument
from AppKit import NSFont
from imp import reload
from utils import decorators, files
reload(decorators)
reload(files)
reload(canvasGroups)
from models import font
reload(font)
from views import sheets
reload(sheets)



import os, json

gitCoverage = decorators.gitCoverage

from mojo.roboFont import *

EditButtonImagePath = os.path.join(os.getcwd(), "resources", "EditButton.pdf")

class SmartTextBox(TextBox):
    def __init__(self, posSize, text="", alignment="natural", 
        selectable=False, callback=None, sizeStyle=40.0,
        red=0,green=0,blue=0, alpha=1.0):
        super(SmartTextBox, self).__init__(posSize, text=text, alignment=alignment, 
            selectable=selectable, sizeStyle=sizeStyle)
        
    def _setSizeStyle(self, sizeStyle):
        value = sizeStyle
        self._nsObject.cell().setControlSize_(value)
        font = NSFont.systemFontOfSize_(value)
        self._nsObject.setFont_(font)

class EditingSheet():

    def __init__(self, controller, RCJKI):
        self.RCJKI = RCJKI
        self.c = controller
        self.w = Sheet((240, 80), self.c.w)
        self.char =  self.c.w.char.get()
        self.w.char = SmartTextBox(
            (0, 0, 80, -0),
            self.char,
            sizeStyle = 65,
            alignment = "center"
            )
        self.w.editField = TextEditor(
            (80, 0, -0, -20),
            "".join(self.RCJKI.dataBase[self.char])
            )
        self.w.closeButton = Button(
            (80, -20, -0, -0),
            "Close",
            sizeStyle = "small",
            callback = self.closeCallback
            )
        self.w.open()

    def closeCallback(self, sender):
        components = list(self.w.editField.get())
        self.RCJKI.dataBase[self.char] = components
        self.c.w.componentList.set(components)
        self.RCJKI.exportDataBase()
        self.w.close()

class CharacterWindow:

    filterRules = [
        "All",
        "In font",
        "Not in font",
        "Can be designed with current deep components",
        "Can't be designed with current deep components",
        # "Custom list"
        ]

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.w = FloatingWindow(
            (240, 100),
            minSize = (240, 120),
            maxSize = (240, 800),
            closable = False,
            textured = True,
            )
        self.w.backgroundCanvas = CanvasGroup((0, 0, -0, -0), delegate = self)
        self.filter = 0
        self.w.filter = PopUpButton(
            (0, 0, -0, 20),
            self.filterRules,
            callback = self.filterCallback,
            sizeStyle = "mini"
            )
        self.w.component = SmartTextBox(
            (0, 16, 80, -0),
            "",
            sizeStyle = 65,
            alignment = "center"
            )
        self.w.charactersList = List(
            (80, 16, 40, -0), 
            [],
            selectionCallback = self.charactersListSelectionCallback,
            doubleClickCallback = self.charactersListDoubleClickCallback,
            drawFocusRing = False
            )
        self.w.previewCheckBox = CheckBox(
            (130, 20, -10, 20),
            'Preview',
            value = False,
            sizeStyle = "small",
            callback = self.previewCheckBoxCallback
            )
        self.w.previewCheckBox.show(False)

    def filterCallback(self, sender):
        self.filter = sender.get()
        self.filterCharacters()

    def filterCharacters(self):
        l = []

        if self.filter == 0:
            l = list(self.relatedChars)
            title = "Related Characters"

        elif self.filter in [1, 2]:
            names = [files.unicodeName(c) for c in self.relatedChars]
            if self.filter == 1:
                result = set(names) & set(self.RCJKI.currentFont.characterGlyphSet)
            else:
                result = set(names) - set(self.RCJKI.currentFont.characterGlyphSet)
            title = self.filterRules[self.filter]
            l = [chr(int(n[3:], 16)) for n in result]

        elif self.filter in [3, 4]:
            DCSet = set(self.RCJKI.currentFont.deepComponentSet)
            for c in self.relatedChars:
                compo = ["DC_%s_00"%hex(ord(v))[2:].upper() for v in self.RCJKI.dataBase[c]]
                inside = len(set(compo) - DCSet) == 0
                if self.filter == 3 and inside:
                    l.append(c)
                elif self.filter == 4 and not inside:
                    l.append(c)
            if self.filter == 3:
                result = set([files.unicodeName(c) for c in l]) - set(self.RCJKI.currentFont.characterGlyphSet)
                l = [chr(int(n[3:], 16)) for n in result]
            title = " ".join(self.filterRules[self.filter].split(' ')[:3])

        self.w.charactersList.set(l)
        self.w.setTitle("%s %s"%(len(l), title))

    def setUI(self):
        self.relatedChars = set()
        try:
            _, code, _ = self.RCJKI.currentGlyph.name.split("_") 
            char = chr(int(code, 16))
            for k, v in self.RCJKI.dataBase.items():
                if char in v:
                    self.relatedChars.add(k)
        except: pass
        self.filterCharacters()
        self.w.component.set(char)

    def open(self):
        self.w.open()

    def close(self):
        self.w.close()

    def charactersListSelectionCallback(self, sender):
        self.w.previewCheckBox.show(self.filter == 1)

        sel = sender.getSelection()
        if not sel:
            return
        char = sender.get()[sel[0]]
        if self.filter in [0, 3]:
            if files.unicodeName(char) in self.RCJKI.currentFont.characterGlyphSet:
                self.w.previewCheckBox.show(True)

    def charactersListDoubleClickCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        char = sender.get()[sel[0]]
        name = files.unicodeName(char)
        font = self.RCJKI.currentFont
        try:
            font[name]
        except:
            font.newGlyph("characterGlyph", name)
        finally:
            g = font[name]._RGlyph
            if font.locker.isLocked(g) == None or font.locker.isLocked(g) == self.RCJKI.user:
                self.RCJKI.gitEngine.pull()
                font.getGlyphs()
                font.locker.lock(font[name])
                OpenGlyphWindow(font[name]._RGlyph)
        
    def previewCheckBoxCallback(self, sender):
        pass

class ComponentWindow():

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.previewGlyph = None
        self.w = FloatingWindow(
            (240, 80),
            "Composition Rules",
            closable = False,
            textured = True,
            )
        self.w.char = SmartTextBox(
            (0, 0, 80, -0),
            "",
            sizeStyle = 65,
            alignment = "center"
            )
        self.w.editButton = ImageButton(
            (0, -15, 15, -0),
            EditButtonImagePath,
            bordered = False,
            callback = self.editButtonCallback
            )
        self.w.componentList = List(
            (80, 0, 40, -0), 
            [],
            selectionCallback = self.componentListCallback
            )
        self.w.variantComponentList = List(
            (120, 0, 40, -0), 
            [],
            selectionCallback = self.variantComponentListCallback,
            doubleClickCallback = self.variantComponentListdoubleClickCallback
            )
        self.w.canvas2 = CanvasGroup(
            (160, 0, -0, -0), 
            delegate = self
            )

    def open(self):
        self.w.open()

    def close(self):
        self.w.close()

    def setUI(self):
        char = chr(int(self.RCJKI.currentGlyph.name[3:], 16))
        if char in self.RCJKI.dataBase:
            self.w.componentList.set(self.RCJKI.dataBase[char])
        self.w.char.set(char)

    def editButtonCallback(self, sender):
        EditingSheet(self, self.RCJKI)

    def draw(self):
        if self.previewGlyph is None: return
        mjdt.save()
        mjdt.translate(20, 25)
        mjdt.scale(.04)
        mjdt.fill(0, 0, 0, 1)
        for i, d in enumerate(self.previewGlyph):
            for atomicInstanceGlyph in d.values():
                mjdt.drawGlyph(atomicInstanceGlyph[0]) 
        mjdt.restore()

    def componentListCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        char = sender.get()[sel[0]]
        self.code = files.normalizeUnicode(hex(ord(char))[2:].upper())
        dcName = "DC_%s_00"%self.code
        if dcName not in self.RCJKI.currentFont.deepComponentSet: 
            self.w.variantComponentList.set([])
            return
        index = self.RCJKI.currentFont.deepComponentSet.index(dcName)
        l = ["00"]
        i = 1
        while True:
            name = "DC_%s_%s"%(self.code, str(i).zfill(2))
            if not name in self.RCJKI.currentFont.deepComponentSet:
                break
            l.append(str(i).zfill(2))
            i += 1
        self.w.variantComponentList.set(l)

    def variantComponentListCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        index = sender.get()[sel[0]]
        self.deepComponentName = "DC_%s_%s"%(self.code, index)
        glyph = self.RCJKI.currentFont[self.deepComponentName]
        self.previewGlyph = glyph.generateDeepComponent(
                glyph, 
                preview=False,
                )
        self.w.canvas2.update()

    def variantComponentListdoubleClickCallback(self, sender):
        self.RCJKI.currentGlyph.addDeepComponentNamed(self.deepComponentName)
        self.RCJKI.updateDeepComponent()


class RoboCJKView(BaseWindowController):
    
    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.prevGlyphName = None
        self.w = Window(
            (620, 600), 
            'RoboCJK'
            )

        self.w.loadProjectButton = Button(
            (10, 10, 200, 20), 
            "Load Git Repo", 
            callback = self.loadProjectButtonCallback,
            )
        self.w.saveProjectButton = Button(
            (210, 10, 200, 20), 
            "Save project", 
            callback = self.saveProjectButtonCallback,
            )
        self.w.saveProjectButton.enable(False)

        self.w.newProjectButton = Button(
            (410, 10, 200, 20), 
            "New project", 
            callback = self.newProjectButtonCallback,
            )
        self.w.newProjectButton.enable(False)

        self.w.fontInfos = Button(
            (210, 40, 200, 20), 
            "Fonts Infos", 
            callback = self.fontInfosCallback,
            )
        self.w.fontInfos.enable(False)

        self.w.pdfProoferButton = Button(
            (410, 40, 200, 20), 
            "PDF Proofer", 
            callback = self.pdfProoferButtonCallback,
            )

        self.w.rcjkFiles = PopUpButton(
            (10, 40, 200, 20),
            [],
            callback = self.rcjkFilesSelectionCallback
            )

        self.w.generateFontButton = Button(
            (10, 70, 200, 20),
            "generateFont",
            callback = self.generateFontButtonCallback,
            )
        self.w.generateFontButton.enable(False)

        self.w.lockerInfoTextBox = TextBox(
            (210, 70, 200, 20),
            "",
            alignment='center'
            )

        self.w.atomicElementSearchBox = SearchBox(
            (10, 130, 200, 20),
            callback = self.atomicElementSearchBoxCallback
            )
        self.w.atomicElement = List(
            (10, 150, 200, 200),
            [],
            allowsMultipleSelection = False,
            doubleClickCallback = self.GlyphsListDoubleClickCallback,
            editCallback = self.GlyphsListEditCallback,
            selectionCallback = self.GlyphsListSelectionCallback, 
            )
        self.w.newAtomicElement = Button(
            (10, 350, 200, 20),
            "New AE",
            callback = self.newAtomicElementCallback
            )
        self.w.atomicElementPreview = canvasGroups.GlyphPreviewCanvas(
            (10, 372, 200, -0),
            self.RCJKI,
            glyphType = "atomicElement")

        self.w.deepComponentSearchBox = SearchBox(
            (210, 130, 200, 20),
            callback = self.deepComponentSearchBoxCallback
            )
        self.w.deepComponent = List(
            (210, 150, 200, 200),
            [],
            allowsMultipleSelection = False,
            doubleClickCallback = self.GlyphsListDoubleClickCallback,
            editCallback = self.GlyphsListEditCallback,
            selectionCallback = self.GlyphsListSelectionCallback, 
            )
        self.w.newDeepComponent = Button(
            (210, 350, 200, 20),
            "New DC",
            callback = self.newDeepComponentCallback
            )
        self.w.deepComponentPreview = canvasGroups.GlyphPreviewCanvas(
            (210, 372, 200, -0),
            self.RCJKI,
            glyphType = "deepComponent")

        self.w.characterGlyphSearchBox = SearchBox(
            (410, 130, 200, 20),
            callback = self.characterGlyphearchBoxCallback
            )
        self.w.characterGlyph = List(
            (410, 150, 200, 200),
            [],
            allowsMultipleSelection = False,
            doubleClickCallback = self.GlyphsListDoubleClickCallback,
            editCallback = self.GlyphsListEditCallback,
            selectionCallback = self.GlyphsListSelectionCallback, 
            )
        self.w.newCharacterGlyph = Button(
            (410, 350, 200, 20),
            "New CG",
            callback = self.newCharacterGlyphCallback
            )
        self.w.characterGlyphPreview = canvasGroups.GlyphPreviewCanvas(
            (410, 372, 200, -0),
            self.RCJKI,
            glyphType = "characterGlyph")
        
        self.lists = [
            self.w.atomicElement,
            self.w.deepComponent,
            self.w.characterGlyph
        ]
        self.RCJKI.toggleObservers()
        self.w.bind('close', self.windowCloses)
        self.w.open()

    def pdfProoferButtonCallback(self, sender):
        # self.RCJKI.pdf = PDFProofer.PDFEngine(self)
        self.RCJKI.pdf.interface.open()

    def atomicElementSearchBoxCallback(self, sender):
        name = str(sender.get())
        l = files._getFilteredListFromName(self.currentFont.atomicElementSet, name)
        if not l:
            l = self.currentFont.atomicElementSet

        self.w.deepComponent.setSelection([])
        self.w.characterGlyph.setSelection([])
        self.w.atomicElement.set(l)

    def deepComponentSearchBoxCallback(self, sender):
        name = str(sender.get())
        l = files._getFilteredListFromName(self.currentFont.deepComponentSet, name)
        if not l:
            l = self.currentFont.deepComponentSet

        self.w.atomicElement.setSelection([])
        self.w.characterGlyph.setSelection([])
        self.w.deepComponent.set(l)

    def characterGlyphearchBoxCallback(self, sender):
        try:
            name = files.unicodeName(sender.get())
        except:
            name = str(sender.get())
        l = files._getFilteredListFromName(self.currentFont.characterGlyphSet, name)
        if not l:
            l = self.currentFont.characterGlyphSet

        self.w.atomicElement.setSelection([])
        self.w.deepComponent.setSelection([])
        self.w.characterGlyph.set(l)

    def windowCloses(self, sender):
        for w in AllWindows():
            try:
                w.close()
            except:
                pass
        if self.RCJKI.get('currentFont'):
            if self.currentFont is not None:
                self.currentFont.save()
            self.RCJKI.toggleWindowController(False)
        self.RCJKI.toggleObservers(forceKill=True)

    def fontInfosCallback(self, sender):
        sheets.FontInfosSheet(self.RCJKI, self.w, (220, 225))

    def generateFontButtonCallback(self, sender):
        # axis = self.RCJKI.currentFont._RFont.lib['robocjk.fontVariations']
        # print(axis)

        """
        - Decompose les DC
        - Crée un glyph pour chaque DC
        - Dico équivalence reglage DC, glyphName
        - Parse les CG
        - import les DC comme Compo normal + offset
        """
        
        f = NewFont(showUI = False)

        deepCompo2Compo = {}
        for n in self.RCJKI.currentFont.characterGlyphSet:
            g = self.RCJKI.currentFont[n]
            g.computeDeepComponents()
            f.newGlyph(n)
            f[n].width = g.width

            # print(g.computedDeepComponentsVariation)
            # print("\n")
            # print(g.computedDeepComponents)
            # print("\n")
            # print("\n")

            for i, e in enumerate(g.computedDeepComponents):
                index = 0

                print(e, '\n')
                
                while True:
                    name = list(e.keys())[0] + "_" + str(index).zfill(2)
                    if name not in deepCompo2Compo.keys():
                        break
                    index += 1
                # if e in deepCompo2Compo: continue
                dc = RGlyph()
                dc.width = g.width
                for dcCoord, l in e.values():
                    for dcAtomicElements in l:
                        for atomicInstanceGlyph, _, _ in dcAtomicElements.values():
                            for c in atomicInstanceGlyph:
                                dc.appendContour(c)
                dc.name = name

                f.insertGlyph(dc)

                deepCompo2Compo[name] = [f[dc.name], list(e.values())[0]]
                f[n].appendComponent(dc.name)
                # print(list(e.values())[0], '\n')



            # print(g.computedDeepComponents)
            # # for deepComponent in g._deepComponents:
            #     if deepComponent in deepCompo2Compo: continue

            # print(g._deepComponents)
            # f.newGlyph(n)
            # f[n].width = g.width

            # for atomicInstance in g.atomicInstances:
            #     for c in atomicInstance:
            #         f[n].appendContour(c) 

            # preview = g.generateDeepComponent(g, False)
            # for d in preview:
            #     for a in d.values():
            #         for c in a[0]:
            #            f[n].appendContour(c) 
                    


        # for n in self.RCJKI.currentFont.characterGlyphSet:
        #     g = self.RCJKI.currentFont[n]
        #     preview = g.generateCharacterGlyph(g, False)
        #     f.newGlyph(n)
        #     f[n].width = g.width
        #     for _, AEInstance in g._getAtomicInstanceGlyph(preview):
        #         for c in AEInstance:
        #             f[n].appendContour(c)


        f.save(os.path.join(self.RCJKI.currentFont.fontPath, "teeest.ufo"))
        
    def loadProjectButtonCallback(self, sender):
        folder = getFolder()
        if not folder: return
        self.RCJKI.projectRoot = folder[0]
        self.RCJKI.setGitEngine()
        self.setrcjkFiles()

    def saveProjectButtonCallback(self, sender):
        if self.RCJKI.get('currentFont'):
            if self.currentFont is not None:
                self.currentFont.save()

    def newProjectButtonCallback(self, sender):
        folder = putFile()
        if not folder: return
        path = '{}.rcjk'.format(folder)
        files.makepath(os.path.join(path, 'folder.proofer'))
        self.RCJKI.projectRoot = os.path.split(path)[0]
        self.RCJKI.setGitEngine()
        self.setrcjkFiles()

    @gitCoverage()
    def setrcjkFiles(self):
        rcjkFiles = list(filter(lambda x: x.endswith(".rcjk"), 
            os.listdir(self.RCJKI.projectRoot)))
        self.w.rcjkFiles.setItems(rcjkFiles)
        self.rcjkFilesSelectionCallback(self.w.rcjkFiles)

    def rcjkFilesSelectionCallback(self, sender):
        self.currentrcjkFile = sender.getItem()
        self.w.saveProjectButton.enable(True)
        self.w.newProjectButton.enable(True)
        self.w.fontInfos.enable(True)
        self.w.generateFontButton.enable(True)

        if self.currentrcjkFile is None: 
            return

        self.w.atomicElement.setSelection([])
        self.w.deepComponent.setSelection([])
        self.w.characterGlyph.setSelection([])
        for w in AllWindows():
            try:
                w.close()
            except:
                pass
        if self.RCJKI.get('currentFont'):
            if self.currentFont is not None:
                self.currentFont.save()
                # self.currentFont.close()
        self.currentrcjkFile = sender.getItem() 
        # if self.currentrcjkFile is None:
        #     self.currentrcjkFile = ""
        fontPath = os.path.join(self.RCJKI.projectRoot, self.currentrcjkFile)
        self.RCJKI.currentFont = font.Font(fontPath)
        self.RCJKI.dataBase = {}

        if 'database.json' in os.listdir(fontPath):
            with open(os.path.join(fontPath, 'database.json'), 'r', encoding = "utf-8") as file:
                self.RCJKI.dataBase = json.load(file)

        self.RCJKI.toggleWindowController()

        self.w.atomicElement.set(self.currentFont.atomicElementSet)
        self.w.deepComponent.set(self.currentFont.deepComponentSet)
        self.w.characterGlyph.set(self.currentFont.characterGlyphSet)

    def GlyphsListDoubleClickCallback(self, sender):
        items = sender.get()
        selection = sender.getSelection()
        if not selection: return
        glyphName = items[selection[0]]

        g = self.currentFont[glyphName]
        font = self.RCJKI.currentFont
        self.RCJKI.currentGlyph = g
        if g._RGlyph.width == 0:
            width = font._RFont.lib.get('robocjk.defaultGlyphWidth', 1000)
            g._RGlyph.width = width
        if font.locker.isLocked(g) == None or font.locker.isLocked(g) == self.RCJKI.user:
            self.RCJKI.gitEngine.pull()
            font.getGlyphs()
            font.locker.lock(self.currentFont[glyphName])
            OpenGlyphWindow(self.currentFont[glyphName]._RGlyph)

    def GlyphsListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel or self.prevGlyphName is None or self.currentFont is None: 
            return
        newGlyphName = sender.get()[sel[0]]
        self.currentFont.renameGlyph(self.prevGlyphName, newGlyphName)
        self.prevGlyphName = newGlyphName
        self.setGlyphNameToCansvas(sender, self.prevGlyphName)

    def GlyphsListSelectionCallback(self, sender):
        if not sender.getSelection(): return
        for lists in self.lists:
            if lists != sender:
                lists.setSelection([])
        self.prevGlyphName = sender.get()[sender.getSelection()[0]]
        self.setGlyphNameToCansvas(sender, self.prevGlyphName)
        user = self.RCJKI.currentFont.locker.isLocked(self.currentFont[self.prevGlyphName])
        if user: 
            self.w.lockerInfoTextBox.set('Locked by: ' + user)
        else:
            self.w.lockerInfoTextBox.set("")

    def setGlyphNameToCansvas(self, sender, glyphName):
        if sender == self.w.atomicElement:
            self.w.atomicElementPreview.glyphName = glyphName
            self.w.atomicElementPreview.update()
        elif sender == self.w.deepComponent:
            self.w.deepComponentPreview.glyphName = glyphName
            self.w.deepComponentPreview.update()
        elif sender == self.w.characterGlyph:
            self.w.characterGlyphPreview.glyphName = glyphName
            self.w.characterGlyphPreview.update()

    @property
    def currentFont(self):
        return self.RCJKI.currentFont

    @property
    def currentGlyph(self):
        return self.RCJKI.currentGlyph

    def newCharacterGlyphCallback(self, sender):
        sheets.NewCharacterGlyph(self.RCJKI, self.w)
        # name = self.dumpName('characterGlyph', self.currentFont.characterGlyphSet)
        # self.currentFont.newGlyph('characterGlyph', name)
        # self.w.characterGlyph.set(self.currentFont.characterGlyphSet)

    def newDeepComponentCallback(self, sender):
        name = self.dumpName('deepComponent', self.currentFont.deepComponentSet)
        self.currentFont.newGlyph('deepComponent', name)
        self.w.deepComponent.set(self.currentFont.deepComponentSet)

    def newAtomicElementCallback(self, sender):
        name = self.dumpName('atomicElement', self.currentFont.atomicElementSet)
        self.currentFont.newGlyph('atomicElement', name)
        self.w.atomicElement.set(self.currentFont.atomicElementSet)

    def dumpName(self, glyphType, sets):
        index = 0
        while True:
            name = "%s%s"%(glyphType, str(index).zfill(5))
            if not name in sets:
                return name
            index+=1
