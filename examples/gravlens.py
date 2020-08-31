import numpy as np

from PyGRB.main.fitpulse import PulseFitter
from PyGRB.backend.makemodels import create_model_from_key



def load_973(sampler = 'dynesty', nSamples = 100):
    test = PulseFitter(973, times = (-2, 50),
                datatype = 'discsc', nSamples = nSamples, sampler = sampler,
                priors_pulse_start = -5, priors_pulse_end = 50,
                priors_td_lo = 0,  priors_td_hi = 30, p_type ='docs')
    return test


def evidence_for_973():
    num_samples = [2000]
    for samples in num_samples:
        GRB = load_973(sampler=SAMPLER, nSamples=samples)
        keys = ['FL', 'FF']
        model_dict = {}
        for key in keys:
            model_dict[key] = create_model_from_key(key)
        models = [model for key, model in model_dict.items()]
        for model in models:
            GRB.main_multi_channel(channels = [0, 1, 2, 3], model = model)

            lens_bounds = [(21, 22.6), (0.25, 0.55)]
            GRB.lens_calc(model = model, lens_bounds = lens_bounds)
        GRB.get_evidence_from_models(model_dict = model_dict)


if __name__ == '__main__':
    SAMPLER = 'nestle'
    evidence_for_973()
