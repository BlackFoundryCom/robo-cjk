from mojo.events import BaseEventTool, getActiveEventTool
from mojo.UI import UpdateCurrentGlyphView
import math

def angle(cx: int, cy: int, ex: int, ey: int) -> int:
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
        shift = modifiers['shiftDown']

        def shiftLock(dx, dy, x, y):
            if abs(dx) > abs(dy):
                return x, 0
            return 0, y
        
        if option:
            rotation = angle(self.px, self.py, *point)
            self.RCJKI.currentGlyph.setRotationAngleToSelectedElements(rotation, append = False)
            
        elif command:
            deltax = int(point.x - self.deltax)
            deltay = int(point.y - self.deltay)
            sensibility = 100
            deltax /= sensibility
            deltay /= sensibility
            if shift:
                deltax, deltay = shiftLock(delta.x, delta.y, deltax, deltay)
            self.RCJKI.currentGlyph.setScaleToSelectedElements((round(deltax, 3), round(deltay, 3)))
            
        else:
            x = int(point.x - self.deltax)
            y = int(point.y - self.deltay)
            if shift:
                x, y = shiftLock(delta.x, delta.y, x, y)
            self.RCJKI.currentGlyph.setPositionToSelectedElements((x, y))

        self.deltax, self.deltay = point
        UpdateCurrentGlyphView()
