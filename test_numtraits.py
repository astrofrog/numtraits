import pytest

import numpy as np
from numtraits import NumericalTrait

from traitlets import HasTraits, TraitError

class ScalarProperties(HasTraits):

    a = NumericalTrait(ndim=0)
    b = NumericalTrait(ndim=0, domain='positive')
    c = NumericalTrait(ndim=0, domain='strictly-positive')
    d = NumericalTrait(ndim=0, domain='negative')
    e = NumericalTrait(ndim=0, domain='strictly-negative')
    f = NumericalTrait(ndim=0, domain=(3, 4))

class TestScalar(object):

    def setup_method(self, method):

        # Make sure we have an instance of ScalarProperties each time
        # a testing method is called.
        self.sp = ScalarProperties()

    def test_simple(self):
        self.sp.a = 1.
        assert self.sp.a == 1.

    def test_scalar(self):
        with pytest.raises(TraitError) as exc:
            self.sp.a = [1, 2]
        assert exc.value.args[0] == "a should be a scalar value"

    def test_numerical(self):
        with pytest.raises(TraitError) as exc:
            self.sp.a = 'a'
        assert exc.value.args[0] == "a should be a numerical value"

    def test_positive(self):
        self.sp.b = 3.
        self.sp.b = 0.
        with pytest.raises(TraitError) as exc:
            self.sp.b = -2
        assert exc.value.args[0] == "b should be positive"

    def test_strictly_positive(self):
        self.sp.c = 3.
        with pytest.raises(TraitError) as exc:
            self.sp.c = 0.
        assert exc.value.args[0] == "c should be strictly positive"
        with pytest.raises(TraitError) as exc:
            self.sp.c = -2
        assert exc.value.args[0] == "c should be strictly positive"

    def test_negative(self):
        self.sp.d = -3.
        self.sp.d = 0.
        with pytest.raises(TraitError) as exc:
            self.sp.d = 2
        assert exc.value.args[0] == "d should be negative"

    def test_strictly_negative(self):
        self.sp.e = -2
        with pytest.raises(TraitError) as exc:
            self.sp.e = 0.
        assert exc.value.args[0] == "e should be strictly negative"
        with pytest.raises(TraitError) as exc:
            self.sp.e = 2
        assert exc.value.args[0] == "e should be strictly negative"

    def test_range(self):
        self.sp.f = 3.
        self.sp.f = 3.5
        self.sp.f = 4.
        with pytest.raises(TraitError) as exc:
            self.sp.f = 0.
        assert exc.value.args[0] == "f should be in the range [3:4]"
        with pytest.raises(TraitError) as exc:
            self.sp.f = 7
        assert exc.value.args[0] == "f should be in the range [3:4]"


class ArrayProperties(HasTraits):

    a = NumericalTrait(shape=(3,))
    b = NumericalTrait(domain='positive', ndim=1)
    c = NumericalTrait(domain='strictly-positive', ndim=1)
    d = NumericalTrait(domain='negative', ndim=1)
    e = NumericalTrait(domain='strictly-negative', ndim=1)
    f = NumericalTrait(domain=(3, 4), ndim=1)
    g = NumericalTrait(shape=(3, 4))

