"""
A preprocessing module to plot the BATSE data files.
Written by James Paynter, 2020.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from abc import ABC, abstractmethod

from matplotlib import rc

from PyGRB.utils.stats import get_Poisson_CI

rc('font',**{'family':'DejaVu Sans','serif':['Computer Modern']})
rc('text', usetex=True)

class AbstractClass(ABC):
    """ An abstract class with useful plotting subroutines. """

    # @abstractmethod
    # def plot_setup(self, *args, **kwargs):
    #     start = kwargs.get('start', self.t_start)
    #     stop  = kwargs.get('stop',  self.t_stop)
    #     channels = kwargs.get('channels', self.channels)
    #     return start, stop, channels

    @abstractmethod
    def plot_labels(self, ax):
        ax.set_title(
        f'BATSE trigger {self.trigger} {self.datatype} count data ({self.detector})')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Counts / second')
        ax.legend()

    def pplot_setup(self, **kwargs):
        start = kwargs.get('start', self.t_start)
        stop  = kwargs.get('stop',  self.t_stop)
        channels = kwargs.get('channels', self.channels)
        return start, stop, channels


class GammaRayBurstPlots(AbstractClass):

    def plot_setup(self, *args, **kwargs):
        """ Just used to allow access of the AbstractBaseClass. """
        super().plot_setup(*args, **kwargs)

    def plot_labels(self, *args, **kwargs):
        """ Just used to allow access of the AbstractBaseClass. """
        super().plot_labels(*args, **kwargs)

    def line_fit(self, ACF):
        """
        Fits a SavGol curve to the ACF.
        Dispersion is defined as per Hirose/Geiger paper.
        """
        ## created to remove the instant decorrelation artefact from moving
        ## forward one bin in extremely noisy data
        fit_ACF = np.array(ACF)
        fit_ACF[0] = fit_ACF[1]

        from scipy.signal import savgol_filter
        y_space = savgol_filter(fit_ACF, 101, 3)
        sigma = np.sqrt(sum(np.square(fit_ACF - y_space)) / len(ACF))
        return y_space, sigma

    def autocorrelate(self, channels, **kwargs):
        """
        Autocorrelate the light-curve.

        Channels are just indices so can pass in eg. [[1,2,3,4],[1],[2],[3],[4]]
        """
        start = kwargs.get('start', self.t_start)
        stop  = kwargs.get('stop',  self.t_stop)

        r = self.rates
        t = self.bin_left
        times = t[(t > start) & (t < stop)]
        rates = r[(t > start) & (t < stop)]
        delta_bin = times - times[0]
        acfs, y_spaces, sigmas, max_detections, the_bins = [], [], [], [], []
        for idx in channels:
            if len(idx) > 1:
                r = np.sum(rates[:,idx], axis = 1)
            else:
                [idx] = idx
                r = rates[:,idx]
            acf = np.correlate(r, r, mode='full')[len(r)-1:]
            acf = acf / np.amax(acf)
            y_space, sigma = self.line_fit(acf)

            cond_array = acf - (y_space + 3 * sigma)
            ## if the first element is positive (i.e. the polyfit is above the ACF)
            ## then return the index of the FIRST intercept between the two curves
            ## so not to return a false positive from the bad fit at the beginning
            if cond_array[0] > 0:
            	inds = np.where(acf - y_space < 0)
            	ind = inds[0][0] # returns first element of the array
            else:
            	ind = 0
            the_bin = delta_bin[ind + (acf[ind:] - y_space[ind:]).argmax()]
            ## returns (array, type)
            ## so the[0] on the end makes it only return the array
            my_list	= np.where(acf[ind:] - (y_space[ind:] + 3 * sigma) > 0)[0]
            my_list += ind
            detection = delta_bin[my_list]
            max_detection = np.round((np.max(acf[ind:] - y_space[ind:]) / sigma), 3)

            acfs.append(acf)
            sigmas.append(sigma)
            y_spaces.append(y_space)
            the_bins.append(the_bin)
            max_detections.append(max_detection)
        return delta_bin, acfs, y_spaces, sigmas, max_detections, the_bins

    def autocorrelationplot(self, channels, **kwargs):
        """
        """
        fig, ax = plt.subplots()
        delta_bin, acfs, y_spaces, sigmas = self.autocorrelate(channels, **kwargs)
        for i, (acf, y_space, sigma) in enumerate(zip(acfs, y_spaces, sigmas)):
            ax.plot(delta_bin, acf, label = f'Channel {channels[i]}')
            ax.plot(delta_bin, y_space, 'k:')
        plt.legend()
        plt.show()

    def spectral_autocorrelation_triplet(self, **kwargs):
        """ """
        # start, stop, channels = super().plot_setup(**kwargs)
        start, stop, channels = self.pplot_setup(**kwargs)

        # plotting setup
        width  = 3.321
        height = (3.321 / 2) * 3
        fig = plt.figure(figsize=(width, height))
        grid = gridspec.GridSpec(5, 1, height_ratios = [0.05, 1, 1, 1, 0.05],
                                        width_ratios = [1])
        grid.update(left=0.17, right=0.97,
                    bottom=0.07, top=0.93,
                    wspace=0.02, hspace=0)
        sum_lc_axes   = fig.add_subplot(grid[1,0])
        sum_acf_axes  = fig.add_subplot(grid[2,0])
        spec_acf_axes = fig.add_subplot(grid[3,0])

        # get light curve
        times, labs, arr = self.get_light_curve(start, stop, channels)
        # # plot under light curve
        # for i, label in enumerate(labs):
        #     sum_lc_axes.bar(times, arr[i,0,:], arr[i,1,:], label = f'channel {i}, {label}',
        #              bottom=arr[i,2,:], color = self.colours[i], align = 'edge')
        bin_edges = times
        rates = np.sum(arr[:,0,:],axis = 0)
        sum_lc_axes.step(bin_edges, rates/1e3, 'k-', where = 'post', linewidth = 0.6)

        sum_lc_axes.set_title('Time since trigger (s)', fontsize=8)
        sum_lc_axes.xaxis.tick_top()
        sum_lc_axes.set_ylabel('$10^3$ counts / second', fontsize=8)
        sum_lc_axes.set_xlim(left = start, right = stop)

        channels = [[0,1,2,3]]
        delta_bin, [acf], [y_space], [sigma], [max_detection], [the_bin] = \
            self.autocorrelate(channels, **kwargs)
        sum_acf_axes.plot(delta_bin, acf, #label = f'Channel sum',
                            c = 'k', linewidth = 0.6)
        sum_acf_axes.plot(delta_bin, y_space, 'k:', linewidth = 0.6)
        sum_acf_axes.axvline(the_bin, color = 'r', linestyle = ':', linewidth = 0.6)
        sum_acf_axes.fill_between(delta_bin, y_space +     sigma,
                            y_space -     sigma, alpha = 0.05, color = 'blue')
        sum_acf_axes.fill_between(delta_bin, y_space + 3 * sigma,
                            y_space - 3 * sigma, alpha = 0.05, color = 'blue')
        sum_acf_axes.fill_between(delta_bin, y_space + 5 * sigma,
                            y_space - 5 * sigma, alpha = 0.05, color = 'blue')

        sum_acf_axes.set_xticks(())
        sum_acf_axes.set_xlim(left = start, right = stop)
        sum_acf_axes.tick_params(labelsize = 8)
        sum_acf_axes.set_ylabel('$C(\\delta t)$', fontsize=8)

        sum_acf_axes.text(
		0.95, 0.95,
		f'{max_detection:.2f} $\\sigma$ detection\n'
        f'$\Delta t$ = {the_bin:.3f} seconds\n'
        f'Filter = SavGol\nPolynomial Order = 3\nWindow = 101',
        color = 'black', fontsize=8,
		transform = sum_acf_axes.transAxes,
		horizontalalignment='right', verticalalignment='top')

        channels = [[0],[1],[2],[3]]
        delta_bin, acfs, y_spaces, sigmas, max_detections, the_bins = \
                self.autocorrelate(channels, **kwargs)
        for i, (acf, y_space, sigma, m, b) in enumerate(
                zip(acfs, y_spaces, sigmas, max_detections, the_bins)):
            [ii] = channels[i]
            spec_acf_axes.plot( delta_bin, acf, #label = f'Channel {ii+1}',
                                c = self.colours[i], linewidth = 0.6,
            label = f'{m:.2f} $\\sigma$ detection at {b:.3f}s',
                                )
            spec_acf_axes.fill_between(delta_bin, y_space + 3 * sigma,
                y_space - 3 * sigma, alpha = 0.1, color = self.colours[i])

        spec_acf_axes.set_xlim(left = start, right = stop)
        spec_acf_axes.tick_params(labelsize = 8)
        spec_acf_axes.set_ylabel('$C(\\delta t)$', fontsize=8)
        spec_acf_axes.legend(fontsize = 8, frameon = False)
        spec_acf_axes.set_xlabel('Time since trigger (s)', fontsize=8)
        plt.show()

    def get_light_curve(self, start, stop, channels):
        """ """
        t = self.bin_left
        times  = t[(t > start) & (t < stop)]
        arr    = np.zeros((16,3,len(times)))
        bottom = np.zeros_like(times)
        labs = []
        for i in channels:
            a = self.rates[:,i][(t > start) & (t < stop)]
            b = self.bin_widths[(t > start) & (t < stop)]
            bin_lo = int(self.mean_energy_bin_edges[i])
            bin_hi = int(self.mean_energy_bin_edges[i+1])
            label  = f'{bin_lo} -- {bin_hi} keV'
            arr[i,0,:] = a
            arr[i,1,:] = b
            arr[i,2,:] = bottom
            labs.append(label)
            bottom += a
        return times, labs, arr

    def plot_stacked_bar(self, **kwargs):
        """ """
        start, stop, channels = super().plot_setup(**kwargs)


        fig, ax = plt.subplots(figsize = (16,8))
        times, labs, arr = self.get_light_curve(start, stop, channels)
        for i, label in enumerate(labs):
            ax.bar(times, arr[i,0,:], arr[i,1,:], label = f'channel {i}, {label}',
                     bottom=arr[i,2,:], color = self.colours[i], align = 'edge')

        super().plot_labels(ax)
        plt.show()

    def plot_lines(self, **kwargs):
        """ """
        offsets = kwargs.pop('offsets', self.offsets)
        start, stop, channels = self.pplot_setup(**kwargs)

        fig, ax = plt.subplots(figsize = (6,4))
        times, labs, arr = self.get_light_curve(start, stop, channels)
        for i, label in enumerate(labs):
            ax.step(times, arr[i,0,:] + offsets[i],
                    label = f'channel {i}, {label}',
                    color = self.colours[i],
                    where = 'pre', linewidth = 0.6,)
            error_lo, error_hi = get_Poisson_CI(0.318,
                (arr[i,0,:] * arr[i,1,:]).astype('int')) #/ arr[i,1,:]
            ax.fill_between(times,
                            arr[i,0,:] + error_hi + offsets[i],
                            arr[i,0,:] - error_lo + offsets[i],
                            step = 'pre',
                            color = self.colours[i],
                            alpha = 0.15)
        super().plot_labels(ax)
        plt.show()






































if __name__ == '__main__':
    pass
