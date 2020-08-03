import os
import unittest

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



class TestABP(unittest.TestCase):
    def setUp(self):

        self.priors_pulse_start = -10
        self.priors_pulse_end   =  20
        self.parameters = {'background_b' : 183,
                            'start_1_b' : -5.47,
                            'scale_1_b' : 263.3,
                            'tau_1_b'   : 14.4,
                            'xi_1_b'    : 2.3}
        self.nSamples = 167
        self.channels = [0, 1, 2, 3]
        self._path = 'test_products/7475_model_comparison_167/BATSE_trigger_7475_discsc_rates'

    def tearDown(self):
        del self.priors_pulse_start
        del self.priors_pulse_end
        del self.parameters
        del self.channels
        del self.nSamples
        del self._path

    def test_presentation_plot(self):
        GRB = PulseTester(7475, times = (-2, 60),
                datatype = 'discsc', nSamples = self.nSamples,
                sampler = 'dynesty',
                priors_pulse_start = self.priors_pulse_start,
                priors_pulse_end = self.priors_pulse_end,
                HPC = True, p_type = 'presentation')
        GRB.plot_lc(channels = self.channels, return_axes = False)
        self.path = f'{self._path}.png'
        assert(os.path.exists(self.path))
        os.remove(self.path)

    def test_docs_plot(self):
        GRB = PulseTester(7475, times = (-2, 60),
                datatype = 'discsc', nSamples = self.nSamples,
                sampler = 'dynesty',
                priors_pulse_start = self.priors_pulse_start,
                priors_pulse_end = self.priors_pulse_end,
                HPC = True, p_type = 'docs')
        GRB.plot_lc(channels = self.channels, return_axes = False)
        self.path = f'{self._path}.png'
        assert(os.path.exists(self.path))
        os.remove(self.path)

    def test_paper_one_col_plot(self):
        GRB = PulseTester(7475, times = (-2, 60),
                datatype = 'discsc', nSamples = self.nSamples,
                sampler = 'dynesty',
                priors_pulse_start = self.priors_pulse_start,
                priors_pulse_end = self.priors_pulse_end,
                HPC = True, p_type = 'paper_one_col')
        GRB.plot_lc(channels = self.channels, return_axes = False)
        self.path = f'{self._path}.pdf'
        assert(os.path.exists(self.path))
        os.remove(self.path)

    def test_paper_two_col_plot(self):
        GRB = PulseTester(7475, times = (-2, 60),
                datatype = 'discsc', nSamples = self.nSamples,
                sampler = 'dynesty',
                priors_pulse_start = self.priors_pulse_start,
                priors_pulse_end = self.priors_pulse_end,
                HPC = True, p_type = 'paper_two_col')
        GRB.plot_lc(channels = self.channels, return_axes = False)
        self.path = f'{self._path}.pdf'
        assert(os.path.exists(self.path))
        os.remove(self.path)

    # def test_thesis_plot(self):
    #     GRB = PulseTester(7475, times = (-2, 60),
    #             datatype = 'discsc', nSamples = self.nSamples,
    #             sampler = 'dynesty',
    #             priors_pulse_start = self.priors_pulse_start,
    #             priors_pulse_end = self.priors_pulse_end,
    #             HPC = True, p_type = 'thesis')
    #     GRB.plot_lc(channels = self.channels, return_axes = False)
    #     self.path = f'{self._path}.pdf'
    #     # not implemented yet
    #     # assert(os.path.exists(self.path))
    #
    # def test_animation_plot(self):
    #     GRB = PulseTester(7475, times = (-2, 60),
    #             datatype = 'discsc', nSamples = self.nSamples,
    #             sampler = 'dynesty',
    #             priors_pulse_start = self.priors_pulse_start,
    #             priors_pulse_end = self.priors_pulse_end,
    #             HPC = True, p_type = 'animation')
    #     GRB.plot_lc(channels = self.channels, return_axes = False)
    #     self.path = f'{self._path}.png'
    #     # not implemented yet
    #     # assert(os.path.exists(self.path))

if __name__ == '__main__':
    unittest.main()
