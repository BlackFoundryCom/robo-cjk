"""
Copyright 2020 Black Foundry.

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
from mojo.UI import CodeEditor
import sys
from io import StringIO
import contextlib
from utils import files

@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

class ScriptingWindow:

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.w = Window((400, 600), "Scripting window", minSize = (200, 200))

        self.w.run = Button(
            (0, 0, -0, 20), 
            'run', 
            callback = self.runCallback
            )
       	self.w.run.bind("r", ["command"])

        self.editorGroup = Group((0, 0, -0, -0))
        self.outputGroup = Group((0, 0, -0, -0))
        paneDescriptors = [
            dict(view=self.editorGroup, identifier="Editor"),
            dict(view=self.outputGroup, identifier="Output"),
        ]
        self.w.splitView = SplitView(
            (0, 0, -0, -0), 
            paneDescriptors, 
            isVertical = False
            )

        self.editorGroup.codeEditor = CodeEditor(
            (0, 20, -0, -0),
            showLineNumbers = True
            )

        self.outputGroup.output = TextEditor(
            (0, 0, -0, -0), 
            readOnly = True
            )        
        
        self.w.open()
        
    def runCallback(self, sender):

        from utils import decorators, files, locker
        from models import atomicElement, deepComponent, characterGlyph
        
        def CurrentRCJKFont():
            return self.RCJKI.currentFont

        def CurrentRCJKGlyph():
            return self.RCJKI.currentGlyph

        def getRCJKI():
            return self.RCJKI

        RCJKI = self.RCJKI
        makepath = files.makepath

        with stdoutIO() as s:
            exec(self.editorGroup.codeEditor.get())
        self.outputGroup.output.set(s.getvalue())

