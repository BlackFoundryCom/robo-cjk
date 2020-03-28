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
import os
import codecs
import subprocess

subprocessThrowException = False

class GitEngine():

    def __init__(self, path):
        self._path = path
        self._ok = self.isInGitRepository()

    def isInGitRepository(self):
        return os.path.exists(os.path.join(self._path, ".git"))

    def createGitignore(self):
        if os.path.isfile(os.path.join(self._path, '.gitignore')): return
        f = open(os.path.join(self._path, '.gitignore'), 'w')
        gitignore = '''*.ufo
        */locker__
        '''
        f.write(gitignore)
        f.close()
        self.commit('add gitignore')
        self.push()

    def commit(self, stamp):
        if not self._ok: return False
        comment =  str(stamp)
        #subprocess.call(['git', 'add', '.', self._path], cwd=self._path)
        # check=True will raise exception of the process does not terminates properly
        cp = subprocess.run(['git', 'add', '.'], cwd=self._path, check=subprocessThrowException) # In case there are new files?
        if cp.returncode != 0: return False
        cp = subprocess.run(['git', 'commit', '-am', comment], cwd=self._path, check=subprocessThrowException)
        if cp.returncode != 0: return False
        return True

    def push(self):
        if not self._ok: return
        cp = subprocess.run(['git', 'push'], cwd=self._path, check=subprocessThrowException)
        return cp.returncode == 0

    def pull(self):
        if not self._ok: return False
        cp = subprocess.run(['git', 'pull'], cwd=self._path, check=subprocessThrowException)
        return cp.returncode == 0

    def user(self):
        u = codecs.decode(subprocess.check_output(
                ['git', 'config', 'user.name'],
                cwd=self._path), 'utf-8')
        return u[:-1].replace(' ','_')
