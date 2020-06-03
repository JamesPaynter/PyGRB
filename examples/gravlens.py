import sys, os
import argparse
import numpy as np

from PyGRB.main.fitpulse import PulseFitter
from PyGRB.backend.makemodels import create_model_from_key
from PyGRB.backend.makemodels import make_two_pulse_models


def load_973(sampler = 'dynesty', nSamples = 100):
    test = PulseFitter(973, times = (-2, 50),
                datatype = 'discsc', nSamples = nSamples, sampler = sampler,
                priors_pulse_start = -5, priors_pulse_end = 50,
                priors_td_lo = 0,  priors_td_hi = 30)
    return test


def analysis_for_973(indices):
    num_samples = [500]
    for samples in num_samples:
        GRB = load_973(sampler=SAMPLER, nSamples=samples)
        GRB.offsets = [0, 4000, 8000, -3000]
        GRB.test_two_pulse_models(indices, channels = [0, 1, 2, 3])


def evidence_for_973():
    num_samples = [500]
    for samples in num_samples:
        GRB = load_973(sampler=SAMPLER, nSamples=samples)
        GRB.offsets = [0, 4000, 8000, -3000]
        keys = ['FL', 'FF']
        model_dict = {}
        for key in keys:
            model_dict[key] = create_model_from_key(key)
        models = [model for key, model in model_dict.items()]
        for model in models:
            GRB.main_multi_channel(channels = [0, 1, 2, 3], model = model)

            lens_bounds = [(0.37, 0.42), (0.60, 1.8)]
            GRB.lens_calc(model = model, lens_bounds = lens_bounds)
        GRB.get_evidence_from_models(model_dict = model_dict)


if __name__ == '__main__':
    SAMPLER = 'nestle'
    analysis_for_973(np.arange(8))
    evidence_for_973()
