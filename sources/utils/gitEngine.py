import os
import codecs
import subprocess

class GitEngine():

    def __init__(self, path):
        self._path = path

    def isInGitRepository(self):
        if not os.path.exists(os.path.join(self._path, ".git")):
            return False
        return True

    def createGitignore(self):
        if os.path.isfile(os.path.join(self._path, '.gitignore')): return
        f = open(os.path.join(self._path, '.gitignore'), 'w')
        gitignore = '*.ufo'
        f.write(gitignore)
        self.commit('add gitignore')
        self.push()

    def commit(self, stamp):
        if not self.isInGitRepository(): return False
        comment =  str(stamp)
        subprocess.call(['git', 'add', '.', self._path], cwd=self._path)
        subprocess.call(['git', 'commit', '-am', comment], cwd=self._path)
        return True
        
    def push(self):
        subprocess.call(['git', 'push'], cwd=self._path)

    def pull(self):
        if not self.isInGitRepository(): return False
        subprocess.call(['git', 'pull'], cwd=self._path)
        return True

    def user(self):
        return codecs.decode(subprocess.check_output(
                ['git', 'config', 'user.name'], 
                cwd=self._path), 'utf-8')