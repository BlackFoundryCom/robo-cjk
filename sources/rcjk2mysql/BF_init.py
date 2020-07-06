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

import logging
import logging.config
from configparser import ConfigParser
from typing import Tuple, Dict 

import urllib.request



from rcjk2mysql import BF_007d

_LOCAL=".local"
_REMOTE=".remote"
_MY_IP = "localhost"
CFG_ENTRY, DIRECTORY_READ, DIRECTORY_WRITE = range(3)
LOCAL = ("mysql"+_LOCAL, "ressources", "ressourcesd")
REMOTE = ("mysql"+_REMOTE, "ressources","ressourcesr")

def get_mycwd(fname: str=__file__) -> str:
    if sys.platform == 'Darwin':
        print("\t\t MACCCCCCC ")
        logfile_path = os.path.join(os.path.expanduser("~/Library"), "Application Support","RoboFont")
    else:
        print("\t\t PC or Linux ")
        logfile_path = os.path.join(os.path.dirname(fname), "logs")

    return os.path.join(logfile_path, os.path.splitext(os.path.basename(fname))[0]+".log")

STR_FMT = '%(asctime)s : %(levelname)s : %(message)s'
DATE_FMT = '%d/%m/%Y %H:%M:%S'
def init_log(path: str=None) -> logging.Logger:
    """ logging ...."""
    if not path:
        path =  os.path.dirname(__file__)
    
    print(f"path is {path}")
    filecfg = os.path.join(path, "Config", 'logging.cfg')
    print(f"filecfg is {filecfg}")
    error_msg = None
    try:
        if sys.platform.upper() == 'DARWIN':
            logging.config.fileConfig(os.path.join(path, "Config", 'logging_mac.cfg'))
        else:
            logging.config.fileConfig(os.path.join(path, "Config", 'logging.cfg'))
    except Exception as e:
        error_msg = f"{type(e)} - {str(e)}" 
        logging.basicConfig(datefmt=DATE_FMT,format=STR_FMT, level=logging.INFO)
    log = logging.getLogger()
    log.info(sys.version)
    if error_msg:
        log.info(error_msg)
    return log


def init_params(log: logging.Logger, path: str, 
                    mysql_entry: str=_LOCAL,
                    msg_entry: str=_LOCAL) -> Tuple[Dict, Dict]:
    """ params to mysql and mosquitto connexion"""
    if not path:
        path =  os.path.dirname(__file__)

    cf=ConfigParser(allow_no_value=True)
    cf.read(os.path.join(path, "Config", 'connectors.cfg'))
    mysql_dict = {}
    if mysql_entry:
        mysql = "mysql"+mysql_entry
        log.info(f"entry: {mysql}")
        for params in ("host", "db", "user", "password", "port"):
            if params == "port":
                mysql_dict[params] = int(cf.get(mysql, params))
            else:
                mysql_dict[params] = cf.get(mysql, params)
        log.info(f"Dict MySQL: {mysql_dict}")
    mos_dict = {}
    if msg_entry:
        msg = "mosquitto"+msg_entry
        log.info(f"entry: {msg}")
        for params in ("host", "port", "password", "username"):
            mos_dict[params] = cf.get(msg, params)
        log.info(f"Dict moquitto: {mos_dict}")

    ip = "external_ip"
    if cf.has_section(ip):
        website = cf.get(ip, "site")
        global _MY_IP
        _MY_IP = urllib.request.urlopen(website).read().decode('utf-8')

    return mysql_dict, mos_dict


def decode(x):
    return BF_007d.d(x.encode()).decode()


def init_import(log) -> bool:
    """ import from pip install """
    import pip
    for lib in ("ufoLib", "paho.mqtt", "pymysql"):
        try:
            log.info(f"import of '{lib}'")
            __import__(lib)
        except:
            inst = f"pip3 install {lib} --user"
            log.info(inst)
            log.info(f"Install in progress of '{lib}'")
            os.system(inst)
            __import__(lib)
            log.info("Install done")
        else:
            log.info("Import already done")            
        finally:
            log.info(f"End of import of '{lib}'")

    return True
