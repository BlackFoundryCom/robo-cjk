from fontPens.penTools import estimateCubicCurveLength, distance, interpolatePoint, getCubicPoint
from fontTools.misc.bezierTools import calcQuadraticArcLength
from fontTools.pens.basePen import BasePen

from mojo.drawingTools import *
from mojo.events import addObserver, removeObserver, getActiveEventTool, extractNSEvent

from mojo.UI import UpdateCurrentGlyphView
from mojo.tools import IntersectGlyphWithLine

from math import sqrt
# from vanilla import *
from mojo.roboFont import *

import os

from AppKit import *


class Ruler():

    def __init__(self, interface):
        self.ui = interface
        self.colorOne = NSColor.colorWithCalibratedRed_green_blue_alpha_(1,0,0,.5)
        self.colorTwo = NSColor.colorWithCalibratedRed_green_blue_alpha_(0,.2,.8,.3)
        self.active = False
        self.closest = None
        self.ortho = None
        self.mousePt = None
        self.activDraw = 0
        self.keydidUp = 0
        self.glyph = self.ui.glyph
        self.ui.w.bind('close', self.windowWillClose)
        self.observer()

    def windowWillClose(self, sender):
        self.observer(remove=True)
        
    def observer(self, remove = False):
        if not remove:
            addObserver(self, "draw", "draw")
            addObserver(self, "draw", "drawPreview")
            addObserver(self, "mouseMoved", "mouseMoved")
            addObserver(self, "currentGlyphChanged", "currentGlyphChanged")
            addObserver(self, "keyDown", "keyDown")
            addObserver(self, "keyUp", "keyUp")
            return
        removeObserver(self, "draw")
        removeObserver(self, "drawPreview")
        removeObserver(self, "mouseMoved")
        removeObserver(self, "currentGlyphChanged")
        removeObserver(self, "keyDown")
        removeObserver(self, "keyUp")

    def keyDown(self, sender):
        self.glyph = CurrentGlyph()
        if self.glyph is None: return
        command = extractNSEvent(sender['event'])["commandDown"]
        if sender['event'].characters() == "r":
            self.activDraw = 1
            self.keydidUp = 0
        if sender['event'].characters() == "r" and command:
            self.activDraw = 0
        UpdateCurrentGlyphView()

    def keyUp(self, sender):
        self.keydidUp = 1
        UpdateCurrentGlyphView()
        
    def currentGlyphChanged(self, info):
        if not self.mousePt: return
        self.closest = self.ortho = None
        self.sections = []
        if not self.glyph: return
        self.pen = ClosestPointPen(self.mousePt, self.glyph.getParent())
        self.glyph.draw(self.pen)
        self.closest, self.ortho = self.pen.getClosestData()
        UpdateCurrentGlyphView()
        
    def draw(self, info):
        if not self.activDraw: return
        if self.closest and self.ortho:
            p = self.closest[0], self.closest[1]
            s = info['scale']
            r = 2.5*s
            rOutline = 5*s
            rOutline2 = 8*s
            strokeWidth(.5*s)
            
            normOrtho = self.normalize(self.ortho)

            save()
            newPath()
            stroke(.2)
            endOut = p[0] + normOrtho[0]*1000, p[1] + normOrtho[1]*1000
            moveTo(endOut)
            endIn = p[0] - normOrtho[0]*1000, p[1] - normOrtho[1]*1000
            lineTo(endIn)
            closePath()
            drawPath()
            restore()
            
            save()
            fill(None)
            stroke(1, 0, 1)
            oval(p[0]-rOutline, p[1]-rOutline, 2*rOutline, 2*rOutline)
            oval(p[0]-rOutline2, p[1]-rOutline2, 2*rOutline2, 2*rOutline2)
            restore()
            
            self.sections = IntersectGlyphWithLine(self.glyph, 
                    (endOut, endIn), 
                    canHaveComponent=True, 
                    addSideBearings=False)
            self.sections.sort()
            
            save()
            lens = len(self.sections)
            if lens > 1:
                for i in range(lens-1):

                    cur = self.sections[i]           
                    next = self.sections[(i+1)%lens]
                    dist = distance(cur, next)
                    fontsize = 9*s#*(max(1, min(1.5, 100/dist)))
                    midPt = (cur[0]+next[0])*.5, (cur[1]+next[1])*.5 

                    if self.glyph.pointInside(midPt):
                        fillText = 0
                        fillDisc = 1              
                    else:
                        fillText = 1
                        fillDisc = 0

                    save()
                    fill(1, 0, 1)
                    stroke(None)
                    oval(cur[0]-r, cur[1]-r, 2*r, 2*r)
                    restore()

                    txt = str(int(dist))  
                    stroke(None)                  
                    fill(fillDisc, fillDisc, fillDisc, .8)

                    oval(midPt[0]-fontsize*1.5, midPt[1]-fontsize*1.35, 2*fontsize*1.5, 2*fontsize*1.5)
                    font('Menlo-Bold', fontsize)
                    
                    fill(fillText)
                    text(txt, midPt[0]-fontsize*.3*len(txt), midPt[1]-fontsize*.5)
                save()
                fill(1, 0, 1)
                stroke(None)
                oval(next[0]-r, next[1]-r, 2*r, 2*r)
                restore()
            restore()
            
    def mouseMoved(self, info):
        if not self.activDraw: return
        if self.keydidUp == 1: return
        self.mousePt = (info['point'].x, info['point'].y)
        self.pen = ClosestPointPen(self.mousePt, self.glyph.getParent())
        self.glyph.draw(self.pen)
        self.closest, self.ortho = self.pen.getClosestData()
        UpdateCurrentGlyphView()
        
    def normalize(self, a):
        l = self.lengtha(a)
        return(a[0]/l, a[1]/l)
    
    def lengtha(self, a):
        return(sqrt(a[0]*a[0]+a[1]*a[1]))


