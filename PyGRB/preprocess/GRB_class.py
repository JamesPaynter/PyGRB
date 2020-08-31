import os
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.stats import bayesian_blocks

from PyGRB.backend.admin import mkdir
from PyGRB.preprocess.grb import EmptyGRB
from PyGRB.fetch.get_BATSE import GetBATSEBurst


def make_GRB(**kwargs):
    GRB = BATSEGRB(**kwargs)
    return GRB.return_GRB()


class BATSETTEList(object):
    """docstring for BATSETTEList."""

    def __init__(self, live_detectors = None):
        super(BATSETTEList, self).__init__()
        if self.verbose:
            print('Analysing BATSE TTE list data')

        fetch = GetBATSEBurst(trigger = self.trigger, datatype = self.datatype)
        with fits.open(fetch.path) as hdu_list:
            self._get_energy_bin_edges(hdu_list[1].data)
            count_data  = hdu_list[2].data

        self.detectors    = np.arange(8)
        self.det_count    = np.zeros( 8)
        self.photon_list  = []
        self.channel_list = []
        for i in range(8):
            det, num_phots, a1, a2, photons, channels = count_data[i]
            self.det_count[i] = num_phots
            self.photon_list.append(photons)
            self.channel_list.append(channels)

        if live_detectors is not None:
            self.live_detectors = live_detectors
        else:
            self.live_detectors = np.arange(8)
            print('Analysis running over all 8 detectors.')
            print('Would you rather analyse only the triggered detectors?')

        self.channel_1_times = self._sum_detectors(1)
        self.channel_2_times = self._sum_detectors(2)
        self.channel_3_times = self._sum_detectors(3)
        self.channel_4_times = self._sum_detectors(4)
        self.channels = [   self.channel_1_times, self.channel_2_times,
                            self.channel_3_times, self.channel_4_times]
        # channel x times are the photon arrival times in ANY channel.
        self.channel_x_times = self._sum_channels([1,2,3,4])
        self.sampling_rate = self._get_sampling_rate()
        if self.verbose:
            self._plot_arrival_histogram()

    def interpolate_data(self):
        times, ch1_rts = self._interpolate_bins(1)
        times, ch2_rts = self._interpolate_bins(2)
        times, ch3_rts = self._interpolate_bins(3)
        times, ch4_rts = self._interpolate_bins(4)
        if self.verbose:
            print(times.shape)
            print(ch1_rts.shape)
            print(ch2_rts.shape)
            print(ch3_rts.shape)
            print(ch4_rts.shape)

        self.bin_left  = times
        self.bin_right = times + self.sampling_rate
        self.counts    = np.zeros((len(self.bin_left),4))
        self.counts[:,0] = ch1_rts
        self.counts[:,1] = ch2_rts
        self.counts[:,2] = ch3_rts
        self.counts[:,3] = ch4_rts

    def _get_energy_bin_edges(self, energy_data):
        ### 8 detectors x 4 bins => 5 edges
        self.energy_bin_edges = np.zeros((8,5))
        for i in range(len(energy_data)):
            self.energy_bin_edges[i,:] = energy_data[i][3]
        if self.verbose:
            print('\n\nThe energy bin edges are (keV):')
            E = self.energy_bin_edges
            (a,b) = np.shape(E)
            for i in range(a):
                print(f'Detector {i}: {E[i,0]:.2f}, {E[i,1]:.2f}, {E[i,2]:.2f},'
                      f'{E[i,3]:.2f}, {E[i,4]:.2f}')
            print('\n\n')

    def _get_triggered_detectors(self):
        """ get triggered detectors. """
        pass

    def _sum_detectors(self, j):
        ''' j indexes channel '''
        ch_j = np.array([])
        # sum photons in the same channel and sort by arrival time
        for k in self.live_detectors:
            ch_j_det_k = self.photon_list[k][self.channel_list[k] == j]
            ch_j       = np.sort(np.hstack((ch_j, ch_j_det_k)))
        return ch_j

    def _sum_channels(self, channels):
        try:
            channels = np.array(channels, dtype = 'i')
        except:
            pass
        idx = channels - 1
        return np.sort(np.hstack(([self.channels[i] for i in idx])))

    def _get_sampling_rate(self, numbins = 100):
        unique_times  = np.unique(self.channel_x_times)
        sort_diff     = np.sort(np.diff(unique_times))
        logbins       = np.geomspace(sort_diff[0], sort_diff[-1], numbins)
        sampling_rate = np.mean(sort_diff[sort_diff < logbins[1]])
        std           = np.std( sort_diff[sort_diff < logbins[1]])
        if self.verbose:
            print(  'The sampling rate is %.6f +/- %.6f us'
                     % (sampling_rate * 1e6, std * 1e6))
        return sampling_rate

    def _interpolate_bins(self, channel = 'sum'):
        if channel == 'sum':
            arrival_times = self.channel_x_times
            string        = 'channel_sum'
        else:
            arrival_times = self.channels[int(channel - 1)]
            string        = f'channel_{channel}'

        direc = 'data/BATSE/TTE_list_data/'
        d_list    = [f'{d}' for d in self.live_detectors]
        dets      = ''.join(d_list)
        file_path = f'{string}_d{dets}'

        path = os.path.join(direc, file_path)

        count_str = f'{path}_counts.npy'
        bin_str   = f'{path}_bins.npy'
        diff_str  = f'{path}_diff.npy'

        unique, counts = np.unique(arrival_times, return_counts = True)
        sttt,endd = self.channel_x_times[0], self.channel_x_times[-1]
        num_bins  = int( ( endd - sttt )
                        / self.sampling_rate )

        try:
            self.interpolated_counts = np.load(count_str, allow_pickle = False)
            self.interpolated_bins   = np.load(bin_str,   allow_pickle = False)
            difference               = np.load(diff_str,  allow_pickle = False)
            new_bins = self.interpolated_bins
            new_counts = self.interpolated_counts
            print('Loaded previously interpolated data.')
        except:
            mkdir(direc)
            print('Interpolating data.')
            new_bins   = np.linspace(arrival_times[0], (arrival_times[0] +
                        (self.sampling_rate * num_bins)), num_bins  )
            og_bin_no  = len(unique)
            ## create a counts bin of req. len
            new_counts = np.zeros(len(new_bins))
            ## create a zero array of length of original arr
            difference = np.zeros(og_bin_no)
            for i in range(og_bin_no):
                ## find posn of photon in new bins cf old time
                difference[i] = np.abs(new_bins - unique[i]).min()
                new_counts[np.abs(new_bins - unique[i]).argmin()] = counts[i]
            self.interpolated_counts = new_counts
            self.interpolated_bins   = new_bins
            print('Finished data interpolation.')
            print('Saving difference...')
            np.save(diff_str,  difference, allow_pickle = False)
            print('Saving new counts...')
            np.save(count_str, new_counts, allow_pickle = False)
            print('Saving new bins...')
            np.save(bin_str,   new_bins,   allow_pickle = False)
            print('Done !')
        return new_bins, new_counts

    def _plot_arrival_histogram(self, channel = 'sum', numbins = 100):
        if channel == 'sum':
            arrival_times = self.channel_x_times
        else:
            arrival_times = self.channels[int(channel - 1)]

        unique_times, counts = np.unique(arrival_times, return_counts = True)
        sort_diff = np.sort(np.diff(unique_times))
        logbins   = np.geomspace(sort_diff[0], sort_diff[-1], numbins)
        plt.hist(sort_diff, bins = logbins)
        plt.xscale('log')
        plt.xlabel('Time to next photon (s)', fontsize = 12)
        plt.ylabel('Histogram counts', fontsize = 12)
        plt.show()

    def bin(self, channels = [0,1,2,3], binsize = 0.0050000027):
        start = self.channel_x_times[ 0]
        finis = self.channel_x_times[-1]
        Nbins = int( (finis - start) / binsize )
        bins  = np.linspace(start, start + binsize*Nbins, Nbins)
        self.bin_left  = bins[:-1]
        self.bin_right = bins[1:]
        self.counts = np.zeros((len(bins)-1,len(channels)))
        for i in channels:
            counts, bin_edges = np.histogram(self.channels[i], bins=bins)
            self.counts[:,i] = counts

    def bin_and_plot(self, channels = [0,1,2,3], binsize = 0.0050000027):
        fig, ax = plt.subplots()
        start = self.channel_x_times[ 0]
        finis = self.channel_x_times[-1]
        Nbins = int( (finis - start) / binsize )
        bins  = np.linspace(start, start + binsize*Nbins, Nbins)
        colours = ['r', 'orange', 'g', 'b']
        for i in channels:
            # times = np.hstack((self.channels[0], self.channels[1]))
            ch, binss = np.histogram(self.channels[i], bins=bins)
            # ch, binss = np.histogram(self.channels[i], bins=bins)
            ax.plot(bins[0:-1], ch, color = colours[i], drawstyle = 'steps')
            ax.fill_between(bins[0:-1], ch + np.sqrt(ch), ch - np.sqrt(ch),
                            step = 'pre', color = colours[i], alpha = 0.15)

        # plt.show()


