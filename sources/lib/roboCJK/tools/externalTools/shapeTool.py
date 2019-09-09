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

This file incorporates work covered by the following copyright and  
permission notice:  

    The MIT License (MIT)

    Copyright (c) 2016 Frederik Berlaen

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

from mojo.events import BaseEventTool, installTool
from AppKit import *

from lib.tools.drawing import strokePixelPath

from dialogKit import ModalDialog, TextBox, EditText
from vanilla import RadioGroup

try:
    from ufoLib.pointPen import ReverseContourPointPen
except:
    from robofab.pens.reverseContourPointPen import ReverseContourPointPen

from mojo.extensions import ExtensionBundle


import os
cwd = os.getcwd()
rdir = os.path.abspath(os.path.join(cwd, os.pardir))
# toolbarIcon = NSImage.alloc().initByReferencingFile_(os.path.join(rdir, "RoboCJK/resources/ShapeTool_ToolbarIcon.pdf"))


shapeBundle = None#ExtensionBundle("roboCJK")
_cursorOval = None#CreateCursor(shapeBundle.get("cursorOval"), hotSpot=(6, 6))

_cursorRect = None#CreateCursor(shapeBundle.get("cursorRect"), hotSpot=(6, 6))

toolbarIcon = NSImage.alloc().initByReferencingFile_(os.path.join(rdir, "RoboCJK/resources/ShapeTool_ToolbarIcon.pdf"))


class GeometricShapesWindow(object):
    """
    The Modal window that allows numbers input to draw basic geometric shapes.
    """

    def __init__(self, glyph, callback, x, y):
        self.glyph = glyph
        self.callback = callback
        # create the modal dialog (from dialogKit)
        self.w = ModalDialog((200, 150),
                            "Shapes Tool",
                            okCallback=self.okCallback,
                            cancelCallback=self.cancelCallback)

        # add some text boxes
        self.w.xText = TextBox((10, 13, 100, 22), "x")
        self.w.yText = TextBox((10, 43, 100, 22), "y")
        self.w.wText = TextBox((100, 13, 100, 22), "w")
        self.w.hText = TextBox((100, 43, 100, 22), "h")

        # adding input boxes
        self.w.xInput = EditText((30, 10, 50, 22), "%i" % x)
        self.w.yInput = EditText((30, 40, 50, 22), "%i" % y)
        self.w.wInput = EditText((120, 10, 50, 22))
        self.w.hInput = EditText((120, 40, 50, 22))

        # a radio shape choice group
        # (the RadioGroup isn't standaard in dialogKit, this is a vanilla object)
        self.shapes = ["rect", "oval"]
        self.w.shape = RadioGroup((10, 70, -10, 22), self.shapes, isVertical=False)
        self.w.shape.set(0)

        self.w.open()

    def okCallback(self, sender):
        # draw the shape in the glyph
        # get the shape from the radio group
        shape = self.shapes[self.w.shape.get()]
        # try to get some integers from the input fields
        try:
            x = int(self.w.xInput.get())
            y = int(self.w.yInput.get())
            w = int(self.w.wInput.get())
            h = int(self.w.hInput.get())
        # if this fails just do nothing and print a tiny traceback
        except:
            print("A number is required!")
            return
        # draw the shape with the callback given on init
        self.callback(shape, (x, y, w, h), self.glyph)

    def cancelCallback(self, sender):
        # do nothing :)
        pass


def _roundPoint(x, y):
    return int(round(x)), int(round(y))


