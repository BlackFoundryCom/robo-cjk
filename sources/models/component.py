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

class DictClass:

    def __getitem__(self, item):
        if not hasattr(self, item):
            return None
        return getattr(self, item)
        
    def __setitem__(self, item, value):
        setattr(self, item, value)
        
    def __delitem__(self, item):
        if not hasattr(self, item):
            return
        delattr(self, item)
        
    def __iter__(self):
        for n in vars(self):
            yield n
            
    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(vars(self))

    def __str__(self):
        return str(self.__dict__)
            
    def items(self):
        for n in vars(self):
            yield n, self[n]
            
    def keys(self):
        return [n for n in vars(self)]
        
    def values(self):
        return [self[n] for n in vars(self)]

    def get(self, item, fallback = None):
        if not hasattr(self, item):
            return fallback
        return getattr(self, item)

class Values(DictClass):

    # __slots__ = "value", "minValue", "maxValue"

    def __init__(self, value, minValue:int = 0, maxValue:int = 1):
        super().__init__()
        self.value = value
        self.minValue = minValue
        self.maxValue = maxValue

    def __call__(self, typ = float):
        return typ(self.value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)

    def _toDict(self):
        return {x:getattr(self, x) for x in vars(self)}

class Coord(DictClass):

    def __init__(self, **kwargs):
        super().__init__()
        for k, v in kwargs.items():
            setattr(self, k, v)

    def add(self, axis: str, value: int = 0):
        """
        Add new axis with its value
        """
        setattr(self, axis, value)

    def remove(self, axis: str):
        """
        Remove axis
        """
        delattr(self, axis)

    @property
    def axes(self):
        """
        Return a list of all the axes
        """
        return self.keys()

class Component(DictClass):

    def __init__(self, 
            coord : dict = {}, 
            rotation: int = 0, 
            scalex: int = 1, 
            scaley: int = 1, 
            x: int = 0, 
            y: int = 0):
        super().__init__()
        self.coord = Coord(**dict(coord))
        self.rotation = rotation
        self.scalex = scalex
        self.scaley = scaley
        self.x = x
        self.y = y

    def set(self, items: dict):
        """
        Reinitialize the components data with dictionary
            items = {
                    'name': 'componentName',
                    'coord': {'axisName':value},
                    'rotation': 0,
                    'scalex': 1,
                    'scaley': 1,
                    'x': 0,
                    'y': 0,
                    }
        """
        for k, v in items.items():
            setattr(self, k, v)
        self.coord = Coord(**dict(items['coord']))

    def _todict(self, exception: str = ''):
        """
        Return a dict representation of the component datas.
        Allows to exclude an attribute in the dictionnary with exception
        """
        d = {x:getattr(self, x) for x in vars(self) if x != exception}
        d["coord"] = {x:getattr(d["coord"], x) for x in vars(d["coord"])}
        return d

    def _unnamed(self):
        """
        Return an unnamed dict representation of the component datas
        """
        return self._todict(exception = "name")

class ComponentNamed(Component):

    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.name = name


class Components:

    def removeComponent(self, index: int):
        """
        Remove component at an index
        """
        if index < len(self._components):
            self._components.pop(index)

    def removeComponents(self, indexes: list):
        """
        Remove components at indexes
        """
        self._components = [x for i, x in enumerate(self._components) if i not in indexes]

    def addComponent(self, component):
        """
        Add new component
        """
        self._components.append(component)

    def append(self, item):
        """
        This function is made for backward compatibility
        Add new component 
        """
        self.addComponent(item)

    def __repr__(self):
        return str(self._components)

    def __iter__(self):
        for component in self._components:
            yield component

    def __getitem__(self, index):
        assert isinstance(index, int)
        return self._components[index]

    def __setitem__(self, item, value):
        setattr(self, item, value)

    def getList(self):
        """
        Return a list reprensentation on the class
        """
        return [x._todict() for x in self._components]

    def _unnamed(self):
        pass


class GlyphComponentsNamed(Components):

    """
    Deep component structure:
        [
            {
                'coord': {'DIAG': 0.5}, 
                'name': 'stem', 
                'rotation': 0, 
                'scalex': 0.02, 
                'scaley': 1, 
                'x': 980, 
                'y': -120
            }, 
            {
                'coord': {'DIAG': 0.5}, 
                'name': 'stem', 
                'rotation': -90, 
                'scalex': 0.02, 
                'scaley': 1, 
                'x': 0, 
                'y': 880
            }
        ]
    """

    """
    Character Glyph strucure:
        [
            {
                'coord': {'HGHT': 0.262, 'HWGT': 0.393, 'LLNG': 0.289, 'RLNG': 0.289, 'VWGT': 0.408, 'WDTH': 0.415}, 
                'name': 'DC_65E5_00', 
                'rotation': 0, 
                'scalex': 1, 
                'scaley': 1, 
                'x': 0, 
                'y': 7
            }
        ]
    """

    def __init__(self, components: list = []):
        super().__init__()
        self._components = []
        for component in components:
            self._components.append(ComponentNamed(**dict(component)))

    def add(self, name: str, items: dict = {}):
        """
        Add new component
        """
        self._components.append(ComponentNamed(name, **items))


class GlyphComponentsVariations(Components):

    def __init__(self, components: list = []):
        super().__init__()
        self._components = []
        for component in components:
            self._components.append(Component(**dict(component)))

    def add(self, items: dict = {}):
        """
        Add new component
        """
        self._components.append(Component(**items))


class GlyphVariations(DictClass):

    """
    Deep component structure:
        {
            'HGHT': [
                        {
                            'coord': {'DIAG': 0.5}, 
                            'rotation': 0, 
                            'scalex': 0.02, 
                            'scaley': 0.07199999999999995, 
                            'x': 980, 
                            'y': 340
                        }, 
                        {
                            'coord': {'DIAG': 0.5}, 
                            'rotation': -90, 
                            'scalex': 0.02, 
                            'scaley': 1, 
                            'x': 0, 
                            'y': 412
                        }
                    ]
        }
    """

    """
    Character Glyph structure:
        {
            'wght': [
                        {
                            'coord': {'HGHT': 0.262, 'HWGT': 0.693, 'LLNG': 0.289, 'RLNG': 0.289, 'VWGT': 0.655, 'WDTH': 0.415}, 
                            'rotation': 0, 
                            'scalex': 1, 
                            'scaley': 1, 
                            'x': 0, 
                            'y': 7
                        }
                    ]
        }
    """

    def __init__(self, axes = {}):
        super().__init__()
        for k, v in axes.items():
            setattr(self, k, GlyphComponentsVariations(v))

    def addAxis(self, axisName: str, components):
        """
        Add new axis with no named components
        """
        #retrieve the components info without their name
        noNamedComponents = [Component(**component._unnamed()) for component in components]
        setattr(self, axisName, noNamedComponents)

    def removeAxis(self, axisName: str):
        """
        Remove a variation axis
        """
        if not hasattr(self, axisName):
            return
        delattr(self, axisName)

    def addComponent(self, component):
        """
        Add a new component to the whole axes
        """
        for x in vars(self):
            getattr(self, x).add(component._unnamed())

    def getDict(self):
        """
        Return a list reprensentation on the class
        """
        return {x: getattr(self, x).getList() for x in vars(self)}     

    @property
    def axes(self):
        """
        Return a list of all the variations axes
        """
        return self.keys()

    def removeComponents(self, indexes: list):
        """
        Remove components variation at indexes
        """
        for x in vars(self):
            getattr(self, x).removeComponents(indexes)