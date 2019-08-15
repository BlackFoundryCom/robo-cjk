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

cwd = os.getcwd()
rdir = os.path.abspath(cwd)

class roboCJK_Icon:
    _roboCJK = None

    @classmethod
    def get(cls):
        if cls._roboCJK is None:
            RoboCJKIconPath = os.path.join(rdir, 'resources/RoboCJKIcon.xml')
            with open(RoboCJKIconPath, "r") as file:
                cls._roboCJK = file.read()
        return cls._roboCJK