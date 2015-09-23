# Copyright (c) 2015, Thomas P. Robitaille
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function

from traitlets import TraitType, TraitError

import numpy as np

__version__ = '0.2'

ASTROPY = 'astropy'
PINT = 'pint'
QUANTITIES = 'quantities'

class NumericalTrait(TraitType):
    info_text = 'a numerical trait, either a scalar or a vector'
    def __init__(self, ndim=None, shape=None, domain=None,
                 default=None, convertible_to=None):
        super(NumericalTrait, self).__init__()

        # Just store all the construction arguments.
        self.ndim = ndim
        self.shape = shape
        self.domain = domain
        # TODO: traitlets supports a `default` argument in __init__(), we should
        # probably link them together once we start using this.
        self.default = default
        self.target_unit = convertible_to

        if self.target_unit is not None:
            self.unit_framework = identify_unit_framework(self.target_unit)

        # Check the construction arguments.
        self._check_args()

    def _check_args(self):
        if self.shape is not None:
            if self.ndim is None:
                self.ndim = len(self.shape)
            else:
                if self.ndim != len(self.shape):
                    raise TraitError("shape={0} and ndim={1} are inconsistent".format(self.shape, self.ndim))

    def validate(self, obj, value):

        # We proceed by checking whether Numpy tells us the value is a
        # scalar. If Numpy isscalar returns False, it could still be scalar
        # but be a Quantity with units, so we then extract the numerical
        # values
        if np.isscalar(value):
            if not np.isreal(value):
                raise TraitError("{0} should be a numerical value".format(self.name))
            else:
                is_scalar = True
                num_value = value
        else:

            # The following works for Astropy and Pint quantities
            try:
                num_value = np.array(value, copy=False, dtype=float)
            except Exception as exc:
                raise TraitError("Could not convert value of {0} to a Numpy array (Exception: {1})".format(self.name, exc))

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
                    raise TraitError("{0} should be a scalar value".format(self.name))

            if self.ndim > 0:
                if is_scalar or num_value.ndim != self.ndim:
                    if self.ndim == 1:
                        raise TraitError("{0} should be a 1-d sequence".format(self.name))
                    else:
                        raise TraitError("{0} should be a {1:d}-d array".format(self.name, self.ndim))

        if self.shape is not None:

            if self.shape is not None and np.any(num_value.shape != self.shape):
                if self.ndim == 1:
                    raise TraitError("{0} has incorrect length (expected {1} but found {2})".format(self.name, self.shape[0], num_value.shape[0]))
                else:
                    raise TraitError("{0} has incorrect shape (expected {1} but found {2})".format(self.name, self.shape, num_value.shape))

        if self.target_unit is not None:
            assert_unit_convertability(self.name, value, self.target_unit, self.unit_framework)

        if is_scalar:
            prefix = ""
        else:
            prefix = "All values of "

        if self.domain == 'positive':
            if np.any(num_value < 0.):
                raise TraitError(prefix + "{0} should be positive".format(self.name))
        elif self.domain == 'strictly-positive':
            if np.any(num_value <= 0.):
                raise TraitError(prefix + "{0} should be strictly positive".format(self.name))
        elif self.domain == 'negative':
            if np.any(num_value > 0.):
                raise TraitError(prefix + "{0} should be negative".format(self.name))
        elif self.domain == 'strictly-negative':
            if np.any(num_value >= 0.):
                raise TraitError(prefix + "{0} should be strictly negative".format(self.name))
        elif type(self.domain) in [tuple, list] and len(self.domain) == 2:
            if np.any(num_value < self.domain[0]) or np.any(num_value > self.domain[-1]):
                raise TraitError(prefix + "{0} should be in the range [{1:g}:{2:g}]".format(self.name, self.domain[0], self.domain[-1]))

        return value

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


def identify_unit_framework(target_unit):
    """
    Identify whether the user is requesting unit validation against
    astropy.units, pint, or quantities.
    """

    if HAS_ASTROPY:

        from astropy.units import UnitBase

        if isinstance(target_unit, UnitBase):

            return ASTROPY

    if HAS_PINT:

        from pint.unit import UnitsContainer

        if hasattr(target_unit, 'units') and isinstance(target_unit.units, UnitsContainer):

            return PINT

    if HAS_QUANTITIES:

        from quantities.unitquantity import IrreducibleUnit
        from quantities import Quantity

        if isinstance(target_unit, IrreducibleUnit) or isinstance(target_unit, Quantity):

            return QUANTITIES

    raise TraitError("Could not identify unit framework for target unit of type {0}".format(type(target_unit).__name__))


def assert_unit_convertability(name, value, target_unit, unit_framework):
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
    unit_framework : str
        The unit framework to use
    """

    if unit_framework == ASTROPY:

        from astropy.units import Quantity

        if not isinstance(value, Quantity):
            raise TraitError("{0} should be given as an Astropy Quantity instance".format(name))

        if not target_unit.is_equivalent(value.unit):
            raise TraitError("{0} should be in units convertible to {1}".format(name, target_unit))

    elif unit_framework == PINT:

        from pint.unit import UnitsContainer

        if not (hasattr(value, 'units') and isinstance(value.units, UnitsContainer)):
            raise TraitError("{0} should be given as a Pint Quantity instance".format(name))

        if value.dimensionality != target_unit.dimensionality:
            raise TraitError("{0} should be in units convertible to {1}".format(name, target_unit.units))

    elif unit_framework == QUANTITIES:

        from quantities import Quantity

        if not isinstance(value, Quantity):
            raise TraitError("{0} should be given as a quantities Quantity instance".format(name))

        if value.dimensionality.simplified != target_unit.dimensionality.simplified:
            raise TraitError("{0} should be in units convertible to {1}".format(name, target_unit.dimensionality.string))
