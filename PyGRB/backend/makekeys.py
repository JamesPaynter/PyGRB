import numpy as np

class MakeKeys(object):
    """
        Doc string goes here.
    """
    gauss_list   = ('start', 'scale', 'sigma')
    conv_list    = ('start', 'scale', 'sigma', 'tau')
    FRED_list    = ('start', 'scale', 'tau', 'xi')
    FREDx_list   = ('start', 'scale', 'tau', 'xi', 'gamma', 'nu')

    res_sg_list  = ('sg_A', 'res_begin', 'sg_lambda', 'sg_omega', 'sg_phi')
    res_bes_list = ('bes_A', 'bes_Omega', 'bes_s', 'res_begin', 'bes_Delta')

    param_lists  = (gauss_list, FRED_list, FREDx_list,
                    conv_list, res_sg_list, res_bes_list)


    def __init__(self, lens, channel, **kwargs):
        super(MakeKeys, self).__init__()

        self.lens         = lens
        self.lens_list    = ['time_delay', 'magnification_ratio']
        self.c = self.get_channel_key(channel)

        # its bad to have a mutable default
        # but it doesnt matter since they are never muted at runtime
        # but should change this
        self.count_gauss  = kwargs.get('count_gauss',   [])
        self.count_FRED   = kwargs.get('count_FRED',    [])
        self.count_FREDx  = kwargs.get('count_FREDx',   [])
        self.count_conv   = kwargs.get('count_conv',    [])
        self.count_sg     = kwargs.get('count_sg',      [])
        self.count_bes    = kwargs.get('count_bes',     [])
        self.max_pulse    = kwargs.get('max_pulse',     [])

        self.pulse_counts = [self.count_gauss, self.count_FRED,
                             self.count_FREDx, self.count_conv]
        self.res_counts   = [self.count_sg,    self.count_bes]
        self.rate_counts  = self.pulse_counts + self.res_counts
        # self.test_pulse_keys(count_FRED, count_FREDx)
        # self.test_residual_keys(count_sg, count_bes)


        self.keys = []
        self._get_max_pulse()
        self.get_residual_list()
        self.fill_keys_list()

    def _get_max_pulse(self):
        max_pulse = 0
        for count_list in self.rate_counts:
            try:
                if count_list[-1] > max_pulse:
                    max_pulse = count_list[-1]
            except:
                pass
        self.max_pulse = max_pulse

    @staticmethod
    def get_channel_key(channel):
        c_keys = ['a', 'b', 'c', 'd']
        return c_keys[channel]

    def fill_list(self, key_list, array):
        return [f'{key_list[k]}_{i}_{self.c}' for k in range(len(key_list))
                                              for i in array]

    def fill_keys_list(self):
        if self.lens:
            self.keys += self.lens_list
        self.keys += [f'background_{self.c}']
        for p_list, p_type in zip(self.param_lists, self.rate_counts):
            self.keys += self.fill_list(p_list, p_type)

    def get_residual_list(self):
        mylist = self.count_sg + self.count_bes
        myarr  = np.array(mylist)
        myarr  = np.unique(myarr)
        mysort = np.sort(myarr)
        mylist = [mysort[i] for i in range(len(mysort))]
        self.residual_list = mylist

    @classmethod
    def _get_pulse_from_key_list(cls, keys):
        """ A method to return the name of the pulse type based on the keys.

        Parameters
        ----------

        keys: str, list
            The list of keys to test.

        Returns
        -------

        pulse: str
            The type of pulse.

        """
        pulses = dict()
        pulses[cls.gauss_list]  = 'Gaussian Pulse'
        pulses[cls.FRED_list]   = 'FRED Pulse'
        pulses[cls.FREDx_list]  = 'FRED-X Pulse'
        pulses[cls.conv_list]   = 'Convolution Pulse'
        pulses[cls.res_sg_list] = 'Sine-Gaussian residual Pulse'
        for list in cls.param_lists:
            if ((len(keys) == len(list)) and (all(k in list for k in keys))):
                return pulses[list]

    # @staticmethod
    # def test_pulse_keys(count_FRED, count_FREDx):
    #     self.test_continuous(count_FRED, count_FREDx)
    #     self.test_no_duplicates(count_FRED, count_FREDx)
    #
    # @staticmethod
    # def test_residual_keys(count_sg, count_bes):
    #     self.test_no_duplicates(count_sg, count_bes)
    #
    # @staticmethod
    # def test_no_duplicates(*args):
    #     pass
    #
    # @staticmethod
    # def test_continuous(*args):
    #     s = set([arg for arg in *args])
    #     n = max(s)
    #     pulse_list = [i+1 for i in range(n)]

if __name__ == '__main__':
    pass
