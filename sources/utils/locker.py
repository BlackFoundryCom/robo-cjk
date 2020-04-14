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
import os, subprocess

class LockInfo():
    def __init__(self, l=0, u=None, r=0):
        self.lock = l # 1: locked, 0: unlocked
        self.user = u
        self.refcount = r # reference count

class Locker():
    def __init__(self, path, gitUserName, gitPassword, gitHostLocker, gitHostLockerPassword, privateLocker):
        self._path = os.path.join(path, 'locker__')
        if not os.path.exists(self._path):
            githubHostLocker = gitHostLocker
            githubHostLockerPassword = gitHostLockerPassword
            githubUsername = gitUserName
            githubPassword = gitPassword
            repoName = 'locker_'+os.path.split(path)[1].split('.')[0]
            cp = subprocess.run(['git', 'clone', "https://"+githubUsername+":"+githubPassword+"@github.com/"+githubHostLocker+"/"+repoName+".git", "locker__"], cwd=path)
            if cp.returncode != 0 and githubHostLockerPassword != '':
                cp = subprocess.run(['curl', '-u', githubHostLocker+":"+githubHostLockerPassword, "https://api.github.com/user/repos", "-d", "{\"name\":\""+repoName+"\", \"private\": true}"])
                print(cp.returncode)
                cp = subprocess.run(['git', 'clone', "https://"+githubHostLocker+":"+githubHostLockerPassword+"@github.com/"+githubHostLocker+"/"+repoName+".git", "locker__"], cwd=path)
                print(cp.returncode)

                with open(os.path.join(self._path, "README.txt"), 'w') as f:
                    f.write("This is a git repo for locking elements from "+path+"\n")
                subprocess.run(['git', 'add', 'README.txt'], cwd=self._path)
                subprocess.run(['git', 'commit', '-m', 'init'], cwd=self._path)
                subprocess.run(['git', 'push'], cwd=self._path)
            
        self._git = gitEngine.GitEngine(self._path)
        self._username = self._git.user()
        print("Locker inited for {} at {}".format(self._username, self._path))
        self.update()

    def update(self):
        if not self._git._ok: return
        try:
            self._git.pull()
        except:
            pass
        print("Locker update")

    def UNSAFEgetLockInfo(self, filepath):
        if not os.path.exists(filepath):
            #print("Locker getLockInfo DEFAULT")
            return LockInfo()
        with open(filepath,'r', encoding='utf-8') as f: line = f.readline()
        if not line: 
            lock = 0 
            user = self._username
            refcount = 0
        else:
            if line[-1] == '\n': line = line[:-1]
            lock, user, refcount = line.split()
        #print("Locker getLockInfo", lock, user, refcount)
        return LockInfo(int(lock), user, int(refcount))

    def getLockInfo(self, filepath):
        self.update()
        return self.UNSAFEgetLockInfo(filepath)

    def UNSAFEsetLockInfo(self, filepath, li, g = None):
        """Write to file but does not commit"""
        #print("Locker UNSAFEsetLockInfo", li.lock, li.user, li.refcount)
        with open(filepath,'w', encoding='utf-8') as f:
            f.write("{} {} {}".format(li.lock, li.user, li.refcount))

    def setLockInfo(self, filepath, li, g, message):
        """Write to file and commit, or revert"""
        #print("Locker setLockInfo", li.lock, li.user, li.refcount)
        self.UNSAFEsetLockInfo(filepath, li, g)
        return self._git.commitPushOrFail(message + ' ' + g.name)

    def potentiallyOutdatedLockingUser(self, g):
        """Returns the user having the lock on 'g', or None"""
        filepath = os.path.join(self._path, files.userNameToFileName(g.name))
        li = self.UNSAFEgetLockInfo(filepath)
        if li.lock == 0:
            return None
        return li.user

    def userHasLock(self, glyph):
        filepath = os.path.join(self._path, files.userNameToFileName(glyph.name))
        # UNSAFE is OK because if we have the lock, then the file cannot (in
        # theory!) be changed by someone else
        li = self.UNSAFEgetLockInfo(filepath)
        return li.user == self._username

    @property           
    def myLockedGlyphs(self):
        for filepath in os.listdir(self._path):
            try:
                with open(os.path.join(self._path, filepath), 'r', encoding = 'utf-8') as file:
                    _, username, _ = file.read().split()
                    if username == self._username:
                        yield files.fileNameToUserName(filepath)
            except: continue

    def lock(self, g):
        """ First returned boolean indicate if lock was succesful.
            Second returned boolean indicate if user already had the lock."""
        filepath = os.path.join(self._path, files.userNameToFileName(g.name))
        li = self.getLockInfo(filepath)
        print("Locker LOCK", filepath)
        if li.lock:
            lockedByMe = li.user == self._username
            return (lockedByMe, lockedByMe) # return True if its already locked by local user
        li.lock = 1
        li.user = self._username
        # return True if remote repo succesfully updated
        return (self.setLockInfo(filepath, li, g, 'lock'), False)

    def unlock(self, g):
        filepath = os.path.join(self._path, files.userNameToFileName(g.name))
        li = self.getLockInfo(filepath)
        print("Locker UNLOCK", filepath)
        if not li.lock: return True # Already unlocked
        if li.user != self._username: return False # Locked by someone else
        li.lock = 0
        li.user = '__None__'
        return self.setLockInfo(filepath, li, g, 'unlock')

    def batchUnlock(self, glyphs):
        self.update()
        print("Locker BATCH UNLOCK")
        for g in glyphs:
            filepath = os.path.join(self._path, files.userNameToFileName(g.name))
            li = self.UNSAFEgetLockInfo(filepath)
            if not li.lock: continue
            if li.user != self._username: continue
            li.lock = 0
            li.user = '__None__'
            self.UNSAFEsetLockInfo(filepath, li, g)
        return self._git.commitPushOrFail("BATCH UNLOCK for {}".format(self._username))

    def batchLock(self, glyphs):
        self.update()
        print("Locker BATCH LOCK")
        for g in glyphs:
            filepath = os.path.join(self._path, files.userNameToFileName(g.name))
            li = self.UNSAFEgetLockInfo(filepath)
            if li.lock: continue
            if li.user == self._username: continue
            li.lock = 1
            li.user = self._username
            self.UNSAFEsetLockInfo(filepath, li, g)
        return self._git.commitPushOrFail("BATCH UNLOCK for {}".format(self._username))

    def changeLockName(self, oldName, newName):
        self.update()
        oldfilepath = os.path.join(self._path, files.userNameToFileName(oldName))
        newNamepath = os.path.join(self._path, files.userNameToFileName(newName))
        self.UNSAFEsetLockInfo(newNamepath, self.UNSAFEgetLockInfo(oldfilepath))
        os.remove(oldfilepath)
        return self._git.commitPushOrFail("CHANGE LOCK NAME {}".format(oldName, newName))

