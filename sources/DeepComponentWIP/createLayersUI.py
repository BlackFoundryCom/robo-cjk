from vanilla import *
from vanilla.dialogs import message
from mojo.canvas import CanvasGroup
from mojo.drawingTools import *
from mojo.events import extractNSEvent
from mojo.UI import OpenGlyphWindow
from ufoLib.pointPen import PointToSegmentPen

layerSuffix = '.deep'

def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]
    
def deepCompatible(masterGlyph, layersNames):
    for layerName in layersNames:
        glyph = masterGlyph.getLayer(layerName)
        if len(glyph) != len(masterGlyph):
            return False
        for c1, c2 in zip(glyph, masterGlyph):
            if len(c1) != len(c2):
                return False
    return True
    
def deepolation(newGlyph, masterGlyph, layersInfo = {}):
    
    if not deepCompatible(masterGlyph, list(layersInfo.keys())):
        return False
    
    pen = PointToSegmentPen(newGlyph.getPen())
    
    for contourIndex, contour in enumerate(masterGlyph):
        
        pen.beginPath()
        
        for pointIndex, point in enumerate(contour.points):
            
            px, py = point.x, point.y
            ptype = point.type if point.type != 'offcurve' else None
            
            points = []
            for layerName, value in layersInfo.items():
                
                ratio = value/1000*len(layersInfo)
                layerGlyph = masterGlyph.getLayer(layerName)
                
                pI = layerGlyph[contourIndex].points[pointIndex]
                pxI, pyI = pI.x, pI.y
                
                newPx = px + (pxI - px) * ratio
                newPy = py + (pyI - py) * ratio
                
                points.append((newPx, newPy))
                
            newX = int(sum(p[0] for p in points) / len(points))
            newY = int(sum(p[1] for p in points) / len(points))
            pen.addPoint((newX, newY), ptype)
            
        pen.endPath()
        
    return newGlyph
    
class deepComponentEditor():
    
    def __init__(self):
        self.windowWidth, self.windowHeight = 737,800
        self.w = Window((self.windowWidth, self.windowHeight),"Deep Component Editor")
        
        ##### ROBO CJK GLOBAL DATAS ######
        self.glyph = CurrentGlyph()
        self.font = CurrentFont()
        
        ##### DEEP COMPONENT GLYPH LIB DATA ######
        self.availableLayers = self.getAvailableLayers_ForGlyph(self.glyph, self.font)
        
        ##### CLS DATA ######
        self.selectedLayer = self.glyph
        
        self.layersList = [layer.name for layer in self.font.layers]
        self.w.layersFontList = List((10,10,180,250), 
            self.layersList, 
            editCallback = self._layersFontList_editCallback, 
            drawFocusRing = False,
            allowsMultipleSelection = False,
            allowsEmptySelection = False)
        
        slider = SliderListCell(minValue = 0, maxValue = 1000)
        self.slidersValuesList = [dict(Layer=layer.name, Values=0) for layer in self.availableLayers if layer.name != "foreground"]
        self.w.sliderList = List((10,-290,350,-10),self.slidersValuesList,
            columnDescriptions = [{"title": "Layer" }, 
                                    {"title": "Values", "cell": slider}],
            editCallback = self._sliderList_editCallback,
            drawFocusRing = False,
            allowsMultipleSelection = False)
        
        self.w.newLayer_Button = Button((10,270,180,20), "add layer", callback = self._newLayer_Button_callback)
        self.w.addLayer2Glyph_Button = Button((10,300,180,20), "add layer to glyph", callback = self._addLayer2Glyph_Button_callback)
        
        self.w.layerCanvas = CanvasGroup((200,10,-10,-300), delegate = layerCanvas(self))
        self.w.previewCanvas = CanvasGroup((370,-290,-10,-10), delegate = previewCanvas(self))
        
        self.w.bind('resize', self._windowDidResize)
        self.w.open()
        
    def getAvailableLayers_ForGlyph(self, g, f):
        return list(filter(lambda x: len(g.getLayer(x.name)), f.layers))
        
    def _windowDidResize(self, sender):
        _, _, self.windowWidth, self.windowHeight = self.w.getPosSize()
        self.w.layerCanvas.update()
        
    def _newLayer_Button_callback(self, sender):
        i=0
        while True:
            index = "_%s"%str(i).zfill(2)
            layerName = "newLayer"+index
            if layerName not in [layer.name for layer in self.font.layers]: 
                break
            i+=1
            
        self.font.newLayer(layerName)
        self.layersList = [layer.name for layer in self.font.layers]
        self.w.layersFontList.set(self.layersList)
        
    def _sliderList_editCallback(self, sender):
        self.slidersValuesList = sender.get()
        self.w.previewCanvas.update()
        
    def _layersFontList_editCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        newName = sender.get()[sel[0]]
        oldName = self.layersList[sel[0]]
        for layer in self.font.layers:
            if layer.name == oldName:
                layer.name = newName
        self.layersList = [layer.name for layer in self.font.layers]
        self.getAvailableLayers_ForGlyph(self.glyph, self.font)
        self.w.layerCanvas.update()
    
    def _addLayer2Glyph_Button_callback(self, sender):
        sel = self.w.layersFontList.getSelection()
        if not sel: return
        layerName = self.layersList[sel[0]]
        self.addLayer2Glyph(self.font, self.selectedLayer, layerName, self.availableLayers)
        
        self.slidersValuesList = self.w.sliderList.get()
        self.slidersValuesList.append(dict(Layer=layerName, Values=0))
        self.w.sliderList.set(self.slidersValuesList)
        
        self.w.layerCanvas.update()
        
        self.openGlyphWindow(self.glyph, layerName)
        
    def addLayer2Glyph(self, f, g, layerName, availableLayers):
        f.getLayer(layerName).insertGlyph(g)
        availableLayers.append(f.getLayer(layerName))
        availableLayers = unique(availableLayers)
        
    def openGlyphWindow(self, g, LayerName):
        OpenGlyphWindow(g.getLayer(LayerName))
        
