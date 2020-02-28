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

class SmartTextBox(TextBox):
    def __init__(self, posSize, text="", alignment="natural", selectable=False, callback=None, sizeStyle=40.0,red=0,green=0,blue=0, alpha=1.0):
        super(SmartTextBox, self).__init__(posSize, text=text, alignment=alignment, selectable=selectable, sizeStyle=sizeStyle)
        
    def _setSizeStyle(self, sizeStyle):
        value = sizeStyle
        self._nsObject.cell().setControlSize_(value)
        font = NSFont.systemFontOfSize_(value)
        self._nsObject.setFont_(font)

class ComponentWindow():

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.previewGlyph = None
        self.w = FloatingWindow(
            (240, 80),
            "Composition Rules",
            closable = False,
            textured = False,
            )
        self.w.char = SmartTextBox(
            (0, 0, 80, -0),
            "",
            sizeStyle = 65,
            alignment = "center"
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
        self.w.canvas = CanvasGroup(
            (160, 0, -0, -0), 
            delegate = self
            )

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
        self.w.canvas.update()

    def variantComponentListdoubleClickCallback(self, sender):
        self.RCJKI.currentGlyph.addDeepComponentNamed(self.deepComponentName)
        self.RCJKI.updateDeepComponent()

    # def open(self):
    #     self.w.open()

    # def close(self):
        self.w.close()

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
        self.w.newProjectButton = Button(
            (410, 10, 200, 20), 
            "New project", 
            callback = self.newProjectButtonCallback,
            )

        self.w.fontInfos = Button(
            (210, 40, 200, 20), 
            "Fonts Infos", 
            callback = self.fontInfosCallback,
            )

        self.w.debug = Button(
            (410, 40, 200, 20), 
            "Debug", 
            callback = self.debugButtonCallback,
            )

        self.w.rcjkFiles = PopUpButton(
            (10, 40, 200, 20),
            [],
            callback = self.rcjkFilesSelectionCallback
            )

        self.w.generateFontButton = Button(
            (10, 70, 200, 20),
            "generateFont",
            callback = self.generateFontButtonCallback
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

    def debugButtonCallback(self, sender):
        pass
        print(self.RCJKI.currentGlyph)
        print(self.RCJKI.currentGlyph.layers)
        print(self.RCJKI.currentGlyph._RGlyph.layers)
        # print(self.RCJKI.currentGlyph._RGlyph.name)
        # print(self.RCJKI.currentGlyph.lib.keys())

    def atomicElementSearchBoxCallback(self, sender):
        name = sender.get()
        go = self.currentFont.atomicElementSet
        for i, e in enumerate(go):
            if e.startswith(name):
                self.w.deepComponent.setSelection([])
                self.w.characterGlyph.setSelection([])
                self.w.atomicElement.setSelection([i])
                return

    def deepComponentSearchBoxCallback(self, sender):
        name = sender.get()
        go = self.currentFont.deepComponentSet
        for i, e in enumerate(go):
            if e.startswith(name):
                self.w.atomicElement.setSelection([])
                self.w.characterGlyph.setSelection([])
                self.w.deepComponent.setSelection([i])
                return

    def characterGlyphearchBoxCallback(self, sender):
        name = sender.get()
        go = self.currentFont.characterGlyphSet
        for i, e in enumerate(go):
            try:
                name = files.unicodeName(name)
            except:pass
            if e.startswith(name):
                self.w.atomicElement.setSelection([])
                self.w.deepComponent.setSelection([])
                self.w.characterGlyph.setSelection([i])
                return

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
        sheets.FontInfosSheet(self.RCJKI, self.w, (400, 400))

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

        self.RCJKI.currentGlyph = self.currentFont[glyphName]
        if self.RCJKI.currentGlyph._RGlyph.width == 0:
            width = self.RCJKI.currentFont._RFont.lib.get('robocjk.defaultGlyphWidth', 1000)
            self.RCJKI.currentGlyph._RGlyph.width = width
        OpenGlyphWindow(self.RCJKI.currentGlyph._RGlyph)

    def GlyphsListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel or self.prevGlyphName is None or self.currentFont is None: 
            return
        newGlyphName = sender.get()[sel[0]]
        self.currentFont.renameGlyph(self.prevGlyphName, newGlyphName)
        self.prevGlyphName = newGlyphName

    def GlyphsListSelectionCallback(self, sender):
        if not sender.getSelection(): return
        for lists in self.lists:
            if lists != sender:
                lists.setSelection([])
        self.prevGlyphName = sender.get()[sender.getSelection()[0]]
        if sender == self.w.atomicElement:
            self.w.atomicElementPreview.glyphName = self.prevGlyphName
            self.w.atomicElementPreview.update()
        elif sender == self.w.deepComponent:
            self.w.deepComponentPreview.glyphName = self.prevGlyphName
            self.w.deepComponentPreview.update()
        elif sender == self.w.characterGlyph:
            self.w.characterGlyphPreview.glyphName = self.prevGlyphName
            self.w.characterGlyphPreview.update()

    @property
    def currentFont(self):
        return self.RCJKI.currentFont

    @property
    def currentGlyph(self):
        return self.RCJKI.currentGlyph

    def newCharacterGlyphCallback(self, sender):
        name = self.dumpName('characterGlyph', self.currentFont.characterGlyphSet)
        self.currentFont.newGlyph('characterGlyph', name)
        self.w.characterGlyph.set(self.currentFont.characterGlyphSet)

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
