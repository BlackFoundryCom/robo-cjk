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
from utils import interpolation

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

    @property
    def names(self):
        for axis in self:
            yield axis.name
        # return self._axesNames
    

    def addAxis(self, axis:dict):
        self.append(Axis(**axis))

    def renameAxis(self, oldName, newName):
        for axis in self:
            if axis.name == oldName:
                axis.name = newName

    def removeAxis(self, arg):
        if isinstance(arg, int):
            index = arg
        else:
            index = 0
            for i, x in enumerate(self):
                if x.name == arg:
                    index = i
        self.pop(index)

    def getList(self):
        # print("Axes", [x._toDict() for x in self])
        return [x._toDict() for x in self]
        # return [x._toDict() for x in self]

    def get(self, name):
        for x in self:
            if x.name == name:
                return x

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
            tcenterx: int = 0,
            tcentery: int = 0,
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
        self.tcenterx = tcenterx
        self.tcentery = tcentery
        self.rotation = self._normalizeRotation(rotation)
        self.scalex = scalex
        self.scaley = scaley
        self.x = x
        self.y = y
        for k, v in kwargs.items():
            if k == "rcenterx":
                self.tcenterx = v
            elif k == "rcentery":
                self.tcentery = v

    def _normalizeRotation(self, rotation):
        r = rotation
        if r:
            if abs(r) != 360:
                r = int(rotation%(360*rotation/abs(rotation)))
        return r

    def convertOffsetFromRCenterToTCenter(self):
        """Take a set of transformation parameters that use a center only for rotation
        ("rcenter"), and return the new x, y offset for the equivalent transform that
        uses a center for rotation and scaling ("tcenter"), so that

            t1 = makeTransform(x, y, rotation, scalex, scaley, tcenterx, tcentery)
            t2 = makeTransform(newx, newy, rotation, scalex, scaley, tcenterx, tcentery, scaleUsesCenter=True)

        return the same transformation (bar floating point rounding errors).
        """
        t = interpolation.makeTransform(self.x, self.y, self.rotation, self.scalex, self.scaley, self.tcenterx, self.tcentery, scaleUsesCenter=False)
        tmp = interpolation.makeTransform(self.x, self.y, self.rotation, self.scalex, self.scaley, self.tcenterx, self.tcentery, scaleUsesCenter=True)
        self.x = self.x + t[4] - tmp[4]
        self.y = self.y + t[5] - tmp[5]
        return self.x, self.y


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

    def _init_with_old_format(self, deepComponents:list = []):
        self._deepComponents = []
        for deepComponent in deepComponents:
            if deepComponent.get("name"):
                self._deepComponents.append(DeepComponentNamed(**dict(deepComponent)))
            else:
                self._deepComponents.append(DeepComponent(**dict(deepComponent)))
        self._convertOffsetFromRCenterToTCenter()

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

    def _convertOffsetFromRCenterToTCenter(self):
        for deepComponent in self._deepComponents:
            deepComponent.transform.convertOffsetFromRCenterToTCenter()

    def __repr__(self):
        return str(self._deepComponents)

    def __len__(self):
        return len(self._deepComponents)

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

    def __init__(self, location: dict = {}, layerName: str = "", deepComponents: dict = {}, sourceName: str = "", on: bool = 1, **kwargs):
        # print("_init_ variation glyphs", location, layerName, deepComponents)
        self.location = MathDict(location) #location is a dict specifiying the design space location {"wght":1, "wdth":1}
        self.layerName = layerName
        self.deepComponents = DeepComponents(deepComponents)
        self.sourceName = sourceName
        self.on = on
        for k, v in kwargs.items():
            if k == "axisName":
                self.sourceName = v

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

    def activate(self):
        self.on = True

    def desactivate(self):
        self.on = False

    def renameAxis(self, oldName, newName):
        if oldName not in self.location: return
        newItems = {}
        for k, v in self.location.items():
            if k == oldName:
                newItems[newName] = v
        self.location = {**self.location, **newItems}
        del self.location[oldName]

    def addLocation(self, name:str, position:float=.0):
        self.location[name] = position

    def removeLocation(self, name:str):
        if name in self.location:
            del self.location[name]
            # self.desactivate()

    def addDeepComponent(self, deepComponent):
        self.deepComponents.addDeepComponent(deepComponent)

    def removeDeepComponents(self, indexes):
        self.deepComponents.removeDeepComponents(indexes)

    def __repr__(self):
        return str({x:getattr(self, x) for x in vars(self)})
        # return f"<location: {self.location}, layerName: {self.layerName}, deepComponent: {self.deepComponents}>"

    def _toDict(self, exception = []):
        d = {"location":self.location, "layerName":self.layerName, "deepComponents":self.deepComponents.getList(), "sourceName":self.sourceName, "on":self.on}
        for e in exception:
            if e in d:
                del d[e]
        return d

    def __getitem__(self, item):
        return getattr(self, item)

