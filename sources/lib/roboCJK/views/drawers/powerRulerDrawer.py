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

from fontPens.penTools import distance

from mojo.drawingTools import *
from mojo.tools import IntersectGlyphWithLine

from math import sqrt
from mojo.roboFont import *

from AppKit import *

class PowerRulerDrawer():

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI

    def draw(self, scale = 1):
        if not self.RCJKI.powerRuler.activDraw: return

        if self.RCJKI.powerRuler.closest and self.RCJKI.powerRuler.ortho:
            p = self.RCJKI.powerRuler.closest[0], self.RCJKI.powerRuler.closest[1]
            s = scale
            r = 2.5*s
            rOutline = 5*s
            rOutline2 = 8*s
            strokeWidth(.5*s)
            
            normOrtho = self.normalize(self.RCJKI.powerRuler.ortho)

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
            
            self.RCJKI.powerRuler.sections = IntersectGlyphWithLine(self.RCJKI.currentGlyph, 
                    (endOut, endIn), 
                    canHaveComponent=True, 
                    addSideBearings=False)
            self.RCJKI.powerRuler.sections.sort()
            
            save()
            lens = len(self.RCJKI.powerRuler.sections)
            if lens > 1:
                for i in range(lens-1):

                    cur = self.RCJKI.powerRuler.sections[i]           
                    next = self.RCJKI.powerRuler.sections[(i+1)%lens]
                    dist = distance(cur, next)
                    fontsize = 9*s#*(max(1, min(1.5, 100/dist)))
                    midPt = (cur[0]+next[0])*.5, (cur[1]+next[1])*.5 

                    if self.RCJKI.currentGlyph.pointInside(midPt):
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
        
    def normalize(self, a):
        l = self.lengtha(a)
        return(a[0]/l, a[1]/l)
    
    def lengtha(self, a):
        return(sqrt(a[0]*a[0]+a[1]*a[1]))
