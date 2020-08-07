import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from matplotlib.colors import LogNorm
from matplotlib.colors import SymLogNorm
from matplotlib import cm


from PyGRB.preprocess.BATSE.detectors.base import BaseBATSE


class SpectralDRM(BaseBATSE):
    """docstring for SpectralDRM."""

    def __init__(self, trigger, *args, **kwargs):
        super(SpectralDRM, self).__init__(trigger, datatype = 'stte_list_drm',
                                            *args, **kwargs)

        self.detectors = np.array(self.calibration_data['DET_NUM'])

        self.drm = dict()

        for i in self.detectors:
            self.get_channel_drm(i)
        # for i in range(5,8):
        #     self.plot_drm(i)
        # plt.show()
        # fig, ax = plt.subplots()
        # for i in range(8):
        #     self.plot_fold(i, ax)
        # plt.show()

    def __str__(self):
        return (f'A spectral time tagged photon drm object for BATSE trigger'
                f'{self.trigger}')


    def get_channel_drm(self, channel):
        num_energy_bins     = self.calibration_data['NUMEBINS'][channel]
        num_energy_channels = self.calibration_data['NUMCHAN'][channel]
        num_zeroes          = self.calibration_data['NUMZERO'][channel]
        energy_bins         = self.calibration_data['E_EDGES'][channel]
        energy_channels     = self.calibration_data['PHT_EDGE'][channel]
        sum_drm             = self.calibration_data['SUMDRM'][channel]
        drm_sum             = self.calibration_data['DRM_SUM'][channel]
        # first non-zero element of array (1-indexed)
        drm_zeroes          = self.calibration_data['N_ZEROS'][channel]

        drm = np.zeros((num_energy_channels - 1, num_energy_bins - 1)) - 1e-15
        n_tot = 0
        for i in range(num_energy_channels - 1):
            n = drm_zeroes[i] - 1 # convert 1-index to python 0-index
            drm[i,n:] = drm_sum[n_tot:n_tot+258-n] + 2e-15
            n_tot += 258-n

        self.drm[f'Detector {channel}'] = drm

    def plot_drm(self, detector):

        fig, ax = plt.subplots()

        # extent = energy_channels[0], energy_channels[-1], \
        # energy_bins[0], energy_bins[-1]
        # im = ax.imshow(drm[:-1,:], extent = extent, origin = 'lower',
        #                 cmap = 'inferno', interpolation = 'None',
        #                 norm=LogNorm(vmin=vmin, vmax=np.max(drm[:-1,:])))

        drm  = self.drm[f'Detector {detector}']
        vmin = 1e-2
        vmax = np.max(drm)
        im = ax.pcolormesh(
            self.calibration_data['PHT_EDGE'][detector],
            self.calibration_data['E_EDGES'][detector],
            drm,
            cmap='inferno',
            norm=LogNorm(vmin=vmin, vmax=vmax),
            )
        ax.set_title(f'Detector {detector} Response Matrix')
        ax.set_xlabel('Incident Photon Energy (keV)')
        ax.set_ylabel('Channel Energy (keV)')
        ax.set_xscale('log')
        ax.set_yscale('log')
        fig.colorbar(im)

    def plot_fold(self, detector, axes):
        e_low  = self.calibration_data['PHT_EDGE'][detector][:-1]
        e_high = self.calibration_data['PHT_EDGE'][detector][1:]

        edges = self.calibration_data['E_EDGES'][detector]
        dE = np.diff(edges)

        true_fluxes = integral(e_low, e_high)
        folded_counts = np.dot(true_fluxes, self.drm[f'Detector {detector}'].T)

        axes.plot(edges[1:], folded_counts / dE, drawstyle = 'steps-pre')
        axes.set_xscale('log')
        axes.set_yscale('log')

if __name__ == '__main__':
    pass
