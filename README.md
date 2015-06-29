Numerical properties for Python objects
=======================================

[![Travis Build Status](https://travis-ci.org/astrofrog/numprops.svg?branch=master)](https://travis-ci.org/astrofrog/numprops)

About
-----

This simple module defines a descriptor class that can be used to define
numerical properties (scalar and n-dimensional arrays) on classes and provide a
way to validate these:

```python
from numprops import NumericalProperty

class Source(object):

    radius = NumericalProperty('radius', domain='strictly-positive')
    position = NumericalProperty('position', shape=(3,))
```
        
When a property is set, it will be validated:

    >>> s = Source()
    >>> s.radius = 1.
    >>> s.radius = -3
    ...
    ValueError: radius should be strictly positive
    >>> s.position = (1,2,3)
    >>> s.position = 3
    ...
    TypeError: position should be a 1-d sequence
    >>> s.position = (1,2,3,4)
    ...
    ValueError: position has incorrect length (expected 3 but found 4)
    
Planned support
---------------

* Linking of properties (e.g. a property should have the same dimensions as another)
* Validation of physical types (for example using ``astropy.units`` or ``quantities``)
