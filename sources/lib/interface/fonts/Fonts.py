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
from vanilla import *
from vanilla.dialogs import message
from mojo.glyphPreview import GlyphPreview
from mojo.roboFont import *
from mojo.UI import AccordionView
from AppKit import NSColor
import shutil
from imp import reload

import os, json, subprocess, datetime, Helpers, getpass, time

reload(Helpers)
from Helpers import makepath, GitHelper, unique, deepolation , normalizeUnicode

class Fonts(Group):

    def __init__(self, posSize, interface):
        super(Fonts, self).__init__(posSize)
        self.ui = interface

        self.fontTextBox = TextBox((0,0,-0,20), 
                'UFO(s)',
                sizeStyle = "small")

        self.fontList = []
        self.fonts_list = List((0,20,-0,-0), 
                self.fontList,
                selectionCallback = self._fonts_list_selectionCallback,
                drawFocusRing = False)

        # self.getMiniFont = SquareButton((0,-30,-0,-0),
        #         "Get Mini Font",
        #         sizeStyle = "small",
        #         callback = self._getMiniFont_callback)

        # self.injectBack = SquareButton((0,-30,-0,-0),
        #         "Inject Back",
        #         sizeStyle = "small",
        #         callback = self._injectBack_callback)
        # self.injectBack.show(False)

    def _fonts_list_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            self.ui.glyphset = []
        else:
            self.ui.font = self.ui.fonts[sender.get()[sel[0]]]
            self.ui.storageFont = self.ui.font2Storage[self.ui.font]
            self.ui.glyphset = self.ui.font.lib['public.glyphOrder']
        
        self.ui.w.font_Group.glyphLists.set_glyphset_List()
        self.ui.w.deepComponentGroup.creator.storageFont_Glyphset.set_glyphset_List()
        # self.ui.setLayer_List()

    # def _getMiniFont_callback(self, sender):
    #     GetMiniFont_Sheet(self.ui)

    # def _injectBack_callback(self, sender):
    #     InjectBack(self.ui)

# class InjectBack():

#     def __init__(self, interface):
#         self.ui = interface
#         self.rdir = self.ui.projectPath
#         self.injectBack()

#     def writeJsonFile(self, name):
#         path = os.path.join(self.rdir, f"resources/{name}.json")
#         makepath(path)
#         myFile = open(path, 'w')
#         d = json.dumps(getattr(self, name), indent=4, separators=(',', ':'))
#         myFile.write(d)
#         myFile.close()

#     def injectBack(self):
#         git = GitHelper(self.rdir)
#         git.pull()
#         user = git.user()

#         dt = datetime.datetime.today()
#         stamp = list(self.ui.fonts.keys())[0].split("-")[1]

#         WIPPath = os.path.join(self.rdir, "resources/WIP_DCEditor.json")
#         self.WIP_DCEditor = json.load(open(WIPPath, "r"))

#         fontsLinkPath = os.path.join(self.rdir, "Temp/Fonts_Link.json")
#         self.Fonts_Link = json.load(open(fontsLinkPath, "r"))

#         fontsList = []
#         fonts = {}
#         font2Storage = {}

#         for tempFontName, tempFont, in self.ui.fonts.items():

#             fontName = self.Fonts_Link["linkFontsName"][tempFontName]
#             fontPath = self.ui.projectPath + "/Design/%s.ufo"%fontName
#             font = OpenFont(fontPath, showUI = False)

#             storageTempFontName = self.Fonts_Link["font2storage"][tempFontName]

#             storageFontName = self.Fonts_Link["linkFontsName"][storageTempFontName]
#             storageFontPath = self.ui.projectPath + "/Storage/%s.ufo"%storageFontName
#             storageFont = OpenFont(storageFontPath, showUI = False)

#             for glyph in tempFont:
#                 font[glyph.name] = glyph

#             for glyph in self.ui.font2Storage[tempFont]:
#                 storageFont.newGlyph(glyph.name)
#                 storageFont[glyph.name] = glyph

#                 for layer in glyph.layers:
#                     if layer.layerName not in [layer.name for layer in storageFont.layers]:
#                         storageFont.newLayer(layer.layerName)
#                         storageFont.getLayer(layer.layerName).insertGlyph(layer)

