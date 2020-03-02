import math

def deepdeepdeepolation(masterCharacterGlyph, characterGlyphVariations, characterGlyphAxisInfos):
    ### CLEANING TODO ###
    deltaCG = []
    for masterDeepComponentInstance in masterCharacterGlyph:
        deltaDC = {}
        deltaDC['name'] = masterDeepComponentInstance['name']
        deltaDC['x'] = masterDeepComponentInstance['x']
        deltaDC['y'] = masterDeepComponentInstance['y']
        deltaDC['scalex'] = masterDeepComponentInstance['scalex']
        deltaDC['scaley'] = masterDeepComponentInstance['scaley']
        deltaDC['rotation'] = masterDeepComponentInstance['rotation']
        deltaDC['coord'] = {}
        for axisName, value in masterDeepComponentInstance['coord'].items():
            deltaDC['coord'][axisName] = 0
        deltaCG.append(deltaDC)
    
    for characterGlyphAxisName, sourceCharacterGlyph in characterGlyphVariations.items():
        ratio = characterGlyphAxisInfos[characterGlyphAxisName]
        for i, sourceDeepComponent in enumerate(sourceCharacterGlyph):
            sourceDeepComponent_x = sourceDeepComponent['x']
            sourceDeepComponent_y = sourceDeepComponent['y']
            sourceDeepComponent_scalex = sourceDeepComponent['scalex']
            sourceDeepComponent_scaley = sourceDeepComponent['scaley']
            sourceDeepComponent_rotation = sourceDeepComponent['rotation']
            sourceDeepComponent_coord = sourceDeepComponent['coord']
            deltaCG[i]['x'] += (masterCharacterGlyph[i]['x'] - sourceDeepComponent_x)* ratio
            deltaCG[i]['y'] += (masterCharacterGlyph[i]['y'] - sourceDeepComponent_y)* ratio
            deltaCG[i]['scalex'] *= (masterCharacterGlyph[i]['scalex'] - sourceDeepComponent_scalex)* ratio
            deltaCG[i]['scaley'] *= (masterCharacterGlyph[i]['scaley'] - sourceDeepComponent_scaley)* ratio
            deltaCG[i]['rotation'] += (masterCharacterGlyph[i]['rotation'] - sourceDeepComponent_rotation)* ratio
            
            for sourceDeepComponentAxisName, sourceDeepComponentAxisRatio in sourceDeepComponent_coord.items():
                deltaCG[i]['coord'][sourceDeepComponentAxisName] += ratio * (masterCharacterGlyph[i]['coord'][sourceDeepComponentAxisName] - sourceDeepComponentAxisRatio)
        
    outputCG = []
    for i, masterDeepComponent in enumerate(masterCharacterGlyph):
        outputDC = {}
        outputDC['name'] = masterDeepComponent['name']
        outputDC['x'] = masterDeepComponent['x'] - deltaCG[i]['x']
        outputDC['y'] = masterDeepComponent['y'] - deltaCG[i]['y']
        outputDC['scalex'] = masterDeepComponent['scalex'] - deltaCG[i]['scalex']
        outputDC['scaley'] = masterDeepComponent['scaley'] - deltaCG[i]['scaley']
        outputDC['rotation'] = masterDeepComponent['rotation'] - deltaCG[i]['rotation']
        outputDC['coord'] = {}
        for axisName, value in masterDeepComponent['coord'].items():
            outputDC['coord'][axisName] = value - deltaCG[i]['coord'][axisName]
        outputCG.append(outputDC)
    return(outputCG)
    
def deepdeepolation(masterDeepComponent, sourceDeepComponents, deepComponentAxisInfos={}):
    deltaDC = []
    for masterAtomicElement in masterDeepComponent:
        deltaAE = {}
        deltaAE['name'] = masterAtomicElement['name']
        deltaAE['x'] = 0#masterAtomicElement['x']
        deltaAE['y'] = 0#masterAtomicElement['y']
        deltaAE['scalex'] = 1#masterAtomicElement['scalex']
        deltaAE['scaley'] = 1#masterAtomicElement['scaley']
        deltaAE['rotation'] = 0#masterAtomicElement['rotation']

        deltaAE['coord'] = {}
        for axisName, value in masterAtomicElement['coord'].items():
            deltaAE['coord'][axisName] = 0#value
        deltaDC.append(deltaAE)

    for deepComponentAxisName, sourceDeepComponent in sourceDeepComponents.items():
        ratio = deepComponentAxisInfos.get(deepComponentAxisName, 0)
        for i, sourceAtomicElement in enumerate(sourceDeepComponent):

            for e in ['x', 'y', 'rotation']:
                deltaDC[i][e] += (masterDeepComponent[i][e] - sourceAtomicElement[e]) * ratio
            for e in ['scalex', 'scaley']:
                deltaDC[i][e] *= (masterDeepComponent[i][e] - sourceAtomicElement[e]) * ratio
        
            for sourceAtomicElementAxisName, sourceAtomicElementAxisRatio in sourceAtomicElement['coord'].items():
                deltaDC[i]['coord'][sourceAtomicElementAxisName] += ratio * (masterDeepComponent[i]['coord'][sourceAtomicElementAxisName] - sourceAtomicElementAxisRatio)
    
    outputDC = []
    for i, masterAtomicElement in enumerate(masterDeepComponent):
        outputAE = {}
        outputAE['name'] = masterAtomicElement['name']
        for e in ['x', 'y', 'scalex', 'scaley', 'rotation']:
            outputAE[e] = masterAtomicElement[e] - deltaDC[i][e]  

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