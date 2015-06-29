import numpy as np

from weakref import WeakKeyDictionary


class NumericalProperty(object):

    def __init__(self, name, domain=None, shape=None, default=None):

        self.name = name
        self.domain = domain
        self.ndim = len(shape) if shape is not None else None
        self.shape = shape
        self.default = default

        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance, self.default)

    def __set__(self, instance, value):
        if self.ndim is None:
            self.data[instance] = self._validate_scalar(instance, value)
        else:
            self.data[instance] = self._validate_array(instance, value)

    def _validate_scalar(self, instance, value):

        if not np.isscalar(value) or (hasattr(value, 'shape') and value.shape != ()):
            raise TypeError("{0} should be a scalar value".format(self.name))

        if not np.isreal(value):
            raise TypeError("{0} should be a numerical value".format(self.name))

        if self.domain == 'positive':
            if value < 0.:
                raise ValueError("{0} should be positive".format(self.name))
        elif self.domain == 'strictly-positive':
            if value <= 0.:
                raise ValueError("{0} should be strictly positive".format(self.name))
        elif self.domain == 'negative':
            if value > 0.:
                raise ValueError("{0} should be negative".format(self.name))
        elif self.domain == 'strictly-negative':
            if value >= 0.:
                raise ValueError("{0} should be strictly negative".format(self.name))
        elif type(self.domain) in [tuple, list] and len(self.domain) == 2:
            if value < self.domain[0] or value > self.domain[-1]:
                raise ValueError("{0} should be in the range [{1:g}:{2:g}]".format(self.name, self.domain[0], self.domain[-1]))

        return value

    def _validate_array(self, instance, value):

        try:
            value = np.array(value, dtype=float, subok=True)
        except Exception as exc:
            raise TypeError("Could not convert value of {0} to a Numpy array ({1})".format(self.name, exc))

        # Check the value is an array with the right number of dimensions
        if not isinstance(value, np.ndarray) or value.ndim != self.ndim:
            if self.ndim == 1:
                raise TypeError("{0} should be a 1-d sequence".format(self.name))
            else:
                raise TypeError("{0} should be a {1:d}-d array".format(self.name, self.ndim))

        # Check that the shape matches that expected
        
        if isinstance(self.shape, str):
            expected_shape = getattr(instance, self.shape).shape
        else:
            expected_shape = self.shape
        
        if expected_shape is not None and np.any(value.shape != expected_shape):
            if self.ndim == 1:
                raise ValueError("{0} has incorrect length (expected {1} but found {2})".format(self.name, expected_shape[0], value.shape[0]))
            else:
                raise ValueError("{0} has incorrect shape (expected {1} but found {2})".format(self.name, expected_shape, value.shape))

        if self.domain == 'positive':
            if np.any(value < 0.):
                raise ValueError("All values of {0} should be positive".format(self.name))
        elif self.domain == 'strictly-positive':
            if np.any(value <= 0.):
                raise ValueError("All values of {0} should be strictly positive".format(self.name))
        elif self.domain == 'negative':
            if np.any(value > 0.):
                raise ValueError("All values of {0} should be negative".format(self.name))
        elif self.domain == 'strictly-negative':
            if np.any(value >= 0.):
                raise ValueError("All values of {0} should be strictly negative".format(self.name))
        elif type(self.domain) in [tuple, list] and len(self.domain) == 2:
            if np.any(value < self.domain[0]) or np.any(value > self.domain[-1]):
                raise ValueError("All values of {0} should be in the range [{1:g}:{2:g}]".format(self.name, self.domain[0], self.domain[-1]))

        return value

