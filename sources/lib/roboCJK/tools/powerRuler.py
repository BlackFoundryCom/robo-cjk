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


from fontPens.penTools import estimateCubicCurveLength, distance, interpolatePoint, getCubicPoint
from fontTools.misc.bezierTools import calcQuadraticArcLength
from fontTools.pens.basePen import BasePen

from mojo.roboFont import *
from AppKit import *


class Ruler():

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.colorOne = NSColor.colorWithCalibratedRed_green_blue_alpha_(1,0,0,.5)
        self.colorTwo = NSColor.colorWithCalibratedRed_green_blue_alpha_(0,.2,.8,.3)
        self.active = False
        self.closest = None
        self.ortho = None
        self.mousePt = None
        self.activDraw = 0
        self.keydidUp = 0

    def keyUp(self):
        self.keydidUp = 1

    def launchPowerRuler(self):
        self.activDraw = 1
        self.keydidUp = 0

    def killPowerRuler(self):
        self.activDraw = 0

    def mouseMoved(self, x, y):
        if not self.activDraw: return
        if self.keydidUp == 1: return
        self.mousePt = (x, y)
        self.pen = ClosestPointPen(self.mousePt, self.RCJKI.currentGlyph.getParent())
        self.RCJKI.currentGlyph.draw(self.pen)
        self.closest, self.ortho = self.pen.getClosestData()

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
    