from imp import reload
import Global
reload(Global)

from interface import RoboCJK

Global.CharactersSets.get()
Global.fontsList.get()
RoboCJK()