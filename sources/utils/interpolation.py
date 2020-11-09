"""
Copyright 2020 Black Foundry.

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
import math
from fontTools.misc.transform import Transform

def makeTransform(x, y, rotation, scalex, scaley, rcenterx, rcentery, scaleUsesCenter=True):
    rotation = math.radians(rotation)
    if not scaleUsesCenter:
        rcenterx *= scalex
        rcentery *= scaley
        t = Transform()
        t = t.translate(x + rcenterx, y + rcentery)
        t = t.rotate(rotation)
        t = t.translate(-rcenterx, -rcentery)
        t = t.scale(scalex, scaley)
    else:
        t = Transform()
        t = t.translate(x + rcenterx, y + rcentery)
        t = t.rotate(rotation)
        t = t.scale(scalex, scaley)
        t = t.translate(-rcenterx, -rcentery)
    return t

def normalizedValue(v, minv, maxv):
    return (v-minv)/(maxv-minv)
    
def deepdeepolation(masterDeepComponent, sourceDeepComponents, deepComponentAxisInfos={}):
    deepComponentAxisInfos = {k:normalizedValue(v, sourceDeepComponents[k].minValue, sourceDeepComponents[k].maxValue) for k, v in deepComponentAxisInfos.items()}

    deltaDC = []
    for masterAtomicElement in masterDeepComponent:
        coord = dict((axisName, 0) for axisName, value in masterAtomicElement['coord'].items())
        deltaAE = {
                'name'     : masterAtomicElement['name'],
                'x'        : 0, #masterAtomicElement['x']
                'y'        : 0, #masterAtomicElement['y']
                'scalex'   : 1, #masterAtomicElement['scalex']
                'scaley'   : 1, #masterAtomicElement['scaley']
                'rotation' : 0, #masterAtomicElement['rotation']
                'coord'    : coord,
                }

        deltaDC.append(deltaAE)

    for deepComponentAxisName, sourceDeepComponent in sourceDeepComponents.items():
        ratio = deepComponentAxisInfos.get(deepComponentAxisName, 0)
        for i, sourceAtomicElement in enumerate(sourceDeepComponent):
            for e in ['x', 'y', 'rotation']:
                deltaDC[i][e] += (masterDeepComponent[i][e] - sourceAtomicElement[e]) * ratio

            for e in ['scalex', 'scaley']:
                deltaDC[i][e] += ((masterDeepComponent[i][e] - sourceAtomicElement[e]) * ratio)
        
            for sourceAtomicElementAxisName, sourceAtomicElementAxisRatio in sourceAtomicElement['coord'].items():
                if sourceAtomicElementAxisName in deltaDC[i]['coord']:
                    deltaDC[i]['coord'][sourceAtomicElementAxisName] += (ratio * (masterDeepComponent[i]['coord'][sourceAtomicElementAxisName] - sourceAtomicElementAxisRatio))
               
    outputDC = []
    for i, masterAtomicElement in enumerate(masterDeepComponent):
        outputAE = {}
        outputAE['name'] = masterAtomicElement['name']
        for e in ['x', 'y', 'rotation']:
            outputAE[e] = masterAtomicElement[e] - deltaDC[i][e]  

        for e in ["scalex", "scaley"]:
            outputAE[e] = masterAtomicElement[e] - (deltaDC[i][e] - 1)

        outputAE['coord'] = {}
        for axisName, value in masterAtomicElement['coord'].items():
            outputAE['coord'][axisName] = (value - deltaDC[i]['coord'][axisName])
        outputDC.append(outputAE)
    return(outputDC)

        
from fontTools.ufoLib.pointPen import PointToSegmentPen

def deepolation(newGlyph, masterGlyph, layersInfo = {}, axisMinValue = 0., axisMaxValue = 1.):
    if not deepCompatible(masterGlyph, list(layersInfo.keys())):
        return None
    pen = PointToSegmentPen(newGlyph.getPen())
    contoursList = []
    for contourIndex, contour in enumerate(masterGlyph):
        pointsList = []
        for pointIndex, point in enumerate(contour.points):
            px, py = point.x, point.y
            ptype = point.type if point.type != 'offcurve' else None
            deltaX, deltaY = 0.0, 0.0
            for layerName, value in layersInfo.items():
                ratio = value
                layerGlyph = masterGlyph.getLayer(layerName)
                pI = layerGlyph[contourIndex].points[pointIndex]
                deltaX += ratio * (px - pI.x)
                deltaY += ratio * (py - pI.y)
            newX = int(px - deltaX)
            newY = int(py - deltaY)
            pointsList.append([[newX, newY], ptype, point])
        contoursList.append(pointsList)

    for pointsList in contoursList:
        lenc = len(pointsList)
        if lenc <= 1: continue
        pen.beginPath()
        for pointIndex, (p, t, point) in enumerate(pointsList):
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

def deepCompatible(masterGlyph, layersNames):
    for layerName in layersNames:
        glyph = masterGlyph.getLayer(layerName)
        if len(glyph) != len(masterGlyph):
            print(layerName, len(glyph), len(masterGlyph))
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
       l = 1e-10 #FIXME: just return a or throw an exception
   return([a[0]/l, a[1]/l])

def interpol_glyph_glyph_ratioX_ratioY_scaleX_scaleY(g1, g2, ratio_x, ratio_y, scale_x, scale_y, f):
    glyphName = g1.name
    if glyphName not in f.keys():
        g = f.newGlyph(glyphName)
    else:
        
        return f[glyphName]
    pen = PointToSegmentPen(g.getPen())
    if not len(g1) == len(g2):
        return 0
    for c1, c2 in zip(g1.contours, g2.contours):
        if not len(c1) == len(c2):
            return 0
        pen.beginPath()
        for p1, p2 in zip(c1.points, c2.points):
            if not p1.type == p2.type:
                g.markColor = (1, 0, 0, 1)
                return 0
            px = (p1.x + ((p2.x - p1.x) * ratio_x)) * scale_x
            py = (p1.y + ((p2.y - p1.y) * ratio_y)) * scale_y
            ptype = p1.type if p1.type != 'offcurve' else None
            pen.addPoint((px, py), ptype)
        pen.endPath()

    g.unicode = g1.unicode
    g.width = (g1.width + ((g2.width - g1.width) * ratio_x)) * scale_x
    
    # for c1, c, c2 in zip(g1, g, g2):
    #     box1x = ((c1.box[0] + ((c1.box[2] - c1.box[0])) ))
    #     box1y = ((c1.box[1] + ((c1.box[3] - c1.box[1])) ))
    #     boxx = (c.box[0] + ((c.box[2] - c.box[0])))
    #     boxy = (c.box[1] + ((c.box[3] - c.box[1])))
    #     box2x = ((c2.box[0] + ((c2.box[2] - c2.box[0])) ))
    #     box2y = ((c2.box[1] + ((c2.box[3] - c2.box[1])) ))
    #     middlex = (box1x+(box2x-box1x)* ratio_x)*scale_x
    #     middley = (box1y+(box2y-box1y)* ratio_y)*scale_y
    #     if not middlex-1 < boxx < middlex+1 or not middley-1 < boxy < middley+1:
    #         print('fail 4')
    #         return 0

    if not len(g1.components) == len(g2.components):
        return g
        
    for c1, c2 in zip(g1.components, g2.components):
        if not c1.baseGlyph == c2.baseGlyph:
            
            return g
        name = c1.baseGlyph
        interpol_glyph_glyph_ratioX_ratioY_scaleX_scaleY_toFont_glyphName(g1.getParent()[name], g2.getParent()[name], ratio_x, ratio_y, scale_x, scale_y, f, name)
        cOffsetX=(c1.offset[0] + ((c2.offset[0] - c1.offset[0]) * ratio_x)) * scale_x
        cOffsetY=(c1.offset[1] + ((c2.offset[1] - c1.offset[1]) * ratio_y)) * scale_y
        g.appendComponent(name, offset=(cOffsetX, cOffsetY))
    
    return g