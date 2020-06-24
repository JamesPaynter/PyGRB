import unittest
from PyGRB.preprocess.GRB_class import BATSEGRB

# def load_3770_tte(sampler = 'dynesty', nSamples = 100):
#     bilby_inst = PulseFitter(3770, times = (-.1, 1),
#                 datatype = 'tte_list', nSamples = nSamples, sampler = sampler,
#                 priors_pulse_start = -.1, priors_pulse_end = 0.6,
#                 priors_td_lo = 0,  priors_td_hi = 0.5,
#                 #### tte scaling is much lower than u think !!!!
#                 #### the scaling is not universal !!!!!
#             priors_scale_min = 1e-4,  priors_scale_max = 1e1,
#             priors_bg_lo     = 1e-4,  priors_bg_hi     = 1e1,
#             live_detectors = np.arange(5,8))
#     return bilby_inst
#

class TestBATSEGRB(unittest.TestCase):

    def setUp(self):
        self.burst    = 3770
        self.datatype = 'tte_list'

    def tearDown(self):
        del self.burst
        del self.datatype

    def test_burst_assignment_tte_list(self):
        burst = 3770
        datatype = 'tte_list'
        test = BATSEGRB(burst, datatype = datatype)
