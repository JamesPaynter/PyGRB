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

+--------------------------+----------------------------+------------+--------------+--------------+
| parameter                | minimum                    | maximum    | type         | units        |
+--------------------------+----------------------------+------------+--------------+--------------+
| $\\Delta\_i$             | \-\-                       | \-\-       | uniform      | seconds      |
+--------------------------+----------------------------+------------+--------------+--------------+
| $\\Delta\_\{i\+1\}$      | $\\Delta\_i$               | \-\-       | uniform      | seconds      |
+--------------------------+----------------------------+------------+--------------+--------------+
| $B$                      | $10^\{\-1\}$               | $10^\{3\}$ | log\-uniform | counts / bin |
+--------------------------+----------------------------+------------+--------------+--------------+
| $A$                      | $10^\{0\\hphantom\{\-\}\}$ | $10^\{5\}$ | log\-uniform | counts / bin |
+--------------------------+----------------------------+------------+--------------+--------------+
| $\\tau$                  | $10^\{\-3\}$               | $10^\{3\}$ | log\-uniform | seconds      |
+--------------------------+----------------------------+------------+--------------+--------------+
| $\\xi $                  | $10^\{\-3\}$               | $10^\{3\}$ | log\-uniform | \-\-         |
+--------------------------+----------------------------+------------+--------------+--------------+
| $\\gamma$                | $10^\{\-1\}$               | $10^\{1\}$ | log\-uniform | \-\-         |
+--------------------------+----------------------------+------------+--------------+--------------+
| $\\nu$                   | $10^\{\-1\}$               | $10^\{1\}$ | log\-uniform | \-\-         |
+--------------------------+----------------------------+------------+--------------+--------------+
| $\\Delta\_\\text\{res\}$ | \-\-                       | \-\-       | uniform      | seconds      |
+--------------------------+----------------------------+------------+--------------+--------------+
| $A\_\\text\{res\}$       | $10^\{0\\hphantom\{\-\}\}$ | $10^\{3\}$ | log\-uniform | counts / bin |
+--------------------------+----------------------------+------------+--------------+--------------+
| $\\tau\_\\text\{res\}$   | $10^\{\-3\}$               | $10^\{3\}$ | log\-uniform | counts / bin |
+--------------------------+----------------------------+------------+--------------+--------------+
| $\\omega$                | $10^\{\-3\}$               | $10^\{3\}$ | log\-uniform | \-\-         |
+--------------------------+----------------------------+------------+--------------+--------------+
| $\\varphi$               | $\-\\pi$                   | $\\pi$     | uniform      | radians      |
+--------------------------+----------------------------+------------+--------------+--------------+


For more on nested sampling, the reader is referred to the following links.


Further reading
---------------

https://lscsoft.docs.ligo.org/bilby/basics-of-parameter-estimation.html

https://dynesty.readthedocs.io/en/latest/overview.html

https://dynesty.readthedocs.io/en/latest/dynamic.html
