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
import sys
import logging

from rcjk2mysql import BF_fontbook_struct as bfs

old_bfs_instances = (bfs.BfFont, bfs.BfCGlyph, bfs.BfDComponent, bfs.BfAElement, bfs.BfLayer)
new_bfs_instances = (bfs.BfFont, bfs.BfCGlyph, bfs.BfDComponent, bfs.BfAElement, bfs.BfLayer)
CLASS, TABLE, PARAMS = range(3)
FIRST_PARAMS_0, FIRST_PARAMS_1, FIRST_PARAMS_2, FIRST_PARAMS_3 = range(1, 5)

old_targets_item = {
               "font": (bfs.BfFont,1 ,(FIRST_PARAMS_0, "'{}','{}','{}','{}'", ("database_name", "database_data", "fontlib_name","fontlib_data"))),
               "cglyph": (bfs.BfCGlyph,2 ,(FIRST_PARAMS_1, "'{}', '{}', {!a}", ("name", "unicode", "xml"))),
               "dcomponent":(bfs.BfDComponent,3 , (FIRST_PARAMS_1, "'{}', {!a}", ("name", "xml"))),
               "aelement":(bfs.BfAElement,4 ,(FIRST_PARAMS_1, "'{}', {!a}", ("name", "xml"))),
               "layer": (bfs.BfLayer, 6 ,(FIRST_PARAMS_3, "'{}', '{}', {!a}", ("axisname", "layername", "xml")))
                }

new_targets_item = {
                  "font": (bfs.BfFont, "font", (FIRST_PARAMS_0, ("update", "insert"), ", '{}','{}','{}','{}'", ("database_name", "database_data", "fontlib_name","fontlib_data"))),
                  "CG": (bfs.BfCGlyph, "glyph", (FIRST_PARAMS_1, ("update", "insert") , ", {!a}, '{}'", ("xml", "unicode"))),
                  "DC": (bfs.BfDComponent, "glyph", (FIRST_PARAMS_1, ("update", "insert"), ", {!a}", ("xml",))),
                  "AE": (bfs.BfAElement, "glyph", (FIRST_PARAMS_1, ("update", "insert"), ", {!a}", ("xml",))),
                  "layer": (bfs.BfLayer, "layer", (FIRST_PARAMS_2, ("update", "insert"), ", '{}', '{}', {!a}", ("axisname", "layername", "xml")))
                  }

orders_item = (
              "insert",
              "update",

              "rename",

              "select",
              "delete",
              "lock",
              "unlock",
              "who_locked"
              )

orders_items = (
               "select_fonts",
               "select_cglyphs",
               "select_cglyphs_layers",
               "select_dcomponents",
               "select_dcomponents_layers",
               "select_aelements",
               "select_aelements_layers",
               )

dict_allow_orders = {
                    bfs.BfFont: ("insert", "update", "delete", "select") ,  
                    bfs.BfCGlyph: ("insert", "update", "delete", "rename", "lock", "unlock", "who_locked", "select") ,  
                    bfs.BfDComponent: ("insert", "update", "delete", "rename", "lock", "unlock", "who_locked", "select") ,  
                    bfs.BfAElement: ("insert", "update", "delete", "rename", "lock", "unlock", "who_locked", "select") ,  
                    bfs.BfLayer: ("insert", "update", "delete", "select") 
                    }

_debug = False
def make_manage_item(bf_log: logging.Logger, bitem: bfs.BfBaseObj, order_sql: str, username: str, *extra_args):
    """
    make request to send to mysql
    """
    if order_sql not in dict_allow_orders[type(bitem)]:
        raise ValueError(f"{order_sql} not allowed for this '{type(bitem)}'")
    
    if not isinstance(bitem, old_bfs_instances):
        raise TypeError(f"'{type(bitem)}' not in list of type '{str(old_bfs_instances)}'") 

    for k in old_targets_item:
        if isinstance(bitem, old_targets_item[k][CLASS]):
            prefix, format_str, names = old_targets_item[k][PARAMS]

            # is there a prefix
            if prefix: 
                if prefix == FIRST_PARAMS_0:
                    format_str = format_str =  f"'{getattr(bitem, 'name')}', " + format_str
                elif prefix in (FIRST_PARAMS_1, FIRST_PARAMS_2):
                    font = getattr(bitem, "font")
                    if prefix == FIRST_PARAMS_1:
                        format_str =  f"'{getattr(font, 'name')}', " + format_str
                    elif prefix == FIRST_PARAMS_2:
                        parent = getattr(bitem, 'aelement')
                        format_str =  f"'{getattr(font, 'name')}', '{bitem.aelement.name}, '" + format_str    

                elif prefix == FIRST_PARAMS_3:
                    parent = getattr(bitem, 'item')
                    font = getattr(parent, 'font')
                    format_str =  f"'{getattr(font, 'name')}', '{getattr(parent, 'name')}, '" + format_str    
            format_str += f", '{username}'"

            datas = [getattr(bitem, name) for name in names]
            if datas:
                return f"ufo_{order_sql}_{k}({format_str.format(*datas)})"
                
            return f"ufo_{order_sql}_{k}({format_str})"

def new_make_manage_item(bf_log: logging.Logger, bitem: bfs.BfBaseObj, order_sql: str, username: str, *extra_args):
    """
    make request to send to mysql
    """
    if order_sql not in dict_allow_orders[type(bitem)]:
        raise ValueError(f"{order_sql} not allowed for this '{type(bitem)}'")
    
    if not isinstance(bitem, new_bfs_instances):
        raise TypeError(f"'{type(bitem)}' not in list of type '{str(new_bfs_instances)}'") 

    for k in new_targets_item:
        # print(new_targets_item[k][CLASS])
        if isinstance(bitem, new_targets_item[k][CLASS]):
            prefix, orders, format_str, names = new_targets_item[k][PARAMS]

            # is there a prefix
            if prefix == FIRST_PARAMS_0:
                prefix_str = f"'{getattr(bitem, 'name')}'"

            elif prefix in (FIRST_PARAMS_1, FIRST_PARAMS_2):
                font = getattr(bitem, "font")
                if prefix == FIRST_PARAMS_1:
                    prefix_str =  f"'{getattr(font, 'name')}', '{getattr(bitem, 'name')}', {getattr(bitem, 'item_type')}"
                elif prefix == FIRST_PARAMS_2:
                    parent = getattr(bitem, 'item')
                    prefix_str =  f"'{getattr(font, 'name')}', '{getattr(parent, 'name')}', {getattr(parent, 'item_type')}"
            
            extra_str = ""
            if extra_args:
                for arg in extra_args:
                    extra_str += f", '{arg}'"
            suffix_str = f", '{username}'"

            if _debug:
                print("1.", prefix_str)
                print("2.", format_str)
                print("3.", extra_str)
                print("4.", suffix_str)
            
            if order_sql in orders:
                req = prefix_str + format_str + extra_str + suffix_str
                datas = [getattr(bitem, name) for name in names]
                req = req.format(*datas)
            else:
                req = prefix_str + extra_str + suffix_str

            my_sql_req = f"rcjk_{order_sql}_{new_targets_item[k][TABLE]}({req})"
            if _debug:
                print("5.", req)            
                print("6. ->", my_sql_req)            

            return my_sql_req

def make_get_items(bf_log: logging.Logger, items: str, order_sql: str, *values_args):
    pass