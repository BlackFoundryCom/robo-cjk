# Proposal for Deep Component support in Variable Fonts

# This document is now historical, see [github.com/BlackFoundryCom/variable-components-spec](https://github.com/BlackFoundryCom/variable-components-spec)

## **1. Motivation & problem statement**

CJK (Chinese, Japanese and Korean) fonts include a very large number of encoded compulsory glyphs. For example a Simplified Chinese font contains at the very least more than 6,700 Hanzi Glyphs. A traditional Chinese for Hong Kong or Taiwan will include more than 21,000 hanzi glyphs, a Korean font contains at least 2,350 Hangul glyphs and up to 11,172 Hangul glyphs to cover the full Unicode range, and simple Japanese font has a couple of hundreds Kana glyphs but also needs to have the minimum of 6,000 Kanji glyphs. These numbers can grow depending on the desired exhaustiveness of the font.

These fonts present challenges to the digital type industry for 2 main reasons:
    - The designing of the glyphs set is long, requires a team of designers and it is difficult to match quality, consistency, and deadlines.
    - The binary fonts have a tendency to become heavy files, file sizes of 5Mb to 20Mb is common.

Most Hanzi and Hangul glyphs are made of a smaller number of elements that are repeated with more or less distortions to their proportions.

Having previous experience in designing CJK fonts with the existing technologies, we came up with a few ideas on how to improve the current situation, make our work easier and better.


## **2. The difficulty to design**

Building up CJK binary fonts with available technologies will always imply heavy files for high quality designs. If a lighter file size is prevalent, the quality of the design is often sacrificed. The designing part itself requires a team that in addition to being well trained needs common design guidelines and ways to work collaboratively on the same project.

We aim to solve both the font engineering and the typeface design issues at once with:

    - A novel working file structure that factorizes the smaller elements into variable glyphs
    
    - A way to embed the most of this working source file data structure into the binary fonts to keep them as compact as possible

## **3. Criteria (what's in scope and what's not)**

We will not assess the collaborative team workflow in this proposal but only focus on the possible binary file structure and its source file structure before compilation. However we propose tooling for the collaborative part in the Robo-CJK RoboFont extension as we see it as essential to carry out such projects. 

The point of the proposal is to make CJK font structure more efficient -or simply possible-, to enable more type-designers and foundries to undertake the design CJK fonts. 
What is in scope is only about enabling the making of such fonts, making their file size lighter, or simply possible to compile. 

The usage of components and composite glyphs in TrueType fonts is both a real file-size saver (factoring the elements of a typeface design) and an efficient tool for type-designers (ie. using the same outline for glyph ‘e’ and all its accented versions) despite the fact that it eventually implies _more_ glyphs in the font (ie. the accents are separated glyphs that are not really needed alone).

In CJK fonts, the factored elements require more transformation than the usual 2-dimensional shift needed in most other writing systems. We cannot either be satisfied with a transformation matrix (shift, scale, rotation) alone as this destroys important characteristics of the design (like weight, contrast, balance…). These elements (or components) need to be variable in order to respect the integrity of the design.

In addition, the limit of 65,535 glyphs in OpenType fonts can actually be reached. In any case it should be a goal to keep the number of unmapped glyphs low. By this we mean that the number of traditional components (shallow components) needed to make the ‘Character Glyphs’ (codepoint glyph, or actual characters) can become very high. Our goal is to make the number of required components glyphs smaller by making them variable (Deep Components) and we shall propose a mechanism to do so.
For type-designers the most important is to have access to such mechanisms in their source files; whether it is supported natively in the binary fonts and by rasterizers does not matter so much. However we believe that if such a mechanism exists, it is a good opportunity to try making it available to binary fonts instead of flattening the whole design to outline glyphs and get rid of these variable components before compilation, or worse flattening all their instances to traditional (shallow) components that can represent a huge quantity of unmapped glyphs. Less unmapped component glyphs means more room for mapped character glyph, and should also bring smaller file size.


## **4. Rough solution space and tradeoffs**

We made several trials before coming up to this proposal. Inner-font glyph variability seemed a must-have for ensuring design consistency amongst a team of several designers. Glyphs’ component variability is a key feature of Han-based typeface design (Hanzi, Kanji, Hanja), we can take advantage of it. A tradeoff with our first experiments was the loss in quality because of the basic linear interpolation we were using. We tried to combine linear and non-linear interpolations but the control of the latter was complex and sometimes counterintuitive.

