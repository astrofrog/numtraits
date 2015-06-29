import pytest

import numpy as np
from numprops import NumericalProperty


class TestScalar(object):

    a = NumericalProperty('a')
    b = NumericalProperty('b', domain='positive')
    c = NumericalProperty('c', domain='strictly-positive')
    d = NumericalProperty('d', domain='negative')
    e = NumericalProperty('e', domain='strictly-negative')
    f = NumericalProperty('f', domain=(3, 4))

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
    b = NumericalProperty('b', domain='positive', shape=(3,))
    c = NumericalProperty('c', domain='strictly-positive', shape=(3,))
    d = NumericalProperty('d', domain='negative', shape=(3,))
    e = NumericalProperty('e', domain='strictly-negative', shape=(3,))
    f = NumericalProperty('f', domain=(3, 4), shape=(3,))

    def test_simple(self):
        self.a = (1,2,3)

    def test_shape(self):
        with pytest.raises(ValueError) as exc:
            self.a = (1,2,3, 4)
        assert exc.value.args[0] == "a has incorrect length (expected 3 but found 4)"

    def test_ndim(self):
        with pytest.raises(TypeError) as exc:
            self.a = np.ones((3,3))
        assert exc.value.args[0] == "a should be a 1-d sequence"

    def test_positive(self):
        self.b = (0.,2.,3.)
        with pytest.raises(ValueError) as exc:
            self.b = (0.,-1., 3.)
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
