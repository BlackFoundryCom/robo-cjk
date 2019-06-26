from vanilla import *
from imp import reload
import Helpers
reload(Helpers)

class Preferences():

    def __init__(self, interface):
        self.ui = interface
        self.w = Sheet((600,550), self.ui.w)
        self.w.close_button = Button((-100,-30,-10,-10),
                'close',
                callback = self._close_button_callback)


        Helpers.setDarkMode(self.w, self.ui.darkMode)
        self.w.open()

    def _close_button_callback(self, sender):
        self.w.close()