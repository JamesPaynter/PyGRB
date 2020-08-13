import numpy as np

from PyGRB.preprocess.BATSE.drm.basedrm import SpectralDRM
from PyGRB.preprocess.BATSE.tte.basette import SpectralTTE
from PyGRB.preprocess.BATSE.tte.photonmask import PhotonMask

import bilby
# from bilby import likelihood.PoissonLikelihood as bilbyPoissonLikelihood
from bilby.core.prior import PriorDict         as bilbyPriorDict
from bilby.core.prior import Uniform           as bilbyUniform
from bilby.core.prior import LogUniform        as bilbyLogUniform

# def background_model()
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt


def power_law(energy, norm, index):
    return norm * np.power(energy/100.,index)

def differential_flux(e):
    return power_law(e, .01, -2)

# integral of the differential flux
def integral(e1, e2):
    # return (e2 - e1) / (differential_flux(e1) + differential_flux(e2)) / 2
    return (e2 - e1) / 6.0 * (differential_flux(e1)
    + 4 * differential_flux((e1 + e2) / 2.0)+ differential_flux(e2))



class SpecFitter(object):
    """docstring for SpecFitter."""

    def __init__(self):
        super(SpecFitter, self).__init__()

    def main(self):
        drms = SpectralDRM(3770)
        stte = SpectralTTE(3770)
        stte._get_energy_bin_edges()

        det = 7
        stte.live_detectors = [det]
        drm = drms.drm[f'Detector {det}']

        photons = stte.photons



        pm = PhotonMask(detector = det,
                        channel_low = 4, channel_high = 255,
                        time_start = 1, time_stop = 15,
                        # energy_low = 10,
                        )

        photons = pm.get_masked_photons(stte.photons)

        u, counts   = stte.get_counts_per_channel(photons)
        energy_bins = np.sort(np.unique(photons[:,5]))
        channels    = np.sort(np.unique(photons[:,2].astype('int'))) - 4
        # print(channels)


        channnnels = np.sort(np.unique(stte.photons[:,2]))
        print(len(channnnels))




        # e_low  = np.sort(np.unique(photons[:,3]))
        # e_high = np.sort(np.unique(photons[:,4]))

        # PHA channels from drm
        e_low  = drms.energy_channels[f'Detector {det}'][:-1] # len 258
        e_high = drms.energy_channels[f'Detector {det}'][1:]  # len 258
        e_mid = (e_high + e_low) / 2
        # integrate PHA channels
        true_fluxes = integral(e_low, e_high) # len 258

        # fig, ax = plt.subplots()
        # ax2 = ax.twinx()
        # ax.bar(e_low, height = true_fluxes, width = e_high - e_low,
        #         align = 'edge', label = 'model', alpha = 0.5, fill = 'False',
        #         facecolor = 'None', edgecolor = 'k')
        # ax2.scatter(e_mid, e_high - e_low, marker = '.', label = 'ebins')
        # ax.set_xscale('log')
        # ax.set_yscale('log')
        # ax.set_ylabel(r'Differential Photon Flux $\frac{d N_p}{dt dA}$')
        # ax2.set_yscale('log')
        # ax2.set_ylabel('Energy Bin Width')
        # plt.legend()
        # # plt.show()
        print(np.shape(drm)) # (252, 258), 252 real channels, 258 PHA channels

        # convolve true_fluxes with drm to get dN/dt
        folded_counts = np.dot(true_fluxes, drm.T) # len 252 normalises by area

        dE = np.diff(drms.energy_bins[f'Detector {det}']) # len 252
        norm_folded_counts = folded_counts / dE # len 252
        # norm_counts = counts / dE


        def folded_power_law(energy_bins, norm, index):

            def _power_law(energy, norm, index):
                return norm * np.power(energy/100.,index)

            def _differential_flux(e):
                return power_law(e, .01, -2)

            # integral of the differential flux
            def _integral(e1, e2):
                return (e2 - e1) / 6.0 * (_differential_flux(e1)
                + 4 * _differential_flux((e1 + e2) / 2.0)+ _differential_flux(e2))

            e_high = energy_bins[1:]
            e_low  = energy_bins[:-1]
            true_fluxes = _integral(e_low, e_high)
            # print(len(true_fluxes))
            dot = np.dot(true_fluxes, drm[:,channels].T) / dE
            # print('drm', np.shape(drm[:,channels]))
            # print('dot', len(dot))
            # print('dot', dot[channels])
            return dot[7:]

        # PHA energy bins (keV) for photons
        energy_low  = np.sort(np.unique(photons[:,3]))
        energy_high = np.sort(np.unique(photons[:,4]))
        energy_bins = np.hstack((energy_low, energy_high[-1]))

        print('energy_low', len(energy_low))
        print('energy_high', len(energy_high))
        print('energy_bins', len(energy_bins))
        print('counts', np.shape(counts))
        likelihood  = bilby.likelihood.PoissonLikelihood(
                                        energy_bins, # with len 247
                                        counts, # counts with len 246
                                        folded_power_law # a function
                                        )

        priors = bilbyPriorDict()
        priors['norm'] = bilbyLogUniform(1e-4, 1e2, 'normalisation')
        priors['index']= bilbyUniform(-5, -.1, 'spectral index')

        import os
        try:
            os.remove('outdir/spec_result.json.old')
        except:
            pass


        result = bilby.run_sampler(
        likelihood=likelihood, priors=priors, sampler='dynesty', nlive=500,
        sample='unif', outdir='outdir',
        label='spec')

        result = bilby.result.read_in_result(filename='outdir/spec_result.json')
        result.plot_corner()


















        map = dict()
        for parameter, i in priors.items():
            posterior_samples = result.posterior[parameter].values
            posterior_samples_median = np.median(posterior_samples)
            map[parameter] = posterior_samples_median

        energy_lo  = drms.energy_bins[f'Detector {det}'][:-1]
        energy_hi  = drms.energy_bins[f'Detector {det}'][1:]
        energy_mid = (energy_hi + energy_lo) / 2
        fit = power_law(energy_mid, **map) / dE
        # fit = power_law(energy_bins, **map) / (e_high - e_low)
        fig, ax = plt.subplots()
        # ax.plot(e_mid, norm_counts, '.', label='data')
        ax.scatter(energy_mid, norm_folded_counts, label='folded') # , marker = '.'
        ax.scatter(energy_mid, fit, label='fit', color = 'r') # , marker = '.'
        ax.set_xlabel('energy')
        ax.set_ylabel('counts / keV')
        ax.set_xscale('log')
        ax.set_yscale('log')
        for key, i in stte.spectral_lines.items():
            ax.axvline(i, c = 'k', linewidth = 0.3)
        for key, i in stte.spectral_lines_unknown.items():
            ax.axvline(i, c = 'k', linestyle = ':', linewidth = 0.3)
        ax.legend()
        plt.show()
        # fig.savefig('outdir/data.png')















































if __name__ == '__main__':
    pass
    # S = SpecFitter()
    # S.main()
