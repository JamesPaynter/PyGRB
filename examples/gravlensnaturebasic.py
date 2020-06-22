import sys, os
import argparse

from PyGRB.main.fitpulse import PulseFitter
from PyGRB.backend.makemodels import create_model_from_key
from PyGRB.backend.makemodels import make_two_pulse_models



def load_3770(sampler = 'dynesty', nSamples = 100, **kwargs):
    test = PulseFitter(3770, times = (-.1, 1),
                datatype = 'tte', nSamples = nSamples, sampler = sampler,
                priors_pulse_start = -.1, priors_pulse_end = 0.6,
                priors_td_lo = 0,  priors_td_hi = 0.5, p_type ='docs', **kwargs)
    return test


def evidence_for_3770():
    num_samples = [500]
    for samples in num_samples:
        GRB = load_3770(sampler = SAMPLER, nSamples = samples)
        GRB.offsets = [0, 4000, 8000, -3000]

        keys = ['FL', 'FF']
        model_dict = {}
        for key in keys:
            model_dict[key] = create_model_from_key(key)
        models = [model for key, model in model_dict.items()]

        for model in models:
            GRB.get_residuals(channels = [0, 1, 2, 3], model = model)
            # GRB.main_multi_channel(channels = [0, 1, 2, 3], model = model)
            lens_bounds = [(0.37, 0.42), (0.60, 1.8)]
            GRB.lens_calc(model = model, lens_bounds = lens_bounds)
        GRB.get_evidence_from_models(model_dict = model_dict)


if __name__ == '__main__':
    SAMPLER = 'nestle'
    evidence_for_3770()
