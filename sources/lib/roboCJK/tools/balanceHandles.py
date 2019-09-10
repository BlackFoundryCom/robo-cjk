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

from mojo.events import addObserver, removeObserver, extractNSEvent
from mojo.roboFont import *
import math

class BalanceHandles():

    # def __init__(self, RCJKI):
    #     self.ui = interface
    #     self.ui.w.bind('close', self.windowWillClose)
        # self.observer()

    # def windowWillClose(self, sender):
    #     self.observer(remove=True)
        
    # def observer(self, remove = False):
    #     if not remove:
    #         addObserver(self, "keyUp", "keyUp")
    #         return
    #     removeObserver(self, "keyUp")

    # def keyUp(self, info):
    #     self.glyph = self.ui.glyph
    #     modifiers = extractNSEvent(info['event'])
    #     command = modifiers["commandDown"] 
    #     shift = modifiers["shiftDown"] 
    #     char = info['event'].characters()
    #     if command and shift and char == "A":
    #         self.balance(self.glyph)

    def balance(self, g):
        s=[]
        select=[]
        g.prepareUndo()
        for c in g:
            for p in c:
                if p.selected:
                    s.append(p.points)
            for e in s:
                if e[0] in c.points:
                    select.append(c.points[c.points.index(e[0])-1])
                    select.extend(e)

                if len(select)==4:
                    p1, p2, p3, p4 = select[0], select[1], select[2], select[3]

                    firstOffCurveX = p1.x - p2.x
                    firstOffCurveY = p1.y - p2.y
                    secondOffCurveX = p3.x - p4.x
                    secondOffCurveY = p3.y - p4.y

                    epsilon = 1e-09
                    m1 = (p2.y - p1.y) / ((p2.x - p1.x) + epsilon)
                    m2 = (p3.y - p4.y) / ((p3.x - p4.x) + epsilon)

                    b1 = p1.y - (m1 * p1.x)
                    b2 = p4.y - (m2 * p4.x)

                    x = (b2-b1) / (m1-m2)
                    y = m1 * x + b1
                    
                    box1x = p1.x - round(x)
                    box1y = p1.y - round(y)

                    box2x = x - p4.x
                    box2y = y - p4.y

                    alpha1 =  box1x/(math.hypot(box1x, box1y)+epsilon)
                    alpha2 =  box2x/(math.hypot(box2x, box2y)+epsilon)

                    if round(alpha1,4) < 0 and round(alpha2,4) > 0 or round(alpha1,4) > 0 and round(alpha2,4) < 0:
                        pass
                    else:

                        ratio1 = max(firstOffCurveX / (box1x+epsilon) , firstOffCurveY / (box1y+epsilon))
                        ratio2 = max(secondOffCurveY / (box2y+epsilon) , secondOffCurveX / (box2x+epsilon))

                        balance = (ratio1 + ratio2)*.5

                        shift1x = round(firstOffCurveX - box1x * balance)
                        shift1y =  round(firstOffCurveY - box1y * balance)

                        shift2x = -round(secondOffCurveX - box2x * balance)
                        shift2y =  -round(secondOffCurveY - box2y * balance)

                        p2.move(( shift1x, shift1y ))
                        p3.move(( shift2x, shift2y ))

                else:
                    pass
                select = []
        g.update()
        g.performUndo()