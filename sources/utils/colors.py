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

INPROGRESS = (1., 0., 0., 1.)
CHECKING1 = (1., .5, 0., 1.)
CHECKING2 = (1., 1., 0., 1.)
CHECKING3 = (0., .5, 1., 1.)
DONE = (0., 1., .5, 1.)

TODO_name = 'todo'
WIP_name = 'wip'
CHECKING1_name = 'checking-1'
CHECKING2_name = 'checking-2'
CHECKING3_name = 'checking-3'
DONE_name = 'done'

STATUS_COLORS = {
	TODO_name: INPROGRESS, 
	WIP_name: INPROGRESS, 
	CHECKING1_name: CHECKING1,
	CHECKING2_name: CHECKING2,
	CHECKING3_name: CHECKING3,
	DONE_name: DONE,
	}