"""
Copyright 2019 Black Foundry.

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


class InjectBack():

    def __init__(self, interface):
        self.ui = interface
        self.rdir = self.ui.projectPath
        self.injectBack()

    def writeJsonFile(self, name):
        path = os.path.join(self.rdir, f"resources/{name}.json")
        makepath(path)
        myFile = open(path, 'w')
        d = json.dumps(getattr(self, name), indent=4, separators=(',', ':'))
        myFile.write(d)
        myFile.close()

    def injectBack(self):
        git = GitHelper(self.rdir)
        git.pull()
        user = git.user()

        dt = datetime.datetime.today()
        stamp = list(self.ui.fonts.keys())[0].split("-")[1]

        WIPPath = os.path.join(self.rdir, "resources/WIP_DCEditor.json")
        self.WIP_DCEditor = json.load(open(WIPPath, "r"))

        fontsLinkPath = os.path.join(self.rdir, "Temp/Fonts_Link.json")
        self.Fonts_Link = json.load(open(fontsLinkPath, "r"))

        fontsList = []
        fonts = {}
        font2Storage = {}

        for tempFontName, tempFont, in self.ui.fonts.items():

            fontName = self.Fonts_Link["linkFontsName"][tempFontName]
            fontPath = self.ui.projectPath + "/Design/%s.ufo"%fontName
            font = OpenFont(fontPath, showUI = False)

            storageTempFontName = self.Fonts_Link["font2storage"][tempFontName]

            storageFontName = self.Fonts_Link["linkFontsName"][storageTempFontName]
            storageFontPath = self.ui.projectPath + "/Storage/%s.ufo"%storageFontName
            storageFont = OpenFont(storageFontPath, showUI = False)

            for glyph in tempFont:
                font[glyph.name] = glyph

            for glyph in self.ui.font2Storage[tempFont]:
                storageFont.newGlyph(glyph.name)
                storageFont[glyph.name] = glyph

                for layer in glyph.layers:
                    if layer.layerName not in [layer.name for layer in storageFont.layers]:
                        storageFont.newLayer(layer.layerName)
                        storageFont.getLayer(layer.layerName).insertGlyph(layer)

            if "deepComponentsGlyph" in self.ui.font2Storage[tempFont].lib:
                if "deepComponentsGlyph" not in storageFont.lib:
                    storageFont.lib['deepComponentsGlyph'] = {}
                for k, v in self.ui.font2Storage[tempFont].lib['deepComponentsGlyph'].items():
                    storageFont.lib['deepComponentsGlyph'][k] = v

            fontsList.append(fontName)
            fonts[fontName] = font
            font2Storage[font] = storageFont

            font.save()
            storageFont.save()

        self.ui.fontList = fontsList
        self.ui.fonts = fonts
        self.ui.font2Storage = font2Storage

        self.ui.font = fonts[fontsList[0]]

        self.ui.glyphsSetDict = {font: [dict(Name = name, Char = chr(int(name[3:],16)) if name.startswith('uni') else "") for name in font.lib['public.glyphOrder']] for font in self.ui.fonts.values()}

        git.commit('DONE: ' + stamp)
        git.push()

        self.ui._setUI()
        self.ui.w.fontsGroup.fonts_list.setSelection([0])
        self.ui.w.fontsGroup.injectBack.show(False)
        self.ui.w.fontsGroup.getMiniFont.show(True)

        shutil.rmtree(self.ui.projectPath+'/Temp')

        del self.WIP_DCEditor[stamp]
        self.writeJsonFile("WIP_DCEditor")
