import pytest

import numpy as np
from numprops import NumericalProperty


class TestScalar(object):

    a = NumericalProperty('a', ndim=0)
    b = NumericalProperty('b', ndim=0, domain='positive')
    c = NumericalProperty('c', ndim=0, domain='strictly-positive')
    d = NumericalProperty('d', ndim=0, domain='negative')
    e = NumericalProperty('e', ndim=0, domain='strictly-negative')
    f = NumericalProperty('f', ndim=0, domain=(3, 4))

    def test_simple(self):
        self.a = 1.
        assert self.a == 1.

    def test_scalar(self):
        with pytest.raises(TypeError) as exc:
            self.a = [1, 2]
        assert exc.value.args[0] == "a should be a scalar value"

    def test_numerical(self):
        with pytest.raises(TypeError) as exc:
            self.a = 'a'
        assert exc.value.args[0] == "a should be a numerical value"

    def test_positive(self):
        self.b = 3.
        self.b = 0.
        with pytest.raises(ValueError) as exc:
            self.b = -2
        assert exc.value.args[0] == "b should be positive"

    def test_strictly_positive(self):
        self.c = 3.
        with pytest.raises(ValueError) as exc:
            self.c = 0.
        assert exc.value.args[0] == "c should be strictly positive"
        with pytest.raises(ValueError) as exc:
            self.c = -2
        assert exc.value.args[0] == "c should be strictly positive"

    def test_negative(self):
        self.d = -3.
        self.d = 0.
        with pytest.raises(ValueError) as exc:
            self.d = 2
        assert exc.value.args[0] == "d should be negative"

    def test_strictly_negative(self):
        self.e = -2
        with pytest.raises(ValueError) as exc:
            self.e = 0.
        assert exc.value.args[0] == "e should be strictly negative"
        with pytest.raises(ValueError) as exc:
            self.e = 2
        assert exc.value.args[0] == "e should be strictly negative"

    def test_range(self):
        self.f = 3.
        self.f = 3.5
        self.f = 4.
        with pytest.raises(ValueError) as exc:
            self.f = 0.
        assert exc.value.args[0] == "f should be in the range [3:4]"
        with pytest.raises(ValueError) as exc:
            self.f = 7
        assert exc.value.args[0] == "f should be in the range [3:4]"


