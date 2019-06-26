from mojo.drawingTools import *
from mojo.roboFont import *

class ReferenceViewerDraw():

    def __init__(self, controller, text):
        self.c = controller
        self.t = text
        self.draw()

    def draw(self):
        save()
        for settings in self.c.referenceViewerSettings:
            fontFamily = settings['font']
            size = settings['size']
            color = settings['color']
            x = settings['x']
            y = settings['y']

            font(fontFamily, size)
            r, g, b, a = color
            fill(r, g, b, a)
            text(self.t, (x, y))

            font(fontFamily, 20)
            text(fontFamily, (x, y-10))
        restore()