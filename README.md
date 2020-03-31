# robo-cjk
**User Guide:**
https://blackfoundrycom.github.io/black-robo-cjk/index.html

**Dependancies:**
Drawbot RoboFont Extension (for PDF proof generation)
https://github.com/typemytype/drawBotRoboFontExtension

**Deep Component binary structure proposal:**
We propose an update to the data structure of OpenType Variable fonts.
We use variable Atomic Elements glyphs that have each their own design-space. 
Atomic Elements behave like component glyphs that can be instantiated at a given position of their design-space into Deep Components glyphs.
Deep Component glyphs also have their own design-space and behave like components for Character Glyphs in which they are instanciated at a given position of their own design-space.
Character Glyphs are 'composite glyphs' made of Deep Components instanciated.

This chart shows how existing data structure of Open Type 1.8 specifications ('glyf', 'gvar' and 'fvar' tables) can be used as a base for this new technology in updated specification.

## Binary Data Structure
![Binary Data Structure](/documentation/DeepComponentBinaryStructure.gv.svg)

In this scheme default values for axis variations are not relevant because every instanciation of Atomic Element or Deep Component is relative and specific to its usage context.

### Atomic Element Example
Mostly behave like a usual glyph in a Variable Font
```
<glyf>
    <TTGlyph name="atomicElementGlyph">
        <contour></contour> # Contour points description
    </TTGlyph>
</glyf>
```

```
<gvar>
    <glyphVariations glyph="atomicElementGlyph">
    <tuple>
        <coord axis="aeLONG" value="1.0"/> # Named axis descriptor 
        <delta/> # List of deltas for the Atomic Element's contour points
    </tuple>
    <tuple>
        <coord axis="aeTHCK" value="1.0"/> # Named axis descriptor 
        <delta/> # List of deltas for the Atomic Element's contour points
    </tuple>
</gvar>
```

```
<fvar>
    <Axis>
        <AxisTag>aeLONG</AxisTag>
        <MinValue>0.0</MinValue>
        <MaxValue>1.0</MaxValue>
    </Axis>
    <Axis>
        <AxisTag>aeTHCK</AxisTag>
        <MinValue>0.0</MinValue>
        <MaxValue>1.0</MaxValue>
    </Axis>
</fvar>
```

### Deep Component Example
Special glyphs behaving a bit like composite glyphs but using instanciated Atomic Element with _scale_, _rotation_ and _axis coordinates_ for the instanciation.
```
<glyf>
    <TTGlyph name="deepComponentGlyph">
        <atomicElement glyphName="atomicElementGlyph" x="775" y="110" scalex="1" scaley="1" rotation="-4.5" >
            <coord axis="aeLONG" value="0.3037138353115727"/>
            <coord axis="aeTHCK" value="0.3"/>
        </atomicElement>
        <atomicElement glyphName="atomicElementGlyph" x="100" y="66" scalex="1" scaley="1" rotation="0.0" >
            <coord axis="aeLONG" value="0.5842104043026706"/>
            <coord axis="aeTHCK" value="0.21369158011869435"/>
        </atomicElement>
        <atomicElement glyphName="atomicElementGlyph" x="100" y="66" scalex="1" scaley="1" rotation="-0.5" >
            <coord axis="aeLONG" value="0.72265625"/>
            <coord axis="aeTHCK" value="0.28"/>
        </atomicElement>
    </TTGlyph>
</glyf>
```

