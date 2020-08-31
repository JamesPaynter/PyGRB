from PyGRB.main.fitpulse import PulseFitter
from PyGRB.backend.makemodels import create_model_from_key

GRB = PulseFitter(3770, times = (-0.1, 0.3),
          datatype = 'tte', nSamples = 200, sampler = 'nestle',
          priors_pulse_start = -.2, priors_pulse_end = .2, p_type ='docs')

key = 'FF'
model = create_model_from_key(key)
GRB.main_multi_channel(channels = [0, 1, 2, 3], model = model)
