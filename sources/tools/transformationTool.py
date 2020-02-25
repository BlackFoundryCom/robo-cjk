from mojo.events import BaseEventTool, getActiveEventTool
from mojo.UI import UpdateCurrentGlyphView
import math

def angle( cx, cy, ex, ey):
        dy = ey - cy
        dx = ex - cx
        theta = math.atan2(dx, dy)
        theta *= 180 / math.pi
        return theta

class TransformationTool(BaseEventTool):

    def __init__(self, RCJKI):
        super().__init__()
        self.RCJKI = RCJKI

    def mouseDown(self, point, clickcount):
        self.px, self.py = self.deltax, self.deltay = point

    def mouseDragged(self, point, delta):
        option = getActiveEventTool().getModifiers()['optionDown']
        
        if option:
            rotation = angle(self.px, self.py, *point)
            self.RCJKI.currentGlyph.setRotationAngleToSelectedElements(rotation, append = False)
        else:
            x = point.x - self.deltax
            y = point.y - self.deltay
            self.RCJKI.currentGlyph.setPositionToSelectedElements((x, y))

        self.deltax, self.deltay = point
        UpdateCurrentGlyphView()