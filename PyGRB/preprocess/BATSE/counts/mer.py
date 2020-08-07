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
        self._get_energy_bin_edges()
        self._get_triggered_detectors()
        self.mean_energy_bin_edges = np.sum(self.energy_bin_edges, axis = 0
                                            ) / self.nTriggeredDetectors


if __name__ == '__main__':
    a = MediumEnergyResolution(3770, times = 'T90')
    a.plot_stacked_bar()

# make an argparse thing to plot ifmain -b 8099 -save True -t T90
# abstract it in another file so it can be used for all ddatatypes.
