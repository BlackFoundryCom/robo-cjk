from pathlib import Path
import os
import string

def makepath(filepath):
    # Create path if it does not exist
    tails = []
    head, tail = os.path.split(os.path.split(filepath)[0])
    path = Path(head)
    while not path.is_dir():
        tails.append(tail)
        head, tail = os.path.split(head)
        path = Path(head)
    tails.append(tail)
    tails.reverse()
    for tail in tails:
        if not Path(os.path.join(head, tail)).is_dir():
            os.mkdir(os.path.join(head, tail))
            head = os.path.join(head, tail)

def normalizeUnicode(code):
    return normalizeCode(code, 4)

def normalizeCode(s, dec):
    if len(s) < dec:
        return '0'*(dec-len((s))) + s
    else:
        return s

def unicodeName(char):
    return "uni" + normalizeUnicode(hex(ord(char))[2:].upper())

def _getFilteredListFromName(fullList: list, name: str) -> list:
    return [e for e in fullList if name in e]

ALPHABET = string.ascii_uppercase
N = len(ALPHABET)
ALPHABET_INDEX = {d: i for i, d in enumerate(ALPHABET, 1)}

def int_to_column_id(num):
    if num < 0:
        raise ValueError("Input should be a non-negative integer.")
    elif num == 0:
        return ""
    else:
        q, r = divmod(num - 1, N)
        return int_to_column_id(q) + ALPHABET[r]
      
def userNameToFileName(userName, existing=[], prefix="", suffix=""):
	
    illegalCharacters = "\" * + / : < > ? [ \ ] | \0".split(" ")
    illegalCharacters += [chr(i) for i in range(1, 32)]
    illegalCharacters += [chr(0x7F)]
    reservedFileNames = "CON PRN AUX CLOCK$ NUL A:-Z: COM1".lower().split(" ")
    reservedFileNames += "LPT1 LPT2 LPT3 COM2 COM3 COM4".lower().split(" ")
    maxFileNameLength = 255

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