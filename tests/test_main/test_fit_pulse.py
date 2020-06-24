import os
import bilby
import shutil
import unittest
import numpy as np

from numpy.testing import (assert_almost_equal, assert_equal, assert_allclose,
                           assert_array_almost_equal, assert_)

from PyGRB.backend.makepriors import MakePriors
from PyGRB.backend.makemodels import create_model_from_key

from PyGRB.backend.admin import mkdir
from PyGRB.main.fitpulse import PulseFitter


class PulseTester(PulseFitter):
    """ Test class for PulseFitter. """

    def __init__(self, *args, **kwargs):
        super(PulseTester, self).__init__(*args, **kwargs)

    def _get_base_directory(self):
        """
        Sets the directory that code products are made to be /products/ in
        the folder the script was ran from.
        """
        dir = f'test_products/{self.tlabel}_model_comparison_{str(self.nSamples)}'
        self.base_folder = dir
        mkdir(dir)

# class TestFredFit(unittest.TestCase):
#
    # def setUp(self):
    #     self.model = 'X'
    #     self.times = np.arange(100) * 0.064
    #
    #     self.st = 1.0
    #     self.sc = 20
    #     self.ta = 1.0
    #     self.xi = 1.0
    #     self.bg = 5
    #
    #
    #     self.IP = dict(start = self.st, scale = self.sc, tau = self.ta, xi = self.xi)
    #     self.injection_parameters = dict(start_1_a = self.st, scale_1_a = self.sc,
    #     tau_1_a = self.ta, xi_1_a = self.xi, background_a = self.bg)
    #     self.GRB = GRB_discsc
    #     self.GRB.counts[:,0] = np.random.poisson(
    #             FRED_pulse(self.times, **self.IP) + self.bg)
    #
    #     nSamples = 200
    #     self.discsc_fit = PulseFitter(0, times = (0, 6.4),
    #             datatype = 'self.discsc_fit', nSamples = nSamples, sampler = 'nestle',
    #             priors_pulse_start = 0, priors_pulse_end = 5,
    #             GRB = self.GRB, test = True,
    #             priors_td_lo = 0,  priors_td_hi = 1,
    #             injection_parameters = self.injection_parameters,
    #             save = True)
    #
    # def tearDown(self):
    #     del self.st
    #     del self.sc
    #     del self.ta
    #     del self.xi
    #     del self.bg
    #     del self.IP
    #     del self.GRB
    #     del self.model
    #     del self.times
    #     del self.injection_parameters
    #
    #     # try:
    #     #     shutil.rmtree(self.discsc_fit.base_folder)
    #     # except OSError:
    #     #     pass
    #
    #     pass




import time
class TestFred3770(unittest.TestCase):



    def setUp(self):
        nSamples = 201
        sampler = 'Nestle'

        self.keys = ['FL', 'FF']

        self.priors_pulse_start = -2
        self.priors_pulse_end   =  50

        self.discsc_fit =  PulseTester(3770, times = (-.1, 1),
                    datatype = 'tte', nSamples = nSamples, sampler = sampler,
                    priors_pulse_start = -.1, priors_pulse_end = 0.6,
                    priors_td_lo = 0,  priors_td_hi = 0.5,
                    p_type ='docs', HPC = True)
        self.discsc_fit.offsets = [0, 4000, 8000, -3000]

    def tearDown(self):
        del self.keys
        del self.discsc_fit

    def test_parameter_recovery(self):
        model_dict = {}
        for key in self.keys:
            model_dict[key] = create_model_from_key(key)
        models = [model for key, model in model_dict.items()]
        for model in models:
            self.discsc_fit.main_multi_channel(channels = [0, 1, 2, 3], model = model)
            lens_bounds = [(0.37, 0.42), (0.60, 1.8)]
            #  lens calc doesnt work because it is trying to multiply together 4 posteriors
            #  WHICH DO NOT OVERLAP
            # they do now 3770 is being tested
            self.discsc_fit.lens_calc(model = model, lens_bounds = lens_bounds)
        self.discsc_fit.get_evidence_from_models(model_dict = model_dict)
        shutil.rmtree('test_products/3770_model_comparison_201')

if __name__ == '__main__':
    unittest.main()