class TestArray(object):

    def setup_method(self, method):

        self.ap = ArrayProperties()

    def test_simple(self):
        self.ap.a = (1, 2, 3)
        self.ap.b = (1, 2, 3, 4)
        np.testing.assert_allclose(self.ap.a, (1, 2, 3))
        np.testing.assert_allclose(self.ap.b, (1, 2, 3, 4))
        assert isinstance(self.ap.a, np.ndarray)
        assert isinstance(self.ap.b, np.ndarray)

    def test_shape(self):
        with pytest.raises(TraitError) as exc:
            self.ap.a = (1, 2, 3, 4)
        assert exc.value.args[0] == "a has incorrect length (expected 3 but found 4)"

    def test_ndim(self):
        with pytest.raises(TraitError) as exc:
            self.ap.a = np.ones((3, 3))
        assert exc.value.args[0] == "a should be a 1-d sequence"

    def test_positive(self):
        self.ap.b = (0., 2., 3.)
        with pytest.raises(TraitError) as exc:
            self.ap.b = (0., -1., 3.)
        assert exc.value.args[0] == "All values of b should be positive"

    def test_strictly_positive(self):
        self.ap.c = (1., 2., 3.)
        with pytest.raises(TraitError) as exc:
            self.ap.c = (0., 2., 3.)
        assert exc.value.args[0] == "All values of c should be strictly positive"
        with pytest.raises(TraitError) as exc:
            self.ap.c = (0., -1., 3.)
        assert exc.value.args[0] == "All values of c should be strictly positive"

    def test_negative(self):
        self.ap.d = (-1., -2., 0.)
        with pytest.raises(TraitError) as exc:
            self.ap.d = (-1., -2., 1.)
        assert exc.value.args[0] == "All values of d should be negative"

    def test_strictly_negative(self):
        self.ap.e = (-1., -2., -3.)
        with pytest.raises(TraitError) as exc:
            self.ap.e = (-1., -2., 0.)
        assert exc.value.args[0] == "All values of e should be strictly negative"
        with pytest.raises(TraitError) as exc:
            self.ap.e = (-1., -2., 1.)
        assert exc.value.args[0] == "All values of e should be strictly negative"

    def test_range(self):
        self.ap.f = (3., 3.5, 4.)
        with pytest.raises(TraitError) as exc:
            self.ap.f = (0., 3.5, 4.)
        assert exc.value.args[0] == "All values of f should be in the range [3:4]"
        with pytest.raises(TraitError) as exc:
            self.ap.f = (0., 3.5, 7.)
        assert exc.value.args[0] == "All values of f should be in the range [3:4]"

    def test_shape_2d(self):
        self.ap.g = np.ones((3, 4))
        with pytest.raises(TraitError) as exc:
            self.ap.g = np.ones((3, 6))
        assert exc.value.args[0] == "g has incorrect shape (expected (3, 4) but found (3, 6))"

    def test_ndim_2d(self):
        with pytest.raises(TraitError) as exc:
            self.ap.g = np.ones((3, 6, 3))
        assert exc.value.args[0] == "g should be a 2-d array"

    def test_invalid(self):
        with pytest.raises(TraitError) as exc:
            self.ap.a = [[1.], [1., 2.]]
        assert exc.value.args[0] == "Could not convert value of a to a Numpy array (Exception: setting an array element with a sequence.)"

# Need to decide on behavior if passing a unit-ed quantity to a trait
# with no convertible_to argument.

try:
    from astropy import units as u
    from pint import UnitRegistry
    import quantities as pq
except ImportError:
    pass
