from vanilla import *
from vanilla.dialogs import message
from mojo.roboFont import *
from mojo.UI import AccordionView, UpdateCurrentGlyphView
from mojo.events import addObserver, removeObserver
from mojo.drawingTools import *

class FlatComponent(Group):

    def __init__(self, posSize, interface):
        super(FlatComponent, self).__init__(posSize)
        self.ui = interface

        self.resetComponentInfo()
        self.suggestComponent_list = List((10,10,135,-55),
                self.ui.suggestComponent,
                allowsMultipleSelection=False, 
                selectionCallback = self._importCompo_suggestComponent_list_selectionCallback,
                drawFocusRing = False)

        self.componentVersion = []
        self.componentVersion_list = List((155,10,-10,-55),
                self.componentVersion,
                allowsMultipleSelection=False, 
                selectionCallback = self._importCompo_componentVersion_list_selectionCallback,
                drawFocusRing = False)

        self.importComponent_button = Button((10,-50,-10,20),
            "Import Component",
            sizeStyle = "small",
            callback = self._importComponent_button_callback)

        self.replaceSelectedComponent_button = Button((10,-25,-10,20),
            "Replace Selected Component",
            sizeStyle = "small",
            callback = self._replaceSelectedComponent_button_callback)

        self.ui.w.bind('close', self.windowWillClose)
        self.observer()

    def _importCompo_suggestComponent_list_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            self.resetComponentInfo()
            self.componentVersion_list.set([])
            UpdateCurrentGlyphView()
            return
        name = self.ui.suggestComponent[sel[0]]
        self.selectedComponentVersions = list(filter(lambda x: name in x, self.ui.font.keys()))
        self.componentVersion = [x[-2:] for x in self.selectedComponentVersions]
        self.componentVersion_list.set(self.componentVersion)
        UpdateCurrentGlyphView()

    def resetComponentInfo(self):
        self.selectedComponentName = ""
        self.selectedComponentOffSet = (0,0)
        self.selectedComponent = None
        self.mouseDragged_Delta = (0,0)

    def _importCompo_componentVersion_list_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            self.resetComponentInfo()
            UpdateCurrentGlyphView()
            return
        self.selectedComponentName = self.selectedComponentVersions[sel[0]]
        self.selectedComponent = self.ui.font[self.selectedComponentName]
        UpdateCurrentGlyphView()

    def _importComponent_button_callback(self, sender):
        if self.selectedComponent is None:
            message("Warning: there is no selected baseGlyph")
            return
        offsetx, offsety = self.selectedComponentOffSet
        self.ui.glyph.prepareUndo("Import %s as component"%self.selectedComponentName)
        self.ui.glyph.appendComponent(self.selectedComponentName, offset = (offsetx, offsety))
        self.ui.glyph.performUndo()
        self.ui.glyph.update()
        self.resetComponentInfo()
        UpdateCurrentGlyphView()

    def _replaceSelectedComponent_button_callback(self, sender):
        if self.selectedComponent is None:
            message("Warning: there is no selected baseGlyph")
            return
        selectedComponent = [c for c in self.ui.glyph.components if c.selected]
        if not selectedComponent:
            message("Warning: there is not selected component")
            return
        if  len(selectedComponent) != 1:
            message("Warning: there is to much seleted components")
            return
        self.ui.glyph.prepareUndo("Replace %s by %s"%(selectedComponent[0].baseGlyph, self.selectedComponentName))
        selectedComponent[0].baseGlyph = self.selectedComponentName
        self.ui.glyph.performUndo()
        self.ui.glyph.update()
        self.resetComponentInfo()
        UpdateCurrentGlyphView()

    def mouseDown(self, info):
        x, y = info['point']
        if self.selectedComponent is not None:
            offsetx, offsety = self.selectedComponentOffSet
            if self.selectedComponent.pointInside((x-offsetx, y-offsety)):
                addObserver(self, "mouseDragged", "mouseDragged")

    def mouseDragged(self, info):
        self.mouseDragged_Delta = info["delta"]
        UpdateCurrentGlyphView()

    def mouseUp(self, info):
        if self.selectedComponent is not None:
            x, y = self.selectedComponentOffSet
            x += int(self.mouseDragged_Delta[0])
            y += int(self.mouseDragged_Delta[1])
            self.selectedComponentOffSet = (x, y)
            self.mouseDragged_Delta = (0,0)
        removeObserver(self, "mouseDragged")
        UpdateCurrentGlyphView()

    def draw(self, info):
        if self.ui.glyph is None: return
        if self.selectedComponent is not None:
            save()
            fill(0, 0, 1, .7)
            offsetx, offsety = self.selectedComponentOffSet
            dragx, dragy = self.mouseDragged_Delta
            translate(offsetx, offsety)
            translate(dragx, dragy)
            drawGlyph(self.selectedComponent)
            restore()

    def windowWillClose(self, sender):
        self.observer(remove=True)
        
    def observer(self, remove = False):
        if not remove:
            addObserver(self, "draw", "draw")
            addObserver(self, "draw", "drawInactive")
            addObserver(self, "mouseDown","mouseDown")
            addObserver(self, "mouseUp", "mouseUp")
            return
        removeObserver(self, "draw")
        removeObserver(self, "drawInactive")
        removeObserver(self, "mouseDown")
        removeObserver(self, "mouseUp")
    