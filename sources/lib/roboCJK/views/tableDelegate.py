"""
Copyright 2019 Black Foundry.

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
from AppKit import NSObject
from AppKit import NSCell, NSColor
import objc

class TableDelegate(NSObject):
    @objc.python_method
    def initWithMaster(self, master, designStep, glist):
        # ALWAYS call the super's designated initializer.  Also, make sure to
        # re-bind "self" just in case it returns something else, or even
        # None!
        self = super(TableDelegate, self).init()
        if self is None: return None

        self.master = master
        self.designStep = designStep
        self.glist = glist
        return self

    def tableView_dataCellForTableColumn_row_(self, tableView, tableColumn, row):
        return self.master.tableView_dataCellForTableColumn_row_(tableView, tableColumn, row, self.designStep, self.glist)