else:

    ureg = UnitRegistry()

    class AstropyUnitsProperties(HasTraits):

        a = NumericalTrait(convertible_to=u.m)
        b = NumericalTrait(convertible_to=u.cm / u.s)

    class TestAstropyUnits(object):

        def setup_method(self, method):

            self.aup = AstropyUnitsProperties()

        def test_valid(self):

            self.aup.a = 3 * u.m
            self.aup.a = [1, 2, 3] * u.cm
            self.aup.a = np.ones((2, 2)) * u.pc

            self.aup.b = 3 * u.m / u.yr
            self.aup.b = [1, 2, 3] * u.cm / u.s
            self.aup.b = np.ones((2, 2)) * u.pc / u.Myr

        def test_invalid_type(self):

            with pytest.raises(TraitError) as exc:
                self.aup.a = 5
            assert exc.value.args[0] == 'a should be given as an Astropy Quantity instance'

            with pytest.raises(TraitError) as exc:
                self.aup.b = np.ones((2, 5))
            assert exc.value.args[0] == 'b should be given as an Astropy Quantity instance'

        def test_invalid_framework(self):

            # pint
            with pytest.raises(TraitError) as exc:
                self.aup.a = 5 * ureg.m
            assert exc.value.args[0] == 'a should be given as an Astropy Quantity instance'

            # quantities
            with pytest.raises(TraitError) as exc:
                self.aup.b = 3 * pq.cm
            assert exc.value.args[0] == 'b should be given as an Astropy Quantity instance'

        def test_invalid_units(self):

            with pytest.raises(TraitError) as exc:
                self.aup.a = 5 * u.s
            assert exc.value.args[0] == 'a should be in units convertible to m'

            with pytest.raises(TraitError) as exc:
                self.aup.b = np.ones((2, 5)) * u.s
            assert exc.value.args[0] == 'b should be in units convertible to cm / s'

    class PintUnitsProperties(HasTraits):

        a = NumericalTrait(convertible_to=ureg.m)
        b = NumericalTrait(convertible_to=ureg.cm / ureg.s)

    class TestPintUnits(object):

        def setup_method(self, method):

            self.pup = PintUnitsProperties()

        def test_valid(self):

            from astropy import units as u

            self.pup.a = 3 * ureg.m
            self.pup.a = [1, 2, 3] * ureg.cm
            self.pup.a = np.ones((2, 2)) * ureg.pc

            self.pup.b = 3 * ureg.m / ureg.year
            self.pup.b = [1, 2, 3] * ureg.cm / ureg.s
            self.pup.b = np.ones((2, 2)) * ureg.pc / ureg.megayear

        def test_invalid_type(self):

            with pytest.raises(TraitError) as exc:
                self.pup.a = 5
            assert exc.value.args[0] == 'a should be given as a Pint Quantity instance'

            with pytest.raises(TraitError) as exc:
                self.pup.b = np.ones((2, 5))
            assert exc.value.args[0] == 'b should be given as a Pint Quantity instance'

        def test_invalid_framework(self):

            # astropy.units
            with pytest.raises(TraitError) as exc:
                self.pup.b = 5 * u.m
            assert exc.value.args[0] == 'b should be given as a Pint Quantity instance'

            # quantitites
            with pytest.raises(TraitError) as exc:
                self.pup.b = 3 * pq.cm
            assert exc.value.args[0] == 'b should be given as a Pint Quantity instance'

        def test_invalid_units(self):

            from astropy import units as u

            with pytest.raises(TraitError) as exc:
                self.pup.a = 5 * ureg.s
            assert exc.value.args[0] == 'a should be in units convertible to meter'

            with pytest.raises(TraitError) as exc:
                self.pup.b = np.ones((2, 5)) * ureg.s
            assert exc.value.args[0] == 'b should be in units convertible to centimeter / second'

    class QuantitiesUnitsProperties(HasTraits):

        a = NumericalTrait(convertible_to=pq.m)
        b = NumericalTrait(convertible_to=pq.cm / pq.s)

    class TestQuantitiesUnits(object):

        def setup_method(self, method):

            self.qup = QuantitiesUnitsProperties()

        def test_valid(self):

            from astropy import units as u

            self.qup.a = 3 * pq.m
            self.qup.a = [1, 2, 3] * pq.cm
            self.qup.a = np.ones((2, 2)) * pq.pc

            self.qup.b = 3 * pq.m / pq.year
            self.qup.b = [1, 2, 3] * pq.cm / pq.s
            self.qup.b = np.ones((2, 2)) * pq.pc / pq.s

        def test_invalid_type(self):

            with pytest.raises(TraitError) as exc:
                self.qup.a = 5
            assert exc.value.args[0] == 'a should be given as a quantities Quantity instance'

            with pytest.raises(TraitError) as exc:
                self.qup.b = np.ones((2, 5))
            assert exc.value.args[0] == 'b should be given as a quantities Quantity instance'

        def test_invalid_framework(self):

            # astropy.units
            with pytest.raises(TraitError) as exc:
                self.qup.a = 5 * u.m
            assert exc.value.args[0] == 'a should be given as a quantities Quantity instance'

            # pint
            with pytest.raises(TraitError) as exc:
                self.qup.b = 3 * ureg.cm
            assert exc.value.args[0] == 'b should be given as a quantities Quantity instance'

        def test_invalid_units(self):

            from astropy import units as u

            with pytest.raises(TraitError) as exc:
                self.qup.a = 5 * pq.s
            assert exc.value.args[0] == 'a should be in units convertible to m'

            with pytest.raises(TraitError) as exc:
                self.qup.b = np.ones((2, 5)) * pq.s
            assert exc.value.args[0] == 'b should be in units convertible to cm/s'



# TODO: add test for domain with units

def test_inconsistent_ndim_shape():

    with pytest.raises(TraitError) as exc:
        a = NumericalTrait(ndim=3, shape=(3, 3))
    assert exc.value.args[0] == "shape=(3, 3) and ndim=3 are inconsistent"


def test_invalid_unit_framework():

    with pytest.raises(TraitError) as exc:
        a = NumericalTrait(convertible_to='m')
    assert exc.value.args[0] == "Could not identify unit framework for target unit of type str"
