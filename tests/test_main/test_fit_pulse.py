import unittest
import bilby
import numpy as np

from numpy.testing import (assert_almost_equal, assert_equal, assert_allclose,
                           assert_array_almost_equal, assert_)

from PyGRB.backend.makepriors import MakePriors
from PyGRB.main.fitpulse import PulseFitter
from PyGRB.backend.makemodels import create_model_from_key


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
        self.discsc_fit = PulseFitter(7475, times = (-2, 60),
                datatype = 'discsc', nSamples = nSamples, sampler = 'dynesty',
                priors_pulse_start = self.priors_pulse_start,
                priors_pulse_end = self.priors_pulse_end, HPC = True)

    def tearDown(self):
        del self.key
        del self.parameters
        del self.discsc_fit

    def test_parameter_recovery(self):
        model = create_model_from_key(self.key)
        self.discsc_fit.main_1_channel(channel = 1, model = model)
        # self.discsc_fit._setup_labels(model) for testing
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


if __name__ == '__main__':
    unittest.main()
