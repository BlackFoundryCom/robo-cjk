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

            except Exception as e:
                raise e
        return wrapper 
    return foo

def lockedProtect(func):
    def wrapper(self, *args, **kwargs):
        try:
            if self.RCJKI.locked: return
            self.RCJKI.locked = True

            func(self, *args, **kwargs)

            self.RCJKI.locked = False
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