import numpy as np
from scipy.stats import gamma
import matplotlib.pyplot as plt
from astropy.io import fits

from PyGRB.utils.stats import get_Poisson_CI
from PyGRB.preprocess.BATSE.detectors.base import BaseBATSE
from PyGRB.preprocess.BATSE.detectors.base import SpectralDetectorBATSE


class SpectralPrivate(BaseBATSE, SpectralDetectorBATSE):
    """ Private methods for SpectralTTE. """

    def __init__(self, *args, **kwargs):
        super(SpectralPrivate, self).__init__(*args, **kwargs)
        self._array_init_value = -800.01

    @staticmethod
    def _make_array(parameter):
        """
        Checks if a parameter is a numpy array. If not, it assumes it is a
        list or single value, and tries to return it as an array.
        Fails if this is not possible.

        This is done even for single values as some functions expect to be
        passed arrays.

        Parameters
        ----------
        parameter: int, float, list, ndarray
            The parameter to be made into an array.

        Returns
        -------
        parameter: ndarray
            The parameter as an array.
        """
        if not isinstance(parameter, (np.ndarray)):
            try:
                parameter = np.array([parameter])
            except TypeError as error:
                print(error)
        return parameter

    @staticmethod
    def _check_detectors(detectors):
        """Checks the detectors are correctly labelled from 0-7."""
        allowed_detectors = np.arange(8)
        unique_detectors  = np.unique(detectors).astype('int')
        stacked_detectors = np.unique(np.hstack((unique_detectors, allowed_detectors)))
        assert np.array_equal(allowed_detectors, stacked_detectors),    (
            "BATSE has 8 spectral detectors (SDs). "
            "These SDs should be labelled from 0-7. "
           f"You have passed in {unique_detectors}. "                   )

    @staticmethod
    def _check_channels(channels):
        """Checks the channels are correctly labelled from 0-255."""
        allowed_channels = np.arange(256)
        unique_channels  = np.unique(channels).astype('int')
        stacked_channels = np.unique(np.hstack((unique_channels, allowed_channels)))
        assert np.array_equal(allowed_channels, stacked_channels),         (
            "BATSE's spectral detectors (SDs) have 256 energy channels. "
            "These channels should be labelled from 0-255. "
           f"You have passed in {unique_channels}. "                       )

    def _check_array_init_value_clear(self, array):
        """Check all array elements have been changed from initialised value."""
        assert not np.any(np.isclose(array, self._array_init_value)),   (
            f"An element of the photon array {array} has not been set. "
             "Check that the number of photons listed in the FITS file "
             "matches the number of photons in the initialised array. "  )

    # def _get_energy_bin_edges(self):
    #     """
    #
    #     Note: Only 253 bin edges are given (for 252 bins), but there are 256
    #     channels of stte data. The lower 4 are not used.
    #     See https://ui.adsabs.harvard.edu/link_gateway/2000ApJS..126...19P/
    #     Section 2.2 Energy Coverage.
    #
    #     """
    #     self.energy_bin_edges = np.zeros((8,253))
    #     for i in range(len(self.calibration_data)):
    #         self.energy_bin_edges[i,:] = self.calibration_data[i][3]

    def _get_photon_number(self):
        """ """
        nPhotons = np.zeros(8, 'int')
        for i in range(8):
            nPhotons[i] = self.count_data[i][1].astype('int')
        self.nPhotons     = np.sum(nPhotons)
        self.nLivePhotons = np.sum(nPhotons[self.live_detectors])

    def _get_photon_list(self):
        """ """
        n = 0
        photons = np.zeros((self.nPhotons, 7)) + self._array_init_value
        for i in range(8):
            det, num_phots, t_start, t_stop, times, channels = self.count_data[i]
            self._check_detectors(det)
            self._check_channels(channels)
            photons[:,0][n:num_phots+n] = det
            photons[:,1][n:num_phots+n] = times
            photons[:,2][n:num_phots+n] = channels
            n+=num_phots

        self._check_array_init_value_clear(photons[:,0])
        self._check_array_init_value_clear(photons[:,1])
        self._check_array_init_value_clear(photons[:,2])
        self.photons = photons

    def _match_photon_energies(self):
        """

        The bottom four energy channels are not used !

        Note: Only 253 energy bin edges are given (for 252 bins), but there are
        256 channels of stte data. The lower 4 are not used.
        See https://ui.adsabs.harvard.edu/link_gateway/2000ApJS..126...19P/
        Section 2.2 Energy Coverage.
        """
        e = np.zeros((8,257))
        for i in range(8):
            e[i,0]  = self.energy_bin_edges[i,0] * 0.35 # these are fake
            e[i,1]  = self.energy_bin_edges[i,0] * 0.40 # these are fake
            e[i,2]  = self.energy_bin_edges[i,0] * 0.45 # these are fake
            e[i,3]  = self.energy_bin_edges[i,0] * 0.50 # these are fake
            e[i,4:] = self.energy_bin_edges[i,:]

        photon_energies = np.zeros((self.nPhotons, 4)) + self._array_init_value
        for i in range(self.nPhotons):
            det = int(self.photons[i, 0])
            bin = int(self.photons[i, 2])
            energy_low  = e[det,bin]
            energy_high = e[det,bin + 1]
            photon_energies[i,0] = energy_low
            photon_energies[i,1] = energy_high

            # e_mid = (e_low + e_high) / 2
            e_mid  = 10**( (np.log10(energy_low) + np.log10(energy_high)) / 2)
            e_diff = energy_high - energy_low
            photon_energies[i,2] = e_mid
            photon_energies[i,3] = e_diff

        self._check_array_init_value_clear(photon_energies[:,0])
        self._check_array_init_value_clear(photon_energies[:,1])
        self._check_array_init_value_clear(photon_energies[:,2])
        self._check_array_init_value_clear(photon_energies[:,3])
        self.photons[:,3] = photon_energies[:,0]
        self.photons[:,4] = photon_energies[:,1]
        self.photons[:,5] = photon_energies[:,2]
        self.photons[:,6] = photon_energies[:,3]

    def _get_source_angles(self):
        """ Get the angles between the source and each detector normal.
            Get the angles between the Earth (geocentre) and each detector normal.

            If the Earth's centre is within 100 degrees of a BATSE burst then
            atmospheric scattering at ~100 keV is significant.
            Schaefer et al. (1992) limit to > 300 keV in these instances.
        """
        self.detector_source_angles = self.calibration_data['DET_S_ZN']
        self.detector_earth_angles  = self.calibration_data['DET_E_ZN']

