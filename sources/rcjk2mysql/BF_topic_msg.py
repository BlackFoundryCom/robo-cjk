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
import BF_author

_COMPAGNY = "B[F]"
_TSEP = "/"
_APP = "RCJK"
_CHAT = "CHAT"
_CHAT_ALL = "#"
_TOPIC_BASE = f"{_COMPAGNY}{_TSEP}{_APP}{_TSEP}"
_TOPIC_MYSQL = f"{_TOPIC_BASE}MYSQL" 
_TOPIC_APPLICATION =  _TOPIC_BASE + "MESSAGE"

TOPIC_MYSQL_ALL = _TOPIC_MYSQL + _TSEP + "TRACE"
TOPIC_APPLICATION_TODO = _TOPIC_APPLICATION + _TSEP + "TODO"
TOPIC_APPLICATION_LISTEN = _TOPIC_APPLICATION + _TSEP + "LISTEN"
TOPIC_CHAT =  f"{_COMPAGNY}{_TSEP}{_CHAT}{_TSEP}{_CHAT_ALL}"
