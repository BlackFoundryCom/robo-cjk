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

import importlib 
from types import ModuleType

def rreload(module, already_reloaded=None):
    """Recursively reloads this module and robocjk-specific dependencies.
    
    Args:
      module: The name of the module.
      already_reloaded: A set of already-reloaded module names, or None.
    """
    already_reloaded_local = already_reloaded or set()
    importlib.reload(module)

    for attribute_name in dir(module):
        # Prevent infinite recursion
        if attribute_name in already_reloaded_local:
            continue
        already_reloaded_local.add(attribute_name)

        # Extract submodule and recurse, if possible.
        submodule = getattr(module, attribute_name)
        if type(submodule) is not ModuleType:
            continue
        if not hasattr(submodule, '__file__'):
            continue

        # Only reload modules in this development repo.
        if 'robo-cjk' not in submodule.__file__:
            continue

        rreload(submodule, already_reloaded_local)