class TestArray(object):

    a = NumericalProperty('a', shape=(3,))
    b = NumericalProperty('b', domain='positive', ndim=1)
    c = NumericalProperty('c', domain='strictly-positive', ndim=1)
    d = NumericalProperty('d', domain='negative', ndim=1)
    e = NumericalProperty('e', domain='strictly-negative', ndim=1)
    f = NumericalProperty('f', domain=(3, 4), ndim=1)
    g = NumericalProperty('g', shape=(3, 4))

    def test_simple(self):
        self.a = (1, 2, 3)
        self.b = (1, 2, 3, 4)
        np.testing.assert_allclose(self.a, (1, 2, 3))
        np.testing.assert_allclose(self.b, (1, 2, 3, 4))
        assert isinstance(self.a, np.ndarray)
        assert isinstance(self.b, np.ndarray)

    def test_shape(self):
        with pytest.raises(ValueError) as exc:
            self.a = (1, 2, 3, 4)
        assert exc.value.args[0] == "a has incorrect length (expected 3 but found 4)"

    def test_ndim(self):
        with pytest.raises(TypeError) as exc:
            self.a = np.ones((3, 3))
        assert exc.value.args[0] == "a should be a 1-d sequence"

    def test_positive(self):
        self.b = (0., 2., 3.)
        with pytest.raises(ValueError) as exc:
            self.b = (0., -1., 3.)
        assert exc.value.args[0] == "All values of b should be positive"

    def test_strictly_positive(self):
        self.c = (1., 2., 3.)
        with pytest.raises(ValueError) as exc:
            self.c = (0., 2., 3.)
        assert exc.value.args[0] == "All values of c should be strictly positive"
        with pytest.raises(ValueError) as exc:
            self.c = (0., -1., 3.)
        assert exc.value.args[0] == "All values of c should be strictly positive"

    def test_negative(self):
        self.d = (-1., -2., 0.)
        with pytest.raises(ValueError) as exc:
            self.d = (-1., -2., 1.)
        assert exc.value.args[0] == "All values of d should be negative"

    def test_strictly_negative(self):
        self.e = (-1., -2., -3.)
        with pytest.raises(ValueError) as exc:
            self.e = (-1., -2., 0.)
        assert exc.value.args[0] == "All values of e should be strictly negative"
        with pytest.raises(ValueError) as exc:
            self.e = (-1., -2., 1.)
        assert exc.value.args[0] == "All values of e should be strictly negative"

    def test_range(self):
        self.f = (3., 3.5, 4.)
        with pytest.raises(ValueError) as exc:
            self.f = (0., 3.5, 4.)
        assert exc.value.args[0] == "All values of f should be in the range [3:4]"
        with pytest.raises(ValueError) as exc:
            self.f = (0., 3.5, 7.)
        assert exc.value.args[0] == "All values of f should be in the range [3:4]"

    def test_shape_2d(self):
        self.g = np.ones((3, 4))
        with pytest.raises(ValueError) as exc:
            self.g = np.ones((3, 6))
        assert exc.value.args[0] == "g has incorrect shape (expected (3, 4) but found (3, 6))"

    def test_ndim_2d(self):
        with pytest.raises(TypeError) as exc:
            self.g = np.ones((3, 6, 3))
        assert exc.value.args[0] == "g should be a 2-d array"

    def test_invalid(self):
        with pytest.raises(TypeError) as exc:
            self.a = [[1.], [1., 2.]]
        assert exc.value.args[0] == "Could not convert value of a to a Numpy array (Exception: setting an array element with a sequence.)"


# Need to decide on behavior if passing a unit-ed quantity to a property
# with no convertible_to argument.

try:
    from astropy import units as u
    from pint import UnitRegistry
    import quantities as pq
except ImportError:
    pass
