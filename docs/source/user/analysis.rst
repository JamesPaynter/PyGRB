Application to Gravitational Lensing
====================================

This software package was created with the intent to discern similar looking gamma-ray bursts from statistically identical gamma-ray bursts.
Two statistically identical gamma-ray bursts would be indicative of a gravitational lensing event.

.. role:: python(code)
   :language: python

Application to candidate lenses
-------------------------------

.. figure:: ../images/BATSE_trigger_973_rates_rates.png
    :figwidth: 80%
    :width: 100%
    :align: center
    :alt: BATSE trigger 973.

    BATSE trigger 973.

----

.. literalinclude:: ../../../examples/gravlens.py
    :name: gravlens.py
    :caption: gravlens.py

----


Channel 1
+-------+----------+-------+--------+
| Model |   ln Z   | error | ln BF  |
+-------+----------+-------+--------+
| FL    | -3852.93 |  0.60 |  0.00  |
| FF    | -3623.66 |  0.67 | 229.27 |
+-------+----------+-------+--------+
Channel 2
+-------+----------+-------+--------+
| Model |   ln Z   | error | ln BF  |
+-------+----------+-------+--------+
| FL    | -3967.64 |  0.61 |  0.00  |
| FF    | -3665.85 |  0.68 | 301.79 |
+-------+----------+-------+--------+
Channel 3
+-------+----------+-------+--------+
| Model |   ln Z   | error | ln BF  |
+-------+----------+-------+--------+
| FL    | -4014.63 |  0.62 |  0.00  |
| FF    | -3640.90 |  0.70 | 373.73 |
+-------+----------+-------+--------+
Channel 4
+-------+----------+-------+-------+
| Model |   ln Z   | error | ln BF |
+-------+----------+-------+-------+
| FL    | -2986.56 |  0.57 |  0.00 |
| FF    | -2970.48 |  0.62 | 16.08 |
+-------+----------+-------+-------+




Notes
^^^^^
If you want to fit two pulses, one FRED and one FRED-X, but you do not know the order in which you would like to fit them in (eg. the two pulses are overlapping), then you will need to do both a ['FX'] model and a ['XF'] model.
The best fitting model is then the one with the higher Bayesian evidence.
This is because the order of the pulses is automatically encoded in the priors.
We do this so that the results are unimodal for degenerate cases, eg ['FF'].


GRB 950830
----------

.. figure:: ../images/trigger3770.PNG
    :figwidth: 80%
    :width: 100%
    :align: center
    :alt: BATSE trigger 3770 with FRED lens fit.

    BATSE trigger 3770 with FRED lens fit.

BATSE trigger 3770, GRB 950830, is the main subject of this analysis.
We first attempt to fit all possible combinations of pulse types.
We find that in the strong majority of cases, a lensing model is preferred over a model of two individual pulses.

Imports:

.. code-block:: python

  import numpy as np

  from PyGRB.main.fitpulse import PulseFitter
  from PyGRB.backend.makemodels import create_model_from_key


Set up the :python:`PulseFitter` object:

.. code-block:: python

  sampler  = 'dynesty'
  nSamples = 2000
  GRB = PulseFitter(3770, times = (-.1, 1),
                datatype = 'tte', nSamples = nSamples, sampler = sampler,
                priors_pulse_start = -.1, priors_pulse_end = 0.6,
                priors_td_lo = 0,  priors_td_hi = 0.5)


Note that in some rare instances the code will choose to fit a small residual quite late to the noise, and the 'gravitationally lens' that noise.
So in the case where one is fitting a lens model, a better choice of start time priors might be :python:`priors_pulse_end = 0.3`.

Set up the models to fit to the light-curve.
:python:`lens_keys` are a single pulse, which is then 'gravitationally lensed' -- the light-curve is duplicated at the time delay and rescaled by the magnification ratio.
:python:`null_keys` are two pulses.

.. code-block:: python

  lens_keys = ['FL', 'FsL', 'XL', 'XsL']
  null_keys = ['FF', 'FsFs', 'XX', 'XsXs']
  keys = lens_keys + null_keys

  model_dict = {}
  for key in keys:
      model_dict[key] = create_model_from_key(key)
  models = [model for key, model in model_dict.items()]


Then run the model fitting code with

.. code-block:: python

  for model in models:
      GRB.main_multi_channel(channels = [0, 1, 2, 3], model = model)


Parallelisation is done through the use of the indices parameter, which can be used to send one channel of one model to a different CPU in the cluster.
The difference would be changing the last two lines of code:

.. code-block:: python
  :emphasize-lines: 1-2,10-11

  # 8 models x 4 channels = 32 separate nested sampling runs.
  # This can be cheaply parallelised by sending each run to a different CPU
  lens_keys = ['FL', 'FsL', 'XL', 'XsL']
  null_keys = ['FF', 'FsFs', 'XX', 'XsXs']
  keys = lens_keys + null_keys

  model_dict = {}
  for key in keys:
      model_dict[key] = create_model_from_key(key)
  models = [model for key, model in model_dict.items()]

  indices = np.arange(32)
  GRB._split_array_job_to_4_channels(models = models, indices = indices, channels = [0, 1, 2, 3])


Example slurm (batch submission) scripts can be found in the dev-james branch of the repository.
After several days on a HPC, hopefully all the jobs will have finished.
The more parameters, the longer the job will take.
The :python:`'FsFs'` and :python:`'XsXs'` models having 18 and 20 parameters each, and may take up to a week depending on the chosen :python:`nSamples` (and other sampler kwargs).
Higher level analysis can be done with the :class:`~PyGRB.postprocess.make_evidence_tables.get_evidence_from_models` method:

.. code-block:: python

  GRB.get_evidence_from_models(model_dict = model_dict)


To create pretty plots of the gravitational lensing parameters, use the :python:`lens_calc` method:

.. code-block:: python

  for model in models:
      lens_bounds = [(0.37, 0.42), (0.60, 1.8)]
      GRB.lens_calc(model = model, lens_bounds = lens_bounds)


.. figure:: ../images/B_3770_YL2000__delmu_delt.png
    :figwidth: 80%
    :width: 100%
    :align: center
    :alt: BATSE trigger 3770 magnification ratio and time delay posterior histogram.

    BATSE trigger 3770 magnification ratio and time delay posterior histogram.


.. figure:: ../images/B_3770_YL2000__mass.png
    :figwidth: 80%
    :width: 100%
    :align: center
    :alt: BATSE trigger 3770 lens mass posterior histogram.

    BATSE trigger 3770 lens mass posterior histogram.

----

.. literalinclude:: ../../../examples/gravlensnature.py
    :name: gravlensnature.py
    :caption: gravlensnature.py

----


Investigation of the effects of priors on model selection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the following script we test the effect of the priors on :math:`\gamma` and :math:`\nu` on the model selection.

If one were to look at the same model with different input parameters, such as over a longer time period or with different initial priors, then one can save the two models in the dict under different names, eg.
This is utlised in the prior test script below.

.. code-block:: python

  keys = [key_1, key_2]
  model_dict['model 1'] = create_model_from_key(key_1)
  model_dict['model 2'] = create_model_from_key(key_2)
  models = [model for key, model in model_dict.items()]


----

.. literalinclude:: ../../../examples/gravlensnaturepriors.py
    :name: gravlensnaturepriors.py
    :caption: gravlensnaturepriors.py

----


Notes
^^^^^
The slurm scripts used to submit these jobs may be found in the dev-james branch of the project.
