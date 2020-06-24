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

        _path = 'data/BATSE/TTE_list_data/'
        path = f'{_path}channel_{1}_d01234567_{"bins"}.npy'

        if os.path.exists(path):
            delete = False
        else:
            delete = True


        test = BATSEGRB(burst, datatype = datatype)
        assert(os.path.exists(path))

        if delete:
            for c in range(4):
                for q in ["bins", "diff", "counts"]:
                    path = f'{_path}channel_{c}_d01234567_{q}.npy'
                    os.remove(path)


if __name__ == '__main__':
    unittest.main()
