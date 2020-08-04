Sampling
========

.. figure:: ../images/pulse_fit_animation.gif
    :figwidth: 80%
    :width: 100%
    :align: center
    :alt: a GRB light-curve fit animation

    Animation of nested sampling converging on channel 3 of BATSE trigger 8099 with a FRED pulse fit.


The equation should read

.. math::

    S(t|A,\Delta,\tau,\xi) = A \exp \left[ - \xi \left(  \frac{t - \Delta}{\tau} + \frac{\tau}{t-\Delta}  \right)  -2 \right]




Background
----------

The background is by default modelled as a constant.
This is sufficient for all but the longest gamma-ray bursts, excepting periods of exceptional background variation.
More complex background models, such as a polynomial, can be included by specifying them as a rate function and including relevant priors.

Likelihood
----------

The likelihood function is a Poisson likelihood, which is a sum of the specified rates.


Priors
------

The default priors are

+----------------------------------+------------------------------------+--------------------+--------------+--------------+
| parameter                        | minimum                            | maximum            | type         | units        |
+----------------------------------+------------------------------------+--------------------+--------------+--------------+
| .. math:: \Delta_i             | \-\-                               | \-\-               | uniform      | seconds      |
+----------------------------------+------------------------------------+--------------------+--------------+--------------+
| .. math:: \Delta_{i\+1}      | .. math:: \Delta\_i               | \-\-               | uniform      | seconds      |
+----------------------------------+------------------------------------+--------------------+--------------+--------------+
| .. math:: B                      | .. math:: 10^{\-1}               | .. math:: 10^{3} | log\-uniform | counts / bin |
+----------------------------------+------------------------------------+--------------------+--------------+--------------+
| .. math:: A                      | .. math:: 10^{0\hphantom{\-}} | .. math:: 10^{5} | log\-uniform | counts / bin |
+----------------------------------+------------------------------------+--------------------+--------------+--------------+
| .. math:: \tau                  | .. math:: 10^{\-3}               | .. math:: 10^{3} | log\-uniform | seconds      |
+----------------------------------+------------------------------------+--------------------+--------------+--------------+
| .. math:: \xi                   | .. math:: 10^{\-3}               | .. math:: 10^{3} | log\-uniform | \-\-         |
+----------------------------------+------------------------------------+--------------------+--------------+--------------+
| .. math:: \gamma                | .. math:: 10^{\-1}               | .. math:: 10^{1} | log\-uniform | \-\-         |
+----------------------------------+------------------------------------+--------------------+--------------+--------------+
| .. math:: \nu                   | .. math:: 10^{\-1}               | .. math:: 10^{1} | log\-uniform | \-\-         |
+----------------------------------+------------------------------------+--------------------+--------------+--------------+
| .. math:: \Delta_\text{res} | \-\-                               | \-\-               | uniform      | seconds      |
+----------------------------------+------------------------------------+--------------------+--------------+--------------+
| .. math:: A_\text{res}       | .. math:: 10^{0\hphantom{\-}} | .. math:: 10^{3} | log\-uniform | counts / bin |
+----------------------------------+------------------------------------+--------------------+--------------+--------------+
| .. math:: \tau_\text{res}   | .. math:: 10^{\-3}               | .. math:: 10^{3} | log\-uniform | counts / bin |
+----------------------------------+------------------------------------+--------------------+--------------+--------------+
| .. math:: \omega                | .. math:: 10^{\-3}               | .. math:: 10^{3} | log\-uniform | \-\-         |
+----------------------------------+------------------------------------+--------------------+--------------+--------------+
| .. math:: \varphi               | .. math:: -\pi                   | .. math:: \pi     | uniform      | radians      |
+----------------------------------+------------------------------------+--------------------+--------------+--------------+

The priors on .. math:: \Delta\_i are determined by the length of the light-curve passed to `PulseFitter`.


Further reading
---------------

For more on nested sampling, the reader is referred to the following links.

https://lscsoft.docs.ligo.org/bilby/basics-of-parameter-estimation.html

https://dynesty.readthedocs.io/en/latest/overview.html

https://dynesty.readthedocs.io/en/latest/dynamic.html
