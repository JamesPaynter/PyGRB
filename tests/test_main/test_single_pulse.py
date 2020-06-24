import os
import bilby
import shutil
import unittest
import numpy as np

from numpy.testing import (assert_almost_equal, assert_equal, assert_allclose,
                           assert_array_almost_equal, assert_)

from PyGRB.backend.admin import mkdir
from PyGRB.backend.makepriors import MakePriors
from tests.test_main.test_fit_pulse import PulseTester
from PyGRB.backend.makemodels import create_model_from_key



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
        del self.priors_pulse_start
        del self.priors_pulse_end
        del self.discsc_fit

    def test_parameter_recovery(self):
        model = create_model_from_key(self.key)
        self.discsc_fit.main_1_channel(channel = 1, model = model)
        result_label = f'{self.discsc_fit.fstring}{self.discsc_fit.clabels[1]}'
        open_result  = f'{self.discsc_fit.outdir}/{result_label}_result.json'
        result = bilby.result.read_in_result(filename=open_result)

        prior_shell = MakePriors(
                            priors_pulse_start = self.priors_pulse_start,
                            priors_pulse_end = self.priors_pulse_end,
                            channel      = 1,
                            **model)
        priors = prior_shell.return_prior_dict()

        posteriors = dict()
        for parameter in priors:
            posteriors[parameter] = np.median(result.posterior[parameter].values)
        for parameter in priors:
            assert( (abs(posteriors[parameter] - self.parameters[parameter]))
                    / self.parameters[parameter]) < 0.1
        shutil.rmtree('test_products/7475_model_comparison_201')
