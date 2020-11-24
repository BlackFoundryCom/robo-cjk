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
from vanilla.dialogs import getFolder, putFile, askYesNo, message
from mojo.canvas import Canvas
from fontParts.ui import AskYesNoCancel, AskString
from mojo.UI import OpenGlyphWindow, AllWindows, CurrentGlyphWindow, UpdateCurrentGlyphView, PostBannerNotification
from defconAppKit.windows.baseWindow import BaseWindowController
from views import canvasGroups
from mojo.canvas import CanvasGroup
import mojo.drawingTools as mjdt
# from lib.doodleDocument import DoodleDocument
from AppKit import NSFont, NumberFormatter 
from imp import reload
from utils import decorators, files
# reload(decorators)
# reload(files)
# reload(canvasGroups)
from models import font
# reload(font)
from views import sheets
# reload(sheets)
from views import PDFProofer

from controllers import teamManager
# reload(PDFProofer)
from views import scriptingWindow
# reload(scriptingWindow)
from views import textCenter
# reload(textCenter)

import os, json, copy

# import BF_fontbook_struct as bfs
# import BF_rcjk2mysql

gitCoverage = decorators.gitCoverage

from mojo.roboFont import *
import threading
import queue

from utils import colors
INPROGRESS = colors.INPROGRESS
CHECKING1 = colors.CHECKING1
CHECKING2 = colors.CHECKING2
CHECKING3 = colors.CHECKING3
DONE = colors.DONE
STATE_COLORS = colors.STATE_COLORS

EditButtonImagePath = os.path.join(os.getcwd(), "resources", "EditButton.pdf")
removeGlyphImagePath = os.path.join(os.getcwd(), "resources", "removeButton.pdf")
duplicateGlyphImagePath = os.path.join(os.getcwd(), "resources", "duplicateButton.pdf")

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
            ""
            )
        self.w.closeButton = Button(
            (80, -20, -0, -0),
            "Close",
            sizeStyle = "small",
            callback = self.closeCallback
            )

        self.setUI()
        self.w.open()

    def setUI(self):
        unicode = str(hex(self.RCJKI.currentGlyph.unicode)[2:])
        self.w.editField.set(self.RCJKI.currentFont.selectDatabaseKey(unicode))
        # if not self.RCJKI.currentFont.mysqlFont:
        #     self.w.editField.set("".join(self.RCJKI.dataBase[self.char]))
        # else:
        #     self.w.editField.set(self.RCJKI.mysql.select_font_database_key(self.RCJKI.currentFont.fontName, str(hex(self.RCJKI.currentGlyph.unicode)[2:])))

    def closeCallback(self, sender):
        components = list(self.w.editField.get())
        self.RCJKI.currentFont.updateDatabaseKey(str(hex(self.RCJKI.currentGlyph.unicode)[2:]), components)
        if not self.RCJKI.currentFont.mysqlFont:
            # self.RCJKI.dataBase[self.char] = components
            self.RCJKI.exportDataBase()
        # else:
        #     data = tuple([hex(ord(x))[2:] for x in components])
        #     self.RCJKI.mysql.update_font_database_key(self.RCJKI.currentFont.fontName, str(hex(self.RCJKI.currentGlyph.unicode)[2:]), data)
        self.c.w.componentList.set(components)
        self.w.close()


def getRelatedGlyphs(font, glyphName, regenerated = []):
    g = font.get(glyphName)
    if glyphName not in regenerated:
        q = queue.Queue()
        threading.Thread(target=font.queueGetGlyphs, args = (q, g.type), daemon=True).start()
        q.put([glyphName])
        regenerated.append(glyphName)
    if not hasattr(g, "_deepComponents"): return
    for dc in g._deepComponents:
        getRelatedGlyphs(font, dc['name'], regenerated)

# This function is outside of any class
def openGlyphWindowIfLockAcquired(RCJKI, glyph):
    font = RCJKI.currentFont
    g = glyph._RGlyph
    # font[glyphName]._initWithLib()
    # locked, alreadyLocked = font.locker.lock(g)
    locked, alreadyLocked = font.lockGlyph(g)
    if not RCJKI.mysql:
        print(locked, alreadyLocked)
        if not locked: return
        if not alreadyLocked:
            RCJKI.gitEngine.pull()
            # font.getGlyphs()
            getRelatedGlyphs(font, glyph.name)
            # font.getGlyph(font[glyphName])
            # g = font.get(glyphName, font._RFont)._RGlyph
    else:
        if not locked: return
    if not g.width:
        g.width = font.defaultGlyphWidth
    try:
        CurrentGlyphWindow().close()
    except: pass
    # font.get(glyphName, font._RFont).update()
    glyph = font.get(glyph.name, font._RFont)
    glyph.update()
    g = glyph._RGlyph
    OpenGlyphWindow(g)
    CurrentGlyphWindow().window().setPosSize(RCJKI.glyphWindowPosSize)
    # if glyph.type != "atomicElement":
    #     RCJKI.currentView.setglyphState()
    

    # glyph.save()
    # font[glyphName]
    # # glyphType = glyph.type
    # # rglyph = glyph._RGlyph
    # g.lib.update(glyph.lib)
    # # font.getGlyph(glyph.name)

# class CharacterWindow:

#     filterRules = [
#         "In font",
#         "Not in font",
#         "Can be designed with current deep components",
#         "Can't be designed with current deep components",
#         "All",
#         "Have outlines", 
#         # "Custom list"
#         ]

#     def __init__(self, RCJKI):
#         self.RCJKI = RCJKI
#         self.w = FloatingWindow(
#             (0, 0, 240, 100),
#             minSize = (240, 120),
#             maxSize = (240, 800),
#             closable = False,
#             textured = True,
#             )
#         self.w.backgroundCanvas = CanvasGroup((0, 0, -0, -0), delegate = self)
#         self.filter = 0
#         self.preview = 1
#         self.w.filter = PopUpButton(
#             (0, 0, -0, 20),
#             self.filterRules,
#             callback = self.filterCallback,
#             sizeStyle = "mini"
#             )
#         self.w.component = SmartTextBox(
#             (0, 16, 80, -0),
#             "",
#             sizeStyle = 65,
#             alignment = "center"
#             )
#         self.w.charactersList = List(
#             (80, 16, 40, -0), 
#             [],
#             selectionCallback = self.charactersListSelectionCallback,
#             doubleClickCallback = self.charactersListDoubleClickCallback,
#             drawFocusRing = False
#             )
#         self.w.previewCheckBox = CheckBox(
#             (130, 20, -10, 20),
#             'Preview',
#             value = self.preview,
#             sizeStyle = "small",
#             callback = self.previewCheckBoxCallback
#             )
#         self.w.previewCheckBox.show(self.preview)
#         self.w.sliders = Group((120, 45, -0, -0))
#         self.w.sliders.show(False)

#         self.w.sliders.x = Slider((0, 0, -0, 20),
#             minValue = -1000,
#             maxValue = 1000,
#             value = 0,
#             callback = self.sliderCallback)
#         self.w.sliders.y = Slider((0, 20, -0, 20),
#             minValue = -1000,
#             maxValue = 1000,
#             value = 0,
#             callback = self.sliderCallback)
#         self.w.sliders.scaleX = EditText((0, 45, 60, 20),
#             100,
#             formatter = NumberFormatter(),
#             sizeStyle = "small",
#             callback = self.scaleCallback)
#         self.w.sliders.scaleY = EditText((60, 45, -0, 20),
#             100,
#             formatter = NumberFormatter(),
#             sizeStyle = "small",
#             callback = self.scaleCallback)
#         self.w.sliders.canvas = Canvas((0, 65, -0, -0), delegate = self)
#         self.char = ""

#     def draw(self):
#         pass

#     def mouseDragged(self, point):
#         x, y = self.RCJKI.drawer.refGlyphPos
#         dx = point.deltaX()
#         dy = point.deltaY()
#         x += dx
#         y -= dy
#         sensibility = 1
#         self.RCJKI.drawer.refGlyphPos = [x*sensibility, y*sensibility]  
#         self.w.sliders.x.set(x)
#         self.w.sliders.y.set(y)
#         UpdateCurrentGlyphView()

#     def sliderCallback(self, sender):
#         self.RCJKI.drawer.refGlyphPos = [self.w.sliders.x.get(), self.w.sliders.y.get()]  
#         UpdateCurrentGlyphView()

#     def scaleCallback(self, sender):
#         self.RCJKI.drawer.refGlyphScale = [self.w.sliders.scaleX.get()/100, self.w.sliders.scaleY.get()/100]  
#         UpdateCurrentGlyphView()        

