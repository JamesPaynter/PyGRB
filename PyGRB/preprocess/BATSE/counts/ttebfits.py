import numpy as np
import matplotlib.pylab as pl

from PyGRB.preprocess.BATSE.counts.basecounts import BaseBurstBATSE

class TimeTaggedRates(BaseBurstBATSE):
    """A class to analyse BATSE tte prebinned data. """

    def __init__(self, trigger, *args, **kwargs):
        super(TimeTaggedRates, self).__init__(trigger, datatype = 'tte',
                                                     *args, **kwargs)
        self._get_mean_energy_bin_edges()
        self.colours  = pl.cm.jet(np.linspace(0,1,self.nChannels))[::-1]
        self.detector = 'LAD'

        self.colours = ['red', 'orange', 'green', 'blue']


    def _get_mean_energy_bin_edges(self):
        """
        """
        self._get_energy_bin_edges()
        self._get_triggered_detectors()
        self.mean_energy_bin_edges = np.sum(self.energy_bin_edges, axis = 0
                                            ) / self.nTriggeredDetectors





if __name__ == '__main__':
    pass

# make an argparse thing to plot ifmain -b 8099 -save True -t T90
# abstract it in another file so it can be used for all ddatatypes.
