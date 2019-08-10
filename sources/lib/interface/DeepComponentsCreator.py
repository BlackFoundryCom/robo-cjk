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
from AppKit import *
from fontTools.pens import cocoaPen
import Quartz
from vanilla import *
from mojo.roboFont import *
from mojo.UI import OpenGlyphWindow, CurrentGlyphWindow
from mojo.canvas import Canvas
from AppKit import NSAppearance, NSColor
from drawers.LayersCanvas import LayersCanvas
# from drawers.LayersPreviewCanvas import LayersPreviewCanvas
from drawers.Tester_DeepComponentDrawer import TesterDeepComponent
from lib.cells.colorCell import RFColorCell
import Helpers

class DeepComponentsCreator(Group):

    def __init__(self, posSize, interface):
        super(DeepComponentsCreator, self).__init__(posSize)
        self.ui = interface

        self.storageGlyph = None
        self.storageGlyphName = ""
        self.StorageGlyphCurrentLayer = ""

        self.title = TextBox((10, 5, -10, 20),
            "Deep Component Creator",
            alignment = "center")

        self.left = Group((0, 30, 195, -0))

        # self.left.jumpTo = SearchBox((0, 0, -0, 20),
        #     placeholder = "Char/Name",
        #     sizeStyle = "small",
        #     callback = self._jumpTo_callback
        #     )

        # self.displayGlyphset_settingList = ['find Char/Name', "Sort by key"]
        # self.displaySettings = 'find Char/Name'
        # self.left.displayGlyphset_setting = PopUpButton((0, 10, -0, 20),
        #     self.displayGlyphset_settingList,
        #     sizeStyle = "small",
        #     callback = self._displayGlyphset_setting_callback)

        self.glyphset = []
        self.left.glyphset_List = List((0,0,-0,100),
            self.glyphset,
            columnDescriptions = [
                                {"title": "Char", "width" : 30},
                                {"title": "Name", "width" : 165},                  
                                ],
            drawFocusRing=False, 
            selectionCallback = self._glyphset_List_selectionCallback,
            doubleClickCallback = self._glyphset_List_doubleClickCallback
            )

        self.set_glyphset_List()

        # self.top.layersCanvas = Canvas((195,10,-0,-0), 
        #     delegate=LayersCanvas(self.ui, self),
        #     hasHorizontalScroller=False, 
        #     hasVerticalScroller=False)

        

        self.left.layersTextBox = TextBox((0,100,-0,20), 
                'Layers',
                sizeStyle = "small")

        self.layerList = []
        self.left.layers_list = List((0,120,-0,-50), 
                self.layerList,
                drawFocusRing = False,
                selectionCallback = self._layers_list_selectionCallback,
                editCallback = self._layers_list_editCallback)

        self.left.newLayer_Button = SquareButton((0, -50, 30, 30),
            '+',
            sizeStyle="small",
            callback = self._newLayer_Button_callback)

        self.left.assignLayerToGlyph_Button = SquareButton((30, -50, 165, 30),
            'Assign Layer ->',
            sizeStyle="small",
            callback = self._assignLayerToGlyph_Button_callback)

        slider = SliderListCell(minValue = 0, maxValue = 1000)
        self.slidersValuesList = []

        self.right = Group((195, 30, -0, -0))

        self.right.sliderList = List((0,0,-0,-20), self.slidersValuesList,

            columnDescriptions = [{"title": "Layer", "editable": False, "width": 140},
                                    {"title": "Image", "editable": False, "cell": ImageListCell(), "width": 60}, 
                                    {"title": "Values", "cell": slider}],
            editCallback = self._sliderList_editCallback,
            doubleClickCallback = self._sliderList_doubleClickCallback,
            drawFocusRing = False,
            allowsMultipleSelection = False,
            rowHeight = 60.0,
            showColumnTitles = False)

        # paneDescriptors = [
        #     dict(view=self.top, identifier="top"),
        #     dict(view=self.bottom, identifier="bottom"),
        # ]

        # self.mainSplitView = SplitView((0, 20, -0, -0), 
        #     paneDescriptors,
        #     isVertical = False,
        #     dividerStyle="thin"
        #     )

    def getGlyphset(self):
        return [dict(Char=chr(int(name.split("_")[0],16)), Name = name) for name in self.ui.font2Storage[self.ui.font].keys()]

    # def _displayGlyphset_setting_callback(self, sender):
    #     self.displaySettings = self.displayGlyphset_settingList[sender.get()]
    #     if self.displaySettings == 'find Char/Name':
    #         self.ui.glyphset = self.ui.font.lib['public.glyphOrder']
    #         # glyphset = [dict(Char=chr(int(name.split("_")[0],16)), Name = name) for name in self.ui.font2Storage[self.ui.font].keys()]
    #         self.glyphset = self.getGlyphset()
    #         self.left.glyphset_List.set(self.glyphset)

    def set_glyphset_List(self):
        if self.ui.font in self.ui.glyphsSetDict: #and self.displaySettings == 'find Char/Name':
            self.glyphset = self.getGlyphset()
            self.left.glyphset_List.set(self.glyphset)
            self.layerList = [layer.name for layer in self.ui.font2Storage[self.ui.font].layers]

            self.left.layers_list.set(self.layerList)
            self.setSliderList()
            

    def _glyphset_List_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            self.storageGlyph = None
            TesterDeepComponent.translateX = 0
            TesterDeepComponent.translateY = 0
            self.ui.w.mainCanvas.update()
            self.setSliderList()
            return
        self.storageFont = self.ui.font2Storage[self.ui.font]
        self.storageGlyphName = sender.get()[sel[0]]["Name"]
        self.storageGlyph = self.ui.font2Storage[self.ui.font][self.storageGlyphName]

        self.setSliderList()

    def _glyphset_List_doubleClickCallback(self, sender):
        sel = sender.getSelection()
        self.storageFont = self.ui.font2Storage[self.ui.font]
        self.storageGlyphName = sender.get()[sel[0]]["Name"]
        self.storageGlyph = self.ui.font2Storage[self.ui.font][self.storageGlyphName]
        self.ui.window = OpenGlyphWindow(self.storageGlyph, newWindow=False)
        Helpers.setDarkMode(self.ui.window, self.ui.darkMode)

    def setSliderList(self):
        self.slidersValuesList = []
        if self.storageGlyph and 'deepComponentsLayer' in self.storageGlyph.lib:
            for layerName in self.storageGlyph.lib['deepComponentsLayer']:
                if layerName == "foreground": continue
                g = self.storageGlyph.getLayer(layerName)
                f = g.getParent()
                path = NSBezierPath.bezierPath()
                pen = cocoaPen.CocoaPen(f, path)
                g.draw(pen)
                margins = 200
                mediaBox = Quartz.CGRectMake(-margins, -margins, self.ui.EM_Dimension_X+2*margins, self.ui.EM_Dimension_Y+2*margins)
                pdfData = Quartz.CFDataCreateMutable(None, 0)
                dataConsumer = Quartz.CGDataConsumerCreateWithCFData(pdfData)
                pdfContext = Quartz.CGPDFContextCreate(dataConsumer, mediaBox, None)
                Quartz.CGContextSaveGState(pdfContext)
                Quartz.CGContextBeginPage(pdfContext, mediaBox)

                for i in range(path.elementCount()):
                    instruction, points = path.elementAtIndex_associatedPoints_(i)
                    if instruction == NSMoveToBezierPathElement:
                        Quartz.CGContextMoveToPoint(pdfContext, points[0].x, points[0].y)
                    elif instruction == NSLineToBezierPathElement:
                        Quartz.CGContextAddLineToPoint(pdfContext, points[0].x, points[0].y)
                    elif instruction == NSCurveToBezierPathElement:
                        Quartz.CGContextAddCurveToPoint(pdfContext, points[0].x, points[0].y, points[1].x, points[1].y, points[2].x, points[2].y)
                    elif instruction == NSClosePathBezierPathElement:
                        Quartz.CGContextClosePath(pdfContext)

                if self.ui.darkMode:
                    Quartz.CGContextSetRGBFillColor(pdfContext, 1.0, 1.0, 1.0, 1.0)
                else:
                    Quartz.CGContextSetRGBFillColor(pdfContext, 0.0, 0.0, 0.0, 1.0)
        
                Quartz.CGContextFillPath(pdfContext)
                Quartz.CGContextEndPage(pdfContext)
                Quartz.CGPDFContextClose(pdfContext)
                Quartz.CGContextRestoreGState(pdfContext)

                d = {'Layer': layerName,
                    'Image': NSImage.alloc().initWithData_(pdfData),
                    'Values': 0}
                self.slidersValuesList.append(d)


            # self.slidersValuesList = [dict(Layer=self.storageGlyph.getLayer(layerName), Values=0) for layerName in self.storageGlyph.lib['deepComponentsLayer'] ]
        else:
            self.slidersValuesList = []
        self.right.sliderList.set(self.slidersValuesList)

    def _sliderList_editCallback(self, sender):
        self.slidersValuesList = sender.get()
        self.ui.w.mainCanvas.update()

    def _sliderList_doubleClickCallback(self, sender):
        sel = sender.getSelection()
        self.storageFont = self.ui.font2Storage[self.ui.font]
        storageLayerName = sender.get()[sel[0]]["Layer"]
        self.storageGlyph = self.ui.font2Storage[self.ui.font][self.storageGlyphName].getLayer(storageLayerName)
        self.ui.window = OpenGlyphWindow(self.storageGlyph, newWindow=False)
        Helpers.setDarkMode(self.ui.window, self.ui.darkMode)

    def _layers_list_editCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        
        newName = sender.get()[sel[0]]
        oldName = self.layerList[sel[0]]

        for storageFont in self.ui.font2Storage.values():
            for layer in storageFont.layers:
                if layer.name == oldName:
                    layer.name = newName

        storageFont = self.ui.font2Storage[self.ui.font]

        self.layerList = [layer.name for layer in storageFont.layers]
        self.selectedLayerName = newName

    def _layers_list_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return

        self.selectedLayerName = sender.get()[sel[0]]


    def _newLayer_Button_callback(self, sender):
        i=0
        name = "NewLayer_00"
        while name in self.layerList:
            index = "_%s"%str(i).zfill(2)
            name = "NewLayer"+index
            i+=1

        for storageFont in self.ui.font2Storage.values():
            # storageFont = self.ui.font2Storage[self.ui.font]
            storageFont.newLayer(name)

        self.layerList.append(name)
        self.left.layers_list.set(self.layerList)
        self.left.layers_list.setSelection([len(self.layerList)-1])

    def _assignLayerToGlyph_Button_callback(self, sender):
        StorageGlyphCurrentLayer = self.StorageGlyphCurrentLayer

        if self.storageGlyphName is None:
            message("Warning there is no selected glyph")
            return

        if not self.selectedLayerName:
            message("Warning there is no selected layer")
            return

        storageFont = self.ui.font2Storage[self.ui.font]
        layer = StorageGlyphCurrentLayer

        if not layer:
            layer = storageFont[self.storageGlyphName]

        layer.round()
        
        for stgFont in self.ui.font2Storage.values():
            if self.selectedLayerName not in stgFont[self.storageGlyphName].lib["deepComponentsLayer"]:
                stgFont.getLayer(self.selectedLayerName).insertGlyph(layer)
                stgFont[self.storageGlyphName].lib["deepComponentsLayer"].append(self.selectedLayerName)

        storageFont[self.storageGlyphName].update()
        
        self.setSliderList()      

    # def _jumpTo_callback(self, sender):
    #     string = sender.get()
    #     if not string:
    #         self.left.glyphset_List.setSelection([])
    #         self.left.glyphset_List.set(self.glyphset)
    #         self.ui.glyphset = self.ui.font.lib['public.glyphOrder']
    #         return

    #     try: 
    #         if self.displaySettings == 'find Char/Name':
    #             glyphSet = [e["Name"].split('_')[0] for e in self.glyphset]
    #             if string.startswith("uni"):
    #                 index = glyphSet.index(string[3:])

    #             elif len(string) == 1:
    #                 code = "uni"+normalizeUnicode(hex(ord(string[3:]))[2:].upper())
    #                 index = glyphSet.index(code)

    #             else:
    #                 index = glyphSet.index(string)

    #             self.left.glyphset_List.setSelection([index])

    #         elif self.displaySettings == 'Sort by key':
    #             glyphSet = [e["Name"] for e in self.glyphset]
    #             name = string
    #             if  string.startswith("uni"):
    #                 name = string[3:]
    #             elif len(string) == 1:
    #                 name = normalizeUnicode(hex(ord(string))[2:].upper())
    #             self.left.glyphset_List.set([dict(Name = names, Char = chr(int(names.split('_')[0],16))) for names in glyphSet if name in names])
    #     except:
    #         pass


