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


class TestAstropyUnits(object):

    from astropy import units as u

    a = NumericalProperty('a')
    b = NumericalProperty('b', convertible_to=u.m)
    c = NumericalProperty('c', convertible_to=u.cm / u.s)

    # Need to decide on behavior if passing a unit-ed quantity to a property
    # with no convertible_to argument.

    def test_valid(self):

        from astropy import units as u

        self.b = 3 * u.m
        self.b = [1, 2, 3] * u.cm
        self.b = np.ones((2, 2)) * u.pc

        self.c = 3 * u.m / u.yr
        self.c = [1, 2, 3] * u.cm / u.s
        self.c = np.ones((2, 2)) * u.pc / u.Myr

    def test_invalid_type(self):

        with pytest.raises(TypeError) as exc:
            self.b = 5
        assert exc.value.args[0] == 'b should be given as an Astropy Quantity object'

        with pytest.raises(TypeError) as exc:
            self.c = np.ones((2, 5))
        assert exc.value.args[0] == 'c should be given as an Astropy Quantity object'

    def test_invalid_units(self):

        from astropy import units as u

        with pytest.raises(ValueError) as exc:
            self.b = 5 * u.s
        assert exc.value.args[0] == 'b should be in units convertible to m'

        with pytest.raises(ValueError) as exc:
            self.c = np.ones((2, 5)) * u.s
        assert exc.value.args[0] == 'c should be in units convertible to cm / s'
