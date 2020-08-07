

from PyGRB.preprocess.BATSE.detectors.base import BaseBATSE
from PyGRB.preprocess.BATSE.detectors.base import SpectralDetectorBATSE


class ScheduledBATSE(BaseBATSE):
    """docstring for ScheduledBATSE."""

    def __init__(self, *args, **kwargs):
        super(ScheduledBATSE, self).__init__(*args, **kwargs)


class ScheduledSD(BaseBATSE, SpectralDetectorBATSE):
    """docstring for ScheduledSD."""

    def __init__(self, trigger, datatype = 'sher_', *args, **kwargs):
        super(ScheduledSD, self).__init__()








class ScheduledLAD(BaseBATSE):
    """docstring for ScheduledLAD."""

    def __init__(self):
        super(ScheduledLAD, self).__init__()
