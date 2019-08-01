Changelog
=========


0.1.4 (2017-04-19)
------------------

Fix
~~~
- ``rgb2hsl`` would produce invalid hsl triplet when red, blue, green
  component would be all very close to ``1.0``. (fixes #30) [Valentin
  Lab]

  Typically, saturation would shoot out of range 0.0..1.0. That could then
  lead to exceptions being casts afterwards when trying to reconvert this
  HSL triplet to RGB values.


0.1.3 (2017-04-08)
------------------

Fix
~~~
- Unexpected behavior with ``!=`` operator. (fixes #26) [Valentin Lab]
- Added mention of the ``hex_l`` property. (fixes #27) [Valentin Lab]


0.1.2 (2015-09-15)
------------------

Fix
~~~
- Support for corner case 1-wide ``range_to`` color scale. (fixes #18)
  [Valentin Lab]


0.1.1 (2015-03-29)
------------------

Fix
~~~
- Avoid casting an exception when comparing to non-``Colour`` instances.
  (fixes #14) [Riziq Sayegh]


0.0.6 (2014-11-18)
------------------

New
~~~
- Provide all missing *2* function by combination with other existing
  ones (fixes #13). [Valentin Lab]
- Provide full access to any color name in HSL, RGB, HEX convenience
  instances. [Valentin Lab]

  Now you can call ``colour.HSL.cyan``, or ``colour.HEX.red`` for a direct encoding of
  ``human`` colour labels to the 3 representations.


0.0.5 (2013-09-16)
------------------

New
~~~
- Color names are case insensitive. [Chris Priest]

  The color-name structure have their names capitalized. And color names
  that are made of only one word will be displayed lowercased.

Fix
~~~
- Now using W3C color recommandation. [Chris Priest]

  Was using X11 color scheme before, which is slightly different from
  W3C web color specifications.
- Inconsistency in licence information (removed GPL mention). (fixes #8)
  [Valentin Lab]
- Removed ``gitchangelog`` from ``setup.py`` require list. (fixes #9)
  [Valentin Lab]


0.0.4 (2013-06-21)
------------------

New
~~~
- Added ``make_color_factory`` to customize some common color
  attributes. [Valentin Lab]
- Pick color to identify any python object (fixes #6) [Jonathan Ballet]
- Equality support between colors, customizable if needed. (fixes #3)
  [Valentin Lab]


0.0.3 (2013-06-19)
------------------

New
~~~
- Colour is now compatible with python3. [Ryan Leckey]


0.0.1 (2012-06-11)
------------------
- First import. [Valentin Lab]