#             if "deepComponentsGlyph" in self.ui.font2Storage[tempFont].lib:
#                 if "deepComponentsGlyph" not in storageFont.lib:
#                     storageFont.lib['deepComponentsGlyph'] = {}
#                 for k, v in self.ui.font2Storage[tempFont].lib['deepComponentsGlyph'].items():
#                     storageFont.lib['deepComponentsGlyph'][k] = v

#             fontsList.append(fontName)
#             fonts[fontName] = font
#             font2Storage[font] = storageFont

#             font.save()
#             storageFont.save()

#         self.ui.fontList = fontsList
#         self.ui.fonts = fonts
#         self.ui.font2Storage = font2Storage

#         self.ui.font = fonts[fontsList[0]]

#         self.ui.glyphsSetDict = {font: [dict(Name = name, Char = chr(int(name[3:],16)) if name.startswith('uni') else "") for name in font.lib['public.glyphOrder']] for font in self.ui.fonts.values()}

#         git.commit('DONE: ' + stamp)
#         git.push()

#         self.ui._setUI()
#         self.ui.w.fontsGroup.fonts_list.setSelection([0])
#         self.ui.w.fontsGroup.injectBack.show(False)
#         self.ui.w.fontsGroup.getMiniFont.show(True)

#         shutil.rmtree(self.ui.projectPath+'/Temp')

#         del self.WIP_DCEditor[stamp]
#         self.writeJsonFile("WIP_DCEditor")


# class GetMiniFont_Sheet():

#     def __init__(self, interface):
#         self.ui = interface
#         self.w = Sheet((200, 250), self.ui.w)

#         self.w.deepComponents_textBox = TextBox((10, 10, -10, 20), 
#             "Deep Components", 
#             sizeStyle = "regular", 
#             alignment = "center")

#         self.selectedMiniFontOption = None
#         self.w.radioGroup = RadioGroup((10, 40, -10, 20), 
#             ["Editor", "Instantiator"],
#             isVertical = False,
#             sizeStyle="small",
#             callback = self._radioGroup_callback)

#         self.w.searchBox = SearchBox((10, 70, -10, 20),
#             placeholder = "Char/Name",
#             sizeStyle = "small",
#             callback = self._searchBox_callback)
#         self.w.searchBox.show(0)

#         self.w.GlyphPreview = GlyphPreview((0, 105, -0, -30))

#         self.selectedGlyph = None
#         self.selectedGlyphName = None

#         self.w.closeButton = Button((10, -30, 30, -10), 
#             "X",
#             callback = self._closeButtonCallback,
#             sizeStyle = "small")

#         self.w.getMiniFont_Button = Button((50, -30, -10, -10), 
#             "Get Mini Font", 
#             callback = self._getMiniFont_Button_callback,
#             sizeStyle = "small")

#         deepCompoEditorData_path = "/Users/gaetanbaehr/Documents/BlackFoundry/TYPE/OTHER/git/TestRoboCJK2/settings/TEMP_deepComponentAxisCompo2charsAGB1_FULL_Edit.json"
#         self.deepCompoEditorData = json.load(open(deepCompoEditorData_path, "r"))
        
#         Helpers.setDarkMode(self.w, self.ui.darkMode)

#         self.w.open()

#     def _closeButtonCallback(self, sender):
#         self.w.close()

#     def _radioGroup_callback(self, sender):
#         self.w.searchBox.show(1)
#         if not sender.get():
#             self.selectedMiniFontOption = self.deepCompoEditorData
#         else:
#             self.selectedMiniFontOption = self.ui.glyphCompositionData

#     def _searchBox_callback(self, sender):
#         string = sender.get()
#         if not string: return
#         try:
#             if string.startswith("uni"):
#                 self.selectedGlyphName = string

#             elif len(string) == 1:
#                 self.selectedGlyphName = "uni"+normalizeUnicode(hex(ord(string))[2:].upper())

#             self.selectedGlyph = self.ui.font[self.selectedGlyphName]
#         except:
#             self.selectedGlyph = None
#             self.selectedGlyphName = None

#         self.w.GlyphPreview.setGlyph(self.selectedGlyph)

#     def _getMiniFont_Button_callback(self, sender):
#         if self.selectedMiniFontOption is None:
#             message("Warning there is no seleted option")
#             return

#         if self.selectedGlyphName is None:
#             message("Warning there is no chosen glyph")
#             return

#         GetMiniFont(self.ui, self.selectedGlyphName, self.selectedMiniFontOption, self)

# class GetMiniFont():

