import sys
import unittest
import numpy as np

from numpy.testing import (assert_almost_equal, assert_equal, assert_allclose,
                           assert_array_almost_equal, assert_)

from PyGRB.backend.rate_functions import *

MIN_FLOAT = sys.float_info[3]


class TestGaussianPulse(unittest.TestCase):

    def setUp(self):
        self.times = np.linspace(0, 10, 10)
        self.start = 4
        self.scale = 5
        self.sigma = 2
        self.tau   = 1
        self.xi    = 4
        self.gamma = 3
        self.nu    = 1
        self.omega = 1
        self.phi   = 1

    def tearDown(self):
        del self.times
        del self.start
        del self.scale
        del self.sigma
        del self.tau
        del self.xi
        del self.gamma
        del self.nu
        del self.omega
        del self.phi

    def test_gaussian_pulse(self):
        y = gaussian_pulse(self.times, self.start, self.scale, self.sigma)
        expected = np.array([0.67667642, 1.76160977, 3.36819228, 4.72979734,
        4.8780549, 3.69495648, 2.05556145, 0.83986618, 0.25202767, 0.05554498])
        assert_allclose(y, expected, rtol=1e-7)

    def test_height_gaussian_pulse(self):
        y = gaussian_pulse(self.times, self.start, self.scale, self.sigma)
        assert(np.max(y) <= self.scale)

    def test_FRED_pulse(self):
        y = FRED_pulse(self.times, self.start, self.scale, self.tau, self.xi)
        expected = np.array([2.22507386e-308, 2.22507386e-308, 2.22507386e-308,
        2.22507386e-308, 3.10882620e-001, 2.26095461e+000, 7.75192680e-002,
        1.41518257e-003, 2.11409326e-005, 2.88887426e-007])
        assert_allclose(y, expected, rtol=1e-7)

    def test_height_FRED_pulse(self):
        y = FRED_pulse(self.times, self.start, self.scale, self.tau, self.xi)
        assert(np.max(y) <= self.scale)

    def test_FRED_pulse_unnorm(self):
        y = FRED_pulse_unnorm(self.times, self.start, self.scale, self.tau, self.xi)
        expected = np.array([2.22507386e-308, 2.22507386e-308, 2.22507386e-308,
        2.22507386e-308,  1.04289501e-004, 7.58465776e-004, 2.60048174e-005,
        4.74740866e-007, 7.09199282e-009, 9.69109351e-011])
        assert_allclose(y, expected, rtol=1e-7)

    def test_FREDx_pulse(self):
        y = FREDx_pulse(self.times, self.start, self.scale, self.tau,
                        self.xi, self.gamma, self.nu)
        expected = np.array([1.11253693e-307, 1.11253693e-307, 1.11253693e-307,
        1.11253693e-307, 2.64784701e-311, 5.11799835e-004, 4.98231205e+000,
        5.21729958e-001, 1.16121498e-002, 1.75348422e-004])
        assert_allclose(y, expected, rtol=1e-7)

    def test_height_FREDx_pulse(self):
        y = FREDx_pulse(self.times, self.start, self.scale, self.tau,
                        self.xi, self.gamma, self.nu)
        assert(np.max(y) <= self.scale)

    def test_FREDx_pulse_unnorm(self):
        y = FREDx_pulse_unnorm(self.times, self.start, self.scale, self.tau,
                        self.xi, self.gamma, self.nu)
        expected = np.array([1.11253693e-307, 1.11253693e-307, 1.11253693e-307,
        1.11253693e-307, 2.11940328e-317, 4.09657463e-010, 3.98796790e-006,
        4.17605783e-007, 9.29465686e-009, 1.40353288e-010])
        assert_allclose(y, expected, rtol=1e-7)

    def test_convolution_gaussian(self):
        y = convolution_gaussian(self.times, self.start, self.scale,
                                 self.sigma, self.tau)
        expected = np.array([0.1408575,  0.53048148, 1.39662887, 2.72520552,
        3.9816915, 4.39531788, 3.71217365, 2.44340352, 1.28690833, 0.56161562])
        assert_allclose(y, expected, rtol=1e-7)

    def test_height_convolution_gaussian(self):
        y = convolution_gaussian(self.times, self.start, self.scale,
                                 self.sigma, self.tau)
        assert(np.max(y) <= self.scale)

    def test_sine_gaussian(self):
        y = sine_gaussian(self.times, self.start, self.scale,
                          self.tau, self.omega, self.phi)
        expected = np.array([ 3.04015072e-07, -6.10651816e-04, -2.11335152e-01,
        -1.18632259e+00, 2.74296218e+00,  4.28323787e-01,  7.59772409e-04,
        -2.52834792e-06, -1.86311665e-10,  5.13275376e-18])
        assert_allclose(y, expected, rtol=1e-7)

    def test_height_sine_gaussian(self):
        y = sine_gaussian(self.times, self.start, self.scale,
                          self.tau, self.omega, self.phi)
        assert(np.max(y) <= self.scale)

if __name__ == '__main__':
    unittest.main()
