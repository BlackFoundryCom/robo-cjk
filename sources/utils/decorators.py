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

from imp import reload
from controllers import roboCJK
reload(roboCJK)

def gitCoverage(msg='save'):

    def foo(func):
        def wrapper(self, *args, **kwargs):
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

def glyphUndo(func):
    def wrapper(self, *args, **kwargs):
        try:
            
            self.RCJKI.currentGlyph.lib.prepareUndo(undoTitle='TestingUndo')
            self.RCJKI.currentGlyph.prepareUndo(undoTitle='TestingUndo')
            self.RCJKI.currentGlyph.update()
            func(self, *args, **kwargs)
            self.RCJKI.currentGlyph.lib.holdChanges()
            self.RCJKI.currentGlyph.update()
            self.RCJKI.currentGlyph.lib.performUndo()
            self.RCJKI.currentGlyph.performUndo()
        except Exception as e:
            raise e
    return wrapper

def refresh(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        UpdateCurrentGlyphView()
    return wrapper