#     def __init__(self, interface, characterName, database, controller):
#         self.ui = interface
#         self.characterName = characterName
#         self.database = database
#         self.c = controller
#         self.rdir = self.ui.projectPath
#         self.makeMiniFonts()

#     def writeJsonFile(self, name):
#         path = os.path.join(self.rdir, f"resources/{name}.json")
#         makepath(path)
#         myFile = open(path, 'w')
#         d = json.dumps(getattr(self, name), indent=4, separators=(',', ':'))
#         myFile.write(d)
#         myFile.close()

#     def makeMiniFonts(self):
#         f = self.ui.font
#         if 'temp' in f.path:
#             message("ERROR: you are tring to get mini font over a mini font")
#             return
        
#         git = GitHelper(self.rdir)
#         if not git.pull(): return
#         user = git.user()

#         fontsPaths = [font.path for font in self.ui.fonts.values()]

#         dt = datetime.datetime.today()
#         stamp = str(dt.year) + str(dt.month) + str(dt.day) + "_" + str(''.join(user[:-1].decode('utf-8').split(' ')))

#         WIPPath = os.path.join(self.rdir, "resources/WIP_DCEditor.json")
#         makepath(WIPPath)

#         if not os.path.exists(WIPPath):
#             self.WIP_DCEditor = {}  
#             self.writeJsonFile("WIP_DCEditor")

#         self.WIP_DCEditor = json.load(open(WIPPath, "r"))

#         if self.characterName in self.WIP_DCEditor:
#             message("This glyph is lock, please choose another one")
#             return

#         self.Fonts_Link = {}
#         fontsLinkPath = os.path.join(self.rdir, "Temp/Fonts_Link.json")
#         makepath(fontsLinkPath)

#         self.Fonts_Link["font2storage"] = {}
#         self.Fonts_Link["linkFontsName"] = {}

#         mini_glyphSet = ["uni"+normalizeUnicode(hex(ord(char))[2:].upper()) for variants in self.database[chr(int(self.characterName[3:],16))] for char in variants]        

#         self.WIP_DCEditor[stamp] = mini_glyphSet

#         self.writeJsonFile("WIP_DCEditor")
 
#         fontsList = []
#         fonts = {}
#         font2Storage = {}

#         for fontName, font in self.ui.fonts.items():
#             ######### UFO #########
#             familyName, styleName = font.info.familyName, font.info.styleName

#             tempFont = NewFont(familyName = "Temp %s"%familyName, styleName = styleName, showInterface = False)
#             tempFont.info.unitsPerEm = 1000

#             for name in mini_glyphSet:
#                 tempFont.newGlyph(name)
#                 tempFont[name] = font[name]

#             tempFont.glyphOrder = mini_glyphSet

#             tempFontName = "temp-%s-%s"%(stamp, tempFont.info.styleName)
#             tempPath = os.path.join(self.rdir, "Temp/%s.ufo" % tempFontName)
#             makepath(tempPath)
#             tempFont.save(tempPath)

#             ######### STORAGE UFO ########
#             storageFont = self.ui.font2Storage[font]
#             familyName, styleName = font.info.familyName, font.info.styleName

#             tempStorageGlyphSet = list(filter(lambda x: x.startswith(self.characterName[3:]), storageFont.keys()))
#             storageTempFont = NewFont(familyName = "Storage Temp %s"%familyName, styleName = styleName, showInterface = False)
#             storageTempFont.info.unitsPerEm = 1000

#             ########################################
#             ######## WRITE STORAGE FONT LIB ########
#             ########################################

#             for name in tempStorageGlyphSet:
#                 storageTempFont.newGlyph(name)
#                 storageTempFont[name] = storageFont[name]

#             storageTempFont.glyphOrder = tempStorageGlyphSet

#             storageTempFontName = "storageTemp-%s-%s"%(stamp, storageTempFont.info.styleName)

#             self.Fonts_Link["linkFontsName"][tempFontName] = fontName
#             self.Fonts_Link["linkFontsName"][storageTempFontName] = storageFont.path.split("/")[-1][:-4]

#             self.Fonts_Link["font2storage"][tempFontName] = storageTempFontName

#             storageTempPath = os.path.join(self.rdir, "Temp/%s.ufo" % storageTempFontName)
#             makepath(storageTempPath)
#             storageTempFont.save(storageTempPath)

#             fonts[tempFontName] = tempFont
#             fontsList.append(tempFontName)
#             font2Storage[tempFont] = storageTempFont

