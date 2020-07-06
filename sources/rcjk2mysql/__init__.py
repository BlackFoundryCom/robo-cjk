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
sys.path.append(os.path.join(os.getcwd(), "rcjk2mysql"))

import BF_007d
import BF_007e
import BF_author
import BF_engine_msg
import BF_engine_mysql
import BF_factory_rcjk
import BF_fontbook_struct
import BF_init
import BF_mysql2rcjk
import BF_rcjk2mysql
import BF_struct2mysql
import BF_tools
import BF_topic_msg