else:

    ureg = UnitRegistry()

    class TestAstropyUnits(object):

        a = NumericalProperty('a', convertible_to=u.m)
        b = NumericalProperty('b', convertible_to=u.cm / u.s)

        def test_valid(self):

            self.a = 3 * u.m
            self.a = [1, 2, 3] * u.cm
            self.a = np.ones((2, 2)) * u.pc

            self.b = 3 * u.m / u.yr
            self.b = [1, 2, 3] * u.cm / u.s
            self.b = np.ones((2, 2)) * u.pc / u.Myr

        def test_invalid_type(self):

            with pytest.raises(TypeError) as exc:
                self.a = 5
            assert exc.value.args[0] == 'a should be given as an Astropy Quantity instance'

            with pytest.raises(TypeError) as exc:
                self.b = np.ones((2, 5))
            assert exc.value.args[0] == 'b should be given as an Astropy Quantity instance'

        def test_invalid_framework(self):

            # pint
            with pytest.raises(TypeError) as exc:
                self.a = 5 * ureg.m
            assert exc.value.args[0] == 'a should be given as an Astropy Quantity instance'

            # quantities
            with pytest.raises(TypeError) as exc:
                self.b = 3 * pq.cm
            assert exc.value.args[0] == 'b should be given as an Astropy Quantity instance'

        def test_invalid_units(self):

            with pytest.raises(ValueError) as exc:
                self.a = 5 * u.s
            assert exc.value.args[0] == 'a should be in units convertible to m'

            with pytest.raises(ValueError) as exc:
                self.b = np.ones((2, 5)) * u.s
            assert exc.value.args[0] == 'b should be in units convertible to cm / s'


    class TestPintUnits(object):

        a = NumericalProperty('a', convertible_to=ureg.m)
        b = NumericalProperty('b', convertible_to=ureg.cm / ureg.s)

        def test_valid(self):

            from astropy import units as u

            self.a = 3 * ureg.m
            self.a = [1, 2, 3] * ureg.cm
            self.a = np.ones((2, 2)) * ureg.pc

            self.b = 3 * ureg.m / ureg.year
            self.b = [1, 2, 3] * ureg.cm / ureg.s
            self.b = np.ones((2, 2)) * ureg.pc / ureg.megayear

        def test_invalid_type(self):

            with pytest.raises(TypeError) as exc:
                self.a = 5
            assert exc.value.args[0] == 'a should be given as a Pint Quantity instance'

            with pytest.raises(TypeError) as exc:
                self.b = np.ones((2, 5))
            assert exc.value.args[0] == 'b should be given as a Pint Quantity instance'

        def test_invalid_framework(self):

            # astropy.units
            with pytest.raises(TypeError) as exc:
                self.b = 5 * u.m
            assert exc.value.args[0] == 'b should be given as a Pint Quantity instance'

            # quantitites
            with pytest.raises(TypeError) as exc:
                self.b = 3 * pq.cm
            assert exc.value.args[0] == 'b should be given as a Pint Quantity instance'

        def test_invalid_units(self):

            from astropy import units as u

            with pytest.raises(ValueError) as exc:
                self.a = 5 * ureg.s
            assert exc.value.args[0] == 'a should be in units convertible to meter'

            with pytest.raises(ValueError) as exc:
                self.b = np.ones((2, 5)) * ureg.s
            assert exc.value.args[0] == 'b should be in units convertible to centimeter / second'


    class TestQuantitiesUnits(object):

        a = NumericalProperty('a', convertible_to=pq.m)
        b = NumericalProperty('b', convertible_to=pq.cm / pq.s)

        def test_valid(self):

            from astropy import units as u

            self.a = 3 * pq.m
            self.a = [1, 2, 3] * pq.cm
            self.a = np.ones((2, 2)) * pq.pc

            self.b = 3 * pq.m / pq.year
            self.b = [1, 2, 3] * pq.cm / pq.s
            self.b = np.ones((2, 2)) * pq.pc / pq.s

        def test_invalid_type(self):

            with pytest.raises(TypeError) as exc:
                self.a = 5
            assert exc.value.args[0] == 'a should be given as a quantities Quantity instance'

            with pytest.raises(TypeError) as exc:
                self.b = np.ones((2, 5))
            assert exc.value.args[0] == 'b should be given as a quantities Quantity instance'

        def test_invalid_framework(self):

            # astropy.units
            with pytest.raises(TypeError) as exc:
                self.a = 5 * u.m
            assert exc.value.args[0] == 'a should be given as a quantities Quantity instance'

            # pint
            with pytest.raises(TypeError) as exc:
                self.b = 3 * ureg.cm
            assert exc.value.args[0] == 'b should be given as a quantities Quantity instance'

        def test_invalid_units(self):

            from astropy import units as u

            with pytest.raises(ValueError) as exc:
                self.a = 5 * pq.s
            assert exc.value.args[0] == 'a should be in units convertible to m'

            with pytest.raises(ValueError) as exc:
                self.b = np.ones((2, 5)) * pq.s
            assert exc.value.args[0] == 'b should be in units convertible to cm/s'


# TODO: add test for domain with units

def test_inconsistent_ndim_shape():

    with pytest.raises(ValueError) as exc:
        a = NumericalProperty('a', ndim=3, shape=(3, 3))
    assert exc.value.args[0] == "shape=(3, 3) and ndim=3 for property 'a' are inconsistent"


def test_invalid_unit_framework():

    with pytest.raises(ValueError) as exc:
        a = NumericalProperty('a', convertible_to='m')
    assert exc.value.args[0] == "Could not identify unit framework for target unit of type str"