Moreover, the current state of OpenType 1.8 that brought Variable Fonts to life has a tradeoff: components’ deltas only support shifting (X and Y) while TrueType specifications previously specified a possible 2 x 2 matrix transformation. We think the reason for this regression is that interpolation of such transformation matrices is a complex task that was avoided. For this reason we propose to split it into 3 isolated values: shift, scale, rotation, so that we can process with simple interpolation of these values between design-space masters. Existing font’s component transformations (shift, scale, and rotation) provide us with sufficient variability precision when combined with linear interpolation. 
Non-linear interpolation can also be, in some cases, an interesting asset for better control of the design, but for the sake of simplicity of this proposal we do not cover it. 

The main goal is to propose:

    - a 3 levels structure of nested variable components glyph within the font.
    
    - the introduction of 3 values (shift, scale, and rotation) that can be linearly interpolated for components.
    
## **5. Proposed solution and why it was picked / is good**

The proposed solution shall attempt to make maximum use of the existing in OpenType specifications. We don’t want, however, to limit the field of possibilities for the sake of backward compatibility. 

**TRANSFORMATIONS:**

We want to highlight that fact that isolating the existing matrix transformation into 3 (interpolatable) values (shift, scale, rotation) shall bring a much higher level of control and design possibilities without requiring the complex non-linear interpolation.
This would be a relatively simple update to the current specifications and bring Variable Fonts to a next level in itself. It is a key to the success of the Deep-Components strategy we are detailing below.

**INTERPOLATIONS:**

All interpolations used in our mechanisme are serial interpolations, meaning each variation ‘layer’ impacts the origin master equally. For example we can have a full size master with one ‘narrow’ master and one ‘flat’ master, that can be combined to give a ‘flat+narrow’ interpolation. We like to call this kind of serial interpolation ‘deepolation’ because it means one doesn’t need to design all extremes of the design-space to cover all possibilities. We have tested this in traditional variable fonts (OT V1.8) and proved it works; the only requirement is to link the same master to the origin of each axis. This unframed system enables some sort of extrapolation to happen within the existing specifications.

**NESTING:**

The proposed nested system is articulated like this:

```Atomic Element -> Deep Component -> Character Glyph```

(CG is composed of DC, DC is composed of AE, AE is variable glyph)

We think it is beneficial to split Deep Components into smaller elements constituting the ‘core’ of the typeface design, because they are repeated many times with identified variations. This ensures that they keep the same design features while being flexible through interpolation, and transformations. We name these smaller elements ‘Atomic Elements’. AE are made of outline nodes and deltas. Deep Components (DC) are made of AE, instantiated with interpolation coordinates, and transformations (shift, scale, rotation). Character Glyphs (mapped glyph) remain compatible with traditional Variable Fonts controlled by the <fvar> table. Deep Components and Atomic Elements may have their own inner behaviour to bring the maximum of their possibilities.

**ATOMIC ELEMENT:**

The Atomic Element (AE) is a traditional glyph (as defined by the ```<glyf>``` table): contours in a <TTGlyph> item:

example:
```
<glyf>
    <TTGlyph name="atomicElementGlyph">
        <contour></contour> # Contour points description
    </TTGlyph>
</glyf>
```

Associated with a gvar-like table (let’s name it ```<aevr>``` ‘atomic elements variations’ for now), it becomes a Variable Glyph, a master associated with interpolatable ‘layers’ that represent variations. AE delta variations use a similar structure as the current ```<gvar>``` table because both define node positions deltas; however it is not certain the AE delta variations can be stored in the same named table as traditional glyph variations. We might need another table for the sake of clarity.

example:
```
<aevr>
    <glyphVariations glyph="atomicElementGlyph">
    <tuple>
        <coord axis="aeLONG" value="1.0"/> # Named axis descriptor 
        <delta/> # List of deltas for the Atomic Element's contour points
    </tuple>
    <tuple>
        <coord axis="aeTHCK" value="0.0"/> # Named axis descriptor 
        <delta/> # List of deltas for the Atomic Element's contour points
    </tuple>
</aevr>
```

The axes definition of AE (its design space) could be stored in an ‘atomic-element variation axis’ table (```<aeva>```) instead of ```<fvar>``` because it is never accessed by the users; it is also important to note that no default value is needed here since it is always instantiated in context. 

example:
```
<aeva>
    <axes glyph="atomicElementGlyph"> 
        <axis name="aeLONG" minValue="10.0" maxValue="1000.0"/>
        <axis name="aeTHCK" minValue="53.0" maxValue="167.0"/>
    </axes>
</aeva>
```

With these AE we can shape basic strokes behaviour for Hanzi or Hangul.

**DEEP COMPONENT:**

