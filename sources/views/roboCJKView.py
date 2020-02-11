from vanilla import *
from vanilla.dialogs import getFolder, putFile
from mojo.UI import OpenGlyphWindow, AllWindows
from defconAppKit.windows.baseWindow import BaseWindowController
from views import canvasGroups
# from lib.doodleDocument import DoodleDocument

from imp import reload
from utils import decorators, files
reload(decorators)
reload(files)
reload(canvasGroups)
from models import font
reload(font)

import os

gitCoverage = decorators.gitCoverage

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
