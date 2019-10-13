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
from fontTools.ufoLib.pointPen import PointToSegmentPen
from mojo.roboFont import *
    
def checkCompatible(g1, g2):
    lenghtContour = lambda g: [len(c) for c in g]
    baseGlyph = lambda g: [c.baseGlyph for c in g.components]
    if lenghtContour(g1) != lenghtContour(g2):
        return False
    if baseGlyph(g1) != baseGlyph(g2):
        return False
    return True

def checkInterpolationResult(g, g1, g2, ratio_x, ratio_y, scale_x, scale_y):
    for c, c1, c2 in zip(g, g1, g2):
        
        boxx = (c.box[0] + ((c.box[2] - c.box[0])))
        boxy = (c.box[1] + ((c.box[3] - c.box[1])))

        box1x = ((c1.box[0] + ((c1.box[2] - c1.box[0]))))
        box1y = ((c1.box[1] + ((c1.box[3] - c1.box[1]))))

        box2x = ((c2.box[0] + ((c2.box[2] - c2.box[0]))))
        box2y = ((c2.box[1] + ((c2.box[3] - c2.box[1]))))

        middlex = (box1x + (box2x - box1x) * ratio_x) * scale_x
        middley = (box1y + (box2y - box1y) * ratio_y) * scale_y

        if not middlex - 1 < boxx < middlex + 1 or not middley - 1 < boxy < middley + 1:
            return "contourFailed", 0
        return True

def interpol_glyph_glyph_ratioX_ratioY_scaleX_scaleY_toFont_glyphName(g1, g2, ratio_x, ratio_y, scale_x, scale_y, f, glyphName):
    if glyphName not in f.keys():
        g = f.newGlyph(glyphName)
    else:
        return f[glyphName]

    if not checkCompatible(g1, g2):
        return False, None

    pen = PointToSegmentPen(g.getPen())
    for c1, c2 in zip(g1.contours, g2.contours):

        pen.beginPath()
        for p1, p2 in zip(c1.points, c2.points):

            if not p1.type == p2.type:
                return "glyphFailed", 0

            px = (p1.x + ((p2.x - p1.x) * ratio_x)) * scale_x
            py = (p1.y + ((p2.y - p1.y) * ratio_y)) * scale_y
            ptype = p1.type if p1.type != 'offcurve' else None
            pen.addPoint((px, py), ptype)

        pen.endPath()

    g.unicode = g1.unicode
    g.width = (g1.width + ((g2.width - g1.width) * ratio_x)) * scale_x
    # g.round()

    for c1, c2 in zip(g1.components, g2.components):
        name = c1.baseGlyph
        interpol_glyph_glyph_ratioX_ratioY_scaleX_scaleY_toFont_glyphName(g1.getParent()[name], g2.getParent()[name], ratio_x, ratio_y, scale_x, scale_y, f, name)

        cOffsetX = (c1.offset[0] + ((c2.offset[0] - c1.offset[0]) * ratio_x)) * scale_x
        cOffsetY = (c1.offset[1] + ((c2.offset[1] - c1.offset[1]) * ratio_y)) * scale_y

        g.appendComponent(name, offset=(cOffsetX, cOffsetY))
    
    return True, g

def deepCompatible(masterGlyph, layersNames):
    for layerName in layersNames:
        glyph = masterGlyph.getLayer(layerName)
        if len(glyph) != len(masterGlyph):
            return False
        for c1, c2 in zip(glyph, masterGlyph):
            if len(c1) != len(c2):
                return False
    return True
    
def deepolation(newGlyph, masterGlyph, layersInfo = {}):
    
    if not deepCompatible(masterGlyph, list(layersInfo.keys())):
        return False
    
    pen = PointToSegmentPen(newGlyph.getPen())
    
    for contourIndex, contour in enumerate(masterGlyph):
        
        pen.beginPath()
        
        for pointIndex, point in enumerate(contour.points):
            
            px, py = point.x, point.y
            ptype = point.type if point.type != 'offcurve' else None
            
            points = [(px, py)]
            for layerName, value in layersInfo.items():
                
                ratio = value / 1000 * (len(layersInfo) + 1)
                layerGlyph = masterGlyph.getLayer(layerName)
                
                pI = layerGlyph[contourIndex].points[pointIndex]
                pxI, pyI = pI.x, pI.y
                
                newPx = px + (pxI - px) * ratio
                newPy = py + (pyI - py) * ratio
                
                points.append((newPx, newPy))
                
            newX = int(sum(p[0] for p in points) / len(points))
            newY = int(sum(p[1] for p in points) / len(points))
            pen.addPoint((newX, newY), ptype)
            
        pen.endPath()
        
    return newGlyph

