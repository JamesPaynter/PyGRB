.. _sampling:
Sampling
========

.. figure:: ../images/pulse_fit_animation.gif
    :figwidth: 80%
    :width: 100%
    :align: center
    :alt: a GRB light-curve fit animation

    Animation of nested sampling converging on channel 3 of BATSE trigger 8099 with a FRED pulse fit.


The equation in the nested sampling animation should read

.. math::

    S(t|A,\Delta,\tau,\xi) = A \exp \left[ - \xi \left(  \frac{t - \Delta}{\tau} + \frac{\tau}{t-\Delta}  \right)  -2 \right]

Photon Counting
---------------

Photon counting is a Poisson process.
High energy detectors like BATSE accumulate photons at discrete multiples of their clock cycles (sampling frequencies).
BATSE has a sampling frequency of 500 Hz (clock cycle 2 :math:`{\mu}`s).
Modern satellites like Fermi record each photon arrival time (time-tagged event, `tte`) to the nearest integer multiple of the clock cycle.
For BATSE, hardware limitations restricted this to the first 32,768 Large Area Detector (LAD) events, inclusive of all detectors.
.. Pre-trigger data is available for all 8 LADs.
.. Post-trigger data is available for the triggered detectors only.
Only the shortest, moderately bright :math:`{\gamma}`-ray bursts are contained completely within the `tte` data.
From this point on for BATSE, counts are collected in 64ms intervals (Discriminator Science Data, `discsc`)

Dead Time
^^^^^^^^^

BATSE has a small dead time after each photon count of approximately one clock cycle.
This dead time is proportional to the energy of the incident photon (or particle event) which triggered the count.

.. math::
  \tau \sim \alpha \ln \frac{E_{\gamma}}{E_0}

Where :math:`E_{\gamma}` is the energy of the incident photon, :math:`E_0= 5.5` keV is the reset level of the detector, and :math:`{\alpha}=0.75`:math:`{\mu}`s is the signal decay time.
This means that photon counting is not a true Poisson process when the count rate approaches the sampling frequency.


Further reading
"""""""""""""""

https://doi.org/10.1029/2007GL032922
https://doi.org/10.1029/2009JA014578
.. ~\cite{2010JGRA..115.0E21G}.

BATSE Data Types
----------------

, and in (Time-to-Spill, `tte`),


Poisson rate
------------

The rate passed to the likelihood function is the sum of the individual pulses, specified in :ref:`pulses`.
An example rate for two FRED pulses would be:

.. math::

    \begin{split}
    S(t|A_1,\Delta_1,\tau_1,\xi_1,A_2,\Delta_2,\tau_2,\xi_2) =
                      &A_1 \exp \left[ - \xi_1 \left(  \frac{t - \Delta_1}{\tau_1}
                              + \frac{\tau_1}{t-\Delta_1}  \right)  -2 \right] \\
                    + &A_2 \exp \left[ - \xi_2 \left(  \frac{t - \Delta_2}{\tau_2}
                              + \frac{\tau_2}{t-\Delta_2}  \right)  -2 \right]
    \end{split}


Background
^^^^^^^^^^

The background is by default modelled as a constant.
This is sufficient for all but the longest gamma-ray bursts, excepting periods of unusually high background variability.
More complex background models, such as a polynomial, can be included by specifying them as a rate function and including relevant priors.

The complete rate is then:

.. math::

  \begin{split}
  S(t|A_1,\Delta_1,\tau_1,\xi_1,A_2,\Delta_2,\tau_2,\xi_2) = B +
                    &A_1 \exp \left[ - \xi_1 \left(  \frac{t - \Delta_1}{\tau_1}
                            + \frac{\tau_1}{t-\Delta_1}  \right)  -2 \right] \\
                  + &A_2 \exp \left[ - \xi_2 \left(  \frac{t - \Delta_2}{\tau_2}
                            + \frac{\tau_2}{t-\Delta_2}  \right)  -2 \right]
  \end{split}

Likelihood
----------

The rate function is then passed into the Poisson likelihood, which is a sum of the specified rates.


Priors
------

The default priors are

+---------------------------------+------------------------------------+--------------------+--------------+--------------+
| parameter                       | minimum                            | maximum            | type         | units        |
+---------------------------------+------------------------------------+--------------------+--------------+--------------+
| :math:`\Delta_i`                | \-\-                               | \-\-               | uniform      | seconds      |
+---------------------------------+------------------------------------+--------------------+--------------+--------------+
| :math:`\Delta_{i+1}`            | :math:`\Delta\_i`                  | \-\-               | uniform      | seconds      |
+---------------------------------+------------------------------------+--------------------+--------------+--------------+
| :math:`B`                       | :math:`10^{-1}`                    | :math:`10^{3}`     | log\-uniform | counts / bin |
+---------------------------------+------------------------------------+--------------------+--------------+--------------+
| :math:`A`                       | :math:`10^{0}`                     | :math:`10^{5}`     | log\-uniform | counts / bin |
+---------------------------------+------------------------------------+--------------------+--------------+--------------+
| :math:`\tau`                    | :math:`10^{-3}`                    | :math:`10^{3}`     | log\-uniform | seconds      |
+---------------------------------+------------------------------------+--------------------+--------------+--------------+
| :math:`\xi`                     | :math:`10^{-3}`                    | :math:`10^{3}`     | log\-uniform | \-\-         |
+---------------------------------+------------------------------------+--------------------+--------------+--------------+
| :math:`\gamma`                  | :math:`10^{-1}`                    | :math:`10^{1}`     | log\-uniform | \-\-         |
+---------------------------------+------------------------------------+--------------------+--------------+--------------+
| :math:`\nu`                     | :math:`10^{-1}`                    | :math:`10^{1}`     | log\-uniform | \-\-         |
+---------------------------------+------------------------------------+--------------------+--------------+--------------+
| :math:`\Delta_\text{res}`       | \-\-                               | \-\-               | uniform      | seconds      |
+---------------------------------+------------------------------------+--------------------+--------------+--------------+
| :math:`A_\text{res}`            | :math:`10^{0}`                     | :math:`10^{3}`     | log\-uniform | counts / bin |
+---------------------------------+------------------------------------+--------------------+--------------+--------------+
| :math:`\tau_\text{res}`         | :math:`10^{-3}`                    | :math:`10^{3}`     | log\-uniform | counts / bin |
+---------------------------------+------------------------------------+--------------------+--------------+--------------+
| :math:`\omega`                  | :math:`10^{-3}`                    | :math:`10^{3}`     | log\-uniform | \-\-         |
+---------------------------------+------------------------------------+--------------------+--------------+--------------+
| :math:`\varphi`                 | :math:`-\pi`                       | :math:`\pi`        | uniform      | radians      |
+---------------------------------+------------------------------------+--------------------+--------------+--------------+

The priors on :math:`\Delta_i` and :math:`\Delta_\text{res}` are determined by the length of the light-curve passed to `PulseFitter`.


Further reading
---------------

For more on nested sampling, the reader is referred to the following links.

https://lscsoft.docs.ligo.org/bilby/basics-of-parameter-estimation.html

https://dynesty.readthedocs.io/en/latest/overview.html

https://dynesty.readthedocs.io/en/latest/dynamic.html