The Deep Component (DC) instantiates Atomic Elements as components and applies transformations (shift, scale, and rotation) to them as well as defining coordinates in the Atomic Element’s design space. We propose to use the Glyph Header’s ‘numberOfContours’ with a value of -2 to indicate this is a ‘deep-component’ (the value of -1 being used for traditional composite glyphs)

example:
```
<glyf>
    <TTGlyph name="deepComponentGlyph", numberOfContours="-2">
        <atomicElement glyphName="atomicElementGlyph" x="775" y="110" scalex="1" scaley="1" rotation="-4.5" >
            <coord axis="aeLONG" value="378.0"/>
            <coord axis="aeTHCK" value="78.0"/>
        </atomicElement>
        <atomicElement glyphName="atomicElementGlyph" x="100" y="66" scalex="1" scaley="1" rotation="0.0" >
            <coord axis="aeLONG" value="759.0"/>
            <coord axis="aeTHCK" value="84.0"/>
        </atomicElement>
        <atomicElement glyphName="atomicElementGlyph" x="100" y="66" scalex="1" scaley="1" rotation="-0.5" >
            <coord axis="aeLONG" value="121.0"/>
            <coord axis="aeTHCK" value="77.0"/>
        </atomicElement>
    </TTGlyph>
</glyf>
```

We are aware that the current ```<gvar>``` table cannot be used for DC deltas because it defines _nodes_ deltas where DC only uses axes coordinate deltas.
The Deep Component has ‘layers’ (or axes) defined in a gvar-like table (named here ```<dcvr>```), but instead of having node deltas, we have AE axis-coordinates deltas.
The same interpolation principles as the Atomic Element are applied: one unique master is the origin of each axis enabling the so-called ‘deepolation’ that combines the transformations generated by each variation master. 

example:
```
<dcvr>
    <glyphVariations glyph="deepComponentGlyph">
    <tuple>
        <coord axis="dcVWGT" value="1.0"/>
        <delta pt="0" x="785" y="90" scalex="1", scaley="1", rotation="-17.5">
            <coord axis="aeLONG" value="378.0"/>
            <coord axis="aeTHCK" value="124.0"/>
        </delta>
        <delta pt="1" x="100" y="66" scalex="1", scaley="1", rotation="-20.5">
            <coord axis="aeLONG" value="759.0"/>
            <coord axis="aeTHCK" value="84.0"/>
        </delta>
        <delta pt="2" x="216" y="242" scalex="1", scaley="1", rotation="-0.5">
            <coord axis="aeLONG" value="121.0"/>
            <coord axis="aeTHCK" value="113.0"/>
        </delta>
    </tuple>
    <tuple>
        <coord axis="dcHWGT" value="1.0"/>
        <delta pt="0" x="495" y="50" scalex="1", scaley="1", rotation="-12.0">
            <coord axis="aeLONG" value="378.0"/>
            <coord axis="aeTHCK" value="78.0"/>
        </delta>
        <delta pt="1" x="100" y="66" scalex="1", scaley="1", rotation="0.0">
            <coord axis="aeLONG" value="759.0"/>
            <coord axis="aeTHCK" value="148.0"/>
        </delta>
        <delta pt="2" x="100" y="66" scalex="1", scaley="1", rotation="13.5">
            <coord axis="aeLONG" value="121.0"/>
            <coord axis="aeTHCK" value="110.0"/>
        </delta>
    </tuple>
</dcvr>
```

With these DC we can build basic keys for Hanzi or Hangul writing systems, the combination of strokes that make ‘keys’ or ‘radicals’– note that this proposed structure DC made of AE is particularly relevant for Hanzi writing system while Hangul that has less variety of shape might in some cases merge the two notions of AE and DC. But even in the case of Hangul, the use of rotation (plus shift and scale) can save some file size by using the same AE for both horizontal and vertical stems, for example. The idea being to factorize as much as possible the root element of these stroke-based writing systems. Of course this is design dependent and a Gothic style may take more advantage of this system than a calligraphic style. 

The axis definition of DC may be stored in a new ‘deep-component variation axis’ table (```<dcva>```) since it never has to be accessed at the font’s level. Like AE, no default value is required because the instantiation of DC will always be dependent on the context of the Character Glyph that uses it.


example:
```<dcva>
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
</dcva>
```

**CHARACTER GLYPH:**