def normalizeUnicode(code):
    if len(code) < 4:
        return '0'*(4-len(code)) + code
    else:
        return code

def setDarkMode(w, darkMode):
    if not w: return
    if darkMode:
        appearance = NSAppearance.appearanceNamed_('NSAppearanceNameVibrantDark')
        if hasattr(w, "accordionView"):
            w.accordionView.setBackgroundColor(NSColor.colorWithCalibratedRed_green_blue_alpha_(.08, .08, .08, 1))
    else:
        appearance = NSAppearance.appearanceNamed_('NSAppearanceNameAqua')
        if hasattr(w, "accordionView"):
            w.accordionView.setBackgroundColor(NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 1, 1))
    if hasattr(w, 'w'):
        w.w.getNSWindow().setAppearance_(appearance)
    else:
        w.getNSWindow().setAppearance_(appearance)
    # if CurrentGlyphWindow():
    #     CurrentGlyphWindow().window().getNSWindow().setAppearance_(appearance)

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
    self.mastersPaths = list(project["UFOsPaths"].keys())
    self.storagePaths = list(project["UFOsPaths"].values())
    # self.fontDict = {path.split("/")[-1][:-4]:path for path in self.mastersPaths}
    self.fonts = {}
    self.fontList = []
    self.storageFonts = {}
    self.storageFontsList = []
    self.font2Storage = {}

    tempFolder = os.path.join(self.projectPath, "Temp")
    tempContents = os.listdir(tempFolder)
    if not tempContents:
        for fontPath, storagePath in project["UFOsPaths"].items():

            fontName = fontPath.split("/")[-1][:-4]
            storageFontName = storagePath.split("/")[-1][:-4]

            try:
                font = OpenFont(self.projectPath + fontPath, showUI = False)
                storageFont = OpenFont(self.projectPath + storagePath, showUI = False)
                self.font2Storage[font] = storageFont
                self.fonts[fontName] = font
                self.storageFonts[storageFontName] = storageFont
            except:pass 

            self.fontList.append(fontName)
            self.storageFontsList.append(storageFontName)
            self.collapse = 0
    else:
        UFOs = list(filter(lambda x: x.endswith('ufo'), os.listdir(self.projectPath + "/Temp")))

        tempsUFOs = list(filter(lambda x: x.startswith('temp'), UFOs))
        storageTempsUFOs = list(filter(lambda x: x.startswith('storageTemp'), UFOs))

        """
        ['temp-2019725_GaëtanBaehr-Regular.ufo', 'temp-2019725_GaëtanBaehr-Bold.ufo', 'storageTemp-2019725_GaëtanBaehr-Bold.ufo', 'storageTemp-2019725_GaëtanBaehr-Regular.ufo']
        """
        for fontPath in tempsUFOs:
            fontName = fontPath[:-4]
            for storagePath in storageTempsUFOs:
                if storagePath.endswith(fontPath.split('-')[-1]):
                    storageFontName = storagePath[:-4]

            try:
                font = OpenFont(self.projectPath + "/Temp/" + fontPath, showUI = False)
                storageFont = OpenFont(self.projectPath + "/Temp/"+ storageFontName+".ufo", showUI = False)
                self.font2Storage[font] = storageFont
                self.fonts[fontName] = font
                self.storageFonts[storageFontName] = storageFont
                self.storageFontsList.append(storageFontName)
            except:pass 

            self.fontList.append(fontName)
            self.collapse = 1

    self.glyphsSetDict = {font: [dict(Name = name, Char = chr(int(name[3:],16)) if name.startswith('uni') else "") for name in font.lib['public.glyphOrder']] for font in self.fonts.values()}

    # print(self.glyphsSetDict)

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
    #Deep Component Extrems Data
    self.deepComponentExtremsData = project["deepComponentExtremsData"]
    #Deep Component Extrems Data
    self.designStep = project["designStep"]

    key2Glyph = {}
    for glyphName, keys in self.glyphCompositionData.items():
        for key in keys:
            elem = key.split('_')
            k = elem[0]
            pos = elem[2]
            if k not in key2Glyph:
                key2Glyph[k] = {}
            if pos not in key2Glyph[k]:
                key2Glyph[k][pos] = []
            key2Glyph[k][pos].append("uni" + glyphName)
    self.key2Glyph = {}
    for k, v in key2Glyph.items():
        if k not in self.key2Glyph:
            self.key2Glyph[k] = []
        for pos, elem in v.items():
            self.key2Glyph[k].extend(elem)

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