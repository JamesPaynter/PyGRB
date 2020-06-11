import os
import bilby
import shutil
import unittest
import numpy as np

from numpy.testing import (assert_almost_equal, assert_equal, assert_allclose,
                           assert_array_almost_equal, assert_)

from PyGRB.backend.admin import mkdir
from PyGRB.backend.makepriors import MakePriors
from PyGRB.main.fitpulse import PulseFitter
from PyGRB.backend.makemodels import create_model_from_key



class PulseTester(PulseFitter):
    """docstring for PulseTester."""

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
    #     self.model = 'F'
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

class TestFred7475(unittest.TestCase):
    def setUp(self):
        self.key = 'F'

        self.priors_pulse_start = -10
        self.priors_pulse_end   =  20

        self.parameters = {'background_b' : 183,
                            'start_1_b' : -5.47,
                            'scale_1_b' : 263.3,
                            'tau_1_b'   : 14.4,
                            'xi_1_b'    : 2.3}

        nSamples = 201
        self.discsc_fit = PulseTester(7475, times = (-2, 60),
                datatype = 'discsc', nSamples = nSamples, sampler = 'dynesty',
                priors_pulse_start = self.priors_pulse_start,
                priors_pulse_end = self.priors_pulse_end, HPC = True)

    def tearDown(self):
        del self.key
        del self.parameters
        del self.discsc_fit

    # def test_parameter_recovery(self):
    #     model = create_model_from_key(self.key)
    #     self.discsc_fit.main_1_channel(channel = 1, model = model)
    #     # self.discsc_fit._setup_labels(model) #for testing
    #     result_label = f'{self.discsc_fit.fstring}{self.discsc_fit.clabels[1]}'
    #     open_result  = f'{self.discsc_fit.outdir}/{result_label}_result.json'
    #     result = bilby.result.read_in_result(filename=open_result)
    #
    #     prior_shell = MakePriors(
    #                         priors_pulse_start = self.priors_pulse_start,
    #                         priors_pulse_end = self.priors_pulse_end,
    #                         channel      = 1,
    #                         **model)
    #     priors = prior_shell.return_prior_dict()
    #
    #     posteriors = dict()
    #     for parameter in priors:
    #         posteriors[parameter] = np.median(result.posterior[parameter].values)
    #     for parameter in priors:
    #         assert( (abs(posteriors[parameter] - self.parameters[parameter]))
    #                 / self.parameters[parameter]) < 0.1
    #     shutil.rmtree('test_products/7475_model_comparison_201')


import time
class TestFred973(unittest.TestCase):



    def setUp(self):
        nSamples = 101
        # CANNOT CREATE VALID CONTOURS
        sampler = 'Nestle'

        self.keys = ['FL', 'FF']
        # self.keys = ['FF']

        self.priors_pulse_start = -2
        self.priors_pulse_end   =  50

        self.discsc_fit = PulseTester(973, times = (-2, 50),
                    datatype = 'discsc', nSamples = nSamples, sampler = sampler,
                    priors_pulse_start = -5, priors_pulse_end = 50,
                    priors_td_lo = 0,  priors_td_hi = 30,
                    p_type ='docs', HPC = True)

    def tearDown(self):
        del self.keys
        del self.discsc_fit

    def test_parameter_recovery(self):
        model_dict = {}
        print(time.time())
        for key in self.keys:
            model_dict[key] = create_model_from_key(key)
        models = [model for key, model in model_dict.items()]
        for model in models:
            # self.discsc_fit.main_multi_channel(channels = [0, 1, 2, 3], model = model)
            self.discsc_fit._setup_labels(model) # for testing
            print(time.time())

            # self.discsc_fit._setup_labels(model) for testing
            lens_bounds = [(21.5, 22.2), (0.3, 5)]
            # self.discsc_fit.lens_calc(model = model, lens_bounds = lens_bounds)
            print(time.time())
        self.discsc_fit.get_evidence_from_models(model_dict = model_dict)


        # shutil.rmtree('test_products/0973_model_comparison_201')


if __name__ == '__main__':
    unittest.main()
    # shutil.rmtree('test_products/')
