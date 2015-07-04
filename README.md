Numerical properties for Python objects
=======================================

[![Travis Build Status](https://travis-ci.org/astrofrog/numprops.svg?branch=master)](https://travis-ci.org/astrofrog/numprops) [![Coverage Status](https://coveralls.io/repos/astrofrog/numprops/badge.svg)](https://coveralls.io/r/astrofrog/numprops)

About
-----

This simple module defines a descriptor class that can be used to define
numerical properties (scalar and n-dimensional arrays) on classes and provide a
way to validate these:

```python
from numprops import NumericalProperty

class Sphere(object):

    radius = NumericalProperty('radius', domain='strictly-positive', ndim=0)
    position = NumericalProperty('position', shape=(3,))
```
        
When a property is set, it will be validated:

```python
>>> s = Sphere()
>>> s.radius = 1.
>>> s.radius = -3
...
ValueError: radius should be strictly positive
>>> s.radius = [1,2]
...
TypeError: radius should be a scalar value
>>> s.position = (1,2,3)
>>> s.position = 3
...
TypeError: position should be a 1-d sequence
>>> s.position = (1,2,3,4)
...
ValueError: position has incorrect length (expected 3 but found 4)
```

The following arguments to ``NumericalProperty`` are available (in addition to the property name):

* ``ndim``: restrict the values to arrays with this number of dimension
* ``shape``: restrict the values to arrays with this shape. If specified, ``ndim`` does not need to be given.
* ``domain``: restrict the values to a particular domain - can be one of ``positive``, ``strictly-positive``, ``negative``, ``strictly-negative``, or a tuple representing a range of values.
* ``default``: the default value to return, if not specified (defaults to ``None``)
* ``convertible_to``: restrict the values to ones with units that would be convertible to a specific set of units (see section below)

Physical units
--------------

While ``NumericalProperty`` can be used for plain scalars and Numpy arrays, it
can also be used for scalars and arrays which have associated units, with support for three
popular unit handling units:
[astropy.units](docs.astropy.org/en/stable/units/),
[pint](http://pint.readthedocs.org/), and
[quantities](https://pythonhosted.org/quantities/).

To restrict a ``NumericalProperty`` to quantities with a certain type of unit,
use the ``convertible_to`` option. This option takes units from any of these
three unit packages, and will ensure that any value passed has units equivalent
(but not necessarily equal) to those specified with the ``convertible_to``
option.

If the units passed to ``convertible_to`` are
[astropy.units](docs.astropy.org/en/stable/units/) units, then any value passed
to the property should then be an
[astropy.units](docs.astropy.org/en/stable/units/) quantity. If the units
passed to ``convertible_to`` are [pint](http://pint.readthedocs.org/) units,
then any quantity passed to the property should be a
[pint](http://pint.readthedocs.org/) property. And finally if the units passed
to ``convertible_to`` are [quantities](https://pythonhosted.org/quantities/)
units, then any quantity passed to the property should be a
[quantities](https://pythonhosted.org/quantities/) quantity.

### astropy.units Quantity example

The following example shows how to restrict the ``radius`` property to be an
[astropy.units](docs.astropy.org/en/stable/units/) quantity in units of length:

```python
from astropy import units as u

class Sphere(object):
    radius = NumericalProperty('radius', convertible_to=u.m)
```

will then behave as follows:

```python
>>> s = Sphere()
>>> s.radius = 3. * u.m
>>> s.radius = 4. * u.cm
>>> s.radius = 4. * u.s
...
ValueError: radius should be in units convertible to m
```

### pint Quantity example

The following example shows how to restrict the ``radius`` property to be a
[pint](http://pint.readthedocs.org/) quantity in units of speed:

```python
from pint import UnitRegistry
ureg = UnitRegistry()

class Sphere(object):
    radius = NumericalProperty('radius', convertible_to=ureg.m)
```

will then behave as follows:

```python
>>> s = Sphere()
>>> s.radius = 3. * ureg.m
>>> s.radius = 4. * ureg.cm
>>> s.radius = 4. * ureg.s
...
ValueError: radius should be in units convertible to meter
```

### quantities Quantity example

Finally, the following example shows how to restrict the ``radius`` property to
be a [quantities](https://pythonhosted.org/quantities/) quantity in units of length:

```python
import quantities as pq

class Sphere(object):
    radius = NumericalProperty('radius', convertible_to=pq.m)
```

will then behave as follows:

```python
>>> s = Sphere()
>>> s.radius = 3. * pq.m
>>> s.radius = 4. * pq.cm
>>> s.radius = 4. * pq.s
...
ValueError: radius should be in units convertible to m
```

Planned support
---------------

* Linking of properties (e.g. a property should have the same dimensions as another)