class layerCanvas():
    
    def __init__(self, interface):
        self.ui = interface
        self.scale = .176
        self.canvasHeight = 490
        self.canvasWidth = 530
        self.boxHeight = 1000
        self.boxWidth = 1000
        self.scroll = 0
        self.ui.selectedLayer = None
        
    def scrollWheel(self, info):
        alt = extractNSEvent(info)['optionDown']
        delta = info.deltaY()
        sensibility = .002
        if not alt:
            scroll = self.scroll
            scroll -= (delta / abs(delta) * 50) / self.scale
            if scroll < 0:
                scroll = 0
            self.scroll = scroll
        else:
            scale = self.scale
            scale += (delta / abs(delta) * sensibility) / self.scale
            minScale = .005
            if scale > minScale:
                self.scale = scale
        self.update()
        
    def mouseDown(self, info):
        pointX, pointY = info.locationInWindow()
        for loc in self.glyphLocation_in_Window:
            x, y, w, h = loc
            if x < (pointX-200)/self.scale < x+w and y < (pointY-300)/self.scale < y+h:
                self.ui.selectedLayer = self.glyphLocation_in_Window[loc]
                if info.clickCount() == 2:
                    OpenGlyphWindow(self.ui.selectedLayer)
        self.update()
        
    def update(self):
        self.ui.w.layerCanvas.update()
        
    def draw(self):
        self.glyphLocation_in_Window = {}
        try:
            canvasHeight = (self.canvasHeight / self.scale - self.boxHeight) + self.scroll
            
            scale(self.scale, self.scale)
            translate(0, canvasHeight)

            columnWidth = self.boxWidth
            lineHeight = canvasHeight

            for i, layer in enumerate(self.ui.availableLayers):
                g = self.ui.glyph.getLayer(layer.name)

                fill(None)
                stroke(0)
                
                rect(0, 0, self.boxWidth, self.boxHeight)
                
                #### DRAW GLYPH ####
                save()
                stroke(None)
                fill(0,0,0,1)
                if not deepCompatible(self.ui.glyph.getLayer("foreground"), [layer.name]):
                    fill(.9,0,.3,1)
                x = (self.boxWidth-g.width)*.5
                y = 200
                translate(x, y)
                drawGlyph(g)
                restore()
                
                #### LAYERS NAMES ####
                save()
                fill(0,.4,1,1)
                stroke(None)
                if g == self.ui.selectedLayer:
                    fill(.9,0,.3,1)
                font('Menlo-Regular', fontSize=int(60))
                text(str(layer.name), (20, self.boxHeight-80))
                restore()
                
                x, y, w, h = columnWidth-self.boxWidth, lineHeight, self.boxWidth, self.boxHeight
                self.glyphLocation_in_Window[(x, y, w, h)] = g
                
                #### TRANSLATE ####
                if (columnWidth + self.boxWidth) * self.scale > self.canvasWidth:
                    lineHeight -= self.boxHeight
                    translate(-columnWidth + self.boxWidth, -self.boxHeight)    
                    columnWidth = 0
                else:
                    translate(self.boxWidth, 0)

                columnWidth += self.boxWidth
        except:
            pass
            
class previewCanvas():
    
    def __init__(self, interface):
        self.ui = interface
        self.translateX, self.translateY = 0,0
        self.scale = .3
        
    def mouseDragged(self, info):
        deltaX = info.deltaX()/self.scale
        deltaY = info.deltaY()/self.scale
        self.translateX += deltaX
        self.translateY -= deltaY
        self.update()
        
    def update(self):
        self.ui.w.previewCanvas.update()
        
    def draw(self):
        try:
            newGlyph = deepolation(RGlyph(), self.ui.glyph, layersInfo = {e["Layer"]:int(e["Values"]) for e in self.ui.slidersValuesList})
            if not newGlyph:
                fill(.9,0,.3,1)
                rect(0,0,1000,1000)
            else:
                scale(self.scale, self.scale)
                translate(0,200)
                translate(self.translateX, self.translateY)
                fill(0,0,0,1)
                drawGlyph(newGlyph)
        except Exception as e:
            print(e)
        
deepComponentEditor()