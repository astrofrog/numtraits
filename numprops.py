import numpy as np

from weakref import WeakKeyDictionary


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
                    raise ValueError("shape={0} and ndim={1} for property '{2}' are inconsistent".format(shape, ndim, name))

        self.ndim = ndim
        self.shape = shape

        self.default = default
        self.target_unit = convertible_to

        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance, self.default)

    def __set__(self, instance, value):

        # We proceed by checking whether Numpy tells us the value is a
        # scalar. If Numpy isscalar returns False, it could still be scalar
        # but be a Quantity with units, so we then extract the numerical
        # values

        if np.isscalar(value):
            if not np.isreal(value):
                raise TypeError("{0} should be a numerical value".format(self.name))
            else:
                is_scalar = True
                num_value = value
        else:

            # The following works for Astropy and Pint quantities
            try:
                num_value = np.array(value, copy=False, dtype=float)
            except Exception as exc:
                raise TypeError("Could not convert value of {0} to a Numpy array (Exception: {1})".format(self.name, exc))

            is_scalar = np.isscalar(num_value)

            if not is_scalar:
                # If value is not scalar, then Pint and Astropy quantities will
                # have a shape and ndim, so we can then safely set value to the
                # unitless Numpy array if either shape or ndim are not present.
                # This will cause e.g. tuples and lists to get converted.
                if not hasattr(value, 'shape') or not hasattr(value, 'ndim'):
                    value = num_value

        if self.ndim is not None:

            if self.ndim == 0:
                if not is_scalar:
                    raise TypeError("{0} should be a scalar value".format(self.name))

            if self.ndim > 0:
                if is_scalar or num_value.ndim != self.ndim:
                    if self.ndim == 1:
                        raise TypeError("{0} should be a 1-d sequence".format(self.name))
                    else:
                        raise TypeError("{0} should be a {1:d}-d array".format(self.name, self.ndim))

        if self.shape is not None:

            if self.shape is not None and np.any(num_value.shape != self.shape):
                if self.ndim == 1:
                    raise ValueError("{0} has incorrect length (expected {1} but found {2})".format(self.name, self.shape[0], num_value.shape[0]))
                else:
                    raise ValueError("{0} has incorrect shape (expected {1} but found {2})".format(self.name, self.shape, num_value.shape))

        if self.target_unit is not None:
            _assert_unit_convertability(self.name, value, self.target_unit)

        if is_scalar:
            prefix = ""
        else:
            prefix = "All values of "

        if self.domain == 'positive':
            if np.any(num_value < 0.):
                raise ValueError(prefix + "{0} should be positive".format(self.name))
        elif self.domain == 'strictly-positive':
            if np.any(num_value <= 0.):
                raise ValueError(prefix + "{0} should be strictly positive".format(self.name))
        elif self.domain == 'negative':
            if np.any(num_value > 0.):
                raise ValueError(prefix + "{0} should be negative".format(self.name))
        elif self.domain == 'strictly-negative':
            if np.any(num_value >= 0.):
                raise ValueError(prefix + "{0} should be strictly negative".format(self.name))
        elif type(self.domain) in [tuple, list] and len(self.domain) == 2:
            if np.any(num_value < self.domain[0]) or np.any(num_value > self.domain[-1]):
                raise ValueError(prefix + "{0} should be in the range [{1:g}:{2:g}]".format(self.name, self.domain[0], self.domain[-1]))

        self.data[instance] = value


try:
    import astropy.units
except ImportError:  # pragma: no cover
    HAS_ASTROPY = False
else:
    HAS_ASTROPY = True

try:
    import pint
except ImportError:  # pragma: no cover
    HAS_PINT = False
else:
    HAS_PINT = True


try:
    import quantities
except ImportError:  # pragma: no cover
    HAS_QUANTITIES = False
else:
    HAS_QUANTITIES = True


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
                raise TypeError("{0} should be given as an Astropy Quantity instance".format(name))

            if not target_unit.is_equivalent(value.unit):
                raise ValueError("{0} should be in units convertible to {1}".format(name, target_unit))

            return

    if HAS_PINT:

        from pint.unit import UnitsContainer

        if hasattr(target_unit, 'units') and isinstance(target_unit.units, UnitsContainer):

            if not (hasattr(value, 'units') and isinstance(value.units, UnitsContainer)):
                raise TypeError("{0} should be given as a Pint Quantity instance".format(name))

            if value.dimensionality != target_unit.dimensionality:
                raise ValueError("{0} should be in units convertible to {1}".format(name, target_unit.units))

            return

    if HAS_QUANTITIES:

        from quantities.unitquantity import IrreducibleUnit
        from quantities import Quantity

        if isinstance(target_unit, IrreducibleUnit) or isinstance(target_unit, Quantity):

            if not isinstance(value, Quantity):
                raise TypeError("{0} should be given as a quantities Quantity instance".format(name))

            if value.dimensionality.simplified != target_unit.dimensionality.simplified:
                raise ValueError("{0} should be in units convertible to {1}".format(name, target_unit.dimensionality.string))

            return