class ShapeTool(BaseEventTool):

    def __init__(self, RCJKI):
        super(ShapeTool, self).__init__()
        self.RCJKI = RCJKI
        self.glyph = self.RCJKI.getCurrentGlyph()

    def setup(self):
        # setup is called when the tool gets active
        # use this to initialize some attributes
        self.minPoint = None
        self.maxPoint = None
        self.shape = "rect"
        self.origin = "corner"
        self.moveShapeShift = None
        self.shouldReverse = False

    def getRect(self):
        # return the rect between mouse down and mouse up
        x = self.minPoint.x
        y = self.minPoint.y
        w = self.maxPoint.x - self.minPoint.x
        h = self.maxPoint.y - self.minPoint.y

        # handle the shift down and equalize width and height
        if self.shiftDown:
            sign = 1
            if abs(w) > abs(h):
                if h < 0:
                    sign = -1
                h = abs(w) * sign
            else:
                if w < 0:
                    sign = -1
                w = abs(h) * sign

        if self.origin == "center":
            # if the orgin is centered substract the width and height
            x -= w
            y -= h
            w *= 2
            h *= 2

        # optimize the retangle, so the width and height are always postive numbers
        if w < 0:
            w = abs(w)
            x -= w
        if h < 0:
            h = abs(h)
            y -= h

        return x, y, w, h

    def drawShapeWithRectInGlyph(self, shape, rect, glyph):
        # draw the shape into the glyph
        # tell the glyph something is going to happen (undo is going to be prepared)
        glyph.prepareUndo("Drawing Shapes")

        # get the pen to draw with
        pen = glyph.getPointPen()
        if glyph.preferredSegmentType == "qcurve" and not self.shouldReverse:
            pen = ReverseContourPointPen(pen)
        elif self.shouldReverse:
            pen = ReverseContourPointPen(pen)

        x, y, w, h = rect

        # draw with the pen a rect in the glyph
        if shape == "rect":
            pen.beginPath()
            pen.addPoint(_roundPoint(x, y), "line")
            pen.addPoint(_roundPoint(x + w, y), "line")
            pen.addPoint(_roundPoint(x + w, y + h), "line")
            pen.addPoint(_roundPoint(x, y + h), "line")

            pen.endPath()

        # draw with the pen an oval in the glyph
        elif shape == "oval":

            hw = w/2.
            hh = h/2.

            r = .55
            segmentType = glyph.preferredSegmentType
            if glyph.preferredSegmentType == "qcurve":
                r = .42

            pen.beginPath()
            pen.addPoint(_roundPoint(x + hw, y), segmentType, True)
            pen.addPoint(_roundPoint(x + hw + hw*r, y))
            pen.addPoint(_roundPoint(x + w, y + hh - hh*r))

            pen.addPoint(_roundPoint(x + w, y + hh), segmentType, True)
            pen.addPoint(_roundPoint(x + w, y + hh + hh*r))
            pen.addPoint(_roundPoint(x + hw + hw*r, y + h))

            pen.addPoint(_roundPoint(x + hw, y + h), segmentType, True)
            pen.addPoint(_roundPoint(x + hw - hw*r, y + h))
            pen.addPoint(_roundPoint(x, y + hh + hh*r))

            pen.addPoint(_roundPoint(x, y + hh), segmentType, True)
            pen.addPoint(_roundPoint(x, y + hh - hh*r))
            pen.addPoint(_roundPoint(x + hw - hw*r, y))

            pen.endPath()

        # tell the glyph you are done with your actions so it can handle the undo properly
        glyph.performUndo()
        glyph.changed()

    def mouseDown(self, point, clickCount):
        # a mouse down, only save the mouse down point
        self.minPoint = point
        # on double click pop up an modal dialog with inputs
        if clickCount == 2:
            # create and open the modal dialog
            GeometricShapesWindow(self.RCJKI.getCurrentGlyph(),
                            callback=self.drawShapeWithRectInGlyph,
                            x=self.minPoint.x,
                            y=self.minPoint.y)

    def mouseDragged(self, point, delta):
        # record the draggin point
        self.maxPoint = point
        # if shift the minPoint by the move shift
        if self.moveShapeShift:
            w, h = self.moveShapeShift
            self.minPoint.x = self.maxPoint.x - w
            self.minPoint.y = self.maxPoint.y - h

    def mouseUp(self, point):
        # mouse up, if you have recorded the rect draw that into the glyph
        if self.minPoint and self.maxPoint:
            self.drawShapeWithRectInGlyph(self.shape, self.getRect(), self.RCJKI.getCurrentGlyph())
        # reset the tool
        self.minPoint = None
        self.maxPoint = None

    def keyDown(self, event):
        # reverse on tab
        if event.characters() == "\t":
            self.shouldReverse = not self.shouldReverse
            self.getNSView().refresh()

    def modifiersChanged(self):
        # is been called when the modifiers changed (shift, alt, control, command)
        self.shape = "rect"
        self.origin = "corner"

        # change the shape when option is down
        if self.optionDown:
            self.shape = "oval"
        # change the origin when command is down
        if self.commandDown:
            self.origin = "center"
        # record the current size of the shape and store it
        if self.controlDown and self.moveShapeShift is None and self.minPoint and self.maxPoint:
            w = self.maxPoint.x - self.minPoint.x
            h = self.maxPoint.y - self.minPoint.y
            self.moveShapeShift = w, h
        else:
            self.moveShapeShift = None
        # refresh the current glyph view
        self.getNSView().refresh()

    def draw(self, scale):
        # draw stuff in the current glyph view
        if self.isDragging() and self.minPoint and self.maxPoint:
            # draw only during drag and when recorded some rect
            # make the rect
            x, y, w, h = self.getRect()
            rect = NSMakeRect(x, y, w, h)
            # set the color
            if self.shouldReverse:
                NSColor.blueColor().set()
            else:
                NSColor.redColor().set()

            if self.shape == "rect":
                # create a rect path
                path = NSBezierPath.bezierPathWithRect_(rect)

            elif self.shape == "oval":
                # create a oval path
                path = NSBezierPath.bezierPathWithOvalInRect_(rect)

            if self.origin == "center":
                # draw a cross hair at the center point
                crossHairLength = 3 * scale
                # get the center of the rectangle
                centerX = x + w * .5
                centerY = y + h * .5

                path.moveToPoint_((centerX, centerY - crossHairLength))
                path.lineToPoint_((centerX, centerY + crossHairLength))
                path.moveToPoint_((centerX - crossHairLength, centerY))
                path.lineToPoint_((centerX + crossHairLength, centerY))

            # set the line width
            path.setLineWidth_(scale)
            # draw without anti-alias
            strokePixelPath(path)

    def getDefaultCursor(self):
        # returns the cursor
        if self.shape == "rect":
            return _cursorRect
        else:
            return _cursorOval

    def getToolbarIcon(self):
        # return the toolbar icon
        return toolbarIcon

    def getToolbarTip(self):
        # return the toolbar tool tip
        return "Shape Tool"

# install the tool!!
# installTool(ShapeTool())