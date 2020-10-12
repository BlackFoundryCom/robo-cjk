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

# # class Coord(DictClass):

# #     def __init__(self, **kwargs):
# #         super().__init__()
# #         for k, v in kwargs.items():
# #             if isinstance(v, (int, float)):
# #                 setattr(self, k, {"value":v, "minValue":0., "maxValue":1.})
# #             else:
# #                 setattr(self, k, v)

# #     def __getitem__(self, item):
# #         return getattr(self, item).get("value")

# #     def getMinValue(self, item):
# #         return getattr(self, item).get("minValue")

# #     def getMaxValue(self, item):
# #         return getattr(self, item).get("maxValue")

# #     def add(self, axis: str, value: int = 0):
# #         """
# #         Add new axis with its value
# #         """
# #         if isinstance(value, float):
# #             setattr(self, axis, {"value":value, "minValue":0., "maxValue":1.})
# #         else:
# #             setattr(self, axis, value)

# #     def remove(self, axis: str):
# #         """
# #         Remove axis
# #         """
# #         delattr(self, axis)

# #     @property
# #     def axes(self):
# #         """
# #         Return a list of all the axes
# #         """
# #         return self.keys()

# #     def clear(self):
# #         """
# #         Remove all axes
# #         """
# #         axes = list(vars(self))
# #         for axis in axes:
# #             self.remove(axis)

# class Coord(DictClass):

#     def __init__(self, **kwargs):
#         super().__init__()
#         for k, v in kwargs.items():
#             setattr(self, k, v)

#     def add(self, axis: str, value: int = 0):
#         """
#         Add new axis with its value
#         """
#         setattr(self, axis, value)

#     def remove(self, axis: str):
#         """
#         Remove axis
#         """
#         delattr(self, axis)

#     @property
#     def axes(self):
#         """
#         Return a list of all the axes
#         """
#         return self.keys()

#     def clear(self):
#         """
#         Remove all axes
#         """
#         axes = list(vars(self))
#         for axis in axes:
#             self.remove(axis)


# class DeepComponent(DictClass):

#     def __init__(self, 
#             coord : dict = {}, 
#             rotation: int = 0, 
#             scalex: int = 1, 
#             scaley: int = 1, 
#             x: int = 0, 
#             y: int = 0,
#             rcenterx: int = 0,
#             rcentery: int = 0,
#             # axisMinValue: float = 0.,
#             # axisMaxValue: float = 1.,
#             maxValue: float = 1.,
#             minValue: float = 0.,
#             ):
#         super().__init__()
#         self.coord = Coord(**dict(coord))
#         self.rotation = rotation
#         self.scalex = scalex
#         self.scaley = scaley
#         self.x = x
#         self.y = y
#         self.rcenterx = rcenterx
#         self.rcentery = rcentery
#         # self.axisMinValue = axisMinValue
#         # self.axisMaxValue = axisMaxValue
#         self.maxValue = maxValue
#         self.minValue = minValue

#     def set(self, items: dict):
#         """
#         Reinitialize the deep components data with dictionary
#             items = {
#                     'name': 'deepComponentName',
#                     'coord': {'axisName':value},
#                     'rotation': 0,
#                     'scalex': 1,
#                     'scaley': 1,
#                     'x': 0,
#                     'y': 0,
#                     }
#         """
#         for k, v in items.items():
#             setattr(self, k, v)
#         self.coord = Coord(**dict(items['coord']))

#     def _toDict(self, exception: str = ''):
#         """
#         Return a dict representation of the deep component datas.
#         Allows to exclude an attribute in the dictionnary with exception
#         """
#         d = {x:getattr(self, x) for x in vars(self) if x != exception}
#         d["coord"] = {x:getattr(d["coord"], x) for x in vars(d["coord"])}
#         return d

#     def _unnamed(self):
#         """
#         Return an unnamed dict representation of the deep component datas
#         """
#         return self._toDict(exception = "name")

# class DeepComponentNamed(DeepComponent):

#     def __init__(self, name: str, **kwargs):
#         super().__init__(**kwargs)
#         self.name = name


# class DeepComponents:

