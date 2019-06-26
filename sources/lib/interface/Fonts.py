from vanilla import *
from vanilla.dialogs import message
from mojo.roboFont import *
from mojo.UI import AccordionView
from AppKit import NSColor
from imp import reload

import os, json, subprocess, datetime, Helpers, getpass

reload(Helpers)
from Helpers import makepath, GitHelper, unique

class Fonts(Group):

    def __init__(self, posSize, interface):
        super(Fonts, self).__init__(posSize)
        self.ui = interface

        self.fontList = []
        self.fonts_list = List((10,10,-10,-30), 
                self.fontList,
                doubleClickCallback = self._fonts_list_doubleClickCallback,
                drawFocusRing = False)

        self.getMiniFont = Button((10,-25,-10,-5),
                "Get Mini Font",
                sizeStyle = "small",
                callback = self._getMiniFont_callback)

    def _fonts_list_doubleClickCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        for i in sel:
            fontPath = self.ui.projectPath+self.ui.fontDict[self.ui.fontList[i]]
            f = OpenFont(fontPath)

    def _getMiniFont_callback(self, sender):
        self.glyph = self.ui.glyph
        if self.glyph is None:
            message("You should have at least one selected glyph to do a minifont")
            return
        self.font = CurrentFont()
        GetMiniFont(self.ui)
        self.ui.setUIMiniFonts()
        self.ui.setMiniFontsView(collapsed = False)

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
        f = self.c.font
        if 'temp' in f.path:
            message("ERROR: you are tring to get mini font over a mini font")
            return

        git = GitHelper(self.rdir)
        if not git.pull(): return
        user = git.user()

        dt = datetime.datetime.today()
        stamp = str(dt.year) + str(dt.month) + str(dt.day) + "_" + str(''.join(user[:-1].decode('utf-8').split(' ')))
        fontsPaths = [self.rdir+e for e in self.c.mastersPaths]

        s = list(f.selection)
        if not len(s):
            message("ERROR: There are no selected glyph(s)")
            return
        
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