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
import subprocess
print(sys.path)
try:
	paho = subprocess.run(['pip3','install','paho-mqtt'])
	pymysql = subprocess.run(['pip3','install','pymysql'])
except:
	paho = subprocess.run(['pip','install','paho-mqtt'])
	pymysql = subprocess.run(['pip','install','pymysql'])

# APPNAME = "RoboFont"
# import sys
# from os import path, environ
# if sys.platform == 'darwin':
#     from AppKit import NSSearchPathForDirectoriesInDomains
#     appdata = path.join(NSSearchPathForDirectoriesInDomains(14, 1, True)[0], APPNAME)
# elif sys.platform == 'win32':
#     appdata = path.join(environ['APPDATA'], APPNAME)
# else:
#     appdata = path.expanduser(path.join("~", "." + APPNAME))
    
# packageDirectory = path.join(appdata, "Python3.7")
# subprocess.run(['git', 'clone', "https://github.com/eclipse/paho.mqtt.python.git", "paho-mqtt"], cwd=packageDirectory)
# subprocess.run(['git', 'clone', "https://github.com/PyMySQL/PyMySQL.git", "pymysql"], cwd=packageDirectory)

# try:
# 	paho = subprocess.run(['pip3','install','setup.py'], cwd = path.join(packageDirectory, "paho-mqtt"))
# 	pymysql = subprocess.run(['pip3','install','setup.py'], cwd = path.join(packageDirectory, "pymysql"))
# except:
# 	paho = subprocess.run(['pip','install','setup.py'], cwd = path.join(packageDirectory, "paho-mqtt"))
# 	pymysql = subprocess.run(['pip','install','setup.py'], cwd = path.join(packageDirectory, "pymysql"))
	
from controllers import roboCJK
sys.path.append(os.path.join(os.getcwd(), "rcjk2mysql"))

RCJKI = roboCJK.RoboCJKController()
RCJKI._launchInterface()