#     """
#     Structure
#     [
#         {
#         'name': glyphName, 
#         'coord': {
#                 VariationAxis0: v, 
#                 VariationAxis1: v
#                 }, 
#         'x': v, 
#         'y': v, 
#         'scalex': v, 
#         'scaley': v, 
#         'rotation': v
#         },
#         {
#         'name': glyphName, 
#         'coord': {
#                 VariationAxis0: v, 
#                 VariationAxis1: v
#                 }, 
#         'x': v, 
#         'y': v, 
#         'scalex': v, 
#         'scaley': v, 
#         'rotation': v
#         }
#     ]   
#     """

#     def __init__(self, deepComponents: list = []):
#         self._deepComponents = []
#         for deepComponent in deepComponents:
#             self._deepComponents.append(DeepComponentNamed(**dict(deepComponent)))

#     def add(self, name: str, items: dict = {}):
#         """
#         Add new deep component
#         """
#         self._deepComponents.append(DeepComponentNamed(name, **items))

#     def removeDeepComponent(self, index: int):
#         """
#         Remove deep component at an index
#         """
#         if index < len(self._deepComponents):
#             self._deepComponents.pop(index)

#     def removeDeepComponents(self, indexes: list):
#         """
#         Remove deep components at indexes
#         """
#         if not indexes: 
#             return
#         self._deepComponents = [x for i, x in enumerate(self._deepComponents) if i not in indexes]

#     def addDeepComponent(self, deepComponent):
#         """
#         Add new deep component
#         """
#         self._deepComponents.append(deepComponent)

#     def append(self, item):
#         """
#         This function is made for backward compatibility
#         Add new deep component 
#         """
#         self.addDeepComponent(item)

#     def __repr__(self):
#         return str(self._deepComponents)

#     def __iter__(self):
#         for deepComponent in self._deepComponents:
#             yield deepComponent

#     def __getitem__(self, index):
#         assert isinstance(index, int)
#         return self._deepComponents[index]

#     def __setitem__(self, item, value):
#         setattr(self, item, value)

#     def __bool__(self):
#         return bool(self._deepComponents)

#     def getList(self):
#         """
#         Return a list reprensentation on the class
#         """
#         return [x._toDict() for x in self._deepComponents]

#     def _unnamed(self):
#         pass

# class Content(DictClass):

#     def __init__(self, outlines:list = [], deepComponents:list = [], width:int = 0):
#         super().__init__()
#         self.outlines = outlines
#         self.deepComponents = [DeepComponent(**dict(x)) for x in deepComponents]
#         self.width = width

#     def _writeOutlines(self, glyph):
#         """
#         Write the outlines instruction of the layer
#         """
#         pen = RecordingPen()
#         glyph.draw(pen)
#         self.outlines = pen.value

#     def _addDeepComponent(self, deepComponentInfos:dict = {}):
#         """
#         Add new deep Component
#         """
#         self.deepComponents.append(DeepComponent(**dict(deepComponentInfos)))

#     def _removeDeepComponent(self, index):
#         """
#         Remove a deep component at index
#         """
#         self.deepComponents.pop(index)

#     def _setAxisWidth(self, width:int = 0):
#         """
#         Set the axis width
#         """
#         self.width = width

#     def _toDict(self):
#         return {"outlines": self.outlines,
#                 "deepComponents": [x._toDict() for x in self.deepComponents],
#                 "width": self.width}

# class VariationGlyphsInfos:

#     def __init__(self, layerName:str = "", minValue:float = 0.0, maxValue:float = 1.0, content:dict = {}, axisMinValue:float=0., axisMaxValue:float=1.):
#         self.minValue = minValue
#         self.maxValue = maxValue
#         # self.axisMinValue = axisMinValue
#         # self.axisMaxValue = axisMaxValue
#         self.layerName = layerName
#         self.content = Content(**content)

#     def initContent(self, outlines = [], deepComponents = []):
#         """
#         Initialize the content with a given outlines and/or deep components
#         """
#         self.content = Content(outlines = outlines, deepComponents = deepComponents)

#     def addDeepComponent(self, deepComponentInfos:dict = {}):
#         """
#         Add new deep Component
#         """
#         self.content._addDeepComponent(deepComponentInfos)