#         self.ui.fontList = fontsList
#         self.ui.fonts = fonts
#         self.ui.font2Storage = font2Storage

#         self.ui.font = fonts[fontsList[0]]

#         self.ui.glyphsSetDict = {font: [dict(Name = name, Char = chr(int(name[3:],16)) if name.startswith('uni') else "") for name in font.lib['public.glyphOrder']] for font in self.ui.fonts.values()}

#         open(fontsLinkPath, "w").write(json.dumps(self.Fonts_Link))

#         if not git.commit('TO DO: ' + stamp): return
#         git.push()

#         stop = time.time()

#         self.c.w.close()
#         self.ui._setUI()
#         self.ui.w.fontsGroup.fonts_list.setSelection([0])
#         self.ui.w.fontsGroup.injectBack.show(True)
#         self.ui.w.fontsGroup.getMiniFont.show(False)
        


"""
EDITOR
    - mini ufo
    - mini storate ufo
    - WIP {char:[chars]}
    - DONE



INSTANTIATOR
"""
"""
class GetMiniFont():

    def __init__(self, controller):
        self.c = controller
        self.rdir = self.c.projectPath
        self.makeMiniFonts()

    def writeJsonFile(self, name):
        path = os.path.join(self.rdir, f"resources/{name}.json")
        makepath(path)
        myFile = open(path, 'w')
        d = json.dumps(getattr(self, name), indent=4, separators=(',', ':'))
        myFile.write(d)
        myFile.close()

    def findBasesInvolved(self, miniGlyphSet, compo2chars, sel):
        bases = unique([char for n in sel if n in compo2chars for char in compo2chars[n] if char not in miniGlyphSet])
        miniGlyphSet.extend(bases)
        return bases

    def findCompoInvolved(self, miniGlyphSet, char2compo, bases):      
        compos = unique([compo for b in bases for compo in char2compo[b] if compo not in miniGlyphSet])
        miniGlyphSet.extend(compos)
        return compos

    def makeMiniFonts(self):
        # f = self.c.font
        # if 'temp' in f.path:
        #     message("ERROR: you are tring to get mini font over a mini font")
        #     return

        # git = GitHelper(self.rdir)
        # if not git.pull(): return
        # user = git.user()

        # dt = datetime.datetime.today()
        # stamp = str(dt.year) + str(dt.month) + str(dt.day) + "_" + str(''.join(user[:-1].decode('utf-8').split(' ')))
        # fontsPaths = [self.rdir+e for e in self.c.mastersPaths]

        # s = list(f.selection)
        # if not len(s):
        #     message("ERROR: There are no selected glyph(s)")
        #     return
        
        #################################
        sel = unique([c.baseGlyph for n in s for c in f[n].components])

        self.char2compo = {g.name:[c.baseGlyph for c in g.components] for g in f}

        self.compo2chars = {}
        for char, compos in self.char2compo.items():
            for c in compos:
                if c not in self.compo2chars:
                    self.compo2chars[c] = []
                if char not in self.compo2chars[c]:
                    self.compo2chars[c].append(char)

        self.writeJsonFile("char2compo")
        self.writeJsonFile("compo2chars")
        ##################################

        self.key2radicals = {}
        self.key2strokes_radicals = {}
        self.nbStrokes2keys2radicals = {}
        radicals = []
        keys = []
        self.unusedComponents = []

        for g in f:
            if '_' not in g.name:
                continue
            if g.name not in self.compo2chars:
                self.unusedComponents.append(g.name)
            uni = g.name.split('_')[0]
            nbStrokes = ''
            for c in g.name.split('_')[0]:
                try:
                    nbStrokes += str(int(c))
                except:
                    pass
            if uni not in self.key2radicals and uni not in self.key2strokes_radicals:
                self.key2radicals[uni] = [g.name]
                self.key2strokes_radicals[uni] = [(int(nbStrokes), g.name)]

            elif uni in self.key2radicals and g.name not in self.key2radicals[uni] \
                and uni in self.key2strokes_radicals and (int(nbStrokes), g.name) not in self.key2strokes_radicals[uni]:
                self.key2radicals[uni].append(g.name)
                self.key2strokes_radicals[uni].append((int(nbStrokes), g.name))

        for uni, strokes_radicals in self.key2strokes_radicals.items():
            for (nbStrokes, radical) in strokes_radicals:
                if int(nbStrokes) not in self.nbStrokes2keys2radicals:
                    self.nbStrokes2keys2radicals[int(nbStrokes)] = {uni:[radical]}
                elif uni not in self.nbStrokes2keys2radicals[int(nbStrokes)]:
                    self.nbStrokes2keys2radicals[int(nbStrokes)][uni] = [radical]
                else:
                    self.nbStrokes2keys2radicals[int(nbStrokes)][uni].append(radical)

        self.WIP = {}
        self.DONE = {}

        for name in ["unusedComponents", "key2radicals", "key2strokes_radicals", "nbStrokes2keys2radicals", "WIP", "DONE"]:
            self.writeJsonFile(name)

        char2compoPath = os.path.join(self.rdir, "resources/char2compo.json")
        makepath(char2compoPath)
        self.char2compo = json.load(open(char2compoPath, 'r'))

        compo2charsPath = os.path.join(self.rdir, "resources/compo2chars.json")
        makepath(compo2charsPath)
        self.compo2chars = json.load(open(compo2charsPath, 'r'))

        key2radicalsPath = os.path.join(self.rdir, "resources/key2radicals.json")
        makepath(key2radicalsPath)
        self.key2radicals = json.load(open(key2radicalsPath, 'r')) 

        WIPPath = os.path.join(self.rdir, "resources/WIP.json")
        makepath(WIPPath)
        self.WIP = json.load(open(WIPPath, 'r'))

        DONEPath = os.path.join(self.rdir, "resources/DONE.json")
        makepath(DONEPath)
        self.DONE = json.load(open(DONEPath, 'r')) 

        additionalRadicals = []

        for e in s:
            if e.startswith('uni'):
                n = e[3:]
                if n in self.key2radicals:
                    for e2 in self.key2radicals[n]:
                        if e2 not in s and e2 not in additionalRadicals:
                            additionalRadicals.append(e2)
        for e in sel:
            if '_' not in e: continue
            n = e.split('_')[0]
            for e2 in self.key2radicals[n]:
                if e2 not in sel and e2 not in additionalRadicals:
                    additionalRadicals.append(e2)

        miniGlyphSet = unique(s+sel+additionalRadicals)
        
        locallyUnusedComponents = []

        bases = self.findBasesInvolved(miniGlyphSet, self.compo2chars, sel+additionalRadicals)
        compos = self.findCompoInvolved(miniGlyphSet, self.char2compo, bases)

        if locallyUnusedComponents:
            print('unused components:', locallyUnusedComponents)

        for f in AllFonts():
            f.close()

        fonts = {}
        for fontPath in fontsPaths:
            f = OpenFont(fontPath, showInterface=False)
            fMask = 'mask' in [layer.name for layer in f.layers]

            f2 = NewFont(familyName='%sMini'%(f.info.familyName), styleName=f.info.styleName, showInterface=False)
            for guide in f.guidelines:
                f2.appendGuideline(position=guide.position, angle=guide.angle, name=guide.name, color=guide.color)

            if fMask:
                f2.newLayer("mask")

            for n in miniGlyphSet:
                f2[n] = f[n]
                if fMask and n in f.getLayer("mask"):
                    f2.getLayer('mask').insertGlyph(f.getLayer("mask")[n])

                if n in self.DONE and n not in self.unusedComponents:
                    a = min(1, 1.0*(1+self.DONE[n])/10)
                    f2[n].markColor = (1, 1, 0, a)

            for wipGlyphs in self.WIP.values():
                for wipGlyph in wipGlyphs:
                    if wipGlyph not in self.unusedComponents:
                        if wipGlyph in f2:
                            f2[wipGlyph].markColor = (1, 0, 0, 1)

            f2.glyphOrder = miniGlyphSet
            path = os.path.join(self.rdir, "Temp/temp-%s-%s.ufo" % (stamp, f2.info.styleName))
            makepath(path)
            fonts[path] = f2

        allWipGlyphs = []
        for wipGlyphs in self.WIP.values():
            allWipGlyphs.extend(wipGlyphs)

        for n in miniGlyphSet:
            if n not in allWipGlyphs:
                if stamp not in self.WIP:
                    self.WIP[stamp] = []
                if n not in self.WIP[stamp]:
                    self.WIP[stamp].append(n)

        if stamp in self.WIP:     
            self.writeJsonFile("WIP")
            self.writeJsonFile("DONE")

            if not git.commit('TO DO: ' + stamp): return
            git.push() 

            for path, font in fonts.items():
                font.save(path)
                font.close()
                OpenFont(path)
"""