# from AppKit import *
# from vanilla import *
# from fontTools.pens import cocoaPen
# import Quartz

# g = CurrentGlyph()
# f = g.getParent()
# path = NSBezierPath.bezierPath()
# pen = cocoaPen.CocoaPen(f, path)
# g.draw(pen)
# margins = 200
# mediaBox = Quartz.CGRectMake(g.box[0]-margins, g.box[1]-margins, g.box[2]+2*margins, g.box[3]+2*margins)
# pdfData = Quartz.CFDataCreateMutable(None, 0)
# dataConsumer = Quartz.CGDataConsumerCreateWithCFData(pdfData)
# pdfContext = Quartz.CGPDFContextCreate(dataConsumer, mediaBox, None)

# Quartz.CGContextSaveGState(pdfContext)

# Quartz.CGContextSetFillColorWithColor(pdfContext, NSColor.blackColor())
# Quartz.CGContextBeginPage(pdfContext, mediaBox)

# for i in range(path.elementCount()):
#     instruction, points = path.elementAtIndex_associatedPoints_(i)
#     print(points)
#     if instruction == NSMoveToBezierPathElement:
#         Quartz.CGContextMoveToPoint(pdfContext, points[0].x, points[0].y)
#     elif instruction == NSLineToBezierPathElement:
#         Quartz.CGContextAddLineToPoint(pdfContext, points[0].x, points[0].y)
#     elif instruction == NSCurveToBezierPathElement:
#         Quartz.CGContextAddCurveToPoint(pdfContext, points[0].x, points[0].y, points[1].x, points[1].y, points[2].x, points[2].y)
#     elif instruction == NSClosePathBezierPathElement:
#         Quartz.CGContextClosePath(pdfContext)

# Quartz.CGContextFillPath(pdfContext)
# Quartz.CGContextEndPage(pdfContext)
# Quartz.CGPDFContextClose(pdfContext)
# Quartz.CGContextRestoreGState(pdfContext)

# class ImageListCellDemo(object):

#     def __init__(self):
#         self.w = Window((100, 300))
#         self.w.myList = List((0, 0, -0, -0),
                    
#                     [
#                         # {"image": NSImage.alloc().initByReferencingFile_(ICON_PATH)},
#                         {"image": NSImage.alloc().initWithData_(pdfData)},
#                         {"image": NSImage.imageNamed_("NSRefreshTemplate")}
#                     ],
#                     columnDescriptions=[
#                         {"title": "image", "cell": ImageListCell()}
#                     ],
#                     rowHeight=60.0,)
#         self.w.open()

# ImageListCellDemo()
