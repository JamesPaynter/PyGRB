import numpy as np
import matplotlib.pyplot as plt

from PyGRB.preprocess import GRB_class
# from PyGRB.preprocess.GRB_class import BATSEGRB
from PyGRB.main.fitpulse import PulseFitter
from PyGRB.backend.makemodels import create_model_from_key


# for jj in [5,6,7]:
#     GRB = BATSEGRB(trigger = 3770, datatype = 'tte_list', live_detectors = [jj])
#     # GRB.bin_and_plot(binsize = 0.003)
#     # ax = plt.gca()
#     # ax.set_xlim(-0.2, 0.6)
#     # plt.show()
#     offsets = [0, 15, 50, 40]
#     fig, ax = plt.subplots()
#     GRB.bin(binsize = 9e-3)
#     for i in range(4):
#         ax.plot(GRB.bin_left, GRB.counts[:,i]+offsets[i], color = GRB.colours[i], drawstyle = 'steps')
#         ax.fill_between(GRB.bin_left,
#             GRB.counts[:,i] + np.sqrt(GRB.counts[:,i])+offsets[i],
#             GRB.counts[:,i] - np.sqrt(GRB.counts[:,i])+offsets[i],
#             step = 'pre', color = GRB.colours[i], alpha = 0.15)
#     # ax.set_xlim(-0.2, 0.6)
# plt.show()




def evidence_for_3770():
    num_samples = [501, 502, 503]
    detectors   = [5, 6, 7]
    for (samples, det) in zip(num_samples, detectors):
        pf = PulseFitter(3770, times = (-.1, 1),
                    datatype = 'tte', nSamples = samples, sampler = 'nestle',
                    priors_pulse_start = -.1, priors_pulse_end = 0.6,
                    priors_td_lo = 0,  priors_td_hi = 0.5)
        # GRB = BATSEGRB(trigger = 3770, datatype = 'tte_list', live_detectors = [5])
        pf.GRB = GRB_class.make_GRB(trigger = 3770, datatype = 'tte_list',
                                    live_detectors = [5], bin_data = True)
        import matplotlib
        matplotlib.use('TKAgg', force=True)
        import matplotlib.pyplot as plt
        plt.plot(pf.GRB.bin_left, pf.GRB.counts)
        plt.show()
        # lens_keys = ['FL', 'FsL', 'XL', 'XsL']
        # null_keys = ['FF', 'FsFs', 'XX', 'XsXs']
        # keys = lens_keys + null_keys
        keys = ['FL', 'FF', 'XX', 'XL']

        model_dict = {}
        for key in keys:
            model_dict[key] = create_model_from_key(key)
        models = [model for key, model in model_dict.items()]
        for model in models:
            pf.main_multi_channel(channels = [0, 1, 2, 3], model = model)
        pf.get_evidence_from_models(model_dict = model_dict)

def analysis_parallel(index):
    num_samples = [4000, 4001, 4002]
    detectors   = [5, 6, 7]
    for (samples, det) in zip(num_samples, detectors):
        if index > 31:
            index -+ 32
        pf = PulseFitter(3770, times = (-.1, 1),
                    datatype = 'tte', nSamples = samples, sampler = 'nestle',
                    priors_pulse_start = -.1, priors_pulse_end = 0.6,
                    priors_td_lo = 0,  priors_td_hi = 0.5)
        # GRB = BATSEGRB(trigger = 3770, datatype = 'tte_list', live_detectors = [5])
        pf.GRB = GRB_class.make_GRB(trigger = 3770, datatype = 'tte_list',
                                    live_detectors = [det], bin_data = True)

        model_dict = {}
        for key in keys:
            model_dict[key] = create_model_from_key(key)
        models = [model for key, model in model_dict.items()]

        GRB._split_array_job_to_4_channels( models   = models,
                                            indices  = index,
                                            channels = [0,1,2,3])

if __name__ == '__main__':
    evidence_for_3770()
