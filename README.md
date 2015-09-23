Numerical properties for Python objects
=======================================

[![Travis Build Status](https://travis-ci.org/astrofrog/numtraits.svg?branch=master)](https://travis-ci.org/astrofrog/numtraits) [![Coverage Status](https://coveralls.io/repos/astrofrog/numtraits/badge.svg)](https://coveralls.io/r/astrofrog/numtraits)

**Please note:** this package is experimental and may still see some changes to the API. If you have any suggestions for improving the API, please open an issue!

About
-----

This simple module defines a descriptor class that can be used to define
numerical properties (scalar and n-dimensional arrays) on classes and provide a
way to validate these. Thus, instead of writing something like:

```python
class Sphere(object):

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value <= 0:
            raise ValueError("Value should be strictly positive")
        if not np.isscalar(value):
            raise TypeError("Value should be a scalar")
        if not np.isreal(value):
            raise TypeError("Value should be numerical")
        self._radius = value
```

for each property you want to define, you can simply do:

```python
from numtraits import NumericalTrait
from traitlets import HasTraits

class Sphere(HasTraits):

    radius = NumericalTrait(domain='strictly-positive', ndim=0)
```

The ``NumericalTrait`` class is implemented on top of the [traitlets](https://github.com/ipython/traitlets)
module. Any class using ``NumericalTrait`` for the definition of a property **must** derive from the
``traitlets.HasTraits`` class.

Support is also included for checking the dimensionality and shape of arrays
(which includes converting tuples and lists to arrays on-the-fly), as well as
checking the units of quantities for the
[astropy.units](docs.astropy.org/en/stable/units/),
[pint](http://pint.readthedocs.org/), and
[quantities](https://pythonhosted.org/quantities/) unit frameworks.

Installing
----------

This package is compatible with Python 2.7, 3.3 and later, and
requires [numpy](http://www.numpy.org) and [traitlets](https://github.com/ipython/traitlets).
If you are interested in doing unit validation, you will also need
[astropy](docs.astropy.org/en/stable/units/),
[pint](http://pint.readthedocs.org/), or
[quantities](https://pythonhosted.org/quantities/), depending on which unit
framework you normally use.

To install, you can do:

    pip install numtraits

You can also bundle ``numtraits.py`` into your package if you want to avoid
using an external dependency, but please be sure to keep the copyright and the
license in the file.

Using
-----

To create self-validating numerical properties on a class, use the
``NumericalTrait`` class:

```python
from traitlets import HasTraits
from numtraits import NumericalTrait

class Sphere(HasTraits):

    radius = NumericalTrait(domain='strictly-positive', ndim=0)
    position = NumericalTrait(shape=(3,))
```

When a property is set, it will be validated:

```python
>>> s = Sphere()
>>> s.radius = 1.
>>> s.radius = -3
...
TraitError: radius should be strictly positive
>>> s.radius = [1,2]
...
TraitError: radius should be a scalar value
>>> s.position = (1,2,3)
>>> s.position = 3
...
TraitError: position should be a 1-d sequence
>>> s.position = (1,2,3,4)
...
TraitError: position has incorrect length (expected 3 but found 4)
```

The following arguments to ``NumericalTrait`` are available:

* ``ndim``: restrict the values to arrays with this number of dimension
* ``shape``: restrict the values to arrays with this shape. If specified, ``ndim`` does not need to be given.
* ``domain``: restrict the values to a particular domain - can be one of ``positive``, ``strictly-positive``, ``negative``, ``strictly-negative``, or a tuple representing a range of values.
* ``default``: the default value to return, if not specified (defaults to ``None``)
* ``convertible_to``: restrict the values to ones with units that would be convertible to a specific set of units (see section below)

Note that tuples and lists will automatically get converted to Numpy arrays, if they are considered valid.

Physical units
--------------

While ``NumericalTrait`` can be used for plain scalars and Numpy arrays, it
can also be used for scalars and arrays which have associated units, with support for three
popular unit handling units:
[astropy.units](docs.astropy.org/en/stable/units/),
[pint](http://pint.readthedocs.org/), and
[quantities](https://pythonhosted.org/quantities/).

To restrict a ``NumericalTrait`` to quantities with a certain type of unit,
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

class Sphere(HasTraits):
    radius = NumericalTrait(convertible_to=u.m)
```

will then behave as follows:

```python
>>> s = Sphere()
>>> s.radius = 3. * u.m
>>> s.radius = 4. * u.cm
>>> s.radius = 4. * u.s
...
TraitError: radius should be in units convertible to m
```

### pint Quantity example

The following example shows how to restrict the ``radius`` property to be a
[pint](http://pint.readthedocs.org/) quantity in units of length:

```python
from pint import UnitRegistry
ureg = UnitRegistry()

class Sphere(HasTraits):
    radius = NumericalTrait(convertible_to=ureg.m)
```

will then behave as follows:

```python
>>> s = Sphere()
>>> s.radius = 3. * ureg.m
>>> s.radius = 4. * ureg.cm
>>> s.radius = 4. * ureg.s
...
TraitError: radius should be in units convertible to meter
```

### quantities Quantity example

Finally, the following example shows how to restrict the ``radius`` property to
be a [quantities](https://pythonhosted.org/quantities/) quantity in units of length:

```python
import quantities as pq

class Sphere(HasTraits):
    radius = NumericalTrait(convertible_to=pq.m)
```

will then behave as follows:

```python
>>> s = Sphere()
>>> s.radius = 3. * pq.m
>>> s.radius = 4. * pq.cm
>>> s.radius = 4. * pq.s
...
TraitError: radius should be in units convertible to m
```

Planned support
---------------

* Linking of properties (e.g. a property should have the same dimensions as another)