#     def filterCallback(self, sender):
#         self.filter = sender.get()
#         self.filterCharacters()

#     def filterCharacters(self):
#         l = []

#         if self.filter == 4:
#             l = list(self.relatedChars)
#             title = "Related Characters"

#         elif self.filter in [0, 1]:
#             names = [files.unicodeName(c) for c in self.relatedChars]
#             if self.filter == 0:
#                 result = set(names) & set(self.RCJKI.currentFont.characterGlyphSet)
#             else:
#                 result = set(names) - set(self.RCJKI.currentFont.characterGlyphSet)
#             title = self.filterRules[self.filter]
#             l = [chr(int(n[3:], 16)) for n in result]

#         elif self.filter in [2, 3]:
#             DCSet = set([x for x in self.RCJKI.currentFont.deepComponentSet if self.RCJKI.currentFont[x]._RGlyph.lib["robocjk.deepComponents"]])
#             for c in self.relatedChars:
#                 compo = ["DC_%s_00"%files.normalizeUnicode(hex(ord(v))[2:].upper()) for v in self.RCJKI.currentFont.dataBase[c]]
#                 # compo = ["DC_%s_00"%files.normalizeUnicode(hex(ord(v))[2:].upper()) for v in self.RCJKI.currentFont.selectDatabaseKey(hex(ord(c))[2:].upper())]
#                 inside = len(set(compo) - DCSet) == 0
#                 if self.filter == 2 and inside:
#                     l.append(c)
#                 elif self.filter == 3 and not inside:
#                     l.append(c)
#             # if self.filter == 2:
#             #     result = set([files.unicodeName(c) for c in l]) - set(self.RCJKI.currentFont.characterGlyphSet)
#             #     l = [chr(int(n[3:], 16)) for n in result]
#             title = " ".join(self.filterRules[self.filter].split(' ')[:3])

#         elif self.filter == 5:
#             names = [files.unicodeName(c) for c in self.relatedChars]
#             l = []
#             for name in names:
#                 try:
#                     if len(self.RCJKI.currentFont[name]):
#                         l.append(chr(int(name[3:], 16)))
#                 except:pass
#             title = self.filterRules[self.filter]
#             # l = [chr(int(name[3:], 16)) for name in names if len(self.RCJKI.currentFont[name])]

#         self.RCJKI.drawer.refGlyph = None
#         self.RCJKI.drawer.refGlyphPos = [0, 0]   
#         UpdateCurrentGlyphView()
#         self.w.charactersList.set(l)
#         self.w.setTitle("%s %s"%(len(l), title))

#     def setUI(self):
#         self.relatedChars = set()
#         try:
#             _, code, _ = self.RCJKI.currentGlyph.name.split("_") 
#             char = chr(int(code, 16))
#             for k, v in self.RCJKI.currentFont.dataBase.items():
#                 if char in v:
#                     self.relatedChars.add(k)
#         except: pass
#         self.filterCharacters()
#         self.w.component.set(char)

#     def open(self):
#         self.w.open()

#     def close(self):
#         self.RCJKI.drawer.refGlyph = None
#         self.RCJKI.drawer.refGlyphPos = [0, 0]
#         self.w.close()

#     def charactersListSelectionCallback(self, sender):
#         self.w.previewCheckBox.show(self.filter in [0, 5])
#         self.w.sliders.show(self.filter in [0, 5])
#         if self.preview:
#             self.setRefGlyph(sender)

#         sel = sender.getSelection()
#         if not sel:
#             return
#         char = sender.get()[sel[0]]
#         if char != self.char:
#             self.w.sliders.x.set(0)
#             self.w.sliders.y.set(0)
#             self.RCJKI.drawer.refGlyphPos = [0, 0]

#             self.w.sliders.scaleX.set(100)
#             self.w.sliders.scaleY.set(100)
#             self.RCJKI.drawer.refGlyphScale = [1, 1]  
#             self.char = char

#         if self.filter in [0, 3]:
#             if files.unicodeName(char) in self.RCJKI.currentFont.characterGlyphSet:
#                 self.w.previewCheckBox.show(True)
#         UpdateCurrentGlyphView()

#     def charactersListDoubleClickCallback(self, sender):
#         sel = sender.getSelection()
#         if not sel: return
#         char = sender.get()[sel[0]]
#         name = files.unicodeName(char)
#         font = self.RCJKI.currentFont
#         if not self.RCJKI.currentFont.mysqlFont:
#             self.RCJKI.gitEngine.createGitignore()
#             self.RCJKI.gitEngine.pull()
#         try:
#             font[name]
#         except:
#             font.newGlyph("characterGlyph", name)
#             # font.locker.batchLock([font[name]])
#             font.batchLockGlyphs([font[name]])
#             if not self.RCJKI.currentFont.mysqlFont:
#                 self.RCJKI.gitEngine.commit("new glyph")
#                 self.RCJKI.gitEngine.push()
#         finally:
#             openGlyphWindowIfLockAcquired(self.RCJKI, self.RCJKI.currentFont[name])

#     def setRefGlyph(self, sender):
#         sel = sender.getSelection()
#         if not sel:
#             self.RCJKI.drawer.refGlyph = None
#             self.RCJKI.drawer.refGlyphPos = [0, 0]
#             return
#         char = sender.get()[sel[0]]
#         if self.preview:
#             try:
#                 glyph = self.RCJKI.currentFont[files.unicodeName(char)]
#             except:
#                 glyph = None
#             self.RCJKI.drawer.refGlyph = glyph
#             self.RCJKI.drawer.refGlyphPos = [self.w.sliders.x.get(), self.w.sliders.y.get()]  
#             UpdateCurrentGlyphView()
        
#     def previewCheckBoxCallback(self, sender):
#         self.preview = sender.get()
#         self.w.sliders.show(self.preview)
#         if self.preview:
#             self.setRefGlyph(self.w.charactersList)
#         else:
#             self.RCJKI.drawer.refGlyph = None 
#             self.RCJKI.drawer.refGlyphPos = [0, 0]
#             UpdateCurrentGlyphView()

# class ComponentWindow():

#     def __init__(self, RCJKI):
#         self.RCJKI = RCJKI
#         self.glyph = None
#         self.w = FloatingWindow(
#             (0, 0, 240, 80),
#             "Composition Rules",
#             closable = False,
#             textured = True,
#             )
#         self.w.char = SmartTextBox(
#             (0, 0, 80, -0),
#             "",
#             sizeStyle = 65,
#             alignment = "center"
#             )
#         self.w.editButton = ImageButton(
#             (0, -15, 15, -0),
#             EditButtonImagePath,
#             bordered = False,
#             callback = self.editButtonCallback
#             )
#         self.w.componentList = List(
#             (80, 0, 40, -0), 
#             [],
#             selectionCallback = self.componentListCallback
#             )
#         self.w.variantComponentList = List(
#             (120, 0, 40, -0), 
#             [],
#             selectionCallback = self.variantComponentListCallback,
#             doubleClickCallback = self.variantComponentListdoubleClickCallback
#             )
#         self.w.canvas2 = CanvasGroup(
#             (160, 0, -0, -0), 
#             delegate = self
#             )

#     def open(self):
#         self.w.open()

#     def close(self):
#         self.w.close()

#     def setUI(self):
#         if not self.RCJKI.currentGlyph.unicode and self.RCJKI.currentGlyph.name.startswith('uni'):
#             try:
#                 self.RCJKI.currentGlyph.unicode = int(self.RCJKI.currentGlyph.name[3:], 16)
#             except:
#                 print('this glyph has no Unicode')
#                 return
#         char = chr(self.RCJKI.currentGlyph.unicode)
#         # if not self.RCJKI.currentFont.mysqlFont:
            
#         #     if char in self.RCJKI.currentFont.dataBase:
#         #         self.w.componentList.set(self.RCJKI.currentFont.selectDatabaseKey(hex(ord(char))[2:]))
#         # else:
#         #     d = self.RCJKI.mysql.select_font_database_key(self.RCJKI.currentFont.fontName, str(hex(self.RCJKI.currentGlyph.unicode)[2:]))
#         #     # d = self.RCJKI.mysql.select_font_database_key(self.RCJKI.currentFont.fontName, "53E3")
#         #     print(d)
#         # d = self.RCJKI.currentFont.selectDatabaseKey(hex(ord(char))[2:])
#         d = self.RCJKI.currentFont.dataBase.get(char, [])
#         if d is None:
#             d = []
#         # print( )
#         self.w.componentList.set(d)
#         self.w.char.set(char)

