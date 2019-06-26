from vanilla import *
from mojo.canvas import CanvasGroup
from mojo.UI import UpdateCurrentGlyphView
from drawers.ProjectCanvas import ProjectCanvas
from mojo.events import addObserver, removeObserver
from mojo.roboFont import *
from drawers.DesignFrameDrawer import DesignFrameDrawer
from mojo.drawingTools import *

class DesignFrame(Group):

    def __init__(self, posSize, interface, sheet):
        super(DesignFrame, self).__init__(posSize)
        self.ui = interface
        self.s = sheet

        y = 10
        self.EM_Dimension_title = TextBox((10,y,200,20), 
                "EM Dimension (FU)", 
                sizeStyle = "small")
        self.EM_DimensionX_title = TextBox((145,y,20,20), 
                "X:", 
                sizeStyle = "small")
        self.EM_DimensionX_editText = EditText((160,y-3,45,20), 
                self.s.EM_Dimension_X, 
                callback = self.EM_DimensionX_editText_callback,
                sizeStyle = "small")
        self.EM_DimensionY_title = TextBox((235,y,20,20), 
                "Y:", 
                sizeStyle = "small")
        self.EM_DimensionY_editText = EditText((250,y-3,45,20), 
                self.s.EM_Dimension_Y,  
                callback = self.EM_DimensionY_editText_callback,
                sizeStyle = "small")
        y += 30
        self.characterFace_title = TextBox((10,y,200,20), 
                "Character Face (EM%)", 
                sizeStyle = "small")
        self.characterFacePercent_title = TextBox((208,y,200,20), 
                "%", 
                sizeStyle = "small")
        self.characterFace_editText = EditText((160,y-3,45,20), 
                self.s.characterFace,
                callback = self.characterFace_editText_callback,
                sizeStyle = "small")
        y += 30
        self.overshoot_title = TextBox((10,y,200,20), 
                "Overshoot (FU)", 
                sizeStyle = "small")
        self.overshootOutside_title = TextBox((110,y,200,20), 
                "Outside:", 
                sizeStyle = "small")
        self.overshootOutside_editText = EditText((160,y-3,45,20), 
                self.s.overshootOutsideValue, 
                callback = self.overshootOutside_editText_callback,
                sizeStyle = "small")
        self.overshootInside_title = TextBox((210,y,200,20), 
                "Inside:", 
                sizeStyle = "small")
        self.overshootInside_editText = EditText((250,y-3,45,20), 
                self.s.overshootInsideValue,  
                callback = self.overshootInside_editText_callback,
                sizeStyle = "small")
        y += 30
        self.horizontalLine_title = TextBox((10,y,200,20), 
                "Horizontal Line (EM%)", 
                sizeStyle = "small")
        self.horizontalLine_slider = Slider((160,y-3 ,135,20), 
                minValue = 0, maxValue = 50, value = 0, 
                sizeStyle = "small",
                callback = self._horizontalLine_slider_callback)
        y += 30
        self.verticalLine_title = TextBox((10,y,200,20), 
                "Vertical Line (EM%)", 
                sizeStyle = "small")
        self.verticalLine_slider = Slider((160,y-3 ,135,20), 
                minValue = 0, maxValue = 50, value = 0, 
                sizeStyle = "small",
                callback = self._verticalLine_slider_callback)
        y += 30
        self.customsFrames_title = TextBox((10,y,200,20), 
                "Customs Frames (EM%):", 
                sizeStyle = "small")
        y += 20
        slider = SliderListCell()

        self.customsFrames_list = List((10,y,285,-30),
                self.s.customsFrames,
                columnDescriptions = [{"title": "Name", "width" : 75}, 
                                    {"title": "Values", "width" : 200, "cell": slider}],
                editCallback = self._customsFrames_list_editCallback,
                drawFocusRing = False)  
        self.addCustomsFrames_button = Button((170,-28,62,-10),
                "+",
                callback = self._addCustomsFrames_button_callback,
                sizeStyle="small")
        self.removeCustomsFrames_button = Button((232,-28,62,-10),
                "-",
                callback = self._removeCustomsFrames_button_callback,
                sizeStyle="small")
        self.s.translateX,self.s.translateY = 0, 0
        self.canvas = CanvasGroup((-295,10,-10,-10), 
                delegate=ProjectCanvas(self.s, "DesignFrame", self))

        self.s.w.bind('close', self.windowWillClose)
        self.observer()

    def update(self):
        self.canvas.update()
        UpdateCurrentGlyphView()

    def EM_DimensionX_editText_callback(self, sender):
        try: self.s.EM_Dimension_X = int(sender.get())        
        except: sender.set(self.s.EM_Dimension_X)
        self.update()

    def EM_DimensionY_editText_callback(self, sender):
        try: self.s.EM_Dimension_Y = int(sender.get())        
        except: sender.set(self.s.EM_Dimension_Y)
        self.update()

    def characterFace_editText_callback(self, sender):
        try:
            value = int(sender.get())
            if 0 <= value <= 100:
                self.s.characterFace = value        
            else:
                sender.set(self.s.characterFace)
        except: sender.set(self.s.characterFace)
        self.update()

    def overshootOutside_editText_callback(self, sender):
        try: self.s.overshootOutsideValue = int(sender.get())
        except: sender.set(self.s.overshootOutsideValue)
        self.update()

    def overshootInside_editText_callback(self, sender):
        try: self.s.overshootInsideValue = int(sender.get())        
        except: sender.set(self.s.overshootInsideValue)
        self.update()

    def _horizontalLine_slider_callback(self, sender):
        self.s.horizontalLine = int(sender.get())
        self.update()

    def _verticalLine_slider_callback(self, sender):
        self.s.verticalLine = int(sender.get())
        self.update()

    def _customsFrames_list_editCallback(self, sender):
        self.s.customsFrames = sender.get()
        self.update()

    def _addCustomsFrames_button_callback(self, sender):
        name = "Frame%i"%len(self.s.customsFrames)
        self.s.customsFrames.append({"Name":name})
        self.customsFrames_list.set(self.s.customsFrames)
        self.update()

    def _removeCustomsFrames_button_callback(self, sender):
        # Get the customsFrames list selection
        sel = self.customsFrames_list.getSelection()
        if not sel: return
        # Delete the selection from the customsFrames
        self.s.customsFrames = [e for i, e in enumerate(self.s.customsFrames) if i not in sel]
        self.customsFrames_list.set(self.s.customsFrames)
        self.update()

    def draw(self, info):
        if self.s.glyph is None: return
        s = info['scale']
        strokeWidth(.6*s)
        DesignFrameDrawer(self.s).draw()

    def windowWillClose(self, sender):
        self.observer(remove=True)
        
    def observer(self, remove = False):
        if not remove:
            addObserver(self, "draw", "draw")
            addObserver(self, "draw", "drawInactive")
            return
        removeObserver(self, "draw")
        removeObserver(self, "drawInactive")
        
        
