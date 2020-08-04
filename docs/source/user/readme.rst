.. figure:: ../images/logo.png
    :figwidth: 100%
    :width: 100%
    :align: center
    :alt: PyGRB logo


.. include::
  ../../../README.rst
  :start-after: inclusion-marker-what-it-does-start
  :end-before: inclusion-marker-what-it-does-end

Note
^^^^

Running `PyGRB` will implicitly import `Bilby`, which is used for Bayesian inference.
Since `Bilby` is primarily used for gravitational wave inference, importing `Bilby` will check for installations of `gwpy` and `lalsuite`, resulting in the following warnings if they are not installed.


.. code-block:: console

  13:23 bilby WARNING : You do not have gwpy installed currently. You will  not be able to use some of the prebuilt functions.
  13:23 bilby WARNING : You do not have lalsuite installed currently. You will not be able to use some of the prebuilt functions.
  13:23 bilby WARNING : You do not have gwpy installed currently. You will  not be able to use some of the prebuilt functions.
  13:23 bilby WARNING : You do not have lalsuite installed currently. You will not be able to use some of the prebuilt functions.
  13:23 bilby WARNING : You do not have gwpy installed currently. You will  not be able to use some of the prebuilt functions.
  13:23 bilby WARNING : You do not have lalsuite installed currently. You will not be able to use some of the prebuilt functions.
  13:23 bilby WARNING : You do not have lalsuite installed currently. You will not be able to use some of the prebuilt functions.


This has no effect on running of `PyGRB`.
