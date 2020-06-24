import os
import unittest


from PyGRB.preprocess.GRB_class import BATSEGRB


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
        path = 'data/BATSE/TTE_list_data/channel_1_d01234567_bins.npy'
        assert(os.path.exists(path))


if __name__ == '__main__':
    unittest.main()
