
from PyGRB.preprocess.BATSE.counts.ttebfits import TimeTaggedRates

GRB = TimeTaggedRates(3770, times = (-.1, 0.8))#, offsets = [-6e3, -1e3, 8e3, 7e3])
# GRB = TimeTaggedRates(973, times = (-2, 60))#, offsets = [-5e3, 0, 8e3, 7e3])
GRB.plot_lines()
# GRB._subtract_rough_backgrounds()
GRB.spectral_autocorrelation_triplet()
# GRB.spectral_autocorrelation_quadlet()
