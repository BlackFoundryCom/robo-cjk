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
from ufoLib.pointPen import PointToSegmentPen
from mojo.roboFont import *
import math

def checkCompatible(g1, g2):
    lenghtContour = lambda g: [len(c) for c in g]
    baseGlyph = lambda g: [c.baseGlyph for c in g.components]
    if lenghtContour(g1) != lenghtContour(g2):
        return False
    if baseGlyph(g1) != baseGlyph(g2):
        return False
    return True

def checkInterpolationResult(g, g1, g2, ratio_x, ratio_y, scale_x, scale_y):
    for c, c1, c2 in zip(g, g1, g2):
        
        boxx = (c.box[0] + ((c.box[2] - c.box[0])))
        boxy = (c.box[1] + ((c.box[3] - c.box[1])))

        box1x = ((c1.box[0] + ((c1.box[2] - c1.box[0]))))
        box1y = ((c1.box[1] + ((c1.box[3] - c1.box[1]))))

        box2x = ((c2.box[0] + ((c2.box[2] - c2.box[0]))))
        box2y = ((c2.box[1] + ((c2.box[3] - c2.box[1]))))

        middlex = (box1x + (box2x - box1x) * ratio_x) * scale_x
        middley = (box1y + (box2y - box1y) * ratio_y) * scale_y

        if not middlex - 1 < boxx < middlex + 1 or not middley - 1 < boxy < middley + 1:
            return "contourFailed", 0
        return True
        
def interpol_glyph_glyph_ratioX_ratioY_scaleX_scaleY_toFont_glyphName(g1, g2, ratio_x, ratio_y, scale_x, scale_y, f, glyphName):
    if glyphName not in f.keys():
        g = f.newGlyph(glyphName)
    else:
        return f[glyphName]

    if not checkCompatible(g1, g2):
        return False, None

    pen = PointToSegmentPen(g.getPen())
    for c1, c2 in zip(g1.contours, g2.contours):

        pen.beginPath()
        for p1, p2 in zip(c1.points, c2.points):

            if not p1.type == p2.type:
                return "glyphFailed", 0

            px = (p1.x + ((p2.x - p1.x) * ratio_x)) * scale_x
            py = (p1.y + ((p2.y - p1.y) * ratio_y)) * scale_y
            ptype = p1.type if p1.type != 'offcurve' else None
            pen.addPoint((px, py), ptype)

        pen.endPath()

    g.unicode = g1.unicode
    g.width = (g1.width + ((g2.width - g1.width) * ratio_x)) * scale_x
    # g.round()

    for c1, c2 in zip(g1.components, g2.components):
        name = c1.baseGlyph
        interpol_glyph_glyph_ratioX_ratioY_scaleX_scaleY_toFont_glyphName(g1.getParent()[name], g2.getParent()[name], ratio_x, ratio_y, scale_x, scale_y, f, name)

        cOffsetX = (c1.offset[0] + ((c2.offset[0] - c1.offset[0]) * ratio_x)) * scale_x
        cOffsetY = (c1.offset[1] + ((c2.offset[1] - c1.offset[1]) * ratio_y)) * scale_y

        g.appendComponent(name, offset=(cOffsetX, cOffsetY))
    
    return True, g

def deepCompatible(masterGlyph, layersNames):
    for layerName in layersNames:
        glyph = masterGlyph.getLayer(layerName)
        if len(glyph) != len(masterGlyph):
            return False
        for c1, c2 in zip(glyph, masterGlyph):
            if len(c1) != len(c2):
                return False
    return True

def distance(pt1, pt2):
   return math.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)

def lengtha(a):
   return(math.sqrt(a[0]*a[0]+a[1]*a[1]))

def normalize(a):
   l = lengtha(a)
   if l == 0:
       l = 1e-10
   return([a[0]/l, a[1]/l])

def deepolation(newGlyph, masterGlyph, layersInfo = {}):

    if not deepCompatible(masterGlyph, list(layersInfo.keys())):
        return False

    pen = PointToSegmentPen(newGlyph.getPen())
    contoursList = []

    for contourIndex, contour in enumerate(masterGlyph):

        pointsList = []

        for pointIndex, point in enumerate(contour.points):

            px, py = point.x, point.y
            ptype = point.type if point.type != 'offcurve' else None

            deltaX, deltaY = 0.0, 0.0
            for layerName, value in layersInfo.items():

                ratio = value / 1000.0
                layerGlyph = masterGlyph.getLayer(layerName)

                pI = layerGlyph[contourIndex].points[pointIndex]
                pxI, pyI = pI.x, pI.y

                deltaX += ratio * (pxI-px)
                deltaY += ratio * (pyI-py)

            newX = int(px + deltaX)
            newY = int(py + deltaY)

            pointsList.append([[newX, newY], ptype, point])

        contoursList.append(pointsList)

        for pointsList in contoursList:

            pen.beginPath()
            lenc = len(pointsList)

            for pointIndex, (p, t, point) in enumerate(pointsList):

                if lenc > 1:
                    prevp, prevt, prevPoint = pointsList[pointIndex-1]
                    prevprevp, prevprevt, prevprevPoint = pointsList[pointIndex-2]
                    nextp, nextt, nextPoint = pointsList[(pointIndex+1)%lenc]
                    nextnextp, nextnextt, nextnextPoint = pointsList[(pointIndex+2)%lenc]

                    if prevPoint.smooth and point.type == 'offcurve':

                        dx, dy = prevp[0] - prevprevp[0], prevp[1] - prevprevp[1]
                        d = distance(p, prevp)
                        dprev = normalize([dx, dy])
                        p = [prevp[0]+ d*dprev[0], prevp[1]+d*dprev[1]]

                    if nextPoint.smooth and point.type == 'offcurve':

                        dx, dy = nextp[0] - nextnextp[0], nextp[1] - nextnextp[1]
                        d = distance(p, nextp)
                        dnext = normalize([dx, dy])
                        p = [nextp[0]+ d*dnext[0], nextp[1]+d*dnext[1]]

                    pen.addPoint((int(p[0]), int(p[1])), t)
            pen.endPath()

    return newGlyph