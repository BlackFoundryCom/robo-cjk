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
from imp import reload
import os

from mojo.events import addObserver, removeObserver, extractNSEvent, installTool, uninstallTool, setToolOrder, getToolOrder
from mojo.roboFont import *
from mojo.UI import PostBannerNotification, OpenGlyphWindow, CurrentGlyphWindow, UpdateCurrentGlyphView, setMaxAmountOfVisibleTools
from AppKit import *
from views import roboCJKView
from views.drawers import currentGlyphViewDrawer
from views import textCenterView
from controllers import projectEditorController
from controllers import initialDesignController
from controllers import deepComponentEditionController
from controllers import keysAndExtremsEditionController
from controllers import deepComponentsController
from controllers import inspectorController
from controllers import textCenterController
from tools import powerRuler
from tools import balanceHandles
from tools.externalTools import shapeTool
from tools.externalTools import scalingEditTool
from resources import characterSets
from utils import git
from utils import interpolations
from views import tableDelegate
from utils import files
import Quartz
from fontTools.pens import cocoaPen

reload(roboCJKView)
reload(currentGlyphViewDrawer)
reload(textCenterView)
reload(projectEditorController)
reload(initialDesignController)
reload(deepComponentEditionController)
reload(keysAndExtremsEditionController)
reload(deepComponentsController)
reload(inspectorController)
reload(textCenterController)
reload(characterSets)
reload(git)
reload(files)
reload(powerRuler)
reload(balanceHandles)
reload(shapeTool)
reload(scalingEditTool)
reload(interpolations)


commandDown = 1048576
shiftDown = 131072
capLockDown = 65536
controlDown = 262144
optionDown = 524288


kMissingColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1)
kThereColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 1, 0, 1)
kEmptyColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 1, 1)
kLockedColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 0, 0, 1)
kFreeColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1)
kReservedColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 1, 1)

class PointLocation(object):
    def __init__(self, rfPoint, cont, seg, idx):
        p = Point(rfPoint)
        self.pos = p
        self.rfPoint = rfPoint
        self.cont = cont
        self.seg = seg
        self.idx = idx

class Point(object):
    __slots__ = ('x', 'y')
    def __init__(self, ix=0.0, iy=0.0):
        self.x = ix
        self.y = iy
    def __len__(self): return 2
    def __getitem__(self, i):
        if i == 0:
            return self.x
        elif i == 1:
            return self.y
        else:
            raise IndexError("coordinate index {} out of range [0,1]".format(i))
    def __repr__(self):
        return "({:f},{:f})".format(self.x, self.y)
    def __str__(self):
        return self.__repr__()
    def __add__(self, rhs): # rhs = right hand side
        return Point(self.x + rhs.x, self.y + rhs.y)
    def __sub__(self, rhs):
        return Point(self.x - rhs.x, self.y - rhs.y)
    def __or__(self, rhs): # dot product
        return (self.x * rhs.x + self.y * rhs.y)
    def __mul__(self, s): # 's' is a number, not a point
        return Point(s * self.x, s * self.y)
    def __rmul__(self, s): # 's' is a number, not a point
        return Point(s * self.x, s * self.y)

    def opposite(self):
        return Point(-self.x, -self.y)
    def rotateCCW(self):
        return Point(-self.y, self.x)
    def squaredLength(self):
        return self.x * self.x + self.y * self.y
    def length(self):
        return math.sqrt(self.squaredLength())

    def sheared(self, angleInDegree):
        r = math.tan(math.radians(angleInDegree))
        return Point(self.x - r*self.y, self.y)
    def absolute(self):
        return Point(abs(self.x), abs(self.y))
    def normalized(self):
        l = self.length()
        if l < 1e-6: return Point(0.0, 0.0)
        return Point(float(self.x)/l, float(self.y)/l)
    def swapAxes(self):
        return Point(self.y, self.x)
    def projectOnX(self):
        return Point(self.x, 0,0)
    def projectOnAxis(self,axis):
        if axis == 0:
            return Point(self.x, 0.0)
        else:
            return Point(0.0, self.y)
    def projectOnY(self):
        return Point(0.0, self.y)