#     def append(self, item):
#         """
#         made for backward compatibility
#         """
#         self.content._addDeepComponent(deepComponentInfos)

#     def removeDeepComponent(self, index):
#         """
#         Remove a deep component at index
#         """
#         self.content._removeDeepComponent(index)  

#     def removeDeepComponents(self, indexes):
#         """
#         Remove multiple deep components at indexes
#         """
#         for index in reversed(sorted(indexes)):
#             self.content._removeDeepComponent(index) 

#     def __repr__(self):
#         return str(self)

#     def __str__(self):
#         return str(self.__dict__)

#     def __getitem__(self, index):
#         return self.content.deepComponents[index]

#     def __setitem__(self, item, value):
#         setattr(self, item, value)

#     def items(self):
#         for x in vars(self):
#             yield (x, getattr(self, x))

#     def _toDict(self):
#         """
#         Return a dict representation 
#         """
#         return {
#                 "minValue": self.minValue, 
#                 "maxValue": self.maxValue, 
#                 # "axisMinValue": self.axisMinValue, 
#                 # "axisMaxValue": self.axisMaxValue, 
#                 "layerName": self.layerName,
#                 "content": self.content._toDict()
#                 }

#     def writeOutlines(self, glyph):
#         """
#         Write the outlines instruction of the layer
#         """
#         self.content._writeOutlines(glyph)

#     def setAxisWidth(self, width:int = 0):
#         """
#         Set the axis width
#         """
#         self.content._setAxisWidth(width)


# class VariationGlyphs(DictClass):

#     """
#     structure:
    
#     {
#         'VariationAxis0': {
#                             'min': 0.0, 
#                             'max': 1.0, 
#                             'content': {
#                                         'outlines': recordingPen.value, 
#                                         'deepComponents':[]
#                                         },
#                             'layerName': 'layerName'
#                             },
#         'VariationAxis1': {
#                             'min': 0.0, 
#                             'max': 1.0, 
#                             'content': {
#                                         'outlines': [], 
#                                         'deepComponents': [
#                                                             {
#                                                             'coord':{
#                                                                     DCAxisName: v, 
#                                                                     DCAxisName:v
#                                                                     }, 
#                                                             'x': v, 
#                                                             'y': v, 
#                                                             'scalex: v, 
#                                                             'scaley: v, 
#                                                             'rotation': v
#                                                             }
#                                                           ]
#                                         },
#                             'layerName': 'layerName'
#                             },
# }

#     """


#     def __init__(self, axes = {}):
#         super().__init__()
#         for k, v in axes.items():
#             if type(v) == list: # test for backward compatibility
#                 setattr(self, k, VariationGlyphsInfos())
#                 getattr(self, k).initContent(deepComponents = v)
#             elif type(v) == dict:
#                 setattr(self, k, VariationGlyphsInfos(**v))
#             else:
#                 setattr(self, k, VariationGlyphsInfos(v)) # fallback for backward compatibility

#     def __bool__(self):
#         return bool(vars(self))

#     def addAxis(self, axisName: str, deepComponents:list = [], layerName:str = "", minValue:float = 0.0, maxValue:float = 1.0):
#         """
#         Add new axis with no named deep components
#         """
#         infos = VariationGlyphsInfos(layerName = layerName, minValue = minValue, maxValue = maxValue)
#         for deepComponent in deepComponents:
#             infos.addDeepComponent(deepComponent._unnamed())
#         setattr(self, axisName, infos)

#     def removeAxis(self, axisName: str):
#         """
#         Remove a variation axis
#         """
#         if not hasattr(self, axisName):
#             return
#         delattr(self, axisName)

#     def addDeepComponent(self, deepComponent):
#         """
#         Add a new component to the whole axes
#         """
#         for x in vars(self):
#             getattr(self, x).addDeepComponent(deepComponent._unnamed())

#     def removeDeepComponents(self, indexes: list):
#         """
#         Remove components variation at indexes
#         """
#         if not indexes:
#             return
#         for x in vars(self):
#             getattr(self, x).removeDeepComponents(indexes)

#     def getDict(self):
#         """
#         Return a list reprensentation on the class
#         """
#         return {x: getattr(self, x)._toDict() for x in vars(self)}     

