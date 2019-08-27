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
reload(inspectorView)

class inspectorController(object):
    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.interface = None

    def launchInspectorInterface(self):
        if not self.interface:
            self.interface = inspectorView.Inspector(self.RCJKI)

    def updateViews(self):
        self.RCJKI.initialDesignController.interface.w.mainCanvas.update()
        if self.RCJKI.textCenterController.interface:
            self.RCJKI.textCenterController.interface.w.canvas.update()
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
            return
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