Deep Components themselves also have Axis descriptors containing specific delta coordinates for the Atomic Elements variations.
```
<gvar>
    <glyphVariations glyph="deepComponentGlyph">
    <tuple>
        <coord axis="dcVWGT" value="1.0"/>
        <delta pt="0" x="785" y="90" scalex="1", scaley="1", rotation="-17.5">
            <coord axis="aeLONG" value="0.11199462166172107"/>
            <coord axis="aeTHCK" value="0.3"/>
        </delta>
        <delta pt="1" x="100" y="66" scalex="1", scaley="1", rotation="0.0">
            <coord axis="aeLONG" value="0.5842104043026706"/>
            <coord axis="aeTHCK" value="0.21369158011869435"/>
        </delta>
        <delta pt="2" x="100" y="66" scalex="1", scaley="1", rotation="-20.5">
            <coord axis="aeLONG" value="0.3654719955489614"/>
            <coord axis="aeTHCK" value="0.14790430267062316"/>
        </delta>
        <delta pt="3" x="216" y="242" scalex="1", scaley="1", rotation="-0.5">
            <coord axis="aeLONG" value="0.09785330118694362"/>
            <coord axis="aeTHCK" value="0.1620572143916914"/>
        </delta>
    </tuple>
    <tuple>
        <coord axis="dcHWGT" value="1.0"/>
        <delta pt="0" x="495" y="50" scalex="1", scaley="1", rotation="-12.0">
            <coord axis="aeLONG" value="0.1346323256676558"/>
            <coord axis="aeTHCK" value="0.3"/>
        </delta>
        <delta pt="1" x="100" y="66" scalex="1", scaley="1", rotation="0.0">
            <coord axis="aeLONG" value="0.13735626854599406"/>
            <coord axis="aeTHCK" value="0.21369158011869435"/>
        </delta>
        <delta pt="2" x="100" y="66" scalex="1", scaley="1", rotation="13.5">
            <coord axis="aeLONG" value="0.5108725890207715"/>
            <coord axis="aeTHCK" value="0.2507418397626113"/>
        </delta>
        <delta pt="3" x="116" y="442" scalex="1", scaley="1", rotation="-0.5">
            <coord axis="aeLONG" value="0.0011823071216617211"/>
            <coord axis="aeTHCK" value="0.18870548961424333"/>
        </delta>
    </tuple>
</gvar>
```

```
<fvar>
    <Axis>
        <AxisTag>dcVWGT</AxisTag>
        <MinValue>0.0</MinValue>
        <MaxValue>1.0</MaxValue>
    </Axis>
    <Axis>
        <AxisTag>dcHWGT</AxisTag>
        <MinValue>0.0</MinValue>
        <MaxValue>1.0</MaxValue>
    </Axis>
</fvar>
```

### Character Glyph Example
Actual glyphs mapped to codepoints using instanciated Deep Components with _scale_, _rotation_ and _axis coordinates_ for the instanciation.
```
<glyf>
    <TTGlyph name="characterGlyph">
      <deepComponent glyphName="deepComponentGlyph" x="0" y="0" scalex="1" scaley="1" rotation="0.0" >
        <coord axis="dcVWGT" value="1.0"/>
        <coord axis="dcHWGT" value="0.0"/>
      </atomicElement>
      <deepComponent glyphName="deepComponentGlyph" x="-600" y="0" scalex="1" scaley="1" rotation="0.0" >
        <coord axis="dcVWGT" value="0.29153143545994065"/>
        <coord axis="dcHWGT" value="1.0"/>
      </atomicElement>
      <deepComponent glyphName="deepComponentGlyph" x="-30" y="480" scalex="0.5" scaley="0.5" rotation="0.0" >
        <coord axis="dcVWGT" value="0.0"/>
        <coord axis="dcHWGT" value="0.0"/>
      </atomicElement>
    </TTGlyph>
</glyf>
```

Character Glyphs themselves also have Axis descriptors containing specific delta coordinates for the Deep Components variations.
```
<gvar>
    <glyphVariations glyph="characterGlyph">
      <tuple>
        <coord axis="wght" value="1.0"/>
        <delta pt="0" x="0" y="0" scalex="1", scaley="1", rotation="0.0">
            <coord axis="dcVWGT" value="0.8377689169139466"/>
            <coord axis="dcHWGT" value="0.19598479228486648"/>
        </delta>
        <delta pt="0" x="-600" y="0" scalex="1", scaley="1", rotation="0.0">
            <coord axis="dcVWGT" value="0.29153143545994065"/>
            <coord axis="dcHWGT" value="0.7314424146884273"/>
        </delta>
        <delta pt="0" x="-30" y="480" scalex="0.5", scaley="0.5", rotation="0.0">
            <coord axis="dcVWGT" value="0.048578913204747776"/>
            <coord axis="dcHWGT" value="0.13664920252225518"/>
        </delta>
        <delta pt="3" x="0" y="0"/>
        <delta pt="4" x="0" y="0"/>
        <delta pt="5" x="0" y="0"/>
        <delta pt="6" x="0" y="0"/>
      </tuple>
    </glyphVariations>
</gvar>
```

Finaly, the font's FVAR table hosts the actual font variations axis (registered or custom) as described by OT 1.8 specifications. It can be noted that here the default value is relevant as with traditional Variable Fonts.
```
<fvar>
    <Axis>
        <AxisTag>wght</AxisTag>
        <MinValue>0.0</MinValue>
        <DefaultValue>0.0</DefaultValue>
        <MaxValue>1.0</MaxValue>
    </Axis>
</fvar>
```
