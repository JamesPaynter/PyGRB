Usage
=====

.. role:: python(code)
   :language: python

.. figure:: ../images/BATSE_trigger_7475_rates_rates.png
   :figwidth: 80%
   :width: 80%
   :align: center
   :alt: BATSE trigger 7475

   BATSE trigger 7475


.. include::
  ../../../README.rst
  :start-after: inclusion-marker-usage-start
  :end-before: inclusion-marker-usage-end


----

The complete script for the above tutorial is here:

.. literalinclude:: ../../../examples/basic.py
    :name: basic.py
    :caption: basic.py

----

Something like the following will be printed to the console:

.. code-block:: console

  18:55 bilby INFO    : Single likelihood evaluation took 4.089e-04 s
  18:55 bilby INFO    : Using sampler Nestle with kwargs {'method': 'multi', 'npoints': 200, 'update_interval': None, 'npdim': None, 'maxiter': None, 'maxcall': None, 'dlogz': None, 'decline_factor': None, 'rstate': None, 'callback': <function print_progress at 0x00000185F8598AE8>, 'steps': 20, 'enlarge': 1.2}
  it=  6048 logz=-4174.731348
  18:55 bilby INFO    : Sampling time: 0:00:15.464772
  18:55 bilby INFO    : Summary of results:
  nsamples: 6249
  log_noise_evidence:    nan
  log_evidence: -4174.477 +/-  0.368
  log_bayes_factor:    nan +/-  0.368

The total number of posterior samples, `nsamples`, in this instance is 6249.
This is the length of posterior chains accessed through the code block at the bottom of this page.
The `log_noise_evidence` is used for `Bilby`'s gravitational wave inference.
It is irrelevant for `PyGRB`, as `PyGRB`'s Poisson likelihood does not specify an additional noise model.
The `log_evidence` is the Bayesian evidence in support of this data given the specified model.
The Bayes factor is the comparison of evidence between two models.
Here, `log_bayes_factor` is `NaN` as there is only one model specified, and the comparison cannot be made.
`PyGRB` does it's model comparison external to the inbuilt `Bilby` functionality.

Errors like the following can be ignored.

.. code-block:: console

  RuntimeWarning: overflow encountered in multiply ...

They are bad evaluations of the likelihood and have no real effect on the results.
In the unlikely event that they happen consistently, it may mean that the sampler is stuck in a bad region of parameter space.
Restarting the sampler for that particular evaluation should fix the problem.


This will create three sets of files in the products directory.

1.  Nested sampling posterior chains, which are stored as JSON files.

2.  Corner plots of the posteriors.

3.  Higher data products, the light-curves of each of the individual channels.
    These include by default analysis of the light-curve fit residuals to test for goodness-of-fit.


These are put into subdirectories based on the trigger number and the number of live points. Files for this example can be found under `/products/7475_model_comparison_200/`.


.. figure:: ../images/B_7475__d_NL200__rates_F.png
    :figwidth: 80%
    :width: 100%
    :align: center
    :alt: BATSE trigger 7475

    BATSE trigger 7475 with FRED fit


.. figure:: ../images/trigger7475chan3.PNG
    :figwidth: 80%
    :width: 100%
    :align: center
    :alt: BATSE trigger 7475 channel 3

    BATSE trigger 7475 with FRED pulse fit on a single channel (channel 3).
    The green shaded regions are the 1-sigma statistical (Poisson) uncertainty.
    The correlogram is a visualisation of the autocorrelation of the residuals in the second panel.
    For a "good" fit, one expects 95% (99%) of the points to lie within the 95% (99%) confidence intervals.
    It is interesting to note in this case there is a sinusoidal structure all the way to the end of the pulse, even though the deviations from the fit are not large.
    The probability plot tests the divergence of the residuals from zero for normality.
    Again we see that the residuals are normally distributed to a good approximation.


.. figure:: ../images/trigger7475post3.PNG
    :figwidth: 80%
    :width: 100%
    :align: center
    :alt: BATSE trigger 7475 channel 3 corner plot

    BATSE trigger 7475 with FRED pulse fit  on a single channel (channel 3) posterior corner plot.
    The parameter space is undersampled, (the posterior histograms are patchy), but that does not matter since this tutorial is for illustrative purposes only.



In answer to our initial question, pulse parameters may be read straight of the posterior distribution (or accessed through the posterior chain JSON file).

The following code block could be appended to the end of *basic.py*

.. code-block:: python

  # pick a channel to analyse
  channel = 0

  # create the right filename to open
  result_label = f'{GRB.fstring}{GRB.clabels[channel]}'
  open_result  = f'{GRB.outdir}/{result_label}_result.json'
  result = bilby.result.read_in_result(filename=open_result)

  # channel 0 parameters are subscripted with _a
  parameter = 'background_a'

  # the posterior samples are accessed through the result object
  posterior_samples = result.posterior[parameter].values

  # to find the median
  import numpy as np
  posterior_samples_median = np.median(posterior_samples)
