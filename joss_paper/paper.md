---
title: "PyGRB"
tags:
  - python
  - astrophysics
  - cosmology
  - gamma-ray bursts
  - gravitational lensing
authors:
  - name: James R. Paynter
    orcid: 0000-0002-9672-4008
    affiliation: 1
affiliations:
- name: School of Physics, University of Melbourne, Parkville, Victoria, 3010, Australia
  index: 1
date: 15 July 2020
bibliography: paper.bib
---


NASA provides the original software packages used to analyse and create binned data-products.
But the software themselves are arcane and outdated, and their algorithms opaque.


# Introduction


Gamma-ray bursts are short and intense bursts of low energy (keV -- MeV) gamma radiation. Their cosmological origin and transient nature makes them important probes of the universe and its structure. Since their discovery astronomers have sought to model the high energy emission. A popular and enduring model, although purely phenomenological, is the fast-rise exponential-decay (FRED) pulse.


# PyGRB

`PyGRB` is a pure Python, open source pulse-fitting package which aims bring gamma-ray burst light-curve fitting and analysis into the 21st century. `PyGRB` is able to download the pre-binned light curves (``bfits`` files), in addition to ``tte_list`` time-tagged photon arrival times. FITS I/O functionality is provided by `Astropy` [@astropy]. `PyGRB` is built on top of the `Bilby` Bayesian inference library, which itself utilises the `Dynesty` and `Nestle` nested sampling packages.
`PyGRB` makes visually appealing light-curves from the 4 broadband energy channel BATSE data.
The main feature of `PyGRB` is its ability to fit analytic light-curve models to data.
In particular, Bayesian model selection allows the user to determine the most appropriate pulse parameterisation for a particular burst.
Ultimately, the model selection of `PyGRB` is used to determine if two light-curves are statistically identical, which is indicative of a gravitational lensing event.


It is quite difficult to compare GRB light-curves occurring at different times due to the variability of the gamma-ray background.
Comparing GRBs observed by different satellites is another matter altogether, owing to the different fields of view, energy sensitivities, time resolution, and detector geometry.
`PyGRB` creates a unified, abstracted framework allowing for the comparison of gamma-ray bursts based on their fitted pulse parameters, rather than visual or bin-wise statistical comparisons of their light-curves, which is inherently fraught with opportunities for mishap.






``PyGRB`` is released under the BSD 3-Clause license.
The source code may be found at https://github.com/JamesPaynter/PyGRB, or alternatively the package may be installed from PyPi via ``pip install PyGRB``.
The online documentation, tutorials and examples are hosted at https://pygrb.readthedocs.io.

# References
