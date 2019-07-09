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

class DeepComponentsInstantiator(Group):

    def __init__(self, posSize, interface):
        super(DeepComponentsInstantiator, self).__init__(posSize)
        self.ui = interface

        segmentedElements = ["Select Deep Component", "New Deep Component"]
        self.deepCompo_segmentedButton = SegmentedButton((0,0,-0,20), 
                [dict(title=e, width = (550)/len(segmentedElements)) for e in segmentedElements],
                callback = self._deepCompo_segmentedButton_callback,
                sizeStyle='regular')
        
        self.selectDeepCompo = Group((0, 30,-0, -0))
        self.newDeepCompo = Group((0, 30,-0, -0))

        self.selectDeepCompo.list = List((0, 0, -170, -0), [])
        self.newDeepCompo.list = List((0, 0, -170, -0), [])

        self.deepCompo_segmentedButton.set(0)
        self.newDeepCompo.show(0)

        self.addDeepCompo = SquareButton((-160, 30, -0, 30), 
            "Add", 
            sizeStyle = "small")
        self.replaceDeepCompo = SquareButton((-160, 65, -0, 30), 
            "Replace", 
            sizeStyle = "small")

    def _deepCompo_segmentedButton_callback(self, sender):
        sel = sender.get()
        self.selectDeepCompo.show(abs(sel-1))
        self.newDeepCompo.show(sel)