#     def editButtonCallback(self, sender):
#         EditingSheet(self, self.RCJKI)

#     def draw(self):
#         if self.glyph is None: return
#         mjdt.save()
#         mjdt.translate(20, 25)
#         mjdt.scale(.04)
#         mjdt.fill(0, 0, 0, 1)
#         # loc = {}
#         # if self.glyph.selectedSourceAxis:
#         #     loc = {self.glyph.selectedSourceAxis:1}
#         for atomicInstance in self.glyph.preview({},forceRefresh=False):
#             mjdt.drawGlyph(atomicInstance.getTransformedGlyph()) 
#         mjdt.restore()

#     def componentListCallback(self, sender):
#         sel = sender.getSelection()
#         if not sel: return
#         char = sender.get()[sel[0]]
#         self.code = files.normalizeUnicode(hex(ord(char))[2:].upper())
#         dcName = "DC_%s_00"%self.code
#         if dcName not in self.RCJKI.currentFont.deepComponentSet: 
#             self.w.variantComponentList.set([])
#             return
#         index = self.RCJKI.currentFont.deepComponentSet.index(dcName)
#         l = ["00"]
#         i = 1
#         while True:
#             name = "DC_%s_%s"%(self.code, str(i).zfill(2))
#             if not name in self.RCJKI.currentFont.deepComponentSet:
#                 break
#             l.append(str(i).zfill(2))
#             i += 1
#         self.w.variantComponentList.set(l)

#     def variantComponentListCallback(self, sender):
#         sel = sender.getSelection()
#         if not sel: return
#         index = sender.get()[sel[0]]
#         self.deepComponentName = "DC_%s_%s"%(self.code, index)
#         self.glyph = self.RCJKI.currentFont[self.deepComponentName]
#         # self.glyph.preview.computeDeepComponents(update = False)
#         self.w.canvas2.update()

