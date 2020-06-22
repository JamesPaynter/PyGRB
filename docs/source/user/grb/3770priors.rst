.. _3770priors:

.. role:: python(code)
   :language: python


GRB 950830 priors
-----------------

Investigation of the effects of priors on model selection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the following script we test the effect of the priors on :math:`\gamma` and :math:`\nu` on the model selection.

To compare the same model with different prior ranges, such as over a longer time period, then save the two models in the dict under different names, eg.

.. code-block:: python

  keys = [key_1, key_2]
  model_dict['model 1'] = create_model_from_key(key_1)
  model_dict['model 2'] = create_model_from_key(key_2)
  models = [model for key, model in model_dict.items()]


This is utlised in the prior test script below.

----

.. literalinclude:: ../../../../examples/gravlensnaturepriors.py
    :name: gravlensnaturepriors.py
    :caption: gravlensnaturepriors.py

----


.. We find that
