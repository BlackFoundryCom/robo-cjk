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
from vanilla import *
from lib.cells.colorCell import RFColorCell
from AppKit import NSColor

smartComponentSuffix=".smart"

class SmartComponents(Group):

    def __init__(self, posSize, interface):
        super(SmartComponents, self).__init__(posSize)
        self.ui = interface
        self.font = self.ui.font

        self.bases = Group((0,25,-0,-0))
        self.bases.show(1)
        self.glyphs = Group((0,25,-0,-0))
        self.glyphs.show(0)

        self.segmentedButton = SegmentedButton((10,5,-10,20), 
                [dict(title="Bases", width = 139), 
                dict(title="Glyphs", width = 139)],
                callback = self._smartComponent_SegmentedButton_callback)

        self.segmentedButton.set(0)

        self.bases.layers_textBox = TextBox((10,10,100,20),
                 'Layers',
                 sizeStyle="small")

        self.smartComponentLayerList = []

        contourColorCell = RFColorCell.alloc().init()

        if self.font:
            smartComponentLayerList = list(filter(lambda x: x.name.endswith(smartComponentSuffix), self.font.layers))
            if smartComponentLayerList:
                self.smartComponentLayerList = [dict(Name = x.name, Color=NSColor.colorWithCalibratedRed_green_blue_alpha_(x.color[0],x.color[1],x.color[2],x.color[3])) for x in smartComponentLayerList]

        self.bases.layers_list = List((10,30,-10,80),
                 self.smartComponentLayerList,
                 columnDescriptions=[{"title": "Name"}, {"title": "Color", "cell":contourColorCell}],
                 drawFocusRing = False,
                 allowsMultipleSelection=False)

        self.bases.addLayer_button = Button((-150,115,-81,20),
                 "+",
                 sizeStyle="small",
                 callback = self._smartComponentBase_addLayer_callback)

        self.bases.delLayer_button = Button((-80,115,-10,20),
                 "-",
                 sizeStyle="small",
                 callback = self._smartComponentBase_delLayer_callback)

        self.bases.copyLayerToLayer_button = Button((10,140,-10,20),
                 "Copy selected layer to current",
                 sizeStyle="small")


    def _smartComponent_SegmentedButton_callback(self, sender):
        sel = sender.get()
        self.bases.show(abs(sel-1))
        self.glyphs.show(sel)

    def _smartComponentBase_addLayer_callback(self, sender):

        i=0
        while True:
            name = "new%s%s"%(str(i).zfill(2), smartComponentSuffix)
            if name not in [x.name for x in self.font.layers]: 
                break
            i+=1

        self.font.newLayer(name)
        smartComponentLayerList = list(filter(lambda x: x.name.endswith(smartComponentSuffix), self.font.layers))
        self.smartComponentLayerList = [dict(Name = x.name, Color=NSColor.colorWithCalibratedRed_green_blue_alpha_(x.color[0],x.color[1],x.color[2],x.color[3])) for x in smartComponentLayerList]
        self.bases.layers_list.set(self.smartComponentLayerList)

    def _smartComponentBase_delLayer_callback(self, sender):
        sel = self.bases.layers_list.getSelection()
        if not sel:
            message("Warning there is no selected layers")
            return
        smartComponentLayerList = []
        for i, e in enumerate(self.smartComponentLayerList):
            if i not in sel:
                smartComponentLayerList.append(e)
            else:
                self.font.removeLayer(e["Name"])
        self.smartComponentLayerList = smartComponentLayerList
        self.bases.layers_list.set(self.smartComponentLayerList)