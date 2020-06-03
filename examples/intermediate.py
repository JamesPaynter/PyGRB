from PyGRB.main.fitpulse import PulseFitter
from PyGRB.backend.makemodels import create_model_from_key

GRB = PulseFitter(7475, times = (-2, 60),
          datatype = 'discsc', nSamples = 200, sampler = 'nestle',
          priors_pulse_start = -5, priors_pulse_end = 30,
          p_type = 'docs', HPC = False, )


keys = ['G', 'F', 'X', 'Gs', 'Fs', 'Xs']
# the last three models will take a non-trivial time to run
model_dict = {}
for key in keys:
    model_dict[key] = create_model_from_key(key)
models = [model for key, model in model_dict.items()]

for model in models:
    GRB.main_multi_channel(channels = [0, 1, 2, 3], model = model)