class ClosestPointPen(BasePen):
    def __init__(self, point, font):
        BasePen.__init__(self, glyphSet=font)
        self.currentPt = None
        self.firstPt = None
        self.orthoPt = None
        self.approximateSegmentLength = 1
        self.point = point
        self.bestDistance = 100000

    def _moveTo(self, pt):
        self.currentPt = pt
        self.firstPt = pt

    def _lineTo(self, pt):
        if pt == self.currentPt:
            return
        d = distance(self.currentPt, pt)
        maxSteps = int(round(d / self.approximateSegmentLength))
        if maxSteps < 1:
            self.currentPt = pt
            return
        step = 1.0 / maxSteps
        for factor in range(1, maxSteps + 1):
            pti = interpolatePoint(self.currentPt, pt, factor * step)
            prev_pt = interpolatePoint(self.currentPt, pt, (factor-1) * step)
            dist = distance(pti, self.point)
            if self.bestDistance > dist:
                self.bestDistance = dist
                self.closest = pti
                self.orthoPt = self.getOrtho(prev_pt, pti)
        self.currentPt = pt
        
    def _curveToOne(self, pt1, pt2, pt3):
        falseCurve = (pt1 == self.currentPt) and (pt2 == pt3)
        if falseCurve:
            self._lineTo(pt3)
            return
        est = estimateCubicCurveLength(self.currentPt, pt1, pt2, pt3) / self.approximateSegmentLength
        maxSteps = int(round(est))
        if maxSteps < 1:
            self.currentPt = pt3
            return
        step = 1.0 / maxSteps
        for factor in range(1, maxSteps + 1):
            pt = getCubicPoint(factor * step, self.currentPt, pt1, pt2, pt3)
            prev_pt = getCubicPoint((factor-1) * step, self.currentPt, pt1, pt2, pt3)
            dist = distance(pt, self.point)
            if self.bestDistance > dist:
                self.bestDistance = dist
                self.closest = pt
                self.orthoPt = self.getOrtho(prev_pt, pt)
        self.currentPt = pt3
        
    def _qCurveToOne(self, pt1, pt2):
        falseCurve = (pt1 == self.currentPt) or (pt1 == pt2)
        if falseCurve:
            self._lineTo(pt2)
            return
        est = calcQuadraticArcLength(self.currentPt, pt1, pt2) / self.approximateSegmentLength
        maxSteps = int(round(est))
        if maxSteps < 1:
            self.currentPt = pt2
            return
        step = 1.0 / maxSteps
        for factor in range(1, maxSteps + 1):
            pt = getQuadraticPoint(factor * step, self.currentPt, pt1, pt2)
            prev_pt = getQuadraticPoint((factor-1) * step, self.currentPt, pt1, pt2)
            dist = distance(pt, self.point)
            if self.bestDistance > dist:
                self.bestDistance = dist
                self.closest = pt
                self.orthoPt = self.getOrtho(prev_pt, pt)
        self.currentPt = pt2

    def _closePath(self):
        self.lineTo(self.firstPt)
        self.currentPt = None

    def _endPath(self):
        self.currentPt = None
    
    def getClosestData(self):
        return(self.closest, self.orthoPt)
    
    def getOrtho(self, p1, p2):
        dx1 = p2[0] - p1[0]
        dy1 = p2[1] - p1[1]
        return(-dy1, dx1)
    