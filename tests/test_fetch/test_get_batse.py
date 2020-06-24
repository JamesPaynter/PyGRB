import os
import unittest

from PyGRB.fetch.get_BATSE import GetBATSEBurst


class TestFetchBATSE(unittest.TestCase):

    def setUp(self):
        self.trigger  = 105
        self.datatype = 'discsc'

    def tearDown(self):
        del self.trigger
        del self.datatype

    def test_datatype(self):
        datatype = "banana"
        with self.assertRaises(AssertionError):
            GetBATSEBurst(trigger = self.trigger, datatype = datatype)

    def test_trigger_not_found(self):
        trigger = 101
        with self.assertRaises(FileNotFoundError):
            GetBATSEBurst(trigger = trigger, datatype = self.datatype)

    def test_trigger_found(self):
        path = 'data/BATSE/discsc/discsc_bfits_105.fits.gz'
        try:
            os.remove(path)
            delete = False
        except:
            delete = True
        GetBATSEBurst(trigger = self.trigger, datatype = self.datatype)
        assert(os.path.exists(path))
        if delete:
            os.remove(path)
