from imp import reload
import hangulModule
reload(hangulModule)

hangulModule = hangulModule.HangulModule()
hangulModule.launchDataControllerInterface()