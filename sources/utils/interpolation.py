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

def deepdeepdeepolation(masterCharacterGlyph, characterGlyphVariations, characterGlyphAxisInfos):
    deltaCG = []
    for masterDeepComponentInstance in masterCharacterGlyph:
        deltaDC = dict(masterDeepComponentInstance)
        deltaDC['coord'] = {}
        for axisName in masterDeepComponentInstance['coord'].keys():
            deltaDC['coord'][axisName] = 0
        deltaCG.append(deltaDC)
    
    for characterGlyphAxisName, sourceCharacterGlyph in characterGlyphVariations.items():
        ratio = characterGlyphAxisInfos[characterGlyphAxisName]
        for i, sourceDeepComponent in enumerate(sourceCharacterGlyph):
            for e in ['x', 'y', 'rotation']:
                deltaCG[i][e] += (masterCharacterGlyph[i][e] - sourceDeepComponent[e]) * ratio 
            for e in ['scalex', 'scaley']:
                deltaCG[i][e] *= (masterCharacterGlyph[i][e] - sourceDeepComponent[e]) * ratio
            
            for sourceDeepComponentAxisName, sourceDeepComponentAxisRatio in sourceDeepComponent['coord'].items():
                deltaCG[i]['coord'][sourceDeepComponentAxisName] += ratio * (masterCharacterGlyph[i]['coord'][sourceDeepComponentAxisName] - sourceDeepComponentAxisRatio)
        
    outputCG = []
    for i, masterDeepComponent in enumerate(masterCharacterGlyph):
        outputDC = {}
        outputDC['name'] = masterDeepComponent['name']
        for e in ['x', 'y', 'scalex', 'scaley', 'rotation']:
            outputDC[e] = masterDeepComponent[e] - deltaCG[i][e]    

        outputDC['coord'] = {}
        for axisName, value in masterDeepComponent['coord'].items():
            outputDC['coord'][axisName] = value - deltaCG[i]['coord'][axisName]
        outputCG.append(outputDC)

    return(outputCG)
    
def deepdeepolation(masterDeepComponent, sourceDeepComponents, deepComponentAxisInfos={}):
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
                'coord'    : coord
                }

        deltaDC.append(deltaAE)

    for deepComponentAxisName, sourceDeepComponent in sourceDeepComponents.items():
        ratio = deepComponentAxisInfos.get(deepComponentAxisName, 0)
        for i, sourceAtomicElement in enumerate(sourceDeepComponent):

            for e in ['x', 'y', 'rotation', 'scalex', 'scaley']:
                deltaDC[i][e] += (masterDeepComponent[i][e] - sourceAtomicElement[e]) * ratio
        
            for sourceAtomicElementAxisName, sourceAtomicElementAxisRatio in sourceAtomicElement['coord'].items():
                if sourceAtomicElementAxisName in deltaDC[i]['coord']:
                    deltaDC[i]['coord'][sourceAtomicElementAxisName] += ratio * (masterDeepComponent[i]['coord'][sourceAtomicElementAxisName] - sourceAtomicElementAxisRatio)
               
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
            outputAE['coord'][axisName] = value - deltaDC[i]['coord'][axisName]
        outputDC.append(outputAE)
    return(outputDC)

        
from fontTools.ufoLib.pointPen import PointToSegmentPen

def deepolation(newGlyph, masterGlyph, layersInfo = {}):
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
