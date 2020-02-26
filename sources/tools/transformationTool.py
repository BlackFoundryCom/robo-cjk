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
        modifiers = getActiveEventTool().getModifiers()
        option = modifiers['optionDown']
        command = modifiers['commandDown']
        
        if option:
            rotation = angle(self.px, self.py, *point)
            self.RCJKI.currentGlyph.setRotationAngleToSelectedElements(rotation, append = False)
        elif command:
            deltax = int(point.x - self.deltax)
            deltay = int(point.y - self.deltay)
            sensibility = 250
            deltax /= sensibility
            deltay /= sensibility
            self.RCJKI.currentGlyph.setScaleToSelectedElements(round(deltax, 3), round(deltay, 3))
        else:
            x = int(point.x - self.deltax)
            y = int(point.y - self.deltay)
            self.RCJKI.currentGlyph.setPositionToSelectedElements((x, y))

        self.deltax, self.deltay = point
        UpdateCurrentGlyphView()
