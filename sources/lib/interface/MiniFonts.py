from vanilla import *
from vanilla.dialogs import message
from mojo.roboFont import *
from mojo.events import addObserver, removeObserver
from mojo.UI import AccordionView, UpdateCurrentGlyphView

from drawers.MiniFont_HighlightComponentDrawer import MiniFont_HighlightComponent

from fontTools.pens.recordingPen import DecomposingRecordingPen

import os, json, subprocess, time, copy, shutil

from imp import reload
import Helpers
reload(Helpers)

from Helpers import GitHelper, unique

class MiniFonts(Group):

    def __init__(self, posSize, interface):
        super(MiniFonts, self).__init__(posSize)
        self.ui = interface

        self.ui.minifontList = []
        self.minifonts_list = List((10,10,-10,-50), 
                self.ui.minifontList,
                doubleClickCallback = self._minifonts_list_callback,
                drawFocusRing = False)

        self.ui.showWipCompo = 1
        self.showWipComponents_checkBox = CheckBox((10,-50,-10,-30),
                "Show Wip Components",
                value = self.ui.showWipCompo,
                sizeStyle = "small",
                callback = self._showWipComponents_checkBox_callback)

        self.injectBack_button = Button((10,-25,-10,-5),
                "Inject Back",
                sizeStyle = "small",
                callback = self._injectBack_button_callback)

        self.ui.w.bind('close', self.windowWillClose)
        self.observer()

    def _minifonts_list_callback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        for i in sel:
            miniFontPath = self.ui.projectPath + "/Temp/" + self.ui.minifontList[i]
            f = OpenFont(miniFontPath)

    def _showWipComponents_checkBox_callback(self, sender):
        self.ui.showWipCompo = sender.get()
        UpdateCurrentGlyphView()

    def _injectBack_button_callback(self, sender):
        InjectBack(self.ui)
        self.ui.setUIMiniFonts()
        self.ui.setMiniFontsView(collapsed = True)

    def windowWillClose(self, sender):
        self.observer(remove=True)
        
    def observer(self, remove = False):
        if not remove:
            addObserver(self, "draw", "draw")
            addObserver(self, "draw", "drawInactive")
            return
        removeObserver(self, "draw")
        removeObserver(self, "drawInactive")

    def draw(self, info):
        self.glyph = self.ui.glyph
        if self.glyph is None: return
        MiniFont_HighlightComponent(self.ui)

class InjectBack():

    def __init__(self, controller):
        self.c = controller
        self.rdir = self.c.projectPath
        self.injectBack()

    def glyphsAreSame(self, glyph1, glyph2):
        differents = []
        font1 = glyph1.getParent()
        font2 = glyph2.getParent()
        pen1 = DecomposingRecordingPen(font1)
        pen2 = DecomposingRecordingPen(font2)
        glyph1.draw(pen1)
        glyph2.draw(pen2)
        return(pen1.value == pen2.value)

    def writeJsonFile(self, name):
        myFile = open(os.path.join(self.rdir, f"resources/{name}.json"), 'w')
        d = json.dumps(getattr(self, name), indent=4, separators=(',', ':'))
        myFile.write(d)
        myFile.close()

    def injectBack(self):
        fontsPath = [self.rdir+e for e in self.c.mastersPaths]
        miniFontsPath = [self.rdir+"/Temp/"+e for e in self.c.minifontList]

        for f in AllFonts():
            if f.fileName in miniFontsPath:
                f.close()

        git = GitHelper(self.rdir)
        git.pull()

        stamps = []
        wipFonts = []
        mastersFonts = []
        for path in miniFontsPath:
            f = OpenFont(path, showUI = 0)
            wipFonts.append(f)
            stamp = path.split("/")[-1].split('-')[1]
            if stamp not in stamps:
                stamps.append(stamp)

        for path in fontsPath:
            f = OpenFont(path, showUI = 0)
            mastersFonts.append(f)

        stamp = stamps[0]
        
        if len(wipFonts) > 2:
            message('warning: more than 2 temp fonts')
            return
            
        if len(stamps) > 1:
            message('warning: more than one stampID')
            return
        
        self.WIP = json.load(open(os.path.join(self.rdir, "resources/WIP.json"), 'r'))
        self.DONE = json.load(open(os.path.join(self.rdir, "resources/DONE.json"), 'r'))

        if stamp in self.WIP:
            wipGlyphs = copy.deepcopy(self.WIP[stamp])
        else:
            message('warning: no WIP stamp found')
            return

        allWipGlyphs = []
        for wpg in self.WIP.values():
            allWipGlyphs.extend(wpg)

        checkLengthofMiniFont = list(set([len(f) for f in wipFonts]))
        if len(checkLengthofMiniFont) > 1:
            message('ERROR: the masters do not have the same number of glyphs')
            return

        addedGlyphs = unique([g.name for f in wipFonts for g in f if g.name not in allWipGlyphs])

        if addedGlyphs:
            print("Added Glyphs:", addedGlyphs)

        for n in wipGlyphs:
            if n not in self.DONE:
                self.DONE[n] = 0
            else:
                self.DONE[n] += 1

        go = list(copy.copy(mastersFonts[0].glyphOrder))

        toAddGlyphs = unique([n for f in mastersFonts for n in addedGlyphs if n not in f])
                
        for n in toAddGlyphs:      
            for f in wipFonts:
                style = f.path.split("/")[-1].split("-")[-1].split(".")[0]
                for m in mastersFonts:
                    if style in m.path:
                        master = m

                hasMask = 'mask' in [layer.name for layer in f.layers]
                if n in f.keys():
                    master.insertGlyph(f[n])
                    if hasMask and n in f.getLayer('mask'):
                        master.getLayer('mask').insertGlyph(f.getLayer('mask')[n])
                else:
                    master.newGlyph(n)
                if not self.glyphsAreSame(f[n], master[n]):
                    master[n].markColor = (1, 0, 1, .6)
                    master[n].note = "NEW"
            go.append(n)
        
        for n in wipGlyphs:
            for f in wipFonts:
                style = f.path.split("/")[-1].split("-")[-1].split(".")[0]
                for m in mastersFonts:
                    if style in m.path:
                        master = m

                hasMask = 'mask' in [layer.name for layer in f.layers]
                masterHasMask = 'mask' in [layer.name for layer in master.layers]

                master[n] = f[n]
                master[n].markColor = (1, 1, 1, 1)
                master[n].note = "Version %s" % str(self.DONE[n]+1)
                if not masterHasMask:
                    master.newLayer("mask")
                if hasMask and n in f.getLayer('mask'):
                        master.getLayer('mask').insertGlyph(f.getLayer('mask')[n])

        for n in wipGlyphs:
            self.WIP[stamp].remove(n)
            
        if self.WIP[stamp] == []:
            del self.WIP[stamp] 

        for f in mastersFonts:
            f.glyphOrder = go
            f.save()

        for f in wipFonts:
            f.close()
            
        for path in miniFontsPath:
            shutil.rmtree(path)

        self.writeJsonFile("WIP")
        self.writeJsonFile("DONE")
        
        git.commit('DONE: '+stamp)
        git.push()