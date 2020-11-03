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
from fontTools.pens.recordingPen import RecordingPen

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

import operator

class InterpolationError(Exception):
    pass

class _MathMixin:
    
    def __add__(self, other):
        return self._doBinaryOperator(other, operator.add)
        
    def __sub__(self, other):
        return self._doBinaryOperator(other, operator.sub)
        
    def __mul__(self, scalar):
        return self._doBinaryOperatorScalar(scalar, operator.mul)
        
    def __rmul__(self, scalar):
        return self._doBinaryOperatorScalar(scalar, operator.mul)
        
class MathDict(dict, _MathMixin):
    
    def _doBinaryOperatorScalar(self, scalar, op):
        result = MathDict()
        for k, v in self.items():
            if isinstance(v, (int, float, MathDict)):
                result[k] = op(v, scalar)
            else:
                result[k] = v
        return result
        
    def _doBinaryOperator(self, other, op):
        # any missing keys will be taken from the other dict
        self_other = dict(other)
        self_other.update(self)
        other_self = dict(self)
        other_self.update(other)
        result = MathDict()
        for k, v1 in self_other.items():
            v2 = other_self[k]
            if isinstance(v1, (int, float, MathDict)):
                result[k] = op(v1, v2)
            else:
                if v1 != v2:
                    print(v1, v2)
                    raise InterpolationError("incompatible dicts")
                result[k] = v1
        return result
        
# class MathList(_MathMixin, list):
    
#     def _doBinaryOperatorScalar(self, scalar, op):
#         result = MathList()
#         for e in self:
#             if isinstance(e, (int, float, MathDict, MathList)):
#                 result.append(op(e, scalar))
#             else:
#                 result.append(e)
#         return result
        
#     def _doBinaryOperator(self, other, op):
#         # any missing keys will be taken from the other dict
#         assert len(self) == len(other)
#         self_other = list(other)
#         other_self = list(self)
#         result = MathList()
#         for i, e1 in enumerate(self_other):
#             e2 = other_self[i]
#             if isinstance(e1, (int, float, MathDict, MathList)):
#                 result.append(op(e1, e2))
#             else:
#                 if e1 != e2:
#                     print(e1, e2)
#                     raise InterpolationError("incompatible lists")
#                 result.append(e1)
#         return result

class Axis:

    def __init__(self, name="", minValue=0, maxValue=1):
        # for k, v in kwargs.items():
        #     self[k] = v
        self.name = name
        self.minValue = minValue
        self.maxValue = maxValue

    def __repr__(self):
        return "<"+str(vars(self))+">"

    def _toDict(self):
        return MathDict({x:getattr(self, x) for x in vars(self)})

class Axes(list):

    """
    This class refere to robocjk.axes key
    """

    def __init__(self, axes = []):
        for axis in axes:
            self.addAxis(axis)

    def _init_with_old_format(self, data):
        for k, v in data.items():
            axis = dict(name = k, minValue = v.get("minValue"), maxValue = v.get("maxValue"))
            self.addAxis(axis)

    def addAxis(self, axis:dict):
        self.append(Axis(**axis))

    def removeAxis(self, arg):
        if isinstance(arg, int):
            index = arg
        else:
            index = self.index(arg)
        self.pop(index)

    def getList(self):
        # print("Axes", [x._toDict() for x in self])
        return [x._toDict() for x in self]
        # return [x._toDict() for x in self]

    # def __repr__(self):
    #     return str(self.getList())

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

    def clear(self):
        """
        Remove all axes
        """
        axes = list(vars(self))
        for axis in axes:
            self.remove(axis)

class Transform(DictClass):

    def __init__(self, 
            rcenterx: int = 0,
            rcentery: int = 0,
            rotation: int = 0,
            scalex: int = 1,
            scaley: int = 1,
            x: int = 0,
            y: int = 0,
            **kwargs
            ):
        super().__init__()
        # for k, v in kwargs.items():
        #     setattr(self, k, v)
        self.rcenterx = rcenterx
        self.rcentery = rcentery
        self.rotation = self._normalizeRotation(rotation)
        self.scalex = scalex
        self.scaley = scaley
        self.x = x
        self.y = y

    def _normalizeRotation(self, rotation):
        r = rotation
        if r:
            r = int(rotation%(360*rotation/abs(rotation)))
        return r

