from PyGRB.main.fitpulse import PulseFitter
from PyGRB.backend.makemodels import create_model_from_key

GRB = PulseFitter(7475, times = (-2, 60),
          datatype = 'discsc', nSamples = 200, sampler = 'nestle',
          priors_pulse_start = -10, priors_pulse_end = 30, p_type ='docs')

key = 'F'
model = create_model_from_key(key)
GRB.main_multi_channel(channels = [0, 1, 2, 3], model = model)
