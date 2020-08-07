"""
A preprocessing module to unpack the BATSE data files.
Written by James Paynter, 2020.
"""

from astropy.io import fits
from PyGRB.fetch.get_BATSE import GetBATSEBurst

class BaseBATSE(object):
    """ A base class for BATSE rate / count data and detector response matrices.
    """

    def __init__(self, trigger, datatype, **kwargs):
        super(BaseBATSE, self).__init__()
        self.trigger  = trigger
        self.datatype = datatype
        self.times = kwargs.pop('times', 'full')

        fetch = GetBATSEBurst(trigger = self.trigger, datatype = self.datatype, **kwargs)
        with fits.open(fetch.path) as hdu_list:
            self.header           = hdu_list[0].header
            self.calibration_data = hdu_list[1].data
            try:
                # try to set count data
                self.count_data       = hdu_list[2].data
            except:
                # drms only have one data HDU.
                pass

    def _get_energy_bin_edges(self):
        """ Get the energy bin edges from the FITS file.
            Will have dimensions of (nEnergy_bins + 1, nTriggeredDetectors).
        """
        self.energy_bin_edges = self.calibration_data['E_EDGES']

    def _get_triggered_detectors(self):

        """ This is wrong. It gives detectors available in file. """

        self.triggered_detectors = self.calibration_data['CAL_DET']
        self.nTriggeredDetectors = len(self.triggered_detectors)

    def print_headers(self):
        """ Print the header info from the FITS file. """
        print('Header Data Unit Info')
        print('---------------')
        print(self.header)
        print('---------------')
        print('Header Data Unit Calibration Info')
        print('---------------')
        print(self.calibration_data.columns)
        print('---------------')
        try:
            print('Header Data Unit Calibration Info')
            print('---------------')
            print(self.count_data.columns)
            print('---------------')
        except:
            # drms only have one data HDU.
            pass

class SpectralDetectorBATSE(object):
    """docstring for SpectralDetectorBATSE."""

    def __init__(self):
        super(SpectralDetectorBATSE, self).__init__()
        self._set_spectral_lines()

    def _set_spectral_lines(self):
        """ The following are spectral lines seen in the constant background
        of BATSE's spectral detectors. See Schaefer et al. (1992), Figure 1.
        The spectral lines are listed in order of vFv strength.
        The electron-positron annihilation line at 511 keV is used to calibrate
        the gain of the SDs.

        There are more weak lines at 242, 292, 620, and 700 keV of unknown
        origin.
        """
        self.spectral_lines = { 'e-p annihilation'  : 511,
                                'potassium-decay'   : 1460,
                                'iodine-decay-1'    : 63,
                                'iodine-decay-2'    : 191,
                                }
        self.spectral_lines_unknown = {
                                'unknown-1'         : 242,
                                'unknown-2'         : 292,
                                'unknown-3'         : 620,
                                'unknown-4'         : 700,
                                }

        self.detector_area = 127.0 # cm^2

class LargeAreaDetectorBATSE(object):
    """docstring for LargeAreaDetectorBATSE."""

    def __init__(self):
        super(LargeAreaDetectorBATSE, self).__init__()


if __name__ == '__main__':
    pass
