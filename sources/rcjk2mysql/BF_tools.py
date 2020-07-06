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
import sys
import os
import datetime
import shutil
import json
import pickle
import logging
from rcjk2mysql import BF_author
from rcjk2mysql import BF_fontbook_struct as bfs

logger = logging.getLogger(__name__)

# filtering items for save, write insert in mysql
ALL = [bfs.CGLYPH, bfs.DCOMPONENT, bfs.AELEMENT, bfs.LAYER]

def _update_filtering(filtering: list):
	"""
	"""
	if bfs.DCOMPONENT in filtering:
		if bfs.CGLYPH in filtering and bfs.CGLYPH_2_DCOMPONENT not in filtering:
			filtering.append(bfs.CGLYPH_2_DCOMPONENT)
		if bfs.AELEMENT in filtering and bfs.DCOMPONENT_2_AELEMENT not in filtering:
			filtering.append(bfs.DCOMPONENT_2_AELEMENT)



# PICKLE tools
# ------------------
def read_tag_pickle(tag, path, name_pickle):
    """
    """
    name = os.path.join(path, name_pickle)
    if os.path.isfile(name):
        try:
            with open(name, 'rb') as fp:
                tag = pickle.load(fp)

        except Exception as e:
            logger.error(str(e))
        
    return tag 

def write_tag_pickle(tag, path, name_pickle=None):
    """
    """
    if name_pickle is None:
        name_pickle = type(tag).__name__ +'.pickle'
    name = os.path.join(path, name_pickle)
    try:
        # print(f"size of pickle is {sys.getsizeof(tag)}")
        with open(name, 'wb') as fp:
            pickle.dump(tag, fp)

    except Exception as e:
        print(f"Error writing pickle {str(e)}")    
    
    return name 

# datetime and string
# ------------------
def get_datetime_string_now():
    """
    """
    return get_datetime_string(datetime.datetime.now())

def get_datetime_string(val):
    """
    """
    return val.strftime("%Y%m%d-%H%M%S")
    

# Folder functions
# ------------------
def clearout_folder(logger, path_folder):
    """
    """
    # erase path_temp
    if os.path.exists(path_folder):
    	shutil.rmtree(path_folder)

    # create it again
    check_folder_or_create_it(logger, path_folder)

def check_folder_or_create_it(log, folder):
    """
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
        log.info("create %s", folder)


# JSON tools 
# ------------------
def read_tag_json(tag,  path, name_json):
    """
    """
    name = os.path.join(path, name_json)
    if os.path.isfile(name):
        try:
            with open(name, 'r') as fp:
                # data = fp.read()
                tag = json.load(fp)

        except Exception as e:
            logger.error(str(e))
        
    return tag 
    
def write_tag_json(tag, path, name_json=None, indendation=4):
    """
    """
    if name_json is None:
        name_json = type(tag).__name__ + '.json'
    name = os.path.join(path, name_json)
    try:
        with open(name, 'w') as fp:
            json.dump(tag, fp, indent=indendation, sort_keys=True)

    except:
        pass
    
    return name 

illegalCharacters = "\" * + / : < > ? [ \ ] | \0".split(" ")
illegalCharacters += [chr(i) for i in range(1, 32)]
illegalCharacters += [chr(0x7F)]
reservedFileNames = "CON PRN AUX CLOCK$ NUL A:-Z: COM1".lower().split(" ")
reservedFileNames += "LPT1 LPT2 LPT3 COM2 COM3 COM4".lower().split(" ")
maxFileNameLength = 255    

def userNameToFileName(userName, existing=[], prefix="", suffix=""):    
    """
    format filename of glyph
    """    
    prefixLength = len(prefix)
    suffixLength = len(suffix)    
    if not prefix and userName[0] == ".":
        userName = "_" + userName[1:]
    filteredUserName = []
    for character in userName:
        if character in illegalCharacters:
            character = "_"
        elif character != character.lower():
            character += "_"
        filteredUserName.append(character)
    userName = "".join(filteredUserName)
    sliceLength = maxFileNameLength - prefixLength - suffixLength
    userName = userName[:sliceLength]
    parts = []
    for part in userName.split("."):
        if part.lower() in reservedFileNames:
            part = "_" + part
        parts.append(part)
    userName = ".".join(parts)
    fullName = prefix + userName + suffix
    if fullName.lower() in existing:
        fullName = handleClash1(userName, existing, prefix, suffix)

    return fullName

def main():
	"""
	"""
	pass
	
if __name__ == "__main__":
	main()