from vanilla import *
from mojo.canvas import CanvasGroup
from mojo.UI import UpdateCurrentGlyphView
from drawers.ProjectCanvas import ProjectCanvas
from AppKit import NSColor

from mojo.events import addObserver, removeObserver
from mojo.roboFont import *
from drawers.ReferenceViewerDrawer import ReferenceViewerDraw



from imp import reload
import Global
reload(Global)

class ReferenceViewer(Group):

    def __init__(self, posSize, interface, sheet):
        super(ReferenceViewer, self).__init__(posSize)
        self.ui = interface
        self.s = sheet

        self.FontList_comboBox = ComboBox((10, 10, 130, 18),
                Global.fontsList.get(),
                sizeStyle='small')
        self.FontList_comboBox.set(Global.fontsList.get()[0])

        self.addReferenceFont_button = Button((150, 9, 70, 20), 
                "Add", 
                sizeStyle="small",
                callback = self._addReferenceFont_button_callback)

        self.removeReference_button = Button((225,9,70,20),
                "Remove",
                sizeStyle="small",
                callback = self._removeReference_button_callback)

        self.s.reference_list_selection = []
        self.reference_list = List((10,35,285,125),
                self.s.referenceViewerList,
                columnDescriptions = [{"title": "Font"}],
                selectionCallback = self._reference_list_selectionCallback,
                drawFocusRing = False)


        self.settings = Group((10,170,295,-0))
        self.settings.show(0)

        y = 3

        self.settings.size_title = TextBox((0,y,100,20),
                "Size (FU)", 
                sizeStyle = "small")
        self.settings.size_editText = EditText((-60,y-3,-10,20),
                "", 
                sizeStyle = "small",
                callback = self._size_editText_callback)

        self.settings.size_slider = Slider((90,y-3,-65,20),
                minValue = 0,
                maxValue = 1000,
                value = 250,
                sizeStyle = "small",
                callback = self._size_slider_callback)

        y += 30
        self.settings.color_title = TextBox((0,y,100,20),
                "Color (FU)", 
                sizeStyle = "small")
        self.settings.color_colorWell = ColorWell((90,y-3,-10,20),
                callback=self._color_editText_callback, 
                color=NSColor.grayColor())

        self.canvas = CanvasGroup((-295,10,-10,-10), 
                delegate=ProjectCanvas(self.s, "ReferenceViewer", self))

        self.s.w.bind('close', self.windowWillClose)
        self.observer()

    def update(self):
        self.canvas.update()
        UpdateCurrentGlyphView()

    def _addReferenceFont_button_callback(self, sender):
        font = self.FontList_comboBox.get()
        if font is None or font == "": return

        # Default values
        new_elem = {
            "font": font,
            "size": 400,
            "x": -500,
            "y": 40,
            "color": (0, 0, 0, .56)
        }

        self.s.referenceViewerSettings.append(new_elem)
        self.s.referenceViewerList.append({"Font": font})
        self.reference_list.set(self.s.referenceViewerList)
        self.reference_list.setSelection([len(self.s.referenceViewerList) - 1])
        self.update()

    def _removeReference_button_callback(self, sender):
        sel = self.reference_list.getSelection()
        if sel is None: return

        def remove(l):
            return [e for i, e in enumerate(l) if i not in sel]

        self.s.referenceViewerSettings = remove(self.s.referenceViewerSettings)
        self.s.referenceViewerList = remove(self.s.referenceViewerList)

        self.reference_list.set(self.s.referenceViewerList)
        self.reference_list.setSelection([len(self.s.referenceViewerList) - 1])
        self.update()

    def _reference_list_selectionCallback(self, sender):
        self.s.reference_list_selection = sender.getSelection()
        if not self.s.reference_list_selection: 
            self.settings.show(0)
            return
        self.settings.show(1)
        settings = self.s.referenceViewerSettings[self.s.reference_list_selection[0]]
        self.settings.size_editText.set(settings["size"])
        self.settings.size_slider.set(settings["size"])
        colors = settings["color"]
        color = NSColor.colorWithCalibratedRed_green_blue_alpha_(
            colors[0], colors[1], colors[2], colors[3])
        self.settings.color_colorWell.set(color)

    def _size_editText_callback(self, sender):
        if not self.s.reference_list_selection: return
        size = self.s.referenceViewerSettings[self.s.reference_list_selection[0]]["size"]
        try: 
            size = int(sender.get())
        except: 
            sender.set(size)
        self.s.referenceViewerSettings[self.s.reference_list_selection[0]]["size"] = size
        self.settings.size_slider.set(size)
        self.update()

    def _size_slider_callback(self, sender):
        if not self.s.reference_list_selection: return
        self.s.referenceViewerSettings[self.s.reference_list_selection[0]]["size"] = int(sender.get())
        self.settings.size_editText.set(self.s.referenceViewerSettings[self.s.reference_list_selection[0]]["size"])
        self.update()

    def _color_editText_callback(self, sender):
        if not self.s.reference_list_selection: return
        color = sender.get()
        self.s.referenceViewerSettings[self.s.reference_list_selection[0]]["color"] = (
            color.redComponent(),
            color.greenComponent(),
            color.blueComponent(),
            color.alphaComponent(),
        )
        self.update()

    def draw(self, info):
        if self.s.glyph is None: return
        if self.s.glyph.name.startswith("uni"):
            txt = chr(int(self.s.glyph.name[3:7],16))
        elif self.s.glyph.unicode: 
            txt = chr(self.s.glyph.unicode)
        else:
            txt=""
        ReferenceViewerDraw(self.s, txt)

    def windowWillClose(self, sender):
        self.observer(remove=True)
        
    def observer(self, remove = False):
        if not remove:
            addObserver(self, "draw", "draw")
            addObserver(self, "draw", "drawInactive")
            return
        removeObserver(self, "draw")
        removeObserver(self, "drawInactive")