from imp import reload
from controllers import roboCJK
reload(roboCJK)

RCJKI = roboCJK.RoboCJKController()
RCJKI._launchInterface()

