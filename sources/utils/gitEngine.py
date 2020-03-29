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
        self.commit('add .gitignore')
        self.push()

    def runCommand(self, command):
        # check=True will raise exception of the process does not terminates properly
        cp = subprocess.run(command, cwd=self._path, check=subprocessThrowException)
        if cp.returncode == 0: return True
        print("GIT ERROR", command, "retcode =", cp.returncode, self._path)
        return False

    def getHeadSHA(self):
        cp = subprocess.run(['git','rev-parse','HEAD'], stdout=subprocess.PIPE, cwd=self._path)
        if cp.returncode != 0:
            print("SHA-SHIT")
            return None
        sha = cp.stdout.decode('utf-8')[:-1]
        return sha

    def commit(self, stamp):
        if not self._ok: return False
        self.runCommand(['git', 'add', '.']) # Purposefully ignore returned boolean
        return self.runCommand(['git', 'commit', '-am', str(stamp)])

    def push(self):
        if not self._ok: return
        return self.runCommand(['git', 'push'])

    def commitPushOrFail(self, stamp):
        curCommit = self.getHeadSHA()
        self.commit(stamp)
        nextCommit = self.getHeadSHA()
        if curCommit == nextCommit: return True # there was nothing to push
        if self.push(): return True
        self.runCommand(['git', 'reset', '--hard', curCommit])
        return False

    def pull(self):
        if not self._ok: return False
        return self.runCommand(['git', 'pull'])

    def user(self):
        u = codecs.decode(
                subprocess.check_output(['git', 'config', 'user.name'], cwd=self._path),
                'utf-8')
        return u[:-1].replace(' ','_')
