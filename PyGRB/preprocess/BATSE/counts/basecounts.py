"""
A preprocessing module to unpack the BATSE data files.
Written by James Paynter, 2020.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


from PyGRB.preprocess.BATSE.detectors.base import BaseBATSE

class BaseBurstBATSE(BaseBATSE):
    """ A base class for BATSE burst data. """

    def __init__(self, *args, **kwargs):
        super(BaseBurstBATSE, self).__init__(*args, **kwargs)

        self.rates      = self.count_data['RATES']
        self.bin_left   = self.count_data['TIMES'][:,0]
        self.bin_right  = self.count_data['TIMES'][:,1]
        self.bin_widths = self.bin_right - self.bin_left

        (self.nBins, self.nChannels) = np.shape(self.rates)
        self.channels = np.arange(self.nChannels)

        self._get_time_edges()

    def _get_time_edges(self):
        """ Define the start and stop time of the burst. """
        try:
            (self.t_start, self.t_stop) = self.times
        except:
            if self.times == 'T90':
                self._read_T90_table()
            elif self.times == 'T100':
                self._read_T90_table()
                self.t_start = min(-2, self.t_start)
                self.t_stop += max(5, 0.25 * self.t90)
            elif self.times == 'full':
                self.t_start, self.t_stop = self.bin_left[0], self.bin_right[-1]

    def _open_T90_excel(self):
        """ Open the BATSE 4B csv information file. """
        xls_file = f'../../../data/BATSE_4B_catalogue.xls'
        path = Path(__file__).parent / xls_file
        cols = ['trigger_num', 't90', 't90_error', 't90_start']
        dtypes = {  'trigger_num': np.int32, 't90' : np.float64,
                    't90_error' : np.float64, 't90_start' : np.float64}
        try:
            table = pd.read_excel(path, sheet_name = 'batsegrb', header = 0,
                                    usecols = cols, dtype = dtypes)
            return table
        except FileNotFoundError as fnf_error:
                    print(fnf_error)

    def _read_T90_table(self):
        """
        Opens the BATSE T90 bursts as a pandas object. Searches for the
        current burst's trigger, T90, T90 error, and T90 start time.
        Throws an exception if the burst is not found in the T90 table.
        (i.e. no T90 exists for this burst).
        """
        table = self._open_T90_excel()
        self.burst_list     = table['trigger_num']
        self.t90_list       = table['t90']
        self.t90_err_list   = table['t90_error']
        self.t90_st_list    = table['t90_start']
        try:
            self.t90 = float(self.t90_list[self.burst_list == self.trigger])
            self.t90_err = float(self.t90_err_list[self.burst_list == self.trigger])
            self.t_start = float(self.t90_st_list[self.burst_list == self.trigger])
            self.t_stop = self.t_start + self.t90
        except:
             raise Exception('There is no T90 for this trigger in the BATSE 4B'
                             'catalogue. Try `full` or enter custom times as a'
                             'tuple, i.e. (start, end).')

    def plot_stacked_bar(self, **kwargs):
        """ """
        start = kwargs.get('start', self.t_start)
        stop  = kwargs.get('stop',  self.t_stop)
        channels = kwargs.get('channels', self.channels)


        fig, ax = plt.subplots(figsize = (16,8))
        bottom = 0
        t = self.bin_left
        times = t[(t > start) & (t < stop)]
        for i in channels:
            a = self.rates[:,i][(t > start) & (t < stop)]
            b = self.bin_widths[(t > start) & (t < stop)]
            bin_lo = int(self.mean_energy_bin_edges[i])
            bin_hi = int(self.mean_energy_bin_edges[i+1])
            label  = f'{bin_lo} -- {bin_hi} keV'
            ax.bar(times, a, b, label = f'channel {i}, {label}',
                         bottom=bottom, color = self.colours[i],
                         align = 'edge')
            bottom += a
        ax.set_title(f'BATSE trigger {self.trigger} {self.datatype} count data ({self.detector})')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Counts / second')
        ax.legend(ncol = 1)
        plt.show()
