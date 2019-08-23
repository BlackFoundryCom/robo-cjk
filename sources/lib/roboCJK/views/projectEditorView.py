"""
Copyright 2019 Black Foundry.

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
#coding=utf-8
from imp import reload
from defconAppKit.windows.baseWindow import BaseWindowController
from vanilla import *
from mojo.roboFont import *
from mojo.drawingTools import *
from mojo.events import extractNSEvent
from mojo.UI import AllGlyphWindows, CurrentGlyphWindow
from vanilla.dialogs import getFile
from mojo.canvas import CanvasGroup
from AppKit import NSColor
import os
import random

from views.drawers import designFrameDrawer
from views.drawers import referenceViewDrawer
from utils import files
from resources import characterSets
reload(designFrameDrawer)
reload(referenceViewDrawer)
reload(files)
reload(characterSets)

class ProjectEditorWindow(BaseWindowController):
    def __init__(self, RCJKI):
        super(ProjectEditorWindow, self).__init__()
        self.RCJKI = RCJKI
        self.w = Window((200, 0, 200, 80), 'Project')
        name = 'No Open Project'
        if self.RCJKI.project:
            name = self.RCJKI.project.name
        self.w.projectNameTextBox = TextBox((0,0,200,20), name, alignment='center')
        self.w.openProjectButton = Button((0,20,200,20), 'Open', callback=self.openProject)
        self.w.newProjectButton = Button((0,40,200,20), 'New', callback=self.newProject)
        self.w.editProjectButton = Button((0,60,200,20), 'Edit', callback=self.editProject)
        self.w.bind('close', self.windowCloses)
        self.w.editProjectButton.enable(self.RCJKI.project!=None)
        self.w.open()

    def editProject(self, sender):
        # for i in range(len(AllGlyphWindows())):
        #     CurrentGlyphWindow().close()
        EditProjectSheet(self)

    def newProject(self, sender):
        self.showPutFile(['roboCJKProject'], self.RCJKI.projectEditorController.saveProject, fileName='Untitled')

    def openProject(self, sender):
        self.showGetFile(['roboCJKProject'], self.RCJKI.projectEditorController.loadProject)

    def windowCloses(self, sender):
        self.RCJKI.projectEditorController.interface = None

class EditProjectSheet():
    def __init__(self, parent):
        self.previewFont = None
        self.previewGlyph = None
        self.parent = parent
        self.parent.sheet = Sheet((600, 400), self.parent.w)

        self.parent.sheet.projectNameEditText = EditText((10, 10, -10, 20), self.parent.RCJKI.project.name, callback=self.projectNameEditTextCallback)

        segmentedElements = ["Masters", "Lockers", "Design Frame", "Reference Viewer"]
        self.parent.sheet.projectSectionsSegmentedButton = SegmentedButton((10,40,-10,20), 
                [dict(title=e, width=577/len(segmentedElements)) for e in segmentedElements],
                callback = self.projectSectionsSegmentedButtonCallback)
        self.parent.sheet.projectSectionsSegmentedButton.set(0)

        self.parent.sheet.masterGroup = Group((0,60,-0,-30))

        l = [{'FamilyName':e.split('-')[0], 'StyleName':e.split('-')[1]} for e in self.parent.RCJKI.project.masterFontsPaths]

        self.parent.sheet.masterGroup.mastersList = List((10, 10, -10, 140), 
                l,
                columnDescriptions = [{"title": "FamilyName"}, {"title": "StyleName"}],
                drawFocusRing = False)

        self.parent.sheet.masterGroup.importMastersButton = Button((10, 155, 190, 20), 
                "Import",
                sizeStyle = "small",
                callback = self.importMastersButtonCallback)

        self.parent.sheet.masterGroup.createMastersButton = Button((205, 155, 190, 20), 
                "Create",
                sizeStyle = "small",
                callback = self.createMastersButtonCallback)

        self.parent.sheet.masterGroup.removeMastersButton = Button((400, 155, -10, 20), 
                "Remove",
                sizeStyle = "small",
                callback = self.removeMastersButtonCallback)

        self.parent.sheet.masterGroup.scriptsRadioGroup = RadioGroup((10, 190, 200, 60), self.parent.RCJKI.scriptsList, callback=self.scriptsRadioGroupCallback)
        self.parent.sheet.masterGroup.scriptsRadioGroup.set(self.parent.RCJKI.scriptsList.index(self.parent.RCJKI.project.script))


        ###
        self.parent.sheet.lockerGroup = Group((0,60,-0,-30))

        
        self.parent.sheet.lockerGroup.usersList = List((10, 10, 280, 65),
                [d['user'] for d in self.parent.RCJKI.project.usersLockers['lockers']],
                selectionCallback = self.usersListSelectionCallback,
                drawFocusRing = False
                )
        self.parent.sheet.lockerGroup.charactersTextEditor = TextEditor((10, 85, -10, -40),
                                    callback=self.charactersTextEditorCallback)
        ###

        self.parent.sheet.designFrameGroup = Group((0,60,-0,-30))

        self.parent.sheet.designFrameGroup.EM_Dimension_title = TextBox((10,13,200,20), 
                "EM Dimension (FU)", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.EM_DimensionX_title = TextBox((145,13,20,20), 
                "X:", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.EM_DimensionX_editText = EditText((160,10,45,20), 
                self.parent.RCJKI.project.settings['designFrame']['em_Dimension'][0], 
                callback = self.EM_DimensionX_editText_callback,
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.EM_DimensionY_title = TextBox((235,13,20,20), 
                "Y:", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.EM_DimensionY_editText = EditText((250,10,45,20), 
                self.parent.RCJKI.project.settings['designFrame']['em_Dimension'][1],
                callback = self.EM_DimensionY_editText_callback,
                sizeStyle = "small")

        self.parent.sheet.designFrameGroup.characterFace_title = TextBox((10,43,200,20), 
                "Character Face (EM%)", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.characterFacePercent_title = TextBox((208,43,30,20), 
                "%", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.characterFace_editText = EditText((160,40,45,20), 
                self.parent.RCJKI.project.settings['designFrame']['characterFace'],
                callback = self.characterFace_editText_callback,
                sizeStyle = "small")

        self.parent.sheet.designFrameGroup.overshoot_title = TextBox((10,73,200,20), 
                "Overshoot (FU)", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.overshootOutside_title = TextBox((110,73,70,20), 
                "Outside:", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.overshootOutside_editText = EditText((160,70,45,20), 
                self.parent.RCJKI.project.settings['designFrame']['overshoot'][0],
                callback = self.overshootOutside_editText_callback,
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.overshootInside_title = TextBox((210,73,60,20), 
                "Inside:", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.overshootInside_editText = EditText((250,70,45,20), 
                self.parent.RCJKI.project.settings['designFrame']['overshoot'][1],
                callback = self.overshootInside_editText_callback,
                sizeStyle = "small")

        self.parent.sheet.designFrameGroup.horizontalLine_title = TextBox((10,103,140,20), 
                "Horizontal Line (EM%)", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.horizontalLine_slider = Slider((160,100,135,20), 
                minValue = 0, maxValue = 50, value = self.parent.RCJKI.project.settings['designFrame']['horizontalLine'], 
                sizeStyle = "small",
                stopOnTickMarks = True,
                tickMarkCount = 26,
                callback = self._horizontalLine_slider_callback)

        self.parent.sheet.designFrameGroup.verticalLine_title = TextBox((10,133,140,20), 
                "Vertical Line (EM%)", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.verticalLine_slider = Slider((160,130,135,20), 
                minValue = 0, maxValue = 50, value = self.parent.RCJKI.project.settings['designFrame']['verticalLine'], 
                sizeStyle = "small",
                stopOnTickMarks = True,
                tickMarkCount = 26,
                callback = self._verticalLine_slider_callback)

        self.parent.sheet.designFrameGroup.customsFrames_title = TextBox((10,163,200,20), 
                "Customs Frames (EM%):", 
                sizeStyle = "small")

        slider = SliderListCell(tickMarkCount=26, stopOnTickMarks=True)

        self.parent.sheet.designFrameGroup.customsFrames_list = List((10,193,285,-30),
                self.parent.RCJKI.project.settings['designFrame']['customsFrames'],
                columnDescriptions = [{"title": "Name", "width" : 75}, 
                                    {"title": "Value", "width" : 200, "cell": slider}],
                editCallback = self._customsFrames_list_editCallback,
                drawFocusRing = False)

        self.parent.sheet.designFrameGroup.addCustomsFrames_button = Button((170,-28,62,-10),
                "+",
                callback = self._addCustomsFrames_button_callback,
                sizeStyle="small")

        self.parent.sheet.designFrameGroup.removeCustomsFrames_button = Button((232,-28,62,-10),
                "-",
                callback = self._removeCustomsFrames_button_callback,
                sizeStyle="small")

        self.parent.sheet.designFrameGroup.changeFontButton = Button((-295,-30,145,-10), 
            'Change Font', callback=self.changeFontButtonCallBack, sizeStyle="small")

        self.parent.sheet.designFrameGroup.changeGlyphButton = Button((-150,-30,145,-10), 
            'Change Glyph', callback=self.changeGlyphButtonCallBack, sizeStyle="small")

        self.fontNames = list(self.parent.RCJKI.project.masterFontsPaths.keys())
        self.selectedFontIndex = 0
        if self.fontNames:
            self.getPreviewFont()
            self.getPreviewGlyph()
        else:
            self.previewGlyph = None

        self.parent.sheet.designFrameGroup.canvas = CanvasGroup((-295,0,-10,-30), 
                delegate=ProjectCanvas("DesignFrame", self))


        ####

        self.parent.sheet.referenceViewerGroup = Group((0,60,-0,-30))

        self.parent.sheet.referenceViewerGroup.FontList_comboBox = ComboBox((10, 10, 130, 18),
                files.fontsList.get(),
                sizeStyle='small')
        self.parent.sheet.referenceViewerGroup.FontList_comboBox.set(files.fontsList.get()[0])

        self.parent.sheet.referenceViewerGroup.addReferenceFont_button = Button((150, 10, 70, 20), 
                "Add", 
                sizeStyle="small",
                callback = self._addReferenceFont_button_callback)

        self.parent.sheet.referenceViewerGroup.removeReference_button = Button((225,10,70,20),
                "Remove",
                sizeStyle="small",
                callback = self._removeReference_button_callback)

        l = [{"Font": e['font']} for e in self.parent.RCJKI.project.settings['referenceViewer']]
        self.parent.sheet.referenceViewerGroup.reference_list = List((10,35,285,125),
                l,
                columnDescriptions = [{"title": "Font"}],
                selectionCallback = self._reference_list_selectionCallback,
                drawFocusRing = False)


        self.parent.sheet.referenceViewerGroup.settings = Group((10,160,295,-0))
        self.parent.sheet.referenceViewerGroup.settings.show(0)

        y = 0

        self.parent.sheet.referenceViewerGroup.settings.size_title = TextBox((0,y,100,20),
                "Size (FU)", 
                sizeStyle = "small")
        self.parent.sheet.referenceViewerGroup.settings.size_editText = EditText((-60,y,-10,20),
                "", 
                sizeStyle = "small",
                callback = self._size_editText_callback)

        self.parent.sheet.referenceViewerGroup.settings.size_slider = Slider((90,y,-65,20),
                minValue = 0,
                maxValue = 1000,
                value = 250,
                sizeStyle = "small",
                callback = self._size_slider_callback)

        y += 30
        self.parent.sheet.referenceViewerGroup.settings.color_title = TextBox((0,y,100,20),
                "Color (FU)", 
                sizeStyle = "small")
        self.parent.sheet.referenceViewerGroup.settings.color_colorWell = ColorWell((90,y-3,-10,20),
                callback=self._color_editText_callback, 
                color=NSColor.grayColor())

        y+=30
        # self.parent.sheet.referenceViewerGroup.settings.message = Helpers.SmartTextBox((0, y, -10, 50),
        #         "To move the selected font in the canvas, press command and drag",
        #         blue = 9,
        #         green = .7,
        #         sizeStyle = 12)

        self.parent.sheet.referenceViewerGroup.canvas = CanvasGroup((-295,0,-10,-10), 
                delegate=ProjectCanvas("ReferenceViewer", self))


        ###


        self.parent.sheet.masterGroup.show(1)
        self.parent.sheet.lockerGroup.show(0)
        self.parent.sheet.designFrameGroup.show(0)
        self.parent.sheet.referenceViewerGroup.show(0)

        self.parent.sheet.saveButton = Button((-160,-30, 150, 20), 'Save', callback=self.saveSheet)
        self.parent.sheet.closeButton = Button((-320,-30, 150, 20), 'Close', callback=self.closeSheet)
        self.parent.sheet.setDefaultButton(self.parent.sheet.saveButton)

        self.parent.sheet.open()

    def getPreviewFont(self):
        if self.fontNames:
            self.previewFont = self.parent.RCJKI.projectFonts[self.fontNames[self.selectedFontIndex%len(self.fontNames)]]
            self.selectedFontIndex += 1

    def getPreviewGlyph(self):
        if not self.previewFont:
            self.previewGlyph = None
            return
        self.previewGlyph = RGlyph()
        self.characterSets = characterSets.sets
        characterSet = ""

        for charset in self.characterSets[self.parent.RCJKI.project.script].values():
            characterSet += charset

        glyphNames = ["uni"+files.normalizeUnicode(hex(ord(c))[2:].upper()) for c in characterSet if "uni"+files.normalizeUnicode(hex(ord(c))[2:].upper()) in self.previewFont.keys()]
        self.previewGlyph = self.previewFont[random.choice(glyphNames)]
    
    def usersListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        user = sender.get()[sel[0]]
        userLocker = self.parent.RCJKI.collab._addLocker(user)
        glyphs = userLocker.glyphs
        chars = [chr(int(glyph[3:], 16)) for glyph in glyphs]
        chars.sort()
        self.parent.sheet.lockerGroup.charactersTextEditor.set(''.join(chars))

    def charactersTextEditorCallback(self, sender):
        chars = sender.get()
        sel = self.parent.sheet.lockerGroup.usersList.getSelection()
        if not sel: return
        user = self.parent.sheet.lockerGroup.usersList.get()[sel[0]]
        userLocker = self.parent.RCJKI.collab._addLocker(user)
        glyphs = ['uni'+files.normalizeUnicode(hex(ord(char))[2:].upper()) for char in chars]
        userLocker._clearGlyphs()
        userLocker._addGlyphs(glyphs)
        self.parent.RCJKI.project.usersLockers = self.parent.RCJKI.collab._toDict

    def projectSectionsSegmentedButtonCallback(self, sender):
        sel = sender.get()
        groups = [
            self.parent.sheet.masterGroup,
            self.parent.sheet.lockerGroup,
            self.parent.sheet.designFrameGroup,
            self.parent.sheet.referenceViewerGroup
            ]
        for i, e in enumerate(groups):
            e.show(i == sel)

        self.parent.RCJKI.projectEditorController.updateSheetUI()

    def projectNameEditTextCallback(self, sender):
        self.parent.RCJKI.project.name = sender.get()

    def closeSheet(self, sender):
        self.parent.sheet.close()

    def saveSheet(self, sender):
        self.parent.RCJKI.projectEditorController.updateProject()

    def importMastersButtonCallback(self, sender):
        getFile(messageText=u"Add new UFO to Project",
                allowsMultipleSelection=True,
                fileTypes=["ufo"],
                parentWindow=self.parent.sheet,
                resultCallback=self.importMastersCallback)

    def importMastersCallback(self, paths):
        for path in paths:
            self.parent.RCJKI.projectEditorController.importFontToProject(path)
        
        self.fontNames = list(self.parent.RCJKI.project.masterFontsPaths.keys())
        self.parent.RCJKI.projectEditorController.updateSheetUI()
        self.getPreviewFont()
        self.getPreviewGlyph()
        if self.parent.RCJKI.initialDesignController.interface:
            self.parent.RCJKI.initialDesignController.loadProjectFonts()

    def createMastersButtonCallback(self, sender):
        familyName = self.parent.RCJKI.project.name
        styleName = "Regular"

        self.parent.RCJKI.projectEditorController.createFontToProject(familyName, styleName)
        self.fontNames.append("%s-%s"%(familyName, styleName))

        self.parent.RCJKI.projectEditorController.updateSheetUI()
        self.getPreviewFont()
        self.getPreviewGlyph()
        if self.parent.RCJKI.initialDesignController.interface:
            self.parent.RCJKI.initialDesignController.loadProjectFonts()

    def removeMastersButtonCallback(self, sender):
        sel = self.parent.sheet.masterGroup.mastersList.getSelection()
        if not sel: return
        for s in sel:
            d = self.parent.sheet.masterGroup.mastersList.get()[s]
            e = d['FamilyName']+'-'+d['StyleName']
            del self.parent.RCJKI.project.masterFontsPaths[e]
        self.parent.RCJKI.projectEditorController.updateSheetUI()
        self.getPreviewFont()
        self.getPreviewGlyph()
        if self.parent.RCJKI.initialDesignController.interface:
            self.parent.RCJKI.initialDesignController.loadProjectFonts()

    def scriptsRadioGroupCallback(self, sender):
        script = self.parent.RCJKI.scriptsList[sender.get()]
        self.parent.RCJKI.project.script = script

    ###

    def EM_DimensionX_editText_callback(self, sender):
        try: self.parent.RCJKI.project.settings['designFrame']['em_Dimension'][0] = int(sender.get())        
        except: sender.set(self.parent.RCJKI.project.settings['designFrame']['em_Dimension'][0])
        self.parent.sheet.designFrameGroup.canvas.update()

    def EM_DimensionY_editText_callback(self, sender):
        try: self.parent.RCJKI.project.settings['designFrame']['em_Dimension'][1]= int(sender.get())        
        except: sender.set(self.parent.RCJKI.project.settings['designFrame']['em_Dimension'][1])
        self.parent.sheet.designFrameGroup.canvas.update()

    def characterFace_editText_callback(self, sender):
        try:
            value = int(sender.get())
            if 0 <= value <= 100:
                self.parent.RCJKI.project.settings['designFrame']['characterFace'] = value        
            else:
                sender.set(self.parent.RCJKI.project.settings['designFrame']['characterFace'])
        except: sender.set(self.parent.RCJKI.project.settings['designFrame']['characterFace'])
        self.parent.sheet.designFrameGroup.canvas.update()

    def overshootOutside_editText_callback(self, sender):
        try: self.parent.RCJKI.project.settings['designFrame']['overshoot'][1] = int(sender.get())
        except: sender.set(self.parent.RCJKI.project.settings['designFrame']['overshoot'][1])
        self.parent.sheet.designFrameGroup.canvas.update()

    def overshootInside_editText_callback(self, sender):
        try: self.parent.RCJKI.project.settings['designFrame']['overshoot'][0] = int(sender.get())        
        except: sender.set(self.parent.RCJKI.project.settings['designFrame']['overshoot'][0])
        self.parent.sheet.designFrameGroup.canvas.update()

    def _horizontalLine_slider_callback(self, sender):
        self.parent.RCJKI.project.settings['designFrame']['horizontalLine'] = int(sender.get())
        self.parent.sheet.designFrameGroup.canvas.update()

    def _verticalLine_slider_callback(self, sender):
        self.parent.RCJKI.project.settings['designFrame']['verticalLine'] = int(sender.get())
        self.parent.sheet.designFrameGroup.canvas.update()

    def _customsFrames_list_editCallback(self, sender):
        l = []
        for d in sender.get():
            d2 = {}
            for k, v in d.items():
                d2[k] = v
            l.append(d2)
        self.parent.RCJKI.project.settings['designFrame']['customsFrames'] = l
        self.parent.sheet.designFrameGroup.canvas.update()

    def _addCustomsFrames_button_callback(self, sender):
        name = "Frame%i"%len(self.parent.RCJKI.project.settings['designFrame']['customsFrames'])
        self.parent.RCJKI.project.settings['designFrame']['customsFrames'].append({"Name":name})
        self.parent.sheet.designFrameGroup.customsFrames_list.set(self.parent.RCJKI.project.settings['designFrame']['customsFrames'])
        self.parent.sheet.designFrameGroup.canvas.update()

    def _removeCustomsFrames_button_callback(self, sender):
        sel = self.parent.sheet.designFrameGroup.customsFrames_list.getSelection()
        if not sel: return
        self.parent.RCJKI.project.settings['designFrame']['customsFrames'] = [e for i, e in enumerate(self.parent.RCJKI.project.settings['designFrame']['customsFrames']) if i not in sel]
        self.parent.sheet.designFrameGroup.customsFrames_list.set(self.parent.RCJKI.project.settings['designFrame']['customsFrames'])
        self.parent.sheet.designFrameGroup.canvas.update()

    def changeFontButtonCallBack(self, sender):
        self.getPreviewFont()
        self.getPreviewGlyph()
        self.parent.sheet.designFrameGroup.canvas.getNSView()._delegate.update()

    def changeGlyphButtonCallBack(self, sender):
        self.getPreviewGlyph()
        self.parent.sheet.designFrameGroup.canvas.getNSView()._delegate.update()
    ###

    def _addReferenceFont_button_callback(self, sender):
        font = self.parent.sheet.referenceViewerGroup.FontList_comboBox.get()
        if font is None or font == "": return
        # Default values
        elem = {
            "font": font,
            "size": 400,
            "x": -500,
            "y": 40,
            "color": (0, 0, 0, .56)
        }

        self.parent.RCJKI.project.settings['referenceViewer'].append(elem)
        l = [{"Font": e['font']} for e in self.parent.RCJKI.project.settings['referenceViewer']]
        self.parent.sheet.referenceViewerGroup.reference_list.set(l)
        self.parent.sheet.referenceViewerGroup.reference_list.setSelection([len(self.parent.sheet.referenceViewerGroup.reference_list) - 1])
        self.parent.sheet.referenceViewerGroup.canvas.update()

    def _removeReference_button_callback(self, sender):
        sel = self.parent.sheet.referenceViewerGroup.reference_list.getSelection()
        if sel is None: return

        def remove(l):
            return [e for i, e in enumerate(l) if i not in sel]

        self.parent.RCJKI.project.settings['referenceViewer'] = remove(self.parent.RCJKI.project.settings['referenceViewer'])
        self.parent.sheet.referenceViewerGroup.reference_list.set({"Font": e['font'] for e in self.parent.RCJKI.project.settings['referenceViewer']})

        # self.reference_list.setSelection([len(self.s.referenceViewerList) - 1])
        self.parent.sheet.referenceViewerGroup.canvas.update()

    def _reference_list_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            return
        self.parent.sheet.referenceViewerGroup.settings.show(1)
        settings = self.parent.RCJKI.project.settings['referenceViewer'][sel[0]]
        self.parent.sheet.referenceViewerGroup.settings.size_editText.set(settings["size"])
        self.parent.sheet.referenceViewerGroup.settings.size_slider.set(settings["size"])
        colors = settings["color"]
        color = NSColor.colorWithCalibratedRed_green_blue_alpha_(
            colors[0], colors[1], colors[2], colors[3])
        self.parent.sheet.referenceViewerGroup.settings.color_colorWell.set(color)

    def _size_editText_callback(self, sender):
        sel = self.parent.sheet.referenceViewerGroup.reference_list.getSelection()
        if not sel: return
        size = self.parent.RCJKI.project.settings['referenceViewer'][sel[0]]["size"]
        try: 
            size = int(sender.get())
        except: 
            sender.set(size)
        self.parent.RCJKI.project.settings['referenceViewer'][sel[0]]["size"] = size
        self.parent.sheet.referenceViewerGroup.settings.size_slider.set(size)
        self.parent.sheet.referenceViewerGroup.canvas.update()

    def _size_slider_callback(self, sender):
        sel = self.parent.sheet.referenceViewerGroup.reference_list.getSelection()
        if not sel: return
        self.parent.RCJKI.project.settings['referenceViewer'][sel[0]]["size"] = int(sender.get())
        self.parent.sheet.referenceViewerGroup.settings.size_editText.set(self.parent.RCJKI.project.settings['referenceViewer'][sel[0]]["size"])
        self.parent.sheet.referenceViewerGroup.canvas.update()

    def _color_editText_callback(self, sender):
        sel = self.parent.sheet.referenceViewerGroup.reference_list.getSelection()
        if not sel: return
        color = sender.get()
        self.parent.RCJKI.project.settings['referenceViewer'][sel[0]]["color"] = (
            color.redComponent(),
            color.greenComponent(),
            color.blueComponent(),
            color.alphaComponent(),
        )
        self.parent.sheet.referenceViewerGroup.canvas.update()


class ProjectCanvas():
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.scale = .2
        self.translateX = 215
        self.translateY = 505
        self.previewGlyph = self.parent.previewGlyph
        self.rvd = referenceViewDrawer.ReferenceViewerDraw(self.parent.parent.RCJKI)
        self.dfv = designFrameDrawer.DesignFrameDrawer(self.parent.parent.RCJKI)
        canvasWidth = 285
        canvasHeight = 270
        
        if self.name == "ReferenceViewer":
            self.scale = .15
            self.translateX = 600
            self.translateY = 300

        elif self.previewGlyph is not None and len(self.previewGlyph):
            self.translateX = ((canvasWidth/self.scale-self.previewGlyph.width)*.5 )
            self.translateY = ((canvasHeight/self.scale-(self.previewGlyph.bounds[3]-self.previewGlyph.bounds[1]))*.5 )

    def update(self):
        self.previewGlyph = self.parent.previewGlyph
        if self.name == "ReferenceViewer":
            self.parent.parent.sheet.referenceViewerGroup.canvas.update()
        else:
            self.parent.parent.sheet.designFrameGroup.canvas.update()

    def mouseDragged(self, info):
        command = extractNSEvent(info)['commandDown']
        deltaX = info.deltaX()/self.scale
        deltaY = info.deltaY()/self.scale
        if not command:
            self.translateX += deltaX
            self.translateY -= deltaY
        elif self.parent.parent.sheet.referenceViewerGroup.reference_list.getSelection() and self.name == "ReferenceViewer":
            currentSetting = self.parent.parent.RCJKI.project.settings['referenceViewer'][self.parent.parent.sheet.referenceViewerGroup.reference_list.getSelection()[0]]
            currentSetting["x"] += deltaX
            currentSetting["y"] -= deltaY
        self.update()

    def scrollWheel(self, info):
        alt = extractNSEvent(info)['optionDown']
        if not alt: return
        scaleOld = self.scale
        delta = info.deltaY()
        sensibility = .009
        scaleOld += (delta / abs(delta) * sensibility) / self.scale
        minScale = .005
        if scaleOld > minScale:
            self.scale = scaleOld
        self.update()

    def draw(self):
        try:
            scale(self.scale, self.scale)
            translate(self.translateX,self.translateY)
            strokeWidth(.4/self.scale)

            if self.name == "ReferenceViewer":
                save()
                translate(150,550)
                save()
                stroke(0)
                fill(None)
                w = self.parent.parent.RCJKI.project.settings['designFrame']['em_Dimension'][0]
                h = self.parent.parent.RCJKI.project.settings['designFrame']['em_Dimension'][0]
                
                designFrameDrawer.DesignFrameDrawer(self.parent.parent.RCJKI).draw(glyph = self.previewGlyph, scale = self.scale)
                
                restore()

                if self.previewGlyph:
                    if self.previewGlyph.name.startswith("uni"):
                        txt = chr(int(self.previewGlyph.name[3:7],16))
                    elif self.previewGlyph.unicode: 
                        txt = chr(self.previewGlyph.unicode)
                    else:
                        txt = "a"
                else:
                    txt = "a"
                
                self.rvd.draw(txt)
                restore()

            else:
                fill(.3)
                if self.previewGlyph:
                    drawGlyph(self.previewGlyph)
                self.dfv.draw(glyph = self.previewGlyph, scale = self.scale)

        except Exception as e:
            print(e)