class VariationGlyphs(list):

    def __init__(self, variationGlyphs=[], axes = []):
        for variation in variationGlyphs:
            self.addVariation(variation, axes)
        # print("variationGlyphs", variationGlyphs)

    def _init_with_old_format(self, data, axes):
        for k, v in data.items():
            variation = {"location": {k:v.get("maxValue")}, "sourceName":k, "layerName": v.get("layerName"), "deepComponents": v.get("content").get("deepComponents")}
            self.addVariation(variation, axes)
        for variation in self:
            variation.deepComponents._convertOffsetFromRCenterToTCenter()

    # def __iter__(self):
    #     for x in super(VariationGlyphs, self).__iter__():
    #         # print(dir(x))
    #         yield x._toDict()

    def addAxisToLocations(self, axisName="", minValue=0):
        for variation in self:
            variation.location[axisName] = minValue

    def addVariation(self, variation, axes):
        loc = self._normalizedLocation(variation.get('location'), axes)
        locations = [self._normalizedLocation(x, axes) for x in self.locations]
        # print(locations, loc)
        if loc in locations or not loc:
            variation["on"] = False
        self.append(VariationGlyphsInfos(**variation))

    def activateSource(self, index, value, axes):
        if not value:
            self[index].on = False
            return False
        loc = self._normalizedLocation(self[index].location, axes)
        locations = [self._normalizedLocation(x, axes) for x in self.locations]
        if loc in locations:
            self[index].on = False
            return False
        else:
            self[index].on = True
            return True


    def setLocationToIndex(self, location, index, axes):
        variation = self[index]
        locations = [self._normalizedLocation(x, axes) for x in self.locations]
        loc = self._normalizedLocation(location, axes)
        if loc in locations or not loc:
            variation.desactivate()
        variation.location = location

    def _normalizedLocation(self, location, axes):
        return {k:v for k,v in location.items() if v != axes.get(k).minValue}

    # def __iter__(self):
    #     for x in self:
    #         yield x._toDict()

    def getFromSourceName(self, sourceName):
        for x in self:
            if x.sourceName == sourceName:
                return x

    def getList(self, exception = []):
        """
        Return a list reprensentation on the class
        """
        # return [x for x in self]
        return [x._toDict(exception) for x in self]
        # return {x: getattr(self, x)._toDict() for x in vars(self)}  
    
    def removeVariation(self, index):
        self.pop(index)

    def removeAxis(self, axisName):
        for variation in self:
            variation.removeLocation(axisName)
            # if variation.location in self.locations or not variation.location:
                # variation.desactivate()

    def desactivateDoubleLocations(self, axes):
        toDesactivate = []
        locations = [self._normalizedLocation(x, axes) for x in self.locations]
        for i, variation in enumerate(self):
            location = self._normalizedLocation(variation.location, axes)
            if locations.count(location) > 1:
                toDesactivate.append(i)
        for i in toDesactivate:
            self[i].desactivate()
        for variation in self:
            empty = True
            for k, v in variation.location.items():
                if v != axes.get(k).minValue:
                    empty = False
                    break
            if empty:
                variation.desactivate()

    def renameAxisInsideLocation(self, oldName, newName):
        for variation in self:
            variation.renameAxis(oldName, newName)

    def addDeepComponent(self, deepComponent):
        """
        Add a new component to the whole axes
        """
        for x in self:
            x.addDeepComponent(DeepComponent(**deepComponent._unnamed()))

    def removeDeepComponents(self, indexes: list):
        """
        Remove components variation at indexes
        """
        if not indexes:
            return
        for x in self:
            x.removeDeepComponents(indexes)

    # def activateSource(self, index):
    #     self[index].activate()

    # def activateSources(self, indexes: list):
    #     for index in indexes:
    #         self.activateSource(index, 1)

    # def desactivateSource(self, index):
    #     self[index].desactivate()

    # def desactivateSources(self, indexes: list):
    #     for index in indexes:
    #         self.desactivateSource(index)

    # def __repr__(self):
    #     return str(self.getList())

    # @property
    def layerNames(self):
        return [x["layerName"] for x in self if x["layerName"]]

    @property
    def sourceNames(self):
        return [x.sourceName for x in self]
    
    @property
    def locations(self):
        return [x.location for x in self if x.on]
    
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
    dc = [{'coord': {'HGHT': 618.4000000000001, 'HWGT': 96.86, 'LLNGG': 101.0, 'RLNG': 0.0, 'VWGT': 75.8, 'WDTH': 0.82}, 'rotation': 0, 'scalex': 1.0, 'scaley': 1.0, 'x': -241, 'y': 70, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0, 'name': 'DC_53E3_00'}, {'coord': {'HGHT': 0.454, 'HWGT': 0.385, 'LLNG': 0.0, 'RLNG': 0.0, 'VWGT': 0.37, 'WDTH': 0.658}, 'rotation': 0, 'scalex': 1, 'scaley': 1, 'x': 176, 'y': 90, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0, 'name': 'DC_65E5_00'}, {'coord': {'WGHT': 0.316}, 'rotation': 0, 'scalex': 0.5559999999999998, 'scaley': 1.008, 'x': 392, 'y': -372, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0, 'name': 'DC_4E00_00'}]
    gv = {'WGHT': {'minValue': 0.0, 'maxValue': 1.0, 'layerName': 'WGHT', 'content': {'outlines': [], 'deepComponents': [{'coord': {'HGHT': 603.1, 'HWGT': 110.54, 'LLNGG': 78.60000000000001, 'RLNG': 0.0, 'VWGT': 107.12, 'WDTH': 0.803}, 'rotation': 0, 'scalex': 1.0, 'scaley': 1.0, 'x': -251, 'y': 70, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'HGHT': 0.454, 'HWGT': 0.534, 'LLNG': 0.0, 'RLNG': 0.0, 'VWGT': 0.504, 'WDTH': 0.658}, 'rotation': 0, 'scalex': 1, 'scaley': 1, 'x': 176, 'y': 90, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'WGHT': 0.548}, 'rotation': 0, 'scalex': 0.5559999999999998, 'scaley': 1.008, 'x': 392, 'y': -372, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}], 'width': 500}}}

    deepComponents = DeepComponents(dc)
    axes = Axes()
    axes._init_with_old_format(gv)
    variations = VariationGlyphs()
    variations._init_with_old_format(gv)

    print('deepComponents:', deepComponents, "\n")
    print('axes:', axes, '\n')
    print('glyphVariations:', variations)
    print("\n\n")


    dc = [{'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1, 'x': 981, 'y': -120, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0, 'name': 'stem'}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1, 'x': 0, 'y': 880, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0, 'name': 'stem'}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1, 'x': 0, 'y': -100, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0, 'name': 'stem'}, {'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1, 'x': 0, 'y': -121, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0, 'name': 'stem'}]
    gv = {'HGHT': {'minValue': 1000.0, 'maxValue': 100.0, 'layerName': '', 'content': {'outlines': [], 'deepComponents': [{'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 0.07199999999999995, 'x': 980, 'y': 340, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1, 'x': 0, 'y': 412, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1, 'x': 0, 'y': 360, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 0.07199999999999995, 'x': 0, 'y': 340, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}], 'width': 1000}}, 'HWGT': {'minValue': 20.0, 'maxValue': 200.0, 'layerName': '', 'content': {'outlines': [], 'deepComponents': [{'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1.08, 'x': 980, 'y': -160, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.2, 'scaley': 1, 'x': 0, 'y': 920, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.2, 'scaley': 1, 'x': 0, 'y': 40, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1.08, 'x': 0, 'y': -160, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}], 'width': 1000}}, 'LLNGG': {'minValue': 0.0, 'maxValue': 200.0, 'layerName': '', 'content': {'outlines': [], 'deepComponents': [{'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1, 'x': 980, 'y': -120, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1, 'x': 0, 'y': 880, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1, 'x': 0, 'y': -100, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1.2, 'x': 0, 'y': -320, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}], 'width': 1000}}, 'RLNG': {'minValue': 0.0, 'maxValue': 200.0, 'layerName': '', 'content': {'outlines': [], 'deepComponents': [{'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1.2, 'x': 980, 'y': -320, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1, 'x': 0, 'y': 880, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1, 'x': 0, 'y': -100, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1, 'x': -10, 'y': -120, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}], 'width': 1000}}, 'VWGT': {'minValue': 20.0, 'maxValue': 200.0, 'layerName': '', 'content': {'outlines': [], 'deepComponents': [{'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.2, 'scaley': 1, 'x': 840, 'y': -120, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1.08, 'x': -40, 'y': 880, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 1.08, 'x': -40, 'y': -100, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.2, 'scaley': 1, 'x': -40, 'y': -120, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}], 'width': 1000}}, 'WDTH': {'minValue': 0.0, 'maxValue': 1.0, 'layerName': '', 'content': {'outlines': [], 'deepComponents': [{'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1, 'x': 510, 'y': -120, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 0.06999999999999995, 'x': 460, 'y': 880, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': -90, 'scalex': 0.02, 'scaley': 0.06999999999999995, 'x': 460, 'y': -100, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}, {'coord': {'DIAG': 500.0}, 'rotation': 0, 'scalex': 0.02, 'scaley': 1, 'x': 460, 'y': -120, 'tcenterx': 0, 'tcentery': 0, 'maxValue': 1.0, 'minValue': 0.0}], 'width': 1000}}}


    axes = Axes()
    axes._init_with_old_format(gv)
    variations = VariationGlyphs()
    variations._init_with_old_format(gv)

    print('deepComponents:', dc, "\n")
    print('axes:', axes, '\n')
    print('glyphVariations:', variations)