#     def variantComponentListdoubleClickCallback(self, sender):
#         self.RCJKI.currentGlyph.addDeepComponentNamed(self.deepComponentName)
#         self.RCJKI.updateDeepComponent(update = False)


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
            "Login & load projects", 
            callback = self.loadProjectButtonCallback,
            )
        self.w.setDefaultButton(self.w.loadProjectButton)
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
        self.w.pdfProoferButton.enable(False)

        self.w.rcjkFiles = PopUpButton(
            (10, 40, 180, 20),
            [],
            callback = self.rcjkFilesSelectionCallback
            )
        self.w.rcjkFiles.enable(False)

        self.w.reloadProject = ImageButton(
            (190, 40, 20, 20),
            imagePath = os.path.join(os.getcwd(), "resources/reloadIcon.pdf"),
            bordered = False,
            callback = self.reloadProjectCallback
            )

        self.w.generateFontButton = Button(
            (10, 70, 200, 20),
            "generateFont",
            callback = self.generateFontButtonCallback,
            )
        self.w.generateFontButton.enable(False)

        self.w.teamManagerButton = Button(
            (10, 100, 200, 20),
            "Team manager",
            callback = self.teamManagerButtonCallback,
            )
        self.w.teamManagerButton.enable(False)

        self.RCJKI.textCenterWindows = []
        self.w.textCenterButton = Button(
            (410, 70, 200, 20),
            "Text Center",
            callback = self.textCenterButtonCallback,
            )
        self.w.textCenterButton.enable(False)

        self.w.codeEditorButton = Button(
            (410, 100, 200, 20),
            "Scripting Window",
            callback = self.codeEditorButtonCallback,
            )
        self.w.codeEditorButton.enable(False)

        self.w.lockControllerDCButton = Button(
            (210, 70, 200, 20),
            "Lock controller",
            callback = self.lockControllerDCButtonCallback,
            )
        self.w.lockControllerDCButton.enable(False)

        self.w.lockerInfoTextBox = TextBox(
            (210, 100, 200, 20),
            "",
            alignment='center'
            )

        self.w.firstFilterAtomicElement = PopUpButton(
            (10, 120, 80, 20),
            ["All those", "Locked and"],
            callback = self.filterAtomicElementCallback,
            sizeStyle = "mini"
            )
        self.w.secondFilterAtomicElement = PopUpButton(
            (90, 120, 120, 20),
            [
            "that are in font", 
            "that are not empty", 
            "that are empty", 
            "that have outlines",
            "that are in progress", 
            "that are checking 1", 
            "that are checking 2", 
            "that are checking 3", 
            "that are done"
            ],
            callback = self.filterAtomicElementCallback,
            sizeStyle = "mini"
            )
        self.w.firstFilterAtomicElement.enable(False)
        self.w.secondFilterAtomicElement.enable(False)

        self.w.atomicElementSearchBox = SearchBox(
            (10, 140, 200, 20),
            callback = self.atomicElementSearchBoxCallback
            )
        self.w.atomicElementSearchBox.enable(False)
        self.w.atomicElement = List(
            (10, 160, 200, 190),
            [],
            allowsMultipleSelection = False,
            doubleClickCallback = self.GlyphsListDoubleClickCallback,
            editCallback = self.GlyphsListEditCallback,
            selectionCallback = self.GlyphsListSelectionCallback, 
            )

        self.w.removeAtomicElement = ImageButton(
            (10, 350, 20, 20),
            imagePath = removeGlyphImagePath,
            bordered = False,
            callback = self.removeAtomicElementCallback
            )
        self.w.removeAtomicElement.enable(False)
        self.w.duplicateAtomicElement = ImageButton(
            (190, 350, 20, 20),
            imagePath = duplicateGlyphImagePath,
            bordered = False,
            callback = self.duplicateAtomicElementCallback
            )
        self.w.duplicateAtomicElement.enable(False)
        self.w.newAtomicElement = Button(
            (30, 350, 160, 20),
            "New AE",
            callback = self.newAtomicElementCallback
            )
        self.w.newAtomicElement.enable(False)
        self.w.atomicElementPreview = canvasGroups.GlyphPreviewCanvas(
            (10, 372, 200, -0),
            self.RCJKI,
            glyphType = "atomicElement")
        self.w.atomicElementDesignStepPopUpButton = PopUpButton(
            (10, -20, 100, -0), 
            [
            "In Progress", 
            "Checking 1", 
            "Checking 2", 
            "Checking 3", 
            "Done"
            ],
            callback = self.atomicElementDesignStepPopUpButtonCallback
            )
        self.w.atomicElementDesignStepPopUpButton.enable(False)

        self.w.firstFilterDeepComponent = PopUpButton(
            (210, 120, 80, 20),
            ["All those", "Locked and"],
            callback = self.filterDeepComponentCallback,
            sizeStyle = "mini"
            )
        self.w.secondFilterDeepComponent = PopUpButton(
            (290, 120, 120, 20),
            [
            "that are in font", 
            "that are not empty", 
            "that are empty", 
            "that have outlines", 
            "that are not locked",
            "that are in progress", 
            "that are checking 1", 
            "that are checking 2", 
            "that are checking 3", 
            "that are done"
            ],
            callback = self.filterDeepComponentCallback,
            sizeStyle = "mini"
            )
        self.w.firstFilterDeepComponent.enable(False)
        self.w.secondFilterDeepComponent.enable(False)

        self.w.deepComponentSearchBox = SearchBox(
            (210, 140, 200, 20),
            callback = self.deepComponentSearchBoxCallback
            )
        self.w.deepComponentSearchBox.enable(False)
        self.w.deepComponent = List(
            (210, 160, 200, 190),
            [],
            allowsMultipleSelection = False,
            doubleClickCallback = self.GlyphsListDoubleClickCallback,
            editCallback = self.GlyphsListEditCallback,
            selectionCallback = self.GlyphsListSelectionCallback, 
            )
        self.w.removeDeepComponent = ImageButton(
            (210, 350, 20, 20),
            imagePath = removeGlyphImagePath,
            bordered = False,
            callback = self.removeDeepComponentCallback
            )
        self.w.removeDeepComponent.enable(False)
        self.w.duplicateDeepComponent = ImageButton(
            (390, 350, 20, 20),
            imagePath = duplicateGlyphImagePath,
            bordered = False,
            callback = self.duplicateDeepComponentCallback
            )
        self.w.duplicateDeepComponent.enable(False)
        self.w.newDeepComponent = Button(
            (230, 350, 160, 20),
            "New DC",
            callback = self.newDeepComponentCallback
            )
        self.w.newDeepComponent.enable(False)
        self.w.deepComponentPreview = canvasGroups.GlyphPreviewCanvas(
            (210, 372, 200, -0),
            self.RCJKI,
            glyphType = "deepComponent")
        self.w.deepComponentDesignStepPopUpButton = PopUpButton(
            (210, -20, 100, -0), 
            [
            "In Progress", 
            "Checking 1", 
            "Checking 2", 
            "Checking 3", 
            "Done"
            ],
            callback = self.deepComponentDesignStepPopUpButtonCallback
            )
        self.w.deepComponentDesignStepPopUpButton.enable(False)

        self.w.firstFilterCharacterGlyph = PopUpButton(
            (410, 120, 80, 20),
            ["All those", "Locked and"],
            callback = self.filterCharacterGlyphCallback,
            sizeStyle = "mini"
            )
        self.w.secondFilterCharacterGlyph = PopUpButton(
            (490, 120, 120, 20),
            [
            "that are in font", 
            "that can be fully designed", 
            "that are not empty", 
            "that are empty", 
            "that have outlines", 
            "that are not locked",
            "that are in progress", 
            "that are checking 1", 
            "that are checking 2", 
            "that are checking 3", 
            "that are done"
            ],
            callback = self.filterCharacterGlyphCallback,
            sizeStyle = "mini"
            )
        self.w.firstFilterCharacterGlyph.enable(False)
        self.w.secondFilterCharacterGlyph.enable(False)
        self.w.characterGlyphSearchBox = SearchBox(
            (410, 140, 200, 20),
            callback = self.characterGlyphearchBoxCallback
            )
        self.w.characterGlyphSearchBox.enable(False)
        self.w.characterGlyph = List(
            (410, 160, 200, 190),
            [],
            columnDescriptions = [
                {"title":"char", "width":20, "editable":False}, 
                {"title":"name"}
                ],
            drawFocusRing = False,
            showColumnTitles = False,
            allowsMultipleSelection = False,
            doubleClickCallback = self.GlyphsListDoubleClickCallback,
            editCallback = self.GlyphsListEditCallback,
            selectionCallback = self.GlyphsListSelectionCallback, 
            )
        self.w.removeCharacterGlyph = ImageButton(
            (410, 350, 20, 20),
            imagePath = removeGlyphImagePath,
            bordered = False,
            callback = self.removeCharacterGlyphCallback
            )
        self.w.removeCharacterGlyph.enable(False)
        self.w.duplicateCharacterGlyph = ImageButton(
            (590, 350, 20, 20),
            imagePath = duplicateGlyphImagePath,
            bordered = False,
            callback = self.duplicateCharacterGlyphCallback
            )
        self.w.duplicateCharacterGlyph.enable(False)
        self.w.newCharacterGlyph = Button(
            (430, 350, 160, 20),
            "New CG",
            callback = self.newCharacterGlyphCallback
            )
        self.w.newCharacterGlyph.enable(False)
        self.w.characterGlyphPreview = canvasGroups.GlyphPreviewCanvas(
            (410, 372, 200, -0),
            self.RCJKI,
            glyphType = "characterGlyph")
        self.w.characterGlyphDesignStepPopUpButton = PopUpButton(
            (410, -20, 100, -0), 
            [
            "In Progress", 
            "Checking 1", 
            "Checking 2", 
            "Checking 3", 
            "Done"
            ],
            callback = self.characterGlyphDesignStepPopUpButtonCallback
            )
        self.w.characterGlyphDesignStepPopUpButton.enable(False)
        
        self.lists = [
            self.w.atomicElement,
            self.w.deepComponent,
            self.w.characterGlyph
        ]
        self.RCJKI.toggleObservers()
        self.w.bind('close', self.windowCloses)
        self.w.open()

    def codeEditorButtonCallback(self, sender):
        scriptingWindow.ScriptingWindow(self.RCJKI)

    def pdfProoferButtonCallback(self, sender):
        self.RCJKI.pdf = PDFProofer.PDFEngine(self.RCJKI)
        self.RCJKI.pdf.interface.open()

    def textCenterButtonCallback(self, sender):
        # if self.RCJKI.textCenterWindow is None:
        self.RCJKI.textCenterWindows.append(textCenter.TextCenter(self.RCJKI))
        print(self.RCJKI.textCenterWindows)

    def atomicElementDesignStepPopUpButtonCallback(self, sender):
        state = sender.get()
        l = self.w.atomicElement
        if not l.getSelection():
            return
        name = l.get()[l.getSelection()[0]]
        glyph = self.currentFont[name]
        glyph.markColor = STATE_COLORS[state]
        self.setGlyphToCanvas(sender, self.currentGlyph)
        self.w.atomicElementPreview.update()

    def deepComponentDesignStepPopUpButtonCallback(self, sender):
        state = sender.get()
        l = self.w.deepComponent
        if not l.getSelection():
            return
        name = l.get()[l.getSelection()[0]]
        glyph = self.currentFont[name]
        glyph.markColor = STATE_COLORS[state]
        self.setGlyphToCanvas(sender, self.currentGlyph)
        self.w.deepComponentPreview.update()

    def characterGlyphDesignStepPopUpButtonCallback(self, sender):
        state = sender.get()
        l = self.w.characterGlyph
        if not l.getSelection():
            return
        name = l.get()[l.getSelection()[0]]["name"]
        glyph = self.currentFont[name]
        glyph.markColor = STATE_COLORS[state]
        if STATE_COLORS[state] == DONE:
            self.RCJKI.decomposeGlyphToBackupLayer(glyph)
        self.setGlyphToCanvas(sender, self.currentGlyph)
        self.w.characterGlyphPreview.update()

    def atomicElementSearchBoxCallback(self, sender):
        if not sender.get():
            self.filterAtomicElementCallback(None)
        else:
            name = str(sender.get())
            l = files._getFilteredListFromName(self.currentFont.staticAtomicElementSet(), name)
            if l:
                self.w.deepComponent.setSelection([])
                self.w.characterGlyph.setSelection([])
                self.w.atomicElement.setSelection([])
                self.w.atomicElement.set(l)
            else:
                self.filterAtomicElementCallback(None)
            
    def deepComponentSearchBoxCallback(self, sender):
        if not sender.get():
            self.filterDeepComponentCallback(None)
        else:
            name = str(sender.get())
            l = files._getFilteredListFromName(self.currentFont.staticDeepComponentSet(), name)
            if l:
                self.w.atomicElement.setSelection([])
                self.w.characterGlyph.setSelection([])
                self.w.deepComponent.setSelection([])
                self.w.deepComponent.set(l)
            else:
                self.filterDeepComponentCallback(None)

    def characterGlyphearchBoxCallback(self, sender):
        l = []
        if not sender.get():
            self.filterCharacterGlyphCallback(None)
        else:
            try:
                name = files.unicodeName(sender.get())
            except:
                name = str(sender.get())
            l = files._getFilteredListFromName(self.currentFont.staticCharacterGlyphSet(), name)
            self.w.atomicElement.setSelection([])
            self.w.deepComponent.setSelection([])
            self.w.characterGlyph.setSelection([])
            charSet = [dict(char = files.unicodeName2Char(x), name = x) for x in l]
            self.w.characterGlyph.set(charSet)
        if not l:
            self.filterCharacterGlyphCallback(None)

    def filterAtomicElementCallback(self, sender):
        aeList = self.currentFont.staticAtomicElementSet()
        filteredList = self.filterGlyphs(
            "atomicElement",
            self.w.firstFilterAtomicElement.getItem(),
            self.w.secondFilterAtomicElement.getItem(),
            aeList,
            # list(set(aeList) & set([x for x in self.currentFont.locker.myLockedGlyphs]))
            set(aeList) & set([x for x in self.currentFont.currentUserLockedGlyphs()])
            )
        self.w.atomicElement.setSelection([])
        self.w.deepComponent.setSelection([])
        self.w.characterGlyph.setSelection([])
        self.w.atomicElement.set(sorted(filteredList))

    def filterDeepComponentCallback(self, sender):
        dcList = self.currentFont.staticDeepComponentSet()
        filteredList = self.filterGlyphs(
            "deepComponent",
            self.w.firstFilterDeepComponent.getItem(),
            self.w.secondFilterDeepComponent.getItem(),
            dcList,
            # list(set(dcList) & set([x for x in self.currentFont.locker.myLockedGlyphs]))
            set(dcList) & set([x for x in self.currentFont.currentUserLockedGlyphs()])
            )
        self.w.atomicElement.setSelection([])
        self.w.deepComponent.setSelection([])
        self.w.characterGlyph.setSelection([])
        self.w.deepComponent.set(sorted(filteredList))

    def filterCharacterGlyphCallback(self, sender):
        cgList = self.currentFont.staticCharacterGlyphSet()
        filteredList = self.filterGlyphs(
            "characterGlyph",
            self.w.firstFilterCharacterGlyph.getItem(),
            self.w.secondFilterCharacterGlyph.getItem(),
            cgList,
            # list(set(cgList) & set([x for x in self.currentFont.locker.myLockedGlyphs]))
            set(cgList) & set([x for x in self.currentFont.currentUserLockedGlyphs()])
            )

        self.w.atomicElement.setSelection([])
        self.w.deepComponent.setSelection([])
        self.w.characterGlyph.setSelection([])
        charSet = [dict(char = files.unicodeName2Char(x), name = x) for x in sorted(filteredList)]
        self.w.characterGlyph.set(charSet)

    def filterGlyphs(self, glyphtype, option1, option2, allGlyphs, lockedGlyphs):
        lockedGlyphs = lockedGlyphs & set(allGlyphs)

        def getFilteredList(option1, l, lockedGlyphs):
            if option1 == "All those":
                return l
            else:
                return list(lockedGlyphs & set(l))

        if option2 == "that can be fully designed":
            l = []
            DCSet = set([x for x in self.RCJKI.currentFont.deepComponentSet if self.RCJKI.currentFont.get(x)._RGlyph.lib["robocjk.deepComponents"]])
            for name in self.currentFont.characterGlyphSet:
                try:
                    c = chr(int(name[3:].split(".")[0], 16))
                    self.RCJKI.currentFont.dataBase[c]
                except: continue
                compo = ["DC_%s_00"%files.normalizeUnicode(hex(ord(v))[2:].upper()) for v in self.RCJKI.currentFont.dataBase[c]]
                inside = len(set(compo) - DCSet) == 0
                if inside:
                    l.append(name)
            return getFilteredList(option1, l, lockedGlyphs)

        elif option2 == "that are not empty":
            if glyphtype == "characterGlyph":
                if option1 == "All those":
                    return [x for x in allGlyphs if self.RCJKI.currentFont.get(x)._deepComponents or len(self.RCJKI.currentFont.get(x))]
                else:
                    return [x for x in lockedGlyphs if self.RCJKI.currentFont.get(x)._deepComponents or len(self.RCJKI.currentFont.get(x))]
            elif glyphtype == "deepComponent":
                if option1 == "All those":
                    return [x for x in allGlyphs if self.RCJKI.currentFont.get(x)._deepComponents or len(self.RCJKI.currentFont.get(x))]
                else:
                    return [x for x in lockedGlyphs if self.RCJKI.currentFont.get(x)._deepComponents or len(self.RCJKI.currentFont.get(x))]
            else:
                if option1 == "All those":
                    return [x for x in allGlyphs if len(self.RCJKI.currentFont.get(x))]
                else:
                    return [x for x in lockedGlyphs if len(self.RCJKI.currentFont.get(x))]
            # return getFilteredList(option1, l, lockedGlyphs)

        elif option2 == "that have outlines":
            if option1 == "All those":
                return [x for x in allGlyphs if len(self.RCJKI.currentFont.get(x))]
            else:
                return [x for x in lockedGlyphs if len(self.RCJKI.currentFont.get(x))]
            # return getFilteredList(option1, l, lockedGlyphs)

        elif option2 == "that are empty":
            if glyphtype == "characterGlyph":
                if option1 == "All those":
                    return [x for x in allGlyphs if not self.RCJKI.currentFont.get(x)._deepComponents and not len(self.RCJKI.currentFont.get(x))]
                else:
                    return [x for x in lockedGlyphs if not self.RCJKI.currentFont.get(x)._deepComponents and not len(self.RCJKI.currentFont.get(x))]
            elif glyphtype == "deepComponent":
                if option1 == "All those":
                    return [x for x in allGlyphs if not self.RCJKI.currentFont.get(x)._deepComponents and not len(self.RCJKI.currentFont.get(x))]
                else:
                    return [x for x in lockedGlyphs if not self.RCJKI.currentFont.get(x)._deepComponents and not len(self.RCJKI.currentFont.get(x))]
            else:
                if option1 == "All those":
                    return [x for x in allGlyphs if not len(self.RCJKI.currentFont.get(x))]
                else:
                    return [x for x in lockedGlyphs if not len(self.RCJKI.currentFont.get(x))]

            # return getFilteredList(option1, l, lockedGlyphs)

        elif option2 == "that are in font":
            l = allGlyphs
            return getFilteredList(option1, l, lockedGlyphs)

        elif option2 == "that are not locked":
            pass

        elif option2 == "that are in progress":
            if option1 == "All those":
                return [x for x in allGlyphs if self.RCJKI.currentFont.get(x).markColor in [None, INPROGRESS]]
            else:
                return [x for x in lockedGlyphs if self.RCJKI.currentFont.get(x).markColor in [None, INPROGRESS]]
            # return getFilteredList(option1, l, lockedGlyphs)

        elif option2 == "that are checking 1":
            if option1 == "All those":
                return [x for x in allGlyphs if self.RCJKI.currentFont.get(x).markColor == CHECKING1]
            else:
                return [x for x in lockedGlyphs if self.RCJKI.currentFont.get(x).markColor == CHECKING1]
            # return getFilteredList(option1, l, lockedGlyphs)

        elif option2 == "that are checking 2":
            if option1 == "All those":
                return [x for x in allGlyphs if self.RCJKI.currentFont.get(x).markColor == CHECKING2]
            else:
                return [x for x in lockedGlyphs if self.RCJKI.currentFont.get(x).markColor == CHECKING2]
            # return getFilteredList(option1, l, lockedGlyphs)

        elif option2 == "that are checking 3":
            if option1 == "All those":
                return [x for x in allGlyphs if self.RCJKI.currentFont.get(x).markColor == CHECKING3]
            else:
                return [x for x in lockedGlyphs if self.RCJKI.currentFont.get(x).markColor == CHECKING3]
            # return getFilteredList(option1, l, lockedGlyphs)

        elif option2 == "that are done":
            if option1 == "All those":
                return [x for x in allGlyphs if self.RCJKI.currentFont.get(x).markColor == DONE]
            else:
                return [x for x in lockedGlyphs if self.RCJKI.currentFont.get(x).markColor == DONE]
            # return getFilteredList(option1, l, lockedGlyphs)

        else:
            return allGlyphs

    def windowCloses(self, sender):
        for w in AllWindows():
            try:
                w.close()
            except:
                pass
        for textCenter in list(self.RCJKI.textCenterWindows):
            textCenter.close()
        # if self.RCJKI.textCenterWindows is not None:
        #     self.RCJKI.textCenterWindow.close()
        if self.RCJKI.get('currentFont'):
            if self.currentFont is not None:
                if self.currentGlyph:
                    self.currentFont.saveGlyph(self.currentGlyph)
                else:
                    self.currentFont.save()
                # self.currentFont.save()
            self.RCJKI.toggleWindowController(False)
        self.RCJKI.toggleObservers(forceKill=True)

    def fontInfosCallback(self, sender):
        sheets.FontInfosSheet(self.RCJKI, self.w, (220, 225))

    def lockControllerDCButtonCallback(self, sender):
        self.lockController = sheets.LockController(self.RCJKI, self.w)
        self.lockController.open()

    def teamManagerButtonCallback(self, sender):
        self.RCJKI.teamManager = teamManager.TeamManagerController(self.RCJKI)
        self.RCJKI.teamManager.launchInterface()

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

            if len(g):
                f.insertGlyph(g, name=n)
                continue

            # g.preview.computeDeepComponents()
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

            # preview = g.computeDeepComponents(g, False)
            # for d in preview:
            #     for a in d.values():
            #         for c in a[0]:
            #            f[n].appendContour(c) 
                    


        # for n in self.RCJKI.currentFont.characterGlyphSet:
        #     g = self.RCJKI.currentFont[n]
        #     preview = g.computeDeepComponents(g, False)
        #     f.newGlyph(n)
        #     f[n].width = g.width
        #     for _, AEInstance in g._getAtomicInstanceGlyph(preview):
        #         for c in AEInstance:
        #             f[n].appendContour(c)


        f.save(os.path.join(self.RCJKI.currentFont.fontPath, "teeest.ufo"))
        
    # def loadProjectButtonCallback(self, sender):
    #     folder = getFolder()
    #     if not folder: return
    #     self.RCJKI.projectRoot = folder[0]
    #     sheets.UsersInfos(self.RCJKI, self.w)
    def loadProjectButtonCallback(self, sender):
        # folder = getFolder()
        # if not folder: return
        # self.RCJKI.projectRoot = folder[0]
        sheets.Login(self.RCJKI, self.w)

    def saveProjectButtonCallback(self, sender):
        if self.RCJKI.get('currentFont'):
            if self.currentFont is not None:
                self.currentFont.save()

    def newProjectButtonCallback(self, sender):
        if not self.RCJKI.mysql:
            folder = putFile()
            if not folder: return
            askYesNo('Would you like to create a private locker repository?', resultCallback = self.askYesNocallback)
            path = '{}.rcjk'.format(folder)
            files.makepath(os.path.join(path, 'folder.proofer'))
            self.RCJKI.projectRoot = os.path.split(path)[0]
            self.RCJKI.setGitEngine()
            self.setrcjkFiles()
        else:
            projectName = AskString('', value = "Untitled", title = "Project Name")
            bfont = bfs.BfFont(projectName)
            print("----")
            print(bfont.database_data, bfont.database_name)
            print(bfont.fontlib_data, bfont.fontlib_name)
            print("----")
            t = BF_rcjk2mysql.insert_newfont_to_mysql(self.RCJKI.bf_log, bfont, self.RCJKI.mysql)
            self.setmySQLRCJKFiles()

    def askYesNocallback(self, sender):
        self.RCJKI.privateLocker = sender

    @property
    def mysql(self):
        return self.RCJKI.mysql

    @gitCoverage()
    def setrcjkFiles(self):
        rcjkFiles = ["Select a project"]
        rcjkFiles.extend(list(filter(lambda x: x.endswith(".rcjk"), 
            os.listdir(self.RCJKI.projectRoot))))
        self.w.rcjkFiles.setItems(rcjkFiles)
        self.rcjkFilesSelectionCallback(self.w.rcjkFiles)

    def setmySQLRCJKFiles(self):
        # if self.RCJKI.mysql is None:
        if not self.RCJKI.mysql:
            rcjkFiles = []
        else:
            rcjkFiles = [x[1] for x in self.RCJKI.mysql.select_fonts()]
        rcjkFiles.append("-- insert .rcjk project")  
        self.w.rcjkFiles.setItems(rcjkFiles)
        self.rcjkFilesSelectionCallback(self.w.rcjkFiles)

    @gitCoverage()
    def reloadProjectCallback(self, sender):
        self.rcjkFilesSelectionCallback(self.w.rcjkFiles)

    def rcjkFilesSelectionCallback(self, sender):
        self.w.rcjkFiles.enable(True)
        self.currentrcjkFile = sender.getItem()
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
        # return
        if self.RCJKI.get('currentFont'):
            if self.currentFont is not None:
                self.currentFont.save()
                # self.currentFont.close()
        self.currentrcjkFile = sender.getItem() 
        # if self.currentrcjkFile is None:
        #     self.currentrcjkFile = ""
        if self.currentrcjkFile == "-- insert .rcjk project":
            paths = getFolder()
            folderpath = paths[0]
            fontname = os.path.basename(folderpath).split(".rcjk")[0]
            self.RCJKI.loadProject(folderpath, fontname)
            message("Load done")

            self.setmySQLRCJKFiles()
        elif self.currentrcjkFile == "Select a project":
            self.w.newProjectButton.enable(True)
            pass
        else:
            # self.RCJKI.dataBase = {}
            self.w.saveProjectButton.enable(True)
            self.w.fontInfos.enable(True)
            self.w.generateFontButton.enable(True)
            self.w.teamManagerButton.enable(True)
            
            self.w.textCenterButton.enable(True)
            self.w.codeEditorButton.enable(True)
            self.w.lockControllerDCButton.enable(True)
            self.w.pdfProoferButton.enable(True)
            self.w.firstFilterAtomicElement.enable(True)
            self.w.secondFilterAtomicElement.enable(True)
            self.w.firstFilterDeepComponent.enable(True)
            self.w.secondFilterDeepComponent.enable(True)
            self.w.firstFilterCharacterGlyph.enable(True)
            self.w.secondFilterCharacterGlyph.enable(True)
            self.w.atomicElementSearchBox.enable(True)
            self.w.characterGlyphSearchBox.enable(True)
            self.w.deepComponentSearchBox.enable(True)
            self.w.newAtomicElement.enable(True)
            self.w.newDeepComponent.enable(True)
            self.w.newCharacterGlyph.enable(True)
            self.w.removeAtomicElement.enable(True)
            self.w.duplicateAtomicElement.enable(True)
            self.w.removeDeepComponent.enable(True)
            self.w.duplicateDeepComponent.enable(True)
            self.w.removeCharacterGlyph.enable(True)
            self.w.duplicateCharacterGlyph.enable(True)
            # self.w.atomicElementDesignStepPopUpButton.enable(True)
            # self.w.deepComponentDesignStepPopUpButton.enable(True)
            # self.w.characterGlyphDesignStepPopUpButton.enable(True)
            
            self.RCJKI.currentFont = font.Font()
            if not self.RCJKI.mysql:
                fontPath = os.path.join(self.RCJKI.projectRoot, self.currentrcjkFile)
                if 'fontLib.json' in os.listdir(fontPath):
                    libPath = os.path.join(fontPath, 'fontLib.json')
                    with open(libPath, 'r') as file:
                        fontLib = json.load(file)
                        version = fontLib.get('robocjk.version', False)
                        if version:
                            if version > self.RCJKI._version:
                                message("Warning you are not using the good RoboCJK version")
                                return
                self.RCJKI.currentFont._init_for_git(fontPath, 
                    self.RCJKI.gitUserName, 
                    self.RCJKI.gitPassword, 
                    self.RCJKI.gitHostLocker, 
                    self.RCJKI.gitHostLockerPassword, 
                    self.RCJKI.privateLocker,
                    self.RCJKI._version
                    )
                if 'database.json' in os.listdir(fontPath):
                    with open(os.path.join(fontPath, 'database.json'), 'r', encoding = "utf-8") as file:
                        self.RCJKI.currentFont.dataBase = json.load(file)

                self.RCJKI.currentFont.deepComponents2Chars = {}
                for k, v in self.RCJKI.currentFont.dataBase.items():
                    for dc in v:
                        if dc not in self.RCJKI.currentFont.deepComponents2Chars:
                            self.RCJKI.currentFont.deepComponents2Chars[dc] = set()
                        self.RCJKI.currentFont.deepComponents2Chars[dc].add(k)
            else:
                # self.RCJKI.dataBase = True
                self.RCJKI.currentFont._init_for_mysql(self.RCJKI.bf_log, self.currentrcjkFile, self.RCJKI.mysql, self.RCJKI.mysql_userName,self.RCJKI.mysql_password, self.RCJKI.hiddenSavePath)
                self.RCJKI.currentFont.loadMysqlDataBase()
                # self.RCJKI.currentFont.dataBase
                # self.RCJKI.dataBase = self.RCJKI.currentFont.dataBase
            

            self.RCJKI.toggleWindowController()

            self.w.atomicElement.set(self.currentFont.atomicElementSet)
            self.w.deepComponent.set(self.currentFont.deepComponentSet)
            charSet = [dict(char = files.unicodeName2Char(x), name = x) for x in self.currentFont.characterGlyphSet]
            self.w.characterGlyph.set(charSet)

    def GlyphsListDoubleClickCallback(self, sender):
        items = sender.get()
        selection = sender.getSelection()
        if not selection: return
        glyphName = items[selection[0]]
        if sender == self.w.characterGlyph:
            glyphName = glyphName["name"]
        try:
            CurrentGlyphWindow().close()
        except:pass
        self.RCJKI.currentGlyph = self.currentFont[glyphName]
        openGlyphWindowIfLockAcquired(self.RCJKI, self.RCJKI.currentGlyph)

    def GlyphsListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel or self.prevGlyphName is None or self.currentFont is None: 
            return
        newGlyphName = sender.get()[sel[0]]
        if sender == self.w.characterGlyph:
            newGlyphName = newGlyphName["name"]
        if newGlyphName == self.prevGlyphName: return
        if not self.currentFont.renameGlyph(self.prevGlyphName, newGlyphName):
            if sender == self.w.characterGlyph:
                sender.set([dict(char = files.unicodeName2Char([x["name"], self.prevGlyphName][x["name"] == newGlyphName]), name = [x["name"], self.prevGlyphName][x["name"] == newGlyphName]) for x in sender.get()])
            else:
                sender.set([[x, self.prevGlyphName][x == newGlyphName] for x in sender.get()])
        else:
            self.prevGlyphName = newGlyphName
            if sender == self.w.characterGlyph:
                charSet = [dict(char = files.unicodeName2Char(x["name"]), name = x["name"]) for x in sender.get()]
                sender.set(charSet)
            self.setGlyphToCanvas(sender, self.currentGlyph)

        self.w.atomicElement.setSelection([])
        self.w.deepComponent.setSelection([])
        self.w.characterGlyph.setSelection([])

        self.w.atomicElement.set(self.currentFont.atomicElementSet)
        self.w.deepComponent.set(self.currentFont.deepComponentSet)
        charSet = [dict(char = files.unicodeName2Char(x), name = x) for x in self.currentFont.characterGlyphSet]
        self.w.characterGlyph.set(charSet)

        index = sender.get().index(newGlyphName)
        sender.setSelection([index])

    def GlyphsListSelectionCallback(self, sender):
        selected = sender.getSelection()
        if not selected: 
            if sender == self.w.atomicElement:
                self.w.atomicElementDesignStepPopUpButton.enable(False)
            elif sender == self.w.deepComponent:
                self.w.deepComponentDesignStepPopUpButton.enable(False)
            elif sender == self.w.characterGlyph:
                self.w.characterGlyphDesignStepPopUpButton.enable(False)
            return
        if sender == self.w.atomicElement:
            self.w.atomicElementDesignStepPopUpButton.enable(True)
            state = self.w.atomicElementDesignStepPopUpButton
        elif sender == self.w.deepComponent:
            self.w.deepComponentDesignStepPopUpButton.enable(True)
            state = self.w.deepComponentDesignStepPopUpButton
        elif sender == self.w.characterGlyph:
            self.w.characterGlyphDesignStepPopUpButton.enable(True)
            state = self.w.characterGlyphDesignStepPopUpButton


        for lists in self.lists:
            if lists != sender:
                lists.setSelection([])
        prevGlyphName = sender.get()[sender.getSelection()[0]]
        # if sender == self.w.characterGlyph:
        #     self.prevGlyphName = prevGlyphName["name"]
        #     self.RCJKI.currentFont.loadCharacterGlyph(self.prevGlyphName)
        # else:
        self.prevGlyphName = prevGlyphName
        glyph = self.currentFont[self.prevGlyphName]
        user = self.RCJKI.currentFont.glyphLockedBy(glyph)
        color = glyph.markColor
        if color is None:
            state.set(0)
        elif color == INPROGRESS:
            state.set(0)
        elif color == CHECKING1:
            state.set(1)
        elif color == CHECKING2:
            state.set(2)
        elif color == CHECKING3:
            state.set(3)
        elif color == DONE:
            state.set(4)
        else:
            state.set(0)
        # self.currentFont[self.prevGlyphName].update()
        
        glyph.createPreviewLocationsStore()
        self.setGlyphToCanvas(sender, glyph)
        # if not self.RCJKI.mysql:
        #     user = self.RCJKI.currentFont.locker.potentiallyOutdatedLockingUser(self.currentFont[self.prevGlyphName])
        # else:
        #     user = self.RCJKI.mysql.who_locked_cglyph(self.currentrcjkFile, prevGlyphName)
        # user = self.RCJKI.currentFont.glyphLockedBy(self.currentFont[self.prevGlyphName])
        if user: 
            self.w.lockerInfoTextBox.set('Locked by: ' + user)
        else:
            self.w.lockerInfoTextBox.set("")

    def setGlyphToCanvas(self, sender, glyph):
        if sender == self.w.atomicElement:
            self.w.atomicElementPreview.glyph = glyph
            self.w.atomicElementPreview.update()
        elif sender == self.w.deepComponent:
            self.w.deepComponentPreview.glyph = glyph
            self.w.deepComponentPreview.update()
        elif sender == self.w.characterGlyph:
            self.w.characterGlyphPreview.glyph = glyph
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
        # self.RCJKI.currentFont.locker.batchLock([self.RCJKI.currentFont[name]])
        # self.RCJKI.currentFont.batchLockGlyphs([self.RCJKI.currentFont[name]])
        self.w.deepComponent.setSelection([])
        self.w.deepComponent.set(self.currentFont.deepComponentSet)

    def newAtomicElementCallback(self, sender):
        name = self.dumpName('atomicElement', self.currentFont.atomicElementSet)
        self.currentFont.newGlyph('atomicElement', name)
        # self.RCJKI.currentFont.locker.batchLock([self.RCJKI.currentFont[name]])
        # self.RCJKI.currentFont.batchLockGlyphs([self.RCJKI.currentFont[name]])
        self.w.atomicElement.setSelection([])
        self.w.atomicElement.set(self.currentFont.atomicElementSet)

    def duplicateAtomicElementCallback(self, sender):
        newGlyphName = self._duplicateGlyph(self.w.atomicElement, self.RCJKI.currentFont.atomicElementSet)
        if newGlyphName:
            # self.prevGlyphName = newGlyphName
            index = self.currentFont.atomicElementSet.index(newGlyphName)
            self.w.atomicElement.setSelection([])
            self.w.atomicElement.set(self.currentFont.atomicElementSet)
            self.w.atomicElement.setSelection([index])

    def duplicateDeepComponentCallback(self, sender):
        newGlyphName = self._duplicateGlyph(self.w.deepComponent, self.RCJKI.currentFont.deepComponentSet)
        if newGlyphName:
            # self.prevGlyphName = newGlyphName
            index = self.currentFont.deepComponentSet.index(newGlyphName)
            self.w.deepComponent.setSelection([])
            self.w.deepComponent.set(self.currentFont.deepComponentSet)
            self.w.deepComponent.setSelection([index])

    def duplicateCharacterGlyphCallback(self, sender):
        newGlyphName = self._duplicateGlyph(self.w.characterGlyph, self.RCJKI.currentFont.characterGlyphSet)
        if newGlyphName:
            # self.prevGlyphName = newGlyphName
            index = self.currentFont.characterGlyphSet.index(newGlyphName)
            self.w.characterGlyph.setSelection([])
            self.w.characterGlyph.set([dict(char = files.unicodeName2Char(x), name = x) for x in self.currentFont.characterGlyphSet])
            self.w.characterGlyph.setSelection([index])

    def _duplicateGlyph(self, UIList, glyphset):
        sel = UIList.getSelection()
        if not sel: return False
        glyphName = UIList[sel[0]]
        if UIList == self.w.characterGlyph:
            glyphName = glyphName["name"]
        glyph = self.currentFont[glyphName]
        # user = self.RCJKI.currentFont.locker.potentiallyOutdatedLockingUser(glyph)
        user = self.RCJKI.currentFont.glyphLockedBy(glyph)
        glyphtype = glyph.type
        # if user != self.RCJKI.currentFont.locker._username:
        if user != self.RCJKI.currentFont.lockerUserName:
            PostBannerNotification(
                'Impossible', "You must lock the glyph before"
                )
            return False
        glyphSet = glyphset
        message = f"Duplicate '{glyphName}' as:"
        i = 0
        while True:
            if glyphtype == "deepComponent":
                newName = "%s%s"%(glyphName[:-2], str(i).zfill(2))    
            else:
                newName = "%s.alt%s"%(glyphName, str(i).zfill(2))
            if newName not in glyphSet:
                break
            i += 1
        newGlyphName = AskString(message, value = newName, title = "Duplicate Glyph")
        if newGlyphName is None: return False
        if newGlyphName in glyphset: 
            PostBannerNotification(
                'Impossible', "'%s' already exist"%newGlyphName
                )
            return False
        self.RCJKI.currentFont.duplicateGlyph(glyphName, newGlyphName)
        # self.RCJKI.currentFont.locker.batchLock([self.RCJKI.currentFont[newGlyphName]])
        self.RCJKI.currentFont.batchLockGlyphs([self.RCJKI.currentFont[newGlyphName]])
        return newGlyphName

    def removeGlyph(self, UIList, glyphset, glyphTypeImpacted):
        sel = UIList.getSelection()
        if not sel: return False
        glyphName = UIList[sel[0]]
        # user = self.RCJKI.currentFont.locker.potentiallyOutdatedLockingUser(self.currentFont[glyphName])
        glyph = self.currentFont[glyphName]
        user = self.RCJKI.currentFont.glyphLockedBy(glyph)
        # if user != self.RCJKI.currentFont.locker._username:
        if user != self.RCJKI.currentFont.lockerUserName:
            PostBannerNotification(
                'Impossible', "You must lock the glyph before"
                )
            return False
        glyphType = glyph.type
        GlyphsthatUse = set()
        if not self.RCJKI.currentFont.mysqlFont:
            if glyphType != 'characterGlyph':
                for name in glyphset:
                    glyph = self.RCJKI.currentFont.get(name)
                    if glyphType == 'atomicElement':
                        d =  glyph._deepComponents
                    elif glyphType == 'deepComponent':
                        d =  glyph._deepComponents
                    for ae in d:
                        if ae["name"] == glyphName:
                            GlyphsthatUse.add(name)
        if not len(GlyphsthatUse):
            message = f"Are you sure you want to delete '{glyphName}'? This action is not undoable"
            answer = AskYesNoCancel(
                message, 
                title='Remove Glyph', 
                default=-1, 
                informativeText="",
                )
            if answer != 1: return False
            else:
                self.RCJKI.currentFont.removeGlyph(glyphName)
        else:
            GlyphsUsed = ""
            for name in list(GlyphsthatUse)[:30]:
                GlyphsUsed += "\n\t-" + name 
            if len(GlyphsthatUse) > 30:
                GlyphsUsed += "\n\t..."
            informativeText = f"'{glyphName}' is use in {len(GlyphsthatUse)} {glyphTypeImpacted}{['', 's'][len(GlyphsthatUse) != 1]}:{GlyphsUsed}"
            message = f"Are you sure you want to delete '{glyphName}'? This action is not undoable"
            answer = AskYesNoCancel(
                message, 
                title='Remove Glyph', 
                default=-1, 
                informativeText=informativeText,
                )
            if answer != 1: return False
            else:
                print("-----------")
                print(f"{GlyphsthatUse} will be impacted by the deletion of '{glyphName}'")
                print("-----------")
                self.RCJKI.currentFont.removeGlyph(glyphName)
        return True

    def removeAtomicElementCallback(self, sender):
        remove = self.removeGlyph(self.w.atomicElement, self.RCJKI.currentFont.deepComponentSet, "deepComponent")
        if remove:
            self.w.atomicElement.setSelection([])
            self.w.atomicElement.set(self.currentFont.atomicElementSet)
            self.prevGlyphName = ""
            self.setGlyphToCanvas(self.w.atomicElement, self.currentGlyph)
            self.w.lockerInfoTextBox.set("")

    def removeDeepComponentCallback(self, sender):
        remove = self.removeGlyph(self.w.deepComponent, self.RCJKI.currentFont.characterGlyphSet, "characterGlyph")
        if remove:
            self.w.deepComponent.setSelection([])
            self.w.deepComponent.set(self.currentFont.deepComponentSet)
            self.prevGlyphName = ""
            self.setGlyphToCanvas(self.w.deepComponent, self.currentGlyph)
            self.w.lockerInfoTextBox.set("")

    def removeCharacterGlyphCallback(self, sender):
        sel = self.w.characterGlyph.getSelection()
        if not sel: return
        glyphName = self.w.characterGlyph[sel[0]]["name"]
        # user = self.RCJKI.currentFont.locker.potentiallyOutdatedLockingUser(self.currentFont[glyphName])
        user = self.RCJKI.currentFont.glyphLockedBy(self.currentFont[glyphName])
        # if user != self.RCJKI.currentFont.locker._username:
        if user != self.RCJKI.currentFont.lockerUserName:
            PostBannerNotification(
                'Impossible', "You must lock the glyph before"
                )
            return
        glyphType = self.RCJKI.currentFont[glyphName].type
        GlyphsthatUse = set()
        for name in self.RCJKI.currentFont.characterGlyphSet:
            glyph = self.RCJKI.currentFont[name]
            for compo in glyph.components:
                if glyphName == compo.baseGlyph :
                    GlyphsthatUse.add(name)
        if not len(GlyphsthatUse):
            message = f"Are you sure you want to delete '{glyphName}'? This action is not undoable"
            answer = AskYesNoCancel(
                message, 
                title='Remove Glyph', 
                default=-1, 
                informativeText="",
                )
            if answer != 1: return
            else:
                self.RCJKI.currentFont.removeGlyph(glyphName)
        else:
            GlyphsUsed = ""
            for name in list(GlyphsthatUse)[:30]:
                GlyphsUsed += "\n\t-" + name 
            if len(GlyphsthatUse) > 30:
                GlyphsUsed += "\n\t..."
            informativeText = f"'{glyphName}' is use in {len(GlyphsthatUse)} characterGlyph{['', 's'][len(GlyphsthatUse) != 1]}:{GlyphsUsed}"
            message = f"Are you sure you want to delete '{glyphName}'? This action is not undoable"
            answer = AskYesNoCancel(
                message, 
                title='Remove Glyph', 
                default=-1, 
                informativeText=informativeText,
                )
            if answer != 1: return
            else:
                print("-----------")
                print(f"{GlyphsthatUse} will be impacted by the deletion of '{glyphName}'")
                print("-----------")
                self.RCJKI.currentFont.removeGlyph(glyphName)
        self.w.characterGlyph.setSelection([])
        self.w.characterGlyph.set([dict(char = files.unicodeName2Char(x), name = x) for x in self.currentFont.characterGlyphSet])
        self.prevGlyphName = ""
        self.setGlyphToCanvas(self.w.characterGlyph, self.currentGlyph)
        self.w.lockerInfoTextBox.set("")

    def dumpName(self, glyphType, sets):
        index = 0
        while True:
            name = "%s%s"%(glyphType, str(index).zfill(5))
            if not name in sets:
                return name
            index+=1