class DeepComponent(DictClass):

    def __init__(self, 
            coord : dict = {}, 
            **kwargs
            ):
        super().__init__()
        self.coord = Coord(**dict(coord))
        if 'transform' in kwargs.keys():
            self.transform = Transform(**dict(kwargs["transform"]))
        else:
            self.transform = Transform(**dict(kwargs))

    def set(self, items: dict):
        """
        Reinitialize the deep components data with dictionary
            items = {
                    'name': 'deepComponentName',
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
        self.transform = Transform(**dict(items['transform']))
        self.coord = Coord(**dict(items['coord']))

    def _toDict(self, exception: str = ''):
        """
        Return a dict representation of the deep component datas.
        Allows to exclude an attribute in the dictionnary with exception
        """
        d = MathDict({x:getattr(self, x) for x in vars(self) if x != exception})
        d["coord"] = MathDict({x:getattr(self.coord, x) for x in vars(self.coord)})
        d["transform"] = MathDict({x:getattr(self.transform, x) for x in vars(self.transform)})
        return d

    def _unnamed(self):
        """
        Return an unnamed dict representation of the deep component datas
        """
        return self._toDict(exception = "name")

    def __repr__(self):
        return str(self._toDict())

class DeepComponentNamed(DeepComponent):

    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.name = name

class DeepComponents:

    """
    Structure
    [
        {
        'name': glyphName, 
        'coord': {
                VariationAxis0: v, 
                VariationAxis1: v
                }, 
        'x': v, 
        'y': v, 
        'scalex': v, 
        'scaley': v, 
        'rotation': v
        },
        {
        'name': glyphName, 
        'coord': {
                VariationAxis0: v, 
                VariationAxis1: v
                }, 
        'x': v, 
        'y': v, 
        'scalex': v, 
        'scaley': v, 
        'rotation': v
        }
    ]   
    """

    def __init__(self, deepComponents: list = []):
        self._deepComponents = []
        for deepComponent in deepComponents:
            if deepComponent.get("name"):
                self._deepComponents.append(DeepComponentNamed(**dict(deepComponent)))
            else:
                self._deepComponents.append(DeepComponent(**dict(deepComponent)))

    def add(self, name: str, items: dict = {}):
        """
        Add new deep component
        """
        self._deepComponents.append(DeepComponentNamed(name, **items))

    def removeDeepComponent(self, index: int):
        """
        Remove deep component at an index
        """
        if index < len(self._deepComponents):
            self._deepComponents.pop(index)

    def removeDeepComponents(self, indexes: list):
        """
        Remove deep components at indexes
        """
        if not indexes: 
            return
        self._deepComponents = [x for i, x in enumerate(self._deepComponents) if i not in indexes]

    def addDeepComponent(self, deepComponent):
        """
        Add new deep component
        """
        self._deepComponents.append(deepComponent)

    def append(self, item):
        """
        This function is made for backward compatibility
        Add new deep component 
        """
        self.addDeepComponent(item)

    def __repr__(self):
        return str(self._deepComponents)

    def __iter__(self):
        for deepComponent in self._deepComponents:
            yield deepComponent._toDict()

    def __getitem__(self, index):
        assert isinstance(index, int)
        return self._deepComponents[index]

    def __setitem__(self, item, value):
        setattr(self, item, value)

    def __bool__(self):
        return bool(self._deepComponents)

    def getList(self):
        """
        Return a list reprensentation on the class
        """
        # print("DeepComponents", [x._toDict() for x in self._deepComponents])
        return [x._toDict() for x in self._deepComponents]

    def _unnamed(self):
        pass


class VariationGlyphsInfos:

    def __init__(self, location: dict = {}, layerName: str = "", deepComponents: dict = {}):
        # print("_init_ variation glyphs", location, layerName, deepComponents)
        self.location = MathDict(location) #location is a dict specifiying the design space location {"wght":1, "wdth":1}
        self.layerName = layerName
        self.deepComponents = DeepComponents(deepComponents)

        # print(self.location)
        # print(self.layerName)
        # print(self.deepComponents)

    # @property
    # def location(self):
    #     return self._location
    
    # @property
    # def layerName(self):
    #     return self._layerName

    # @layerName.setter
    # def layerName(self, name):
    #     self._layerName = name    

    def addLocation(self, name:str, position:float=.0):
        self.location[name] = position

    def removeLocation(self, name:str):
        del self.location[name]

    def addDeepComponent(self, deepComponent):
        for x in self.deepComponents:
            x.addDeepComponent(deepComponent)

    def removeDeepComponents(self, indexes):
        for x in self.deepComponents:
            x.removeDeepComponents(indexes)

    def __repr__(self):
        return str({x:getattr(self, x) for x in vars(self)})
        return f"<location: {self.location}, layerName: {self.layerName}, deepComponent: {self.deepComponents}>"

    def _toDict(self):
        return {"location":self.location, "layerName":self.layerName, "deepComponents":self.deepComponents.getList()}

    def __getitem__(self, item):
        return getattr(self, item)

class VariationGlyphs(list):

    def __init__(self, variationGlyphs=[]):
        for variation in variationGlyphs:
            self.addAxis(variation)
        # print("variationGlyphs", variationGlyphs)

    def _init_with_old_format(self, data):
        for k, v in data.items():
            variation = {"location": {k:v.get("maxValue")}, "layerName": v.get("layerName"), "deepComponents": v.get("content").get("deepComponents")}
            self.addAxis(variation)

    # def __iter__(self):
    #     for x in super(VariationGlyphs, self).__iter__():
    #         # print(dir(x))
    #         yield x._toDict()

    def addAxis(self, variation):
        self.append(VariationGlyphsInfos(**variation))

    # def __iter__(self):
    #     for x in self:
    #         yield x._toDict()

    def getList(self):
        """
        Return a list reprensentation on the class
        """
        # return [x for x in self]
        return [x._toDict() for x in self]
        # return {x: getattr(self, x)._toDict() for x in vars(self)}  
    
    def removeAxis(self, arg):
        if isinstance(arg, int):
            index = arg
        else:
            index = self.index(arg)
        self.pop(index)

####################################

    def addDeepComponent(self, deepComponent):
        """
        Add a new component to the whole axes
        """
        for x in self:
            x.addDeepComponent(deepComponent._unnamed())

    def removeDeepComponents(self, indexes: list):
        """
        Remove components variation at indexes
        """
        if not indexes:
            return
        for x in self:
            x.removeDeepComponents(indexes)

   


    # def __repr__(self):
    #     return str(self.getList())

    # @property
    def layerNames(self):
        return [x["layerName"] for x in self]
    

    @property
    def axes(self):
        """
        Return a list of all the variations axes
        """
        return [x["layerName"] for x in self]

    @property
    def infos(self):
        """
        Return a list of all the variations
        """
        return [x["deepComponents"] for x in self]

if __name__ == "__main__":
    dc = [{'coord': {'HGHT': 618.4000000000001, 'HWGT': 96.86, 'LLNGG': 101.0, 'RLNG': 0.0, 'VWGT': 75.8, 'WDTH': 0.82}, 'rotation': 0, 'scalex': 1.0, 'scaley': 1.0, 'x': -241, 'y': 70, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0, 'name': 'DC_53E3_00'}, {'coord': {'HGHT': 0.454, 'HWGT': 0.385, 'LLNG': 0.0, 'RLNG': 0.0, 'VWGT': 0.37, 'WDTH': 0.658}, 'rotation': 0, 'scalex': 1, 'scaley': 1, 'x': 176, 'y': 90, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0, 'name': 'DC_65E5_00'}, {'coord': {'WGHT': 0.316}, 'rotation': 0, 'scalex': 0.5559999999999998, 'scaley': 1.008, 'x': 392, 'y': -372, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0, 'name': 'DC_4E00_00'}]
    gv = {'WGHT': {'minValue': 0.0, 'maxValue': 1.0, 'layerName': 'WGHT', 'content': {'outlines': [], 'deepComponents': [{'coord': {'HGHT': 603.1, 'HWGT': 110.54, 'LLNGG': 78.60000000000001, 'RLNG': 0.0, 'VWGT': 107.12, 'WDTH': 0.803}, 'rotation': 0, 'scalex': 1.0, 'scaley': 1.0, 'x': -251, 'y': 70, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'HGHT': 0.454, 'HWGT': 0.534, 'LLNG': 0.0, 'RLNG': 0.0, 'VWGT': 0.504, 'WDTH': 0.658}, 'rotation': 0, 'scalex': 1, 'scaley': 1, 'x': 176, 'y': 90, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'WGHT': 0.548}, 'rotation': 0, 'scalex': 0.5559999999999998, 'scaley': 1.008, 'x': 392, 'y': -372, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}], 'width': 500}}}

    deepComponents = DeepComponents(dc)
    axes = Axes()
    axes._init_with_old_format(gv)
    variations = VariationGlyphs()
    variations._init_with_old_format(gv)

    print('deepComponents:', deepComponents, "\n")
    print('axes:', axes, '\n')
    print('glyphVariations:', variations)
    print("\n\n")


    dc = [{'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1, 'x': 981, 'y': -120, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0, 'name': 'stem'}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1, 'x': 0, 'y': 880, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0, 'name': 'stem'}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1, 'x': 0, 'y': -100, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0, 'name': 'stem'}, {'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1, 'x': 0, 'y': -121, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0, 'name': 'stem'}]
    gv = {'HGHT': {'minValue': 1000.0, 'maxValue': 100.0, 'layerName': '', 'content': {'outlines': [], 'deepComponents': [{'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 0.07199999999999995, 'x': 980, 'y': 340, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1, 'x': 0, 'y': 412, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1, 'x': 0, 'y': 360, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 0.07199999999999995, 'x': 0, 'y': 340, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}], 'width': 1000}}, 'HWGT': {'minValue': 20.0, 'maxValue': 200.0, 'layerName': '', 'content': {'outlines': [], 'deepComponents': [{'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1.08, 'x': 980, 'y': -160, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.2, 'scaley': 1, 'x': 0, 'y': 920, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.2, 'scaley': 1, 'x': 0, 'y': 40, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1.08, 'x': 0, 'y': -160, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}], 'width': 1000}}, 'LLNGG': {'minValue': 0.0, 'maxValue': 200.0, 'layerName': '', 'content': {'outlines': [], 'deepComponents': [{'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1, 'x': 980, 'y': -120, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1, 'x': 0, 'y': 880, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1, 'x': 0, 'y': -100, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1.2, 'x': 0, 'y': -320, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}], 'width': 1000}}, 'RLNG': {'minValue': 0.0, 'maxValue': 200.0, 'layerName': '', 'content': {'outlines': [], 'deepComponents': [{'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1.2, 'x': 980, 'y': -320, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1, 'x': 0, 'y': 880, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1, 'x': 0, 'y': -100, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1, 'x': -10, 'y': -120, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}], 'width': 1000}}, 'VWGT': {'minValue': 20.0, 'maxValue': 200.0, 'layerName': '', 'content': {'outlines': [], 'deepComponents': [{'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.2, 'scaley': 1, 'x': 840, 'y': -120, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1.08, 'x': -40, 'y': 880, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1.08, 'x': -40, 'y': -100, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.2, 'scaley': 1, 'x': -40, 'y': -120, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}], 'width': 1000}}, 'WDTH': {'minValue': 0.0, 'maxValue': 1.0, 'layerName': '', 'content': {'outlines': [], 'deepComponents': [{'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1, 'x': 510, 'y': -120, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 0.06999999999999995, 'x': 460, 'y': 880, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 0.06999999999999995, 'x': 460, 'y': -100, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1, 'x': 460, 'y': -120, 'rcenterx': 0, 'rcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}], 'width': 1000}}}


    axes = Axes()
    axes._init_with_old_format(gv)
    variations = VariationGlyphs()
    variations._init_with_old_format(gv)

    print('deepComponents:', dc, "\n")
    print('axes:', axes, '\n')
    print('glyphVariations:', variations)