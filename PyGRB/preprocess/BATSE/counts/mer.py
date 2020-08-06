import numpy as np
import matplotlib.pylab as pl

from PyGRB.preprocess.BATSE.counts.basecounts import BaseBurstBATSE

class MediumEnergyResolution(BaseBurstBATSE):
    """A class to analyse BATSE mer data. """

    def __init__(self, trigger, *args, **kwargs):
        super(MediumEnergyResolution, self).__init__(trigger, datatype = 'mer',
                                                     *args, **kwargs)
        self._get_mean_energy_bin_edges()
        self.colours  = pl.cm.jet(np.linspace(0,1,self.nChannels))[::-1]
        self.detector = 'LAD'


    def _get_mean_energy_bin_edges(self):
        """
        """
        self.mean_energy_bin_edges = np.sum(
                        self.calibration_data['E_EDGES'], axis = 0) / 3


if __name__ == '__main__':
    a = MediumEnergyResolution(6404, times = 'T100')
    a.plot_stacked_bar()
