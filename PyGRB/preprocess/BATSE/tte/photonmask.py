import numpy as np

class PhotonMask(object):
    """ A PhotonMask class for (spectral) time-tagged event data (tte/stte). """

    def __init__(self, **kwargs):
        super(PhotonMask, self).__init__()
        self.detector       = kwargs.get('detector', None)
        self.channel_low    = kwargs.get('channel_low', 0)
        self.channel_high   = kwargs.get('channel_high', 256)
        self.time_start     = kwargs.get('time_start', None)
        self.time_stop      = kwargs.get('time_stop', None)
        self.energy_low     = kwargs.get('energy_low', 1e-1)
        self.energy_high    = kwargs.get('energy_high', 1e6)

        self.mask = {   'detector'     : self.detector,
                        'channel_low'   : self.channel_low,
                        'channel_high'  : self.channel_high,
                        'time_start'    : self.time_start,
                        'time_stop'     : self.time_stop,
                        'energy_low'    : self.energy_low,
                        'energy_high'   : self.energy_high,
                    }

    def get_masked_photons(self, photons):
        """
        Returns the photons that satisfy the masking conditions. """
        masked_photons = photons[
                        (photons[:,0].astype('int')==self.detector)
                    &   (photons[:,2].astype('int')>=self.channel_low)
                    &   (photons[:,2].astype('int')< self.channel_high)
                    &   (photons[:,1]>=self.time_start)
                    &   (photons[:,1]< self.time_stop)
                    &   (photons[:,5]>=self.energy_low)
                    &   (photons[:,5]< self.energy_high)
                        ]
        return masked_photons
