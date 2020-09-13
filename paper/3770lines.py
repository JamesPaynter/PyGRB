import numpy as np
import matplotlib.pyplot as plt

import bilby
from PyGRB.preprocess import BATSEpreprocess


times = (-.1, 1)
trigger = 3770
datatype = 'tte'

GRB = BATSEpreprocess.make_GRB(
    burst = trigger, times = times,
    datatype = datatype, bgs = False)

for i in range(1,5):
    print(i)
    loc = f'products/3770_model_comparison_2000/'
    loc+= f'lens_model_1_XsL_large_box_log_flat_nr'
    loc+= f'/B_3770_YL2000__result_{i}_result.json'
    # loc = f'products/3770_model_comparison_2000/lens_model_1_XsXs_large_box_log_flat_nr/B_3770_YL2000__result_{i}_result.json'
    result = bilby.result.read_in_result(loc)

    # keys = ['XsXs', 'XsL']
    posteriors = dict()
    for parameter in priors:
        posteriors[parameter] = result.posterior[parameter].values
    p_chain_len = len(posteriors[f'background_{k}'])


    key = 'XsL'
    plt.plot(GRB.bin_left, 1)
