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
import os

class RoboCJKProject(object):
    def __init__(self, name, admin):
        self.name = name
        self.admin = admin
        self.usersLockers = {'lockers':[]}
        self.masterFontsPaths = {}
        self.script = ['Hanzi']
        self.settings = {
            'designFrame': {'em_Dimension':[1000, 1000],
                            'characterFace': 90,
                            'overshoot': [20, 20],
                            'horizontalLine': 15,
                            'verticalLine': 15,
                            'customsFrames': []
                            },
            'referenceViewer': []
        }
        self.deepComponentsLayers = {}
        self.deepComponentsInstances = {}
        self.mastersFontsGlyphDCComposition = {}
        
    def _initWithDict(self, d):
        for k, v in d.items():
            if hasattr(self, k):
                setattr(self, k, v)

    @property
    def _toDict(self):
        return {e: getattr(self, e) for e in dir(self) if not e.startswith('_')}


def testProject(name, admin):
    project = RoboCJKProject(name, admin)
    print(project._toDict)

if __name__ == "__main__":
    testProject('projectName', 'admin')