class ImportDeepComponentFromAnotherCharacterGlyph:

    def updateView(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.w.canvas.update()
        return wrapper

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.w = FloatingWindow((200, 150), "Import DC From CG")
        self.refGlyph = None
        self.index = None
        self.w.searchGlyph = SearchBox(
            (10, 10, -10, 20),
            callback = self.searchGlyphCallback
            )
        self.w.deepComponentList = List(
            (10, 40, 50, -10),
            [],
            doubleClickCallback = self.deepComponentListDoubleClickCallback,
            selectionCallback = self.deepComponentListSelectionCallback
            )
        self.w.canvas = CanvasGroup(
            (60, 40, -0, -0), 
            delegate = self
            )

    def open(self):
        self.w.open()

    def close(self):
        self.w.close()

    @updateView
    def searchGlyphCallback(self, sender):
        try:
            name = files.unicodeName(sender.get())
        except:
            name = str(sender.get())
        if not set([name]) & self.RCJKI.currentFont.staticCharacterGlyphSet():
            return
        self.charName = name
        self.refGlyph = self.RCJKI.currentFont[name]
        # self.refGlyph.preview.computeDeepComponents(update = False)
        self.deepComponents = self.refGlyph._deepComponents
        self.glyphVariations = self.refGlyph._glyphVariations
        self.deepComponentsName = [chr(int(dc["name"].split("_")[1], 16)) for dc in self.deepComponents]
        self.w.deepComponentList.set(self.deepComponentsName)

    @updateView
    def deepComponentListDoubleClickCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            self.index = None
            return
        self.index = sel[0]
        dc = copy.deepcopy(self.deepComponents[self.index])
        self.RCJKI.currentGlyph.addDeepComponentNamed(dc.name, dc)

        if len(self.glyphVariations) == len(self.RCJKI.currentGlyph._glyphVariations):
            for i, variation in enumerate(self.RCJKI.currentGlyph._glyphVariations):
                dc = copy.deepcopy(self.glyphVariations[i].deepComponents[self.index])
                self.RCJKI.currentGlyph._glyphVariations[i].deepComponents[-1].set(dc._toDict())

        self.RCJKI.updateDeepComponent()

    def draw(self):
        if self.refGlyph is None: return
        mjdt.save()
        mjdt.translate(20, 21)
        mjdt.scale(.09)
        # loc = {}
        # if self.refGlyph.selectedSourceAxis:
            # loc = {self.refGlyph.selectedSourceAxis:1}
        for i, atomicElement in enumerate(self.refGlyph.preview({}, forceRefresh=False)):
            if i == self.index:
                mjdt.fill(.7, 0, .15, 1)
            else:
                mjdt.fill(0, 0, 0, 1)
            mjdt.drawGlyph(atomicElement.glyph)
        mjdt.restore()

    @updateView
    def deepComponentListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            self.index = None
            return
        self.index = sel[0]
