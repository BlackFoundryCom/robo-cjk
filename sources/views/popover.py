from mojo.events import getActiveEventTool
from vanilla import *
from AppKit import NSColor, NSNoBorder
import copy

transparentColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 1, 0)

def makeEmptyPopover(size, pos, view):
    p = Popover(size)
    if not hasattr(p, "_bindings"):
        p._bindings = {}
    offsetX, offsetY = view.offset()
    return (p, (pos.x+offsetX, pos.y+offsetY))

class EditPopover(object):
    def __init__(self, size, point):
        eventTool = getActiveEventTool()
        p,v = makeEmptyPopover(size, point, eventTool.getNSView())
        p.controller = self
        self._popover = p
        self._viewPos = v

    @property
    def relativeRect(self):
        x,y = self._viewPos
        return (x-2, y-2, 4, 4)

    @property
    def popover(self):
        return self._popover

    def close(self):
        self.popover.close()

    def open(self):
        self.popover.open(
            parentView=getActiveEventTool().getNSView(), 
            relativeRect=self.relativeRect
            )

def editTextAesthetic(element):
    element.getNSTextField().setBordered_(False)
    element.getNSTextField().setDrawsBackground_(False)
    element.getNSTextField().setFocusRingType_(1)

def buttonAsthetic(element):
    element.getNSButton().setFocusRingType_(1)
    element.getNSButton().setBackgroundColor_(transparentColor)
    element.getNSButton().setBordered_(False)

def tryfunc(func):
    def wrapper(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
            self.RCJKI.updateDeepComponent()
        except:
            pass
    return wrapper

def resetDict(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        lib = self.getLib()
        lib[self.glyph.selectedElement[0]] = self.infos
    return wrapper


class EditPopoverAlignTool(EditPopover):

    def __init__(self, RCJKI, point, glyph):
        super(EditPopoverAlignTool, self).__init__((170,150), point)
        self.RCJKI = RCJKI
        self.glyph = glyph

        lib = self.getLib()
        self.infos = lib[self.glyph.selectedElement[0]]

        y = 10
        if self.infos.get("name"):
            self.popover.Title = TextBox(
                (5, y, -5, 20), 
                self.infos["name"], 
                sizeStyle = "small", 
                alignment = 'center'
                )
            y += 25
        self.popover.xTextBox = TextBox(
            (10, y, 20, 20), 
            "x:", 
            sizeStyle = "mini"
            )
        self.popover.xEditText = EditText(
            (30, y, 30, 20), 
            self.infos["x"], 
            sizeStyle = "mini",
            callback = self.xCallback
            )
        editTextAesthetic(self.popover.xEditText)

        self.popover.scalexTextBox = TextBox(
            (70, y, 20, 20), 
            "↔:", 
            sizeStyle = "mini"
            )
        self.popover.scalexEditText = EditText(
            (90, y, 30, 20), 
            self.infos["scalex"], 
            sizeStyle = "mini",
            callback = self.scalexCallback
            )
        editTextAesthetic(self.popover.scalexEditText)

        self.popover.rotationTextBox = TextBox(
            (120, y, 20, 20), 
            "⟳:", 
            sizeStyle = "mini"
            )

        self.popover.rotationEditText = EditText(
            (140, y, 30, 20), 
            self.infos["rotation"], 
            sizeStyle = "mini",
            callback = self.rotationCallback
            )
        editTextAesthetic(self.popover.rotationEditText)
        y += 20
        self.popover.yTextBox = TextBox(
            (10, y, 20, 20), 
            "y:", 
            sizeStyle = "mini"
            )
        self.popover.yEditText = EditText(
            (30, y, 30, 20), 
            self.infos["y"], 
            sizeStyle = "mini",
            callback = self.yCallback
            )
        editTextAesthetic(self.popover.yEditText)

        self.popover.scaleyTextBox = TextBox(
            (70, y, 20, 20), 
            "↕:", 
            sizeStyle = "mini"
            )
        self.popover.scaleyEditText = EditText(
            (90, y, 30, 20), 
            self.infos["scaley"], 
            sizeStyle = "mini",
            callback = self.scaleyCallback
            )

        editTextAesthetic(self.popover.scaleyEditText)

        y+=20

        self.popover.coord = List(
            (10,y, -10, -30),
            [dict(layer = k, value = v) for k, v in self.infos["coord"].items()],
            columnDescriptions = [
                {"title": "layer", "editable" : False},
                {"title": "value"},
                ],
            showColumnTitles=False,
            allowsMultipleSelection=False,
            editCallback = self.coordEditCallback,
            rowHeight=17.0,
            drawFocusRing = False
            )
        tableView = self.popover.coord.getNSTableView()
        tableView.setUsesAlternatingRowBackgroundColors_(False)
        tableView.setBackgroundColor_(transparentColor)
        scrollView = self.popover.coord.getNSScrollView()
        scrollView.setDrawsBackground_(False)
        scrollView.setBorderType_(NSNoBorder)

        self.popover.copy = SquareButton(
            (10, -30, 75, -10),
            "copy",
            callback = self.copyCallback,
            sizeStyle = "small"
            )
        buttonAsthetic(self.popover.copy)

        self.popover.paste = SquareButton(
            (85, -30, 75, -10),
            "paste",
            callback = self.pasteCallback,
            sizeStyle = "small"
            )
        buttonAsthetic(self.popover.paste)

        self.open()

    def getLib(self):
        if self.RCJKI.isDeepComponent and self.glyph.computedAtomicInstances:
            return self.RCJKI.currentGlyph._atomicElements
            
        elif self.RCJKI.isDeepComponent and self.glyph.computedAtomicSelectedSourceInstances:
            return self.RCJKI.currentGlyph._glyphVariations[self.glyph.selectedSourceAxis]
            
        if self.RCJKI.isCharacterGlyph and self.glyph.computedDeepComponents:
            return self.RCJKI.currentGlyph._deepComponents
            
        elif self.RCJKI.isCharacterGlyph and self.glyph.computedDeepComponentsVariation:
            return self.RCJKI.currentGlyph._glyphVariations[self.glyph.selectedSourceAxis]

    def copyCallback(self, sender):
        self.RCJKI.copy = copy.deepcopy(self.infos)

    @tryfunc
    @resetDict
    def pasteCallback(self, sender):
        c = copy.deepcopy(self.RCJKI.copy)
        self.infos["scalex"] = c["scalex"]
        self.infos["scaley"] = c["scaley"]
        self.infos["rotation"] = c["rotation"]
        if self.infos.get("name") == c.get("name"):
            self.infos["coord"] = c["coord"]

    @tryfunc
    @resetDict
    def xCallback(self, sender):
        self.infos["x"] = int(sender.get())
        
    @tryfunc
    @resetDict
    def yCallback(self, sender):
        self.infos["y"] = int(sender.get())

    @tryfunc
    @resetDict
    def scalexCallback(self, sender):
        self.infos["scalex"] = float(sender.get())

    @tryfunc
    @resetDict
    def scaleyCallback(self, sender):
        self.infos["scaley"] = float(sender.get())

    @tryfunc
    @resetDict
    def rotationCallback(self, sender):
        self.infos["rotation"] = float(sender.get())

    @tryfunc
    @resetDict
    def coordEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        d = {e["layer"]:float(str(e["value"]).replace(',','.')) for e in sender.get()}
        self.infos["coord"] = d
