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
import os, subprocess
from pathlib import Path
from vanilla.dialogs import message
from AppKit import NSColor, NSFont, NSAppearance
from mojo.UI import CurrentGlyphWindow
from vanilla import TextBox
from mojo.roboFont import *

def normalizeUnicode(code):
    if len(code) < 4:
        return '0'*(4-len(code)) + code
    else:
        return code

def setDarkMode(w, darkMode):
    if darkMode:
        appearance = NSAppearance.appearanceNamed_('NSAppearanceNameVibrantDark')
        if hasattr(w, "accordionView"):
            w.accordionView.setBackgroundColor(NSColor.colorWithCalibratedRed_green_blue_alpha_(.08, .08, .08, 1))
    else:
        appearance = NSAppearance.appearanceNamed_('NSAppearanceNameAqua')
        if hasattr(w, "accordionView"):
            w.accordionView.setBackgroundColor(NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 1, 1))
    w.getNSWindow().setAppearance_(appearance)
    if CurrentGlyphWindow():
        CurrentGlyphWindow().window().getNSWindow().setAppearance_(appearance)

def makepath(filepath):
    # Create path if it do not exist
    tails = []
    head, tail = os.path.split(os.path.split(filepath)[0])
    path = Path(head)
    while not path.is_dir():
        tails.append(tail)
        head, tail = os.path.split(head)
        path = Path(head)
    tails.append(tail)
    tails.reverse()
    for tail in tails:
        if not Path(os.path.join(head, tail)).is_dir():
            os.mkdir(os.path.join(head, tail))
            head = os.path.join(head, tail)

def reformatNSDictionaryM(listDict):
	return [{str(k):v for k, v in e.items()} for e in listDict]

def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]

def readCurrentProject(self, project):
    # Project 
    self.projectPath = project["Project"]["Path"]
    self.projectName = project["Project"]["Name"]

    # Characters Sets
    self.selectedCharactersSets = project["CharactersSets"]

    # Masters
    self.mastersPaths = project["MastersPaths"]
    self.fontDict = {path.split("/")[-1][:-4]:path for path in self.mastersPaths}
    self.fontList = [name for name in sorted(self.fontDict.keys())]
    self.fonts = {name:OpenFont(self.projectPath + path, showUI = False) for name, path in self.fontDict.items()}
    self.masterslist = [{"FamilyName": name.split("-")[0], "StyleName": name.split("-")[1]} for name in self.fontList]

    # Design Frame
    designFrame = project["DesignFrame"]
    self.EM_Dimension_X = designFrame["EM_Dimension"][0]
    self.EM_Dimension_Y = designFrame["EM_Dimension"][1] 
    self.characterFace = designFrame["CharacterFace"]
    self.overshootOutsideValue = designFrame["Overshoot"]["Outside"]
    self.overshootInsideValue = designFrame["Overshoot"]["Inside"]
    self.horizontalLine = designFrame["HorizontalLine"]
    self.verticalLine = designFrame["VerticalLine"]
    self.customsFrames = designFrame["CustomsFrames"]

    # Reference Viewer
    self.referenceViewerSettings = project["ReferenceViewer"]
    self.referenceViewerList = [{"Font": f["font"]} for f in self.referenceViewerSettings]

    # Calendar
    self.calendar = project["Calendar"]

    #Glyph composition Data
    self.glyphCompositionData = project["glyphCompositionData"]

class GitHelper():

    def __init__(self, path):
        self._path = path
        self.isInGitRepository()

    def isInGitRepository(self):
        # Check if the folder is a git repository
        if not os.path.exists(os.path.join(self._path, ".git")):
            message('Warning: this is not a GIT repository')
            return False
        return True

    def commit(self, stamp):
        if not self.isInGitRepository(): return False
        comment =  str(stamp)
        subprocess.call(['git', 'add', '.', self._path], cwd=self._path)
        subprocess.call(['git', 'commit', '-am', comment], cwd=self._path)
        return True
        
    def push(self):
        subprocess.call(['git', 'push'], cwd=self._path)

    def pull(self):
        if not self.isInGitRepository(): return False
        subprocess.call(['git', 'pull'], cwd=self._path)
        return True

    def user(self):
        # return the user name
        return subprocess.check_output(['git', 'config', 'user.name'], cwd=self._path)

class SmartTextBox(TextBox):
    
    def __init__(self, posSize, text="", alignment="natural", selectable=False, callback=None, sizeStyle=12.0,red=0,green=0,blue=0, alpha=1.0):
        self.color = NSColor.colorWithCalibratedRed_green_blue_alpha_(red, green, blue, alpha)

        super().__init__(posSize, text=text, alignment=alignment, selectable=selectable, sizeStyle=sizeStyle)

    def _setSizeStyle(self, sizeStyle):
        value = sizeStyle
        self._nsObject.cell().setControlSize_(value)
        font = NSFont.systemFontOfSize_(value)
        self._nsObject.setFont_(font)
        self._nsObject.setTextColor_(self.color)