The Character Glyph (CG) is the final piece of the chain. It makes use of DC that uses AE. It may also be interesting -in some cases- to use directly AE into CG for some simple situations where the added value of an intermediate DC is not needed. A CG instantiates one or more Deep Components at a given position of its design space with the additional possibility to apply shift, scale, and rotation to it. This instantiation gives a glyph shape to actual characters, with potentially associated code-points in ```<cmap>```. Again CG can have variation axes, but this time at the actual font level (defined in ```<fvar>```), they can be standard like ‘wght’, ‘opsz’, …, or any custom name. From the user perspective only these axes are visible and usable –unlike those of AE and DC that are only defined and used by the designers of the font. This makes CG glyphs, a novel type of glyph that can be seen as ‘deep-composites’ (made of Deep Components). We propose to use the Glyph Header’s ‘numberOfContours’ with a value of -3 to indicate this is a ‘deep-composite’ (the value of -1 being used for traditional composite glyphs, and -2 for DC). A rasterizer that sees the -3 value will attempt to access the axes of the DCs that make this CG, then will access the axes of the AEs making this DC.

example:
```
<glyf>
    <TTGlyph name="characterGlyph" numberOfContours="-3">
      <deepComponent glyphName="deepComponentGlyph" x="0" y="0" scalex="1" scaley="1" rotation="0.0" >
        <coord axis="dcVWGT" value="1.0"/>
        <coord axis="dcHWGT" value="0.0"/>
      </atomicElement>
      <deepComponent glyphName="deepComponentGlyph" x="-600" y="0" scalex="1" scaley="1" rotation="0.0" >
        <coord axis="dcVWGT" value="0.292"/>
        <coord axis="dcHWGT" value="1.0"/>
      </atomicElement>
      <deepComponent glyphName="deepComponentGlyph" x="-30" y="480" scalex="0.5" scaley="0.5" rotation="0.0" >
        <coord axis="dcVWGT" value="0.0"/>
        <coord axis="dcHWGT" value="0.0"/>
      </atomicElement>
    </TTGlyph>
</glyf>
```

The case where AEs are used directly in CG is not modelled yet –it could simply be a mapped DC. 

We are aware that the current ```<gvar>``` table cannot be used for CG deltas because it defines _nodes_ deltas where CG only uses axes positions deltas. So we name this gvar-like table ```<cgvr>```. It contains the axes definitions of the font with the DC coordinate deltas for each CG.

example:
```
<cgvr>
    <glyphVariations glyph="characterGlyph">
      <tuple>
        <coord axis="wght" value="1.0"/>
        <delta pt="0" x="0" y="0" scalex="1", scaley="1", rotation="0.0">
            <coord axis="dcVWGT" value="0.838"/>
            <coord axis="dcHWGT" value="0.196"/>
        </delta>
        <delta pt="0" x="-600" y="0" scalex="1", scaley="1", rotation="0.0">
            <coord axis="dcVWGT" value="0.292"/>
            <coord axis="dcHWGT" value="0.732"/>
        </delta>
        <delta pt="0" x="-30" y="480" scalex="0.5", scaley="0.5", rotation="0.0">
            <coord axis="dcVWGT" value="0.0486"/>
            <coord axis="dcHWGT" value="0.137"/>
        </delta>
        <delta pt="3" x="0" y="0"/>
        <delta pt="4" x="0" y="0"/>
        <delta pt="5" x="0" y="0"/>
        <delta pt="6" x="0" y="0"/>
      </tuple>
    </glyphVariations>
</cgvr>
```

Finally, at the font level the usual ```<fvar>``` table defines the font’s axes.

example:
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

**TABLES STRUCTURE SUMMARY:**
```
AE: <glyf> + <aeva> + <aevr>
DC: <glyf> + <dcva> + <dcvr>
CG: <glyf> + <cgva> + <fvar>
```

## **6. Notes and Conclusions**

There would be no use of the current ```<gvar>``` table but the ```<aevr>``` table would be very similar.

We would also need a mechanism to tell the ```<fvar>``` table to look into the ```<cgvr>``` table in addition to <gvar>

The question of how to store the transformations remains open. We think the existing 2 x 2 matrix is not ideal because it makes interpolations of the values uneasy. 
We propose to store each transformation separately:

shift-x: integer (default 0)

shift-y: integer (default 0)

scale-x: float (default 1.0)

scale-y: float (default 1.0)

rotation-angle: float (default 0.0)


One issue is that the transformation data structure is not supported in the current ```<glyf>``` table (with the exception of shifts) and scale+rotation is redundant with the existing 2x2 matrix. Whether the table should be updated or if we would need another specific table is not clear. Perhaps the ‘numberOfContours’ value set to -2 (for DC) or -3 (for CG) could be enough to tell the rasterizer to access these extra informations.

More testing and prototyping would be needed to evaluate the actual file size saving because despite the fact much less contour nodes need to be stored, the proposal implies extra data to store axes definitions and instantiate the nested elements.

We would also need to prototype a rasterizer to evaluate the performance of these live chained interpolations in actual context.