class BATSEGRB(BATSETTEList):
    """docstring for BATSEGRB."""

    def __init__(self, trigger, datatype, verbose = False, **kwargs):
        self.colours   = ['red', 'orange', 'green', 'blue']
        self.clabels   = ['1', '2', '3', '4']
        self.datatypes = {'discsc':'discsc', 'tte':'tte', 'tte_list' : 'tte_list'}
        try:
            self.trigger = int(trigger)
        except:
            raise ValueError(
                'Input variable `burst` should be an integer. '
                'Is {} when it should be int.'.format(type(burst)))
        try:
            self.datatype = self.datatypes[datatype]
        except:
            raise AssertionError(
                'Input variable `datatype` is {} when it '
                'should be `discsc` or `tte`.'.format(datatype))
        self.verbose   = verbose

        bin_data = kwargs.pop('bin_data', False)
        super(BATSEGRB, self).__init__(**kwargs)

        self.kwargs    = {  'colours'   : self.colours,
                            'clabels'   : self.clabels,
                            # 'labels'    : self.labels,
                            'datatype'  : self.datatype,
                            'burst'     : self.trigger,
                            'satellite' : 'BATSE'}
        if bin_data:
            self.bin()

    def return_GRB(self):
        """ Creates a new GRB object with only bins and rates. """
        return EmptyGRB(self.bin_left, self.bin_right, self.counts, **self.kwargs)

if __name__ == '__main__':
    pass