#     @property
#     def layerNames(self):
#         return [x.layerName for x in self.values()]
    

#     @property
#     def axes(self):
#         """
#         Return a list of all the variations axes
#         """
#         return self.keys()

#     @property
#     def infos(self):
#         """
#         Return a list of all the variations
#         """
#         return self.values()

# if __name__ == "__main__":
#     deepComponentTest = DeepComponents(
#         [{
#             'name': "53E3",
#             'coord': {'DIAG': 0.5}, 
#             'rotation': 0, 
#             'scalex': 0.02, 
#             'scaley': 0.07199999999999995, 
#             'x': 980, 
#             'y': 340
#         }])


#     deepComponentTest.add("test", {
#                     'coord': {'DIAG': 0.5}, 
#                     'rotation': 90, 
#                     'scalex': 0.02, 
#                     'scaley': 0.07199999999999995, 
#                     'x': 980, 
#                     'y': 340
#                     })
#     print("---")
#     print(deepComponentTest)
#     glyphVariationTest = VariationGlyphs()
#     glyphVariationTest.addAxis("wght", deepComponentTest)
#     glyphVariationTest.addAxis("slnt", deepComponentTest)
#     print("---")
#     print(glyphVariationTest)
#     glyphVariationTest.removeDeepComponents([0])
#     print("---")
#     print(glyphVariationTest)
#     print("---")
#     print(glyphVariationTest.getDict())
#     print("---")

#     glyphVariationTest1 = VariationGlyphs()
#     glyphVariationTest1.addAxis("axis2")
#     print(glyphVariationTest1.axis2.minValue)
#     glyphVariationTest1.axis2.minValue = 30
#     print(glyphVariationTest1.axis2.minValue)
#     glyphVariationTest1["axis2"].maxValue = 60
#     print(glyphVariationTest1.axis2)

class Axis:

    def __init__(self, name, minValue = 0, maxValue = 1):
        self.name = name
        self.minValue = minValue
        self.maxValue = maxValue

    # def __repr__(self):
    #     return "<"+str(vars(self))+">"

    def _toDict(self):
        return {x:getattr(self, x) for x in vars(self)}

class Axes(list):

    """
    This class refere to robocjk.axes key
    """

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

class Coord(dict):

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

class Transform(dict):

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
        self.rcenterx = rcenterx
        self.rcentery = rcentery
        self.rotation = rotation
        self.scalex = scalex
        self.scaley = scaley
        self.x = x
        self.y = y

class DeepComponent(dict):

    def __init__(self, 
            coord : dict = {}, 
            **kwargs
            ):
        super().__init__()
        self.coord = Coord(**dict(coord))
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
        self.coord = Coord(**dict(items['coord']))

    def _toDict(self, exception: str = ''):
        """
        Return a dict representation of the deep component datas.
        Allows to exclude an attribute in the dictionnary with exception
        """
        # d = {x:getattr(self, x) for x in vars(self) if x != exception}
        d = {}
        d["coord"] = {x:getattr(self.coord, x) for x in vars(self.coord)}
        d["transform"] = {x:getattr(self.transform, x) for x in vars(self.transform)}
        # print("DeepComponent ",d)
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
            yield deepComponent

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
        self.location = location #location is a dict specifiying the design space location {"wght":1, "wdth":1}
        self.layerName = layerName
        self.deepComponents = DeepComponents(deepComponents)

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

    def _init_with_old_format(self, data):
        for k, v in data.items():
            variation = dict(location = {k:v.get("maxValue")}, layerName = v.get("layerName"), deepComponents = v.get("content").get("deepComponents"))
            self.addAxis(variation)

    def addAxis(self, variation):
        self.append(VariationGlyphsInfos(**variation))
    
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

    def getDict(self):
        """
        Return a list reprensentation on the class
        """
        # return [x for x in self]
        return [x._toDict() for x in self]
        # return {x: getattr(self, x)._toDict() for x in vars(self)}     

    # @property
    def layerNames(self):
        return [x["layerName"] for x in self]
    

    @property
    def axes(self):
        """
        Return a list of all the variations axes
        """
        return self.keys()

    @property
    def infos(self):
        """
        Return a list of all the variations
        """
        return self.values()

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