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
from views import inspectorView
from mojo.UI import UpdateCurrentGlyphView
from mojo.roboFont import *
reload(inspectorView)

class inspectorController(object):
    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.interface = None

    def launchInspectorInterface(self):
        if not self.interface:
            self.interface = inspectorView.Inspector(self.RCJKI)

    def updateViews(self):
        if self.RCJKI.initialDesignController.interface:
            self.RCJKI.initialDesignController.interface.w.mainCanvas.update()
        if self.RCJKI.textCenterController.interface:
            self.RCJKI.textCenterController.interface.w.canvas.update()
        if self.RCJKI.deepComponentEditionController.interface:
            self.RCJKI.deepComponentEditionController.interface.w.mainCanvas.update()
        UpdateCurrentGlyphView()

    def setProperties(self):
        (dist_x, dist_y, nbContours, nbON, nbOFF, offSelection) = self.getSelected()
        (bcpDist_x, bcpDist_y) = self.bcpDistance(offSelection)

        self.RCJKI.properties = "⥓ %s ⥔ %s | ↔︎ %s ↕︎ %s | ◦ %s ⋅ %s ⟜ %s" % (bcpDist_x, bcpDist_y, dist_x, dist_y, nbContours, nbON, nbOFF)

        if self.interface is not None:
            self.interface.properties.properties_textBox.set(self.RCJKI.properties)

    def getDist(self, a_list):
        if a_list:
            return max(a_list) - min(a_list)
        else:
            return 0

    def getSelected(self):
        if self.RCJKI.currentGlyph == None:
            return (0, 0, 0, 0, 0, None)
        nbContours = 0
        nbON = 0
        nbOFF = 0
        list_x = []
        list_y = []
        offSelection = None
        for contour in self.RCJKI.currentGlyph:
            nbContours += 1
            segIdx = -1
            for segment in contour:
                segIdx += 1
                for point in segment:
                    if point.type not in ['offCurve', 'offcurve']:
                        nbON += 1
                    elif point.type in ['offCurve', 'offcurve']:
                        nbOFF += 1
                        if point.selected:
                            offSelection = (contour, segIdx, point)
                    if point.selected:
                        list_x.append(point.x)
                        list_y.append(point.y)

        return (self.getDist(list_x), self.getDist(list_y), nbContours, nbON, nbOFF, offSelection)

    def bcpDistance(self, offSelection):
        if offSelection == None:
            return (0, 0)
        con, segIdx, pt = offSelection
        seg = con[segIdx]
        onPt = pt

        if pt == seg.offCurve[-1]: # 'Incoming'
            onPt = seg.onCurve
        elif pt == seg.offCurve[0]: # 'Outcoming'
            onPt = con[segIdx-1].onCurve
        dx = pt.x - onPt.x
        dy = pt.y - onPt.y
        return (dx, dy)

    def scaleTransformation(self, values):
        if not self.RCJKI.currentGlyph: return

        self.RCJKI.currentGlyph.update()
        self.RCJKI.currentGlyph.prepareUndo()

        contours = list(filter(lambda c: c.selected, self.RCJKI.currentGlyph)) 
        points = [p for c in self.RCJKI.currentGlyph for p in c.points if p.selected]

        if contours:  
            self.scaleContours(contours, values) 
             
        elif points:
            self.scalePoints(points, values) 
             
        else:
            self.scaleContours(self.RCJKI.currentGlyph, values)  

        self.RCJKI.currentGlyph.performUndo()
        self.RCJKI.currentGlyph.update()

        self.RCJKI.updateViews()

    def scaleContours(self, contours, values):
        x, y, w, h = [], [], [], []

        for contour in contours:
            x.append(contour.box[0])
            y.append(contour.box[1])
            w.append(contour.box[2])
            h.append(contour.box[3])

        x = min(x)
        y = min(y)
        w = max(w)
        h = max(h)

        self.scale(contours, values, (x, y, w, h))

    def scale(self, elements, values, pos):
        xValue, yValue = values

        x, y, w, h = pos
        
        centerX = x + (w - x) * .5
        centerY = y + (h - y) * .5

        for element in elements:
            element.scaleBy((xValue, yValue), (centerX, centerY))

    def scalePoints(self, points, values):
        posx, posy = [], []

        for point in points:
            posx.append(point.x)
            posy.append(point.y)

        x = min(posx)
        y = min(posy)
        w = max(posx)
        h = max(posy)

        self.scale(points, values, (x, y, w, h))


