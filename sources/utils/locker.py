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
from utils import gitEngine, files
import os

class LockInfo():
    def __init__(self, l=0, u=None, r=0):
        self.lock = l # 1: locked, 0: unlocked
        self.user = u
        self.refcount = r # reference count

class Locker():
    def __init__(self, path):
        self._path = os.path.join(path, 'locker__')
        self._git = gitEngine.GitEngine(self._path)
        self._username = self._git.user()
        print("Locker inited for {} at {}".format(self._username, path))

    def update(self):
        if not self._git._ok: return
        try:
            self._git.pull()
        except:
            pass
        print("Locker update")

    def getLockInfo(self, filepath):
        self.update()
        if not os.path.exists(filepath): return LockInfo()
        with open(filepath,'r') as f: line = f.readline()
        if line[-1] == '\n': line = line[:-1]
        lock, user, refcount = line.split()
        print("Locker getLockInfo", lock, user, refcount)
        return LockInfo(int(lock), user, int(refcount))

    def setLockInfo(self, filepath, li):
        with open(filepath,'w') as f:
            f.write("{} {} {}".format(li.lock, li.user, li.refcount))
        try:
            self._git.commit()
            self._git.push()
        except:
            pass
        print("Locker setLockInfo", li.lock, li.user, li.refcount)

    def lock(self, g):
        filepath = os.path.join(self._path, files.userNameToFileName(g.name))
        li = self.getLockInfo(filepath)
        print("Locker LOCK", filepath)
        if li.lock: return li.user == self._username
        li.lock = 1
        li.user = self._username
        self.setLockInfo(filepath, li)
        return True

    def unlock(self, g):
        filepath = os.path.join(self._path, files.userNameToFileName(g.name))
        li = self.getLockInfo(filepath)
        print("Locker UNLOCK", filepath)
        if not li.lock: return True
        if li.user != self._username: return False
        li.lock = 0
        li.user = '__None__'
        self.setLockInfo(filepath, li)
        return True
