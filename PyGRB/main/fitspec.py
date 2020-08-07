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

        det = 5
        stte.live_detectors = [det]
        drm = drms.drm[f'Detector {det}']

        photons = stte.photons



        pm = PhotonMask(detector = det,
                        # channel_low = 4, channel_high = 255,
                        time_start = 1, time_stop = 15,
                        # energy_low = 10,
                        )

        photons = pm.get_masked_photons(stte.photons)

        u, counts = stte.get_counts_per_channel(photons)
        energy_bins = np.sort(np.unique(photons[:,5]))

        likelihood  = bilby.likelihood.PoissonLikelihood(
                                        energy_bins, counts, power_law)

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

        e_low  = np.sort(np.unique(photons[:,3]))
        e_high = np.sort(np.unique(photons[:,4]))
        true_fluxes = integral(e_low, e_high)
        fig, ax = plt.subplots()
        ax.step(e_low, e_high - e_low, where = 'pre', label = 'ebins')
        ax.step(e_low, true_fluxes, where = 'pre', label = 'model')
        ax.set_xscale('log')
        ax.set_yscale('log')
        plt.legend()
        # plt.show()

        folded_counts = np.dot(true_fluxes, drm.T)
        norm_folded_counts = folded_counts /  (e_high - e_low)
        norm_counts = counts / (e_high - e_low)

        map = dict()
        for parameter, i in priors.items():
            posterior_samples = result.posterior[parameter].values
            posterior_samples_median = np.median(posterior_samples)
            map[parameter] = posterior_samples_median


        fit = power_law(energy_bins, **map) / (e_high - e_low)
        fig, ax = plt.subplots()
        ax.plot(energy_bins, norm_counts, '.', label='data')
        ax.plot(energy_bins, norm_folded_counts, '.', label='folded')
        ax.plot(energy_bins, fit, '.r', label='fit')
        ax.set_xlabel('energy')
        ax.set_ylabel('counts / keV')
        ax.set_xscale('log')
        ax.set_yscale('log')
        for key, i in stte.spectral_lines.items():
            ax.axvline(i, c = 'k', linewidth = 0.1)
        for key, i in stte.spectral_lines_unknown.items():
            ax.axvline(i, c = 'k', linestyle = ':', linewidth = 0.1)
        ax.legend()
        fig.savefig('outdir/data.png')















































if __name__ == '__main__':
    S = SpecFitter()
    S.main()
