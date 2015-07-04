import numpy as np

from weakref import WeakKeyDictionary


def is_scalar(value):
    return np.isscalar(value) and (not hasattr(value, 'shape') or value.shape != ())


class NumericalProperty(object):

    def __init__(self, name, ndim=None, shape=None, domain=None,
                 default=None, convertible_to=None):

        self.name = name
        self.domain = domain

        if shape is not None:
            if ndim is None:
                ndim = len(shape)
            else:
                if ndim != len(shape):
                    raise ValueError("shape={0} and ndim={1} are inconsistent".format(shape, ndim))

        self.ndim = ndim
        self.shape = shape

        self.default = default
        self.target_unit = convertible_to

        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance, self.default)

    def __set__(self, instance, value):

        is_scalar = np.isscalar(value) and (not hasattr(value, 'shape') or value.shape != ())

        if is_scalar:
            if not np.isreal(value):
                raise TypeError("{0} should be a numerical value".format(self.name))
        else:
            try:
                value = np.array(value, dtype=float, subok=True)
            except Exception as exc:
                raise TypeError("Could not convert value of {0} to a Numpy array (Exception: {1})".format(self.name, exc))

        if self.ndim is not None:

            if self.ndim == 0:
                if not is_scalar:
                    raise TypeError("{0} should be a scalar value".format(self.name))

            if self.ndim > 0:
                if is_scalar or value.ndim != self.ndim:
                    if self.ndim == 1:
                        raise TypeError("{0} should be a 1-d sequence".format(self.name))
                    else:
                        raise TypeError("{0} should be a {1:d}-d array".format(self.name, self.ndim))

        if self.shape is not None:

            if isinstance(self.shape, str):
                if getattr(instance, self.shape) is None:
                    expected_shape = None
                else:
                    expected_shape = getattr(instance, self.shape).shape
            else:
                expected_shape = self.shape

            if expected_shape is not None and np.any(value.shape != expected_shape):
                if self.ndim == 1:
                    raise ValueError("{0} has incorrect length (expected {1} but found {2})".format(self.name, expected_shape[0], value.shape[0]))
                else:
                    raise ValueError("{0} has incorrect shape (expected {1} but found {2})".format(self.name, expected_shape, value.shape))

        if self.target_unit is not None:
            _assert_unit_convertability(self.name, value, self.target_unit)

        if is_scalar:
            prefix = ""
        else:
            prefix = "All values of "

        if self.domain == 'positive':
            if np.any(value < 0.):
                raise ValueError(prefix + "{0} should be positive".format(self.name))
        elif self.domain == 'strictly-positive':
            if np.any(value <= 0.):
                raise ValueError(prefix + "{0} should be strictly positive".format(self.name))
        elif self.domain == 'negative':
            if np.any(value > 0.):
                raise ValueError(prefix + "{0} should be negative".format(self.name))
        elif self.domain == 'strictly-negative':
            if np.any(value >= 0.):
                raise ValueError(prefix + "{0} should be strictly negative".format(self.name))
        elif type(self.domain) in [tuple, list] and len(self.domain) == 2:
            if np.any(value < self.domain[0]) or np.any(value > self.domain[-1]):
                raise ValueError(prefix + "{0} should be in the range [{1:g}:{2:g}]".format(self.name, self.domain[0], self.domain[-1]))

        return value

try:
    import astropy.units
except:
    HAS_ASTROPY = False
else:
    HAS_ASTROPY = True

try:
    from quantities import Quantity
except:
    HAS_QUANTITIES = False
else:
    HAS_QUANTITIES = True

try:
    from pint.unit import UnitsContainer
except:
    HAS_PINT = False
else:
    HAS_PINT = True


def _assert_unit_convertability(name, value, target_unit):
    """
    Check that a value has physical type consistent with user-specified units

    Note that this does not convert the value, only check that the units have
    the right physical dimensionality.

    Parameters
    ----------
    name : str
        The name of the value to check (used for error messages).
    value : `numpy.ndarray` or instance of `numpy.ndarray` subclass
        The value to check.
    target_unit : unit
        The unit that the value should be convertible to.
    """

    if HAS_ASTROPY:

        from astropy.units import UnitBase, Quantity

        if isinstance(target_unit, UnitBase):

            if not isinstance(value, Quantity):
                raise TypeError("{0} should be given as an Astropy Quantity object".format(name))

            if not target_unit.is_equivalent(value.unit):
                raise ValueError("{0} should be in units convertible to {1}".format(name, target_unit))

    if HAS_QUANTITIES:

        from quantities.unitquantity import IrreducibleUnit
