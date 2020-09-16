---
title: "PyGRB: A pure Python gamma-ray burst analysis package."
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
date: 16 July 2020
bibliography: paper.bib
---


# Introduction


Gamma-ray bursts (GRBs) are short and intense bursts of low energy (keV -- MeV) gamma radiation.
Their cosmological origin and transient nature makes them important probes of the universe and its structure.
Since their discovery astronomers have sought to model the high energy emission.
A popular and enduring model, although phenomenological, is the fast-rise exponential-decay (FRED) pulse [@norris2005; @norris1996],

$$
S(t|A,\Delta,\tau,\xi) = A \exp \left[ - \xi \left(  \frac{t - \Delta}{\tau} + \frac{\tau}{t-\Delta}  \right)   \right].
$$

# Statement of Need

The analysis of large amounts of light-curves requires downloading FITS files from the relevant server.
To do this by hand is a tiring prospect for the 2,704 BATSE GRBs.
Having downloaded a FITS file, a scientist would then need to unpack the data from the file, and extract the relevant tables to construct a light-curve.
They may then want to plot the light-curve for publication, requiring them to write more software to appropriately represent the data.
Ultimately, they may want to look at population statistics, or compare different GRB pulses.
There is a gap in the market for software to get researchers off the ground quickly.
This is where `PyGRB` comes in.


# PyGRB

`PyGRB` is a pure Python, open source pulse-fitting package which aims bring gamma-ray burst light-curve fitting and analysis into the 21st century.
`PyGRB` is able to download the pre-binned BATSE [@batse] light curves (``bfits`` files), in addition to ``tte_list`` time-tagged photon arrival times.
FITS I/O functionality is provided by `Astropy` [@astropy]. `PyGRB` is built on top of the `Bilby` Bayesian inference library [@bilby], through which `PyGRB` utilises the `Dynesty` [@dynesty] and `Nestle` [@nestle] nested sampling packages [@skilling; @feroz; @multinest].

`PyGRB` makes visually appealing and scientifically instructive light-curves from the 4 broadband energy channel BATSE data.
The main feature of `PyGRB` is its ability to fit analytic light-curve models to data.
In particular, Bayesian model selection allows the user to determine the most appropriate pulse parameterisation for a particular burst.
Available pulse parameterisations are Gaussian pulses, FRED pulses and FRED variations.
Residual fitting is additionally possible, for which we implement a sine-Gaussian function.

![BATSE trigger 7475, GRB 990316 with FRED fit by `PyGRB`](../docs/source/images/B_7475__d_NL200__rates_F.png)


Ultimately, the model selection of `PyGRB` is used to determine if two light-curves are statistically identical, which would be indicative of a gravitational lensing event [@paczynski; @blaes; @mao].
It is quite difficult to compare GRB light-curves occurring at different times due to the variability of the gamma-ray background.
Comparing GRBs observed by different satellites is another matter altogether, owing to the different energy sensitivities, time resolution, and detector geometry.
`PyGRB` creates a unified, abstracted framework allowing for the comparison of gamma-ray bursts based on their fitted pulse parameters, rather than visual or bin-wise statistical comparisons of their light-curves, which is inherently fraught with opportunities for mishap.

In the present release only BATSE functionality is available.
However, due to the modular nature of the code, including additional GRB catalogues is as simple as creating the relevant `fetch`, and `preprocess` modules.
Future releases will allow for the easy comparison of gamma-ray bursts observed by different satellites.
As `PyGRB` is open source, the community is actively encouraged to contribute functionality for the many available GRB catalogues.

`PyGRB` is released under the BSD 3-Clause license.
The source code may be found at https://github.com/JamesPaynter/PyGRB, or alternatively the package may be installed from PyPi via ``pip install PyGRB``.
The online documentation, tutorials and examples are hosted at https://pygrb.readthedocs.io.

# Acknowledgements

I would like to thank Rachel Webster for introducing me to the problem of gravitationally lensed gamma-ray bursts, which spawned this project.
I would like to thank Eric Thrane for introducing me to modern computational statistics, particularly through `Bilby`, on whose shoulders this package stands.
Additionally I would like to thank Julian Carlin, Aman Chokshi for supporting me on my journey from novice programmer to published developer.

# References