class SpectralTTE(SpectralPrivate):
    """ An object to represent BATSE spectral time tagged event triggers.

    """

    def __init__(self, trigger, **kwargs):
        super(SpectralTTE, self).__init__(trigger, datatype = 'stte_list')
        self.colours = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red',
                        'tab:purple', 'tab:brown', 'tab:pink', 'tab:grey']

        self._get_triggered_detectors()
        self.live_detectors = kwargs.get('live_detectors',
                                            self.triggered_detectors)
        self._get_source_angles()
        self._get_energy_bin_edges()
        self._get_photon_number()
        self._get_photon_list()
        self._match_photon_energies()

    def diagnostics(self):
        """Creates a pdf file with all the interim diagnostic plots."""
        from matplotlib.backends.backend_pdf import PdfPages
        with PdfPages("diagnostics.pdf") as pdf:
            for i in self.live_detectors:
                fig, ax = self.plot_counts_hist(detectors = [i], return_axes = True,
                                                show_plot = False, vlines = False)
                pdf.savefig(fig)
                plt.close()
            fig, ax = self.plot_counts_hist(detectors = self.live_detectors,
                                            return_axes = True,
                                            show_plot = False, vlines = False)
            pdf.savefig(fig)
            plt.close()
            for i in self.live_detectors:
                fig, ax = self.plot_energy_hist(detectors = [i], return_axes = True,
                                                show_plot = False, plot = 'barplot',
                                                channel_mask = (5, 255))
                pdf.savefig(fig)
                plt.close()
            fig, ax = self.plot_energy_hist(detectors = self.live_detectors,
                                            return_axes = True,
                                            show_plot = False, plot = 'barplot',
                                            channel_mask = (5, 255))
            pdf.savefig(fig)
            plt.close()

    def diagnostics3770(self):
        from matplotlib.backends.backend_pdf import PdfPages
        with PdfPages("diagnostics.pdf") as pdf:
            for i in self.live_detectors:
                fig, ax = self.plot_energy_hist(detectors = [i], return_axes = True,
                                                show_plot = False, plot = 'barplot',
                                                channel_mask = (0, 255),
                                                # time_mask = (0.35, 0.5))
                                                time_mask = (-.05, 0.1))
                norm = (15 - 1 ) / (0.15)
                colours = ['blue']*8
                fig2, ax2 = self.plot_energy_hist(detectors = [i], return_axes = True,
                                                show_plot = False, plot = 'barplot',
                                                channel_mask = (0, 255),
                                                time_mask = (1,15),
                                                normalisation = norm,
                                                axes = (fig, ax),
                                                colours =  colours)
                pdf.savefig(fig2)
                plt.close()

    def plot_light_curve(self, **kwargs):
        detectors = kwargs.get('detectors', self.live_detectors)
        channels  = kwargs.get('channels',  np.arange(256))
        show_plot = kwargs.get('show_plot', True)
        # uses python indexing convention [start included, end not included)
        (strt, end) = kwargs.get('time_mask', (-1e5, 1e5))
        (bin_st, bin_en) = kwargs.get('channel_mask', (0, 256))
        if show_plot:
            plt.show()

    def plot_waterfall(self, **kwargs):
        """ """
        if show_plot:
            plt.show()

    def plot_counts_hist(self, **kwargs):
        """ """
        detectors = kwargs.get('detectors', self.live_detectors)
        channels  = kwargs.get('channels',  np.arange(256))
        show_plot = kwargs.get('show_plot', True)
        cut_ovflw = kwargs.get('cut_overflow', False)
        vlines    = kwargs.get('vlines', True)
        fig, ax   = kwargs.get('axes', plt.subplots())
        return_axes = kwargs.get('return_axes', False)

        m = [(4, 2, 90/8 * i) for i in range(8)]
        fig, ax = plt.subplots()
        for i in detectors:
            ax.scatter( np.arange(253)+3.5, self.energy_bin_edges[i,:],
                        s = 20, marker = m[i], c = self.colours[i],
                        label = f'Detector {i} Energy Bins')
        ax.set_yscale('log')
        ax.set_xlabel('Channel')
        ax.set_ylabel('Energy (keV)')

        if vlines:
            for i in range(257):
                ax.axvline(i-.5, c = 'k', linewidth = 0.1)

        ax2 = ax.twinx()
        for i in detectors:
            histo, edges = np.histogram(
                        self.photons[:,2][self.photons[:,0].astype('int')==i],
                        bins = np.arange(256)+0.5
                        )
            if cut_ovflw:
                e, h = edges[:-2], histo[:-1]
            else:
                e, h = edges[:-1], histo
            ax2.bar(e, h,   width = 1, alpha = 0.3,
                            color = self.colours[i], align = 'edge',
                            label = f'Detector {i} Counts')
        ax2.set_yscale('log')
        ax2.set_ylabel('Counts')
        fig.legend(loc = 1)
        if show_plot:
            plt.show()
        if return_axes:
            return fig, ax

    def plot_energy_hist(self, **kwargs):
        detectors = kwargs.get('detectors', self.live_detectors)
        channels  = kwargs.get('channels',  np.arange(256))
        show_plot = kwargs.get('show_plot', True)
        plot      = kwargs.get('plot', 'barplot')
        # uses python indexing convention [start included, end not included)
        (strt, end) = kwargs.get('time_mask', (-1e5, 1e5))
        (bin_st, bin_en) = kwargs.get('channel_mask', (0, 256))
        return_axes = kwargs.get('return_axes', False)
        fig, ax = kwargs.get('axes', plt.subplots())
        colours = kwargs.get('colours', self.colours)
        normalisation = kwargs.get('normalisation', 1)

        for i in detectors:
            e_mid = self.photons[:,5][  (self.photons[:,0].astype('int')==i)
                                      & (self.photons[:,2].astype('int')>=bin_st)
                                      & (self.photons[:,2].astype('int')<bin_en)
                                      & (self.photons[:,1] > strt)
                                      & (self.photons[:,1] <= end)]

            logbins = np.logspace(np.log10(np.min(e_mid)),np.log10(np.max(e_mid)),100)
            histo, edges = np.histogram(e_mid, bins = logbins)
            errors = np.zeros((2, len(histo)))
            for kk, hist in enumerate(histo):
                # 1 sigma errors
                errors[:,kk] = get_Poisson_CI(0.318, hist)

            histo   = histo  / normalisation
            errors  = errors / normalisation

            errors[0,:] = histo - errors[0,:]
            errors[1,:] = errors[1,:] - histo

            bin_centres = 10**( (np.log10(edges[1:]) + np.log10(edges[:-1])) / 2)

            if plot == 'scatterplot':
                bin_widths  = np.zeros((2, len(histo)))
                bin_widths[0,:] = bin_centres - edges[:-1]
                bin_widths[1,:] = edges[1:] - bin_centres
                ax.errorbar(bin_centres, histo,
                            xerr = bin_widths,
                            yerr = errors,
                            linestyle="None", color = colours[i])

            elif plot == 'barplot':
                bin_widths = edges[1:] - edges[:-1]
                ax.bar( edges[:-1], histo, width = bin_widths,
                        alpha = 0.3, color = colours[i], align = 'edge')

        ax.set_title(f'{strt}, {end}')
        ax.set_xscale('log')
        # ax.set_yscale('log')
        ax.set_xlabel('Energy (keV)')
        ax.set_ylabel('Counts')
        labels = [f'Detector {detectors[i]}' for i in range(len(detectors))]
        plt.legend(labels)

        if show_plot:
            plt.show()
        if return_axes:
            return fig, ax

    def _normalise_counts(self, photons, live_time):
        def _detector_area_normalisation(detector):
            """ Calculate the effective cross-sectional area of the detector,
            the area normal to the gamma-ray burst.

            Parameters
            ----------

            Detector: int
                The detector to calculate the effective area for.

            Returns
            -------

            effective_area: float
                The effective collecting area of the detector.
                Might be superceded by the detector response matrices?

            """
            alpha = self.detector_source_angles[detector.astype('int')]
            effective_area = self.detector_area * np.abs(np.cos(alpha * np.pi / 2))
            return effective_area

        # normalisation array for each photon
        norms = 1. / live_time / photons[:,6] #/ self.detector_area
        #/ _detector_area_normalisation(photons[:,0])
        # get number of channels in photon data
        # ASSUMES ALL PHOTONS ARE FROM THE SAME DETECTOR
        unique_channels, channel_idx = np.unique(photons[:,2], return_inverse=True)
        # histogram the data into channel bins
        # associates
        rates = norms[channel_idx]
        unique = np.unique(channel_idx)
        rates = np.zeros(len(unique))
        for i, idx in enumerate(unique):
            rates[i] = np.sum(norms[channel_idx[channel_idx==idx]])
        x_axis = np.sort(np.unique(photons[:,5]))
        y_axis = rates # * np.square(x_axis / 200)
        plt.plot(x_axis, y_axis, drawstyle = 'steps-mid', label = f'Detector {int(photons[0,0])}')
        plt.xscale('log')
        plt.yscale('log')
        # plt.plot(channels, counts, drawstyle = 'steps-mid')
        # plt.show()

        return x_axis, y_axis

    def make_spectra(self, **kwargs):
        detectors = kwargs.get('detectors', self.live_detectors)
        (src_strt, src_end) = kwargs.get('src_time_mask', (-1e5, 1e5))
        (bg_strt, bg_end)   = kwargs.get('bg_time_mask', (-1e5, 1e5))
        (bin_st, bin_en)    = kwargs.get('channel_mask', (0, 256))
        (e_low, e_high)     = kwargs.get('energy_mask', (1e-1, 2e5))

        base_mask = kwargs.get('base_mask', None)

        for i in detectors:
            base_mask['detector'] = i
            src_mask = PhotonMask(**base_mask, time_start = src_strt, time_stop = src_end)
            bg_mask  = PhotonMask(**base_mask, time_start = bg_strt, time_stop = bg_end)
            on_source_photons = src_mask.get_masked_photons(self.photons)
            off_source_photons = bg_mask.get_masked_photons(self.photons)

            bg_time = bg_end - bg_strt
            bg_energies, bg_spectra = self._normalise_counts(off_source_photons, bg_time)

            source_time = src_end - src_strt
            energies, spectra = self._normalise_counts(on_source_photons, source_time)

            bins = 10
            logbins  = np.logspace(np.log10(np.min(off_source_photons[:,5])),
                                   np.log10(np.max(off_source_photons[:,5])), bins)
            new_x = np.zeros(bins-1)
            new_y = np.zeros(bins-1)
            for j in range(bins-1):
                for k, E in enumerate(energies):
                    if (E > logbins[j]) & (E <= logbins[j+1]):
                        new_x[j] += spectra[k]
                for k, E in enumerate(bg_energies):
                    if (E > logbins[j]) & (E <= logbins[j+1]):
                        new_y[j] += bg_spectra[k]

        plt.legend()
        plt.show()

    @staticmethod
    def get_counts_per_channel(photons):
        """ Pass in the full photon array. """
        channels = photons[:,2].astype('int')
        nChannels = len(np.unique(channels))
        u = np.sort(np.unique(channels))
        if nChannels == len(u):
            u, counts = np.unique(photons[:,2], return_counts = True)
        else:
            counts = np.zeros(nChannels)
            for i in channels:
                counts[i] += 1
        return u.astype('int'), counts













if __name__ == '__main__':
    pass