class RoboCJKController(object):
    def __init__(self):
        self.observers = False
        self.project = None
        self.projectFileLocalPath = None
        self.collab = None
        self.projectFonts = {}
        self.scriptsList = ['Hanzi', 'Hangul', 'Kana']
        self.characterSets = characterSets.sets
        self.currentFont = None
        self.currentGlyph = None

        self.pathsGlyphs = {}
        self.ploc = None

        self.designStep = "_initialDesign_glyphs"
        self.deepComponentGlyph = None
        self.currentGlyphWindow = None
        self.allFonts = []
        self.fonts2DCFonts = {}
        self.lockedGlyphs = []
        self.reservedGlyphs = []
        self.user = git.GitEngine(None).user()
        self.settings = {
            'showDesignFrame':True,
            'designFrame':{'showMainFrames': True,
                            'showSecondLines': True,
                            'showCustomsFrames': True,
                            'showproximityPoints': True,
                            'translate_secondLine_X': 0,
                            'translate_secondLine_Y': 0,
                            'drawPreview': False,
                            },

            'stackMasters': True,
            'stackMastersColor': NSColor.colorWithCalibratedRed_green_blue_alpha_(1, .4, 0, .4),
            'waterFall': False,
            'waterFallColor': NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1),

            'interpolaviour':{'onOff': False,
                            'showPoints': False,
                            'showStartPoints': False,
                            'showInterpolation': True,
                            'interpolationValue': .5,
                            'interpolationColor': NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 1, 1),
                            },
            'referenceViewer' : {
                            'onOff': True,
                            'drawPreview': False,
                            },

            'previousGlyph' : [0, "p"],
            'nextGlyph' : [0, "n"],

            'activePowerRuler' : [0, "r"],
            'unactivePowerRuler' : [commandDown, "r"],

            'balanceHandles' : [commandDown+shiftDown, "a"],

            'saveFonts' : [commandDown, "s"]
        }
        self.properties = ""
        self.projectEditorController = projectEditorController.ProjectEditorController(self)
        self.initialDesignController = initialDesignController.InitialDesignController(self)
        self.deepComponentEditionController = deepComponentEditionController.DeepComponentEditionController(self)
        self.keysAndExtremsEditionController = keysAndExtremsEditionController.keysAndExtremsEditionController(self)
        self.deepComponentsController = deepComponentsController.DeepComponentsController(self)
        self.inspectorController = inspectorController.inspectorController(self)
        self.textCenterController = textCenterController.textCenterController(self)
        self.powerRuler = powerRuler.Ruler(self)
        self.balanceHandles = balanceHandles.BalanceHandles()
        self.shapeTool = shapeTool.ShapeTool(self)
        self.scalingEditTool = scalingEditTool.RCJKScalingEditTool(self)

        self.designControllers = [
            self.initialDesignController,
            self.deepComponentEditionController,
            self.keysAndExtremsEditionController,
            ]

        installTool(self.shapeTool)
        installTool(self.scalingEditTool)

        toolOrder = getToolOrder()
        toolOrder.remove('ShapeTool')
        toolOrder.insert(4, 'ShapeTool')
        toolOrder.remove('RCJKScalingEditTool')
        toolOrder.insert(5, 'RCJKScalingEditTool')
        setToolOrder(toolOrder)
        setMaxAmountOfVisibleTools(6)

        self.textCenterInterface = None

    def windowCloses(self):
        setMaxAmountOfVisibleTools(14)
        uninstallTool(self.shapeTool)
        uninstallTool(self.scalingEditTool)

        self.toggleObservers(forceKill=True)

        if self.projectEditorController.interface:
            self.projectEditorController.interface.w.close()

        if self.initialDesignController.interface:
            self.initialDesignController.interface.w.close()

        if self.deepComponentsController.interface:
            self.deepComponentsController.interface.w.close()

        if self.keysAndExtremsEditionController.interface:
            self.keysAndExtremsEditionController.interface.w.close()

        if self.textCenterInterface:
            self.textCenterInterface.w.close()

        if self.inspectorController.interface:
            self.inspectorController.interface.w.close()

        if self.textCenterController.interface:
            self.textCenterController.interface.w.close()

        if self.deepComponentEditionController.interface:
            self.deepComponentEditionController.interface.w.close()

    def closeDesignControllers(self):
        for designController in self.designControllers:
            if designController.interface:
                designController.interface.w.close()
                designController.interface = None

    def resetController(self):
        self.currentFont = None
        self.currentGlyph = None
        self.designStep = "_initialDesign_glyphs"
        # self.allFonts = []
        # self.fonts2DCFonts = {}
        # self.lockedGlyphs = []
        # self.reservedGlyphs = []


    def toggleObservers(self, forceKill=False):
        if self.observers or forceKill:
            removeObserver(self, "draw")
            removeObserver(self, "drawPreview")
            removeObserver(self, "drawInactive")
            removeObserver(self, "keyDown")
            removeObserver(self, "keyUp")
            removeObserver(self, "mouseMoved")
            removeObserver(self, "mouseDown")
            # removeObserver(self, "mouseUp")
            removeObserver(self, "mouseDragged")
            # removeObserver(self, "viewWillChangeGlyph")
        else:
            addObserver(self, "drawInGlyphWindow", "draw")
            addObserver(self, "drawInGlyphWindow", "drawPreview")
            addObserver(self, "drawInGlyphWindow", "drawInactive")
            addObserver(self, "keyDownInGlyphWindow", "keyDown")
            addObserver(self, "keyUpInGlyphWindow", "keyUp")
            addObserver(self, "mouseMovedInGlyphWindow", "mouseMoved")
            addObserver(self, "mouseDownInGlyphWindow", "mouseDown")
            # removeObserver(self, "mouseUpInGlyphWindow" "mouseUp")
            addObserver(self, "mouseDraggedInGlyphWindow", "mouseDragged")
            # addObserver(self, "viewWillChangeGlyph", "viewWillChangeGlyph")

        self.observers = not self.observers

    # def viewWillChangeGlyph(self, info):
    #     print(info)

    def getLayerPDFImage(self, g, emDimension):
        f = g.getParent()
        path = NSBezierPath.bezierPath()
        pen = cocoaPen.CocoaPen(f, path)
        g.draw(pen)
        margins = 200
        EM_Dimension_X, EM_Dimension_Y = emDimension
        mediaBox = Quartz.CGRectMake(-margins, -margins, EM_Dimension_X+2*margins, EM_Dimension_Y+2*margins)
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

        Quartz.CGContextSetRGBFillColor(pdfContext, 0.0, 0.0, 0.0, 1.0)
        # if self.ui.darkMode:
        #     Quartz.CGContextSetRGBFillColor(pdfContext, 1.0, 1.0, 1.0, 1.0)
        # else:
        #     Quartz.CGContextSetRGBFillColor(pdfContext, 0.0, 0.0, 0.0, 1.0)

        Quartz.CGContextFillPath(pdfContext)
        Quartz.CGContextEndPage(pdfContext)
        Quartz.CGPDFContextClose(pdfContext)
        Quartz.CGContextRestoreGState(pdfContext)

        return pdfData

    def getGlyphSetList(self, charset, designStep):
        l = []
        if self.currentFont is not None:
            later = []
            for c in charset:
                name = files.unicodeName(c)
                code = c
                if name in self.collab._userLocker(self.user).glyphs[designStep]:
                    l.append(({'#':'', 'Char':code, 'Name':name, 'MarkColor':''}))
                else:
                    later.append(({'#':'', 'Char':code, 'Name':name, 'MarkColor':''}))
            l += later
        return l

    def saveAllSubsetFonts(self):
        for d in self.allFonts:
            for name, f in d.items():
                f.save()
        PostBannerNotification("Fonts saved", "")
        

    def updateViews(self):
        UpdateCurrentGlyphView()
        if self.initialDesignController.interface:
            self.initialDesignController.interface.w.mainCanvas.update()
        if self.deepComponentEditionController.interface:
            self.deepComponentGlyph = self.getDeepComponentGlyph()
            self.deepComponentEditionController.interface.w.mainCanvas.update()
        # if self.textCenterController.interface:
        #     self.textCenterController.interface.w.canvas.update()

    def launchInterface(self):
        self.interface = roboCJKView.RoboCJKWindow(self)
        self.powerRuler = powerRuler.Ruler(self)
        self.updateUI()

    def updateUI(self):
        self.interface.w.initialDesignEditorButton.enable(self.project!=None)
        self.interface.w.textCenterButton.enable(self.project!=None)
        self.interface.w.deepComponentButton.enable(self.project!=None)
        self.interface.w.inspectorButton.enable(self.project!=None)

    def launchTextCenterInterface(self):
        if self.textCenterInterface is None:
            self.textCenterInterface = textCenterView.TextCenterWindow(self)

    def drawInGlyphWindow(self, info):
        if self.currentGlyph is None: return
        currentGlyphViewDrawer.CurrentGlyphViewDrawer(self).draw(info)

    def keyDownInGlyphWindow(self, info):
        if self.currentGlyph is None: return

        event = extractNSEvent(info)
        modifiers = sum([
            event['shiftDown'], 
            event['capLockDown'],
            event['optionDown'],
            event['controlDown'],
            event['commandDown'],
            ])

        character = info["event"].characters()
        inputKey = [modifiers, character]

        if inputKey == self.settings['saveFonts']:
            if self.initialDesignController.interface:
                self.saveAllSubsetFonts()

            elif self.deepComponentEditionController.interface:
                self.deepComponentEditionController.saveSubsetFonts()

        elif inputKey == self.settings['unactivePowerRuler']:
            self.powerRuler.killPowerRuler()

        elif inputKey == self.settings['activePowerRuler']:
            self.powerRuler.launchPowerRuler()

        elif inputKey == self.settings['balanceHandles']:
            self.balanceHandles.balance(self.currentGlyph)

        elif inputKey in [self.settings['previousGlyph'], self.settings['nextGlyph']]:

            glyphsetList = self.initialDesignController.interface.w.glyphSetList
            if inputKey == self.settings['previousGlyph']:
                sel = glyphsetList.getSelection()[0]-1 if glyphsetList.getSelection()[0] != 0 else len(glyphsetList)-1
            else:
                sel = glyphsetList.getSelection()[0]+1 if glyphsetList.getSelection()[0] != len(glyphsetList)-1 else 0
            self.currentGlyph = self.currentFont[glyphsetList.get()[sel]["Name"]]
            glyphsetList.setSelection([sel])
            self.openGlyphWindow(self.currentGlyph)

        self.updateViews()

    def pointClickedOnGlyph(self, clickPos, glyph, best, dist):
        if len(glyph) == 0: return
        thresh = 10.0 * 10.0
        def update(p, cont, seg, idx):
            d = (Point(clickPos[0], clickPos[1]) - Point(p.x, p.y)).squaredLength()
            if d < dist[0]:
                dist[0] = d
                best[0] = PointLocation(Point(p), cont, seg, idx)
                
        for cont, contour in enumerate(glyph):
            for seg, segment in enumerate(contour):
                for idx, p in enumerate(segment.offCurve):
                    update(p, cont, seg, idx)
        if dist[0] <= thresh:
            return best[0]
        else:
            return None

    def mouseDownInGlyphWindow(self, info):
        if self.currentGlyph.name not in self.pathsGlyphs: return
        if self.currentGlyph.layerName == 'foreground': return
        pClick = info['point']
        best = [None]
        dist = [999999999.0]
        self.ploc = self.pointClickedOnGlyph(pClick, self.pathsGlyphs[self.currentGlyph.name]['paths_'+self.currentGlyph.layerName], best, dist)
        

    def mouseDraggedInGlyphWindow(self, info):
        if not self.ploc: return
        point = info['point']
        mouseDraggedPos = Point(point.x, point.y)
        pmoved = self.pathsGlyphs[self.currentGlyph.name]['paths_'+self.currentGlyph.layerName][self.ploc.cont][self.ploc.seg][self.ploc.idx]
        pmoved.x = mouseDraggedPos.x
        pmoved.y = mouseDraggedPos.y

    def keyUpInGlyphWindow(self, info):
        self.powerRuler.keyUp()
        self.updateViews()

    def mouseMovedInGlyphWindow(self, info):
        x, y = info['point'].x, info['point'].y
        self.powerRuler.mouseMoved(x, y)
        self.updateViews()

    def injectGlyphsBack(self, glyphs, user, step):
        for d in self.allFonts:
            for name, subsetFont in d.items():
                if name in self.projectFonts:
                    f = self.projectFonts[name]
                    for glyphName in glyphs:
                        if glyphName in self.reservedGlyphs[step] and glyphName in subsetFont:
                            f.insertGlyph(subsetFont[glyphName].naked())
                    f.save()

    def pullMastersGlyphs(self, glyphs, step):
        self.projectEditorController.loadProject([self.projectFileLocalPath])
        for d in self.allFonts:
            for name, subsetFont in d.items():
                if name in self.projectFonts:
                    f = self.projectFonts[name]
                    for glyphName in glyphs: 
                        if glyphName not in self.reservedGlyphs[step]:
                            subsetFont[glyphName] = RGlyph(f[glyphName])
                    subsetFont.save()

    def saveProjectFonts(self):
        rootfolder = os.path.split(self.projectFileLocalPath)[0]
        gitEngine = git.GitEngine(rootfolder)
        gitEngine.pull()
        for name in self.projectFonts:
            f = self.projectFonts[name]
            f.save()
        stamp = "Masters Fonts Saved"
        gitEngine.commit(stamp)
        gitEngine.push()
        PostBannerNotification('Git Push', stamp)

    def openGlyphWindow(self, glyph):
        self.currentGlyphWindow = CurrentGlyphWindow()
        if self.currentGlyphWindow is not None:
            self.currentGlyphWindow.setGlyph(glyph)
            self.currentGlyphWindow.w.getNSWindow().makeKeyAndOrderFront_(self)
        else:
            self.currentGlyphWindow = OpenGlyphWindow(glyph)
            self.currentGlyphWindow.w.bind("became main", self.glyphWindowBecameMain)
        self.currentGlyphWindow.w.bind("close", self.glyphWindowCloses)

    def getCurrentGlyph(self):
        if CurrentGlyphWindow() is not None:
            doodleGlyph = CurrentGlyphWindow().getGlyph()
            if doodleGlyph is not None:
                layerName = doodleGlyph.layer.name
                if doodleGlyph.name in self.currentFont.keys():
                    self.currentGlyph = self.currentFont[doodleGlyph.name].getLayer(layerName)
        else:
            self.currentGlyphWindow = None
        return self.currentGlyph

    def getDeepComponentGlyph(self):
        if self.currentGlyph is None: return
        self.deepComponentEditionController.makeNLIPaths()
        return interpolations.deepolation(RGlyph(), self.currentGlyph.getLayer("foreground"), self.pathsGlyphs, self.layersInfos)
        

    def glyphWindowBecameMain(self, sender):
        self.getCurrentGlyph()
        self.inspectorController.updateViews()

    def glyphWindowCloses(self, sender):
        self.currentGlyphWindow = None

    def tableView_dataCellForTableColumn_row_(self, tableView, tableColumn, row, window, step, font):
        if tableColumn is None: return None
        cell = tableColumn.dataCell()
        if window is None:
            return None
        if (row < 0) or (row >= len(window.glyphSetList.get())):
            return cell
        uiGlyph  = window.glyphSetList.get()[row]
        uiGlyphName = uiGlyph['Name']
        uiGlyphReserved = uiGlyphName in self.collab._userLocker(self.user).glyphs[step]

        state = 'missing'
        locked = False
        reserved = False
        markColor = None
        if font:
            if uiGlyphName in font:
                state = 'there'
                markColor = font[uiGlyphName].markColor
                if len(font[uiGlyphName]) == 0 and not font[uiGlyphName].components:
                    state = 'empty'
        if uiGlyphName in self.lockedGlyphs:
            locked = True

        colID = tableColumn.identifier()
        if colID == '#':
            cell.setDrawsBackground_(True)
            cell.setBezeled_(False)
            if state == 'missing':
                cell.setBackgroundColor_(kMissingColor)
            elif state == 'there':
                cell.setBackgroundColor_(kThereColor)
            elif state == 'empty':
                cell.setBackgroundColor_(kEmptyColor)
            else:
                cell.setDrawsBackground_(False)
                cell.setBezeled_(False)
        elif colID == 'Name' or colID == 'Char':
            if locked:
                cell.setTextColor_(kLockedColor)
            elif uiGlyphReserved == True:
                cell.setTextColor_(kReservedColor)
            else:
                cell.setTextColor_(kFreeColor)
        elif colID == 'MarkColor':
            cell.setDrawsBackground_(True)
            cell.setBezeled_(False)
            if markColor is not None:
                cell.setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(markColor[0], markColor[1], markColor[2], markColor[3]))
            else:
                cell.setDrawsBackground_(False)
                cell.setBezeled_(False)
        return cell



