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
import sys, os

from controllers import roboCJK
from utils import hotReload

import sentry_sdk

sentry_sdk.init(
    "https://961a602da08346909a7eecb37d423d7c@o425940.ingest.sentry.io/5598166",
    traces_sample_rate=1.0
)
# sys.path.append(os.path.join(os.getcwd(), "rcjk2mysql"))

hotReload.rreload(roboCJK)
RCJKI = roboCJK.RoboCJKController()
RCJKI._launchInterface()

