from vanilla import *
# from mojo.canvas import Canvas
from mojo.UI import OpenSpaceCenter
from utils import files
from mojo.drawingTools import *

class CharacterUsingDC:

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.interface = CharacterUsingDCInterface(self.RCJKI, self)

    def characterGlyphUsing(self, code):
        characters = []
        for name in self.RCJKI.currentFont.characterGlyphSet:
            glyph = self.RCJKI.currentFont[name]
            for dc in glyph._deepComponents:
                if code in dc["name"]:
                    characters.append(name)
                    break
        return characters

    def getCodeVariants(self, char):
        if not char: return []
        var = []
        code = files.normalizeUnicode(hex(ord(char))[2:].upper())
        for name in self.RCJKI.currentFont.deepComponentSet:
            if code in name.split("_"):
                var.append(name.split("_")[2])
        return var
        
class CharacterUsingDCInterface:

    def __init__(self, RCJKI, controller):
        self.RCJKI = RCJKI
        self.c = controller
        self.char = ""
        self.charactersNamesList = []
        self.w = Window((220, 200), "Character Using DC", minSize = (200, 200))
        self.w.search = SearchBox((10, 10, 100, 20),
            callback = self.searchCallback)
        self.deepComponentList = set()
        for dcname in self.RCJKI.currentFont.deepComponentSet:
            if len(dcname.split('_')) > 1:
                self.deepComponentList.add(chr(int(dcname.split("_")[1], 16)))
        self.deepComponentList = list(self.deepComponentList)
        self.w.deepComponentList = List(
            (10, 30, 50, -10),
            self.deepComponentList,
            selectionCallback = self.deepComponentListSelectionCallback
            )
        self.w.variantList = List(
            (60, 30, 50, -10),
            [],
            selectionCallback = self.variantListSelectionCallback
            )
        self.w.characters = TextEditor(
            (110, 10, -10, -10),
            readOnly = True
            )
        # self.w.canvas = Canvas(
        #     (110, 10, -10, -100),
        #     delegate = self
        #     )

    def open(self):
        self.w.open()

    def searchCallback(self, sender):
        char = sender.get()
        if char not in self.deepComponentList: return
        self.char = char
        self.w.deepComponentList.setSelection([self.deepComponentList.index(self.char)])

    def deepComponentListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            return
        self.char = sender.get()[sel[0]]
        self.w.variantList.set(self.c.getCodeVariants(self.char))

    def variantListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            return
        index = sender.get()[sel[0]]
        code = files.normalizeUnicode(hex(ord(self.char))[2:].upper())
        self.charactersNamesList = self.c.characterGlyphUsing("%s_%s"%(code, index))
        self.characters = ""
        for name in self.charactersNamesList:
            try:
                self.characters+=chr(int(name.split(".")[0][3:], 16))
            except:
                pass
        self.w.characters.set(self.characters)
        OpenSpaceCenter(self.RCJKI.currentFont._RFont).set(self.charactersNamesList)
        # self.w.canvas.update()

    # def draw(self):
    #     save()
    #     s = .1
    #     scale(s, s)
    #     for name in self.charactersNamesList:
    #         glyph = self.RCJKI.currentFont[name]
    #         glyph.computeDeepComponents()
            
    #         self.RCJKI.drawer.drawGlyphAtomicInstance(
    #             glyph, 
    #             (0, 0, 0, 1), 
    #             s, 
    #             (0, 0, 0, 1), 
    #             view = False, 
    #             flatComponentColor = (.8, .6, 0, .7)
    #             )
    #         translate(glyph.width, 0)
    #     restore()