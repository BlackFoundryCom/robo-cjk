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
from mojo.UI import PostBannerNotification, UpdateCurrentGlyphView
from mojo.roboFont import *
import copy
from imp import reload
from controllers import roboCJK
# reload(roboCJK)

def gitCoverage(msg='save'):

    def foo(func):
        def wrapper(self, *args, **kwargs):
            if not self.mysql:
                try:
                    gitEngine = roboCJK.gitEngine
                    if not gitEngine.isInGitRepository():
                        PostBannerNotification(
                            'Impossible', "Project is not is GIT repository"
                            )
                        return
                    gitEngine.createGitignore()
                    gitEngine.pull()
                    func(self, *args, **kwargs)
                    gitEngine.commit(msg)   
                    gitEngine.push()
                    PostBannerNotification(
                        'font did save', ""
                            ) 

                except Exception as e:
                    raise e
            else:

                func(self, *args, **kwargs)
        return wrapper 
    return foo

def lockedProtect(func):
    def wrapper(self, *args, **kwargs):
        try:
            e = self
            if hasattr(self, 'RCJKI'):
                e = self.RCJKI
            if e.locked: return
            e.locked = True

            func(self, *args, **kwargs)

            e.locked = False
        except Exception as e:
            raise e
    return wrapper

deepComponentsKey = 'robocjk.characterGlyph.deepComponents'
glyphVariationsKey = 'robocjk.characterGlyph.glyphVariations'

def _getKeys(glyph):
    if glyph.type == "characterGlyph":
        return 'robocjk.deepComponents', 'robocjk.axes', 'robocjk.variationGlyphs'
    else:
        return 'robocjk.deepComponents', 'robocjk.axes', 'robocjk.variationGlyphs'

def glyphUndo(func):
    def wrapper(self, *args, **kwargs):
        try:
            modifiers, inputKey, character = args[0]
            if self.type in ["characterGlyph", "deepComponent"]:
                if not (modifiers[4] and character == 'z') and not (modifiers[0] and modifiers[4] and character == 'Z'):
                    lib = RLib()
                    deepComponentsKey, axesKey, glyphVariationsKey = _getKeys(self)
                    lib[deepComponentsKey] = copy.deepcopy(self._deepComponents.getList())
                    lib[axesKey] = copy.deepcopy(self._axes.getList(with_global_axes = True))
                    lib[glyphVariationsKey] = copy.deepcopy(self._glyphVariations.getList())
                    self.stackUndo_lib = self.stackUndo_lib[:self.indexStackUndo_lib]
                    self.stackUndo_lib.append(lib)
                    self.indexStackUndo_lib += 1

            func(self, *args, **kwargs)

        except Exception as e:
            raise e
    return wrapper

def glyphAddRemoveUndo(func):
    def wrapper(self, *args, **kwargs):
        try:
            if self.type in ["characterGlyph", "deepComponent"]:
                lib = RLib()
                deepComponentsKey, axesKey, glyphVariationsKey = _getKeys(self)
                lib[deepComponentsKey] = copy.deepcopy(self._deepComponents.getList())
                lib[axesKey] = copy.deepcopy(self._axes.getList(with_global_axes = True))
                lib[glyphVariationsKey] = copy.deepcopy(self._glyphVariations.getList())
                self.stackUndo_lib = self.stackUndo_lib[:self.indexStackUndo_lib]
                self.stackUndo_lib.append(lib)
                self.indexStackUndo_lib += 1

            func(self, *args, **kwargs)

        except Exception as e:
            raise e
    return wrapper

def glyphTransformUndo(func):
    def wrapper(self, *args, **kwargs):
        try:
            if self.RCJKI.currentGlyph.type in ["characterGlyph", "deepComponent"]:
                lib = RLib()
                deepComponentsKey, axesKey, glyphVariationsKey = _getKeys(self.RCJKI.currentGlyph)
                lib[deepComponentsKey] = copy.deepcopy(self.RCJKI.currentGlyph._deepComponents.getList())
                lib[axesKey] = copy.deepcopy(self.RCJKI.currentGlyph._axes.getList(with_global_axes = True))
                lib[glyphVariationsKey] = copy.deepcopy(self.RCJKI.currentGlyph._glyphVariations.getList())
                self.RCJKI.currentGlyph.stackUndo_lib = self.RCJKI.currentGlyph.stackUndo_lib[:self.RCJKI.currentGlyph.indexStackUndo_lib]
                self.RCJKI.currentGlyph.stackUndo_lib.append(lib)
                self.RCJKI.currentGlyph.indexStackUndo_lib += 1

            func(self, *args, **kwargs)

        except Exception as e:
            raise e
    return wrapper

def refresh(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        UpdateCurrentGlyphView()
        e = self
        if hasattr(self, 'RCJKI'):
            e = self.RCJKI
        if e.glyphInspectorWindow is not None:
            e.glyphInspectorWindow.updatePreview()
    return wrapper