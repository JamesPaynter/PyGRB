import sys
import math
import numpy as np
import scipy.special as special
from scipy.signal import convolve

MIN_FLOAT = sys.float_info[3]
MAX_FLOAT = sys.float_info[0]
MAX_EXP   = np.log(MAX_FLOAT)


def gaussian_pulse(times, start, scale, sigma):
    r"""
    The amplitude-normalised equation for a fast-rise expontential-decay pulse.
    The rate is calculated at each input time and returned as an array.

    .. math::

        S(t|A,\Delta,\sigma) = A \exp \left[
        \frac{\left( t - \Delta \right)^2}{2\sigma^2}
        \right]


    Parameters
    ----------
    times : array_like
        The input time array.
    start : float
        The start time of the pulse.
    scale : float
        The amplitude of the pulse.
    sigma : float
        The width of the pulse.

    Returns
    -------
    rate : ndarray
         Output array containing the pulse.

    """
    rate = scale * np.exp(- np.power(times - start, 2.) / (
                        2 * np.power(sigma, 2.) + MIN_FLOAT))
    return rate


def FRED_pulse(times, start, scale, tau, xi):
    r"""
    The amplitude-normalised equation for a fast-rise expontential-decay pulse.
    The rate is calculated at each input time and returned as an array.

    .. math::

        S(t|A,\Delta,\tau,\xi) = A \exp \left[ - \xi \left(
        \frac{t - \Delta}{\tau} + \frac{\tau}{t-\Delta}  \right) -2  \right]


    Parameters
    ----------
    times : array_like
        The input time array.
    start : float
        The start time of the pulse.
    scale : float
        The amplitude of the pulse.
    tau : float
        The duration of the pulse.
    xi : float
        The asymmetry of the pulse.

    Returns
    -------
    rate : ndarray
         Output array containing the pulse.

    """

    rate = np.where(times - start <= 0, MIN_FLOAT, scale * np.exp( - xi * (
            (tau / np.where(times - start <= 0,
            times - start - MIN_FLOAT, times - start + MIN_FLOAT))
         +  ((times - start) / (tau + MIN_FLOAT)) - 2.)))
    return rate


def FRED_pulse_unnorm(times, start, scale, tau, xi):
    r"""
    The amplitude-unnormalised equation for a fast-rise expontential-decay pulse.
    The rate is calculated at each input time and returned as an array.

    .. math::

        S(t|A,\Delta,\tau,\xi) = A \exp \left[ - \xi \left(
        \frac{t - \Delta}{\tau} + \frac{\tau}{t-\Delta}  \right)   \right]


    Parameters
    ----------
    times : array_like
        The input time array.
    start : float
        The start time of the pulse.
    scale : float
        The amplitude of the pulse.
    tau : float
        The duration of the pulse.
    xi : float
        The asymmetry of the pulse.

    Returns
    -------
    rate : ndarray
         Output array containing the pulse.

    """

    rate = np.where(times - start <= 0, MIN_FLOAT, scale * np.exp( - xi * (
            (tau / np.where(times - start <= 0,
            times - start - MIN_FLOAT, times - start + MIN_FLOAT))
         +  ((times - start) / (tau + MIN_FLOAT)))))
    return rate


def FREDx_pulse(times, start, scale, tau, xi, gamma, nu):
    r"""
    The amplitude-normalised equation for a fast-rise expontential-decay pulse.
    The rate is calculated at each input time and returned as an array.

    .. math::

        S(t|A,\Delta,\tau,\xi,\gamma,\nu) = A \exp{\left[
            -\xi^\gamma\left(\frac{t-\Delta}{\tau}\right)^\gamma
            -\xi^\nu\left(\frac{\tau}{t-\Delta}\right)^\nu
            +\xi^{\frac{2\gamma\nu}{\gamma + \nu}}\cdot \left(
    \left( \frac{\gamma}{\nu}\right)^{\frac{-\gamma}{\gamma + \nu}} +
    \left( \frac{\gamma}{\nu}\right)^{\frac{\nu}{\gamma + \nu}} \right) \right]}


    Parameters
    ----------
    times : array_like
        The input time array.
    start : float
        The start time of the pulse.
    scale : float
        The amplitude of the pulse.
    tau : float
        The duration of the pulse.
    xi : float
        The asymmetry of the pulse.
    gamma: float
        An extra exponent on the pulse.
    nu: float
        An extra exponent on the pulse.

    Returns
    -------
    rate : ndarray
         Output array containing the pulse.

    """
    pow_1 = xi * (tau / (times - start))
    pow_2 = xi * ((times - start) / tau)
    norm  =   (xi ** ((2 * gamma * nu) / (gamma + nu) )
            * (
            + (gamma / nu) **(       nu / (gamma + nu))
            + (gamma / nu) **((- gamma) / (gamma + nu)) ))

    exp = ( - np.power( pow_1, gamma )
            - np.power( pow_2, nu )
            + norm
            )
    X   = np.where(times - start <= 0, MIN_FLOAT,
            np.where(exp < MAX_EXP, np.exp( exp ), MAX_EXP))

    rate = X * scale
    return rate


def FREDx_pulse_unnorm(times, start, scale, tau, xi, gamma, nu):
    r"""
    The amplitude-unnormalised equation for a fast-rise expontential-decay pulse.
    The rate is calculated at each input time and returned as an array.

    .. math::

        S(t|A,\Delta,\tau,\xi,\gamma,\nu) = A \exp \left[
        - \xi^\gamma \left(\frac{t - \Delta}{\tau}\right)^\gamma
        - \xi^\nu   \left(\frac{\tau}{t-\Delta}\right)^\nu
        \right]


    Parameters
    ----------
    times : array_like
        The input time array.
    start : float
        The start time of the pulse.
    scale : float
        The amplitude of the pulse.
    tau : float
        The duration of the pulse.
    xi : float
        The asymmetry of the pulse.
    gamma: float
        An extra exponent on the pulse.
    nu: float
        An extra exponent on the pulse.

    Returns
    -------
    rate : ndarray
         Output array containing the pulse.

    """
    pow_1 = xi * (tau / (times - start))
    pow_2 = xi * ((times - start) / tau)

    exp   = ( - np.power( pow_1, gamma )
              - np.power( pow_2, nu )
            )
    X   = np.where(times - start <= 0, MIN_FLOAT,
            np.where(exp < MAX_EXP, np.exp( exp ), MAX_EXP))

    rate = X * scale
    return rate


def sine_gaussian(times, res_begin, sg_A, sg_lambda, sg_omega, sg_phi):
    r"""
    The sine-gaussian residual function. This pulse is not amplitude-normalised.

    .. math::

        \text{res}(t)= A_\text{res} \exp \left[
        - \left(\frac{t-\Delta_\text{res}} {\lambda_\text{res}}\right)^2
        \right] \cos\left(\omega t + \varphi \right)


    Parameters
    ----------
    times : array_like
        The input time array.
    res_begin : float
        The start time of the pulse.
    sg_A : float
        The amplitude of the pulse.
    sg_lambda : float
        The duration of the pulse.
    sg_omega : float
        The angular frequency of the cosine function.
    sg_phi: float
        The phase of the cosine function.

    Returns
    -------
    rate : ndarray
         Output array containing the residual.

    """
    s = (np.exp(- np.square((times - res_begin) / sg_lambda)) *
         np.cos(sg_omega * times + sg_phi))
    return sg_A * s


def modified_bessel(times, bes_A, bes_Omega, bes_s, res_begin, bes_Delta):
    """ Not Tested. """
    b = np.where(times > res_begin + bes_Delta / 2.,
            special.j0(bes_s * bes_Omega *
           (- res_begin + times - bes_Delta / 2.) ),
           (np.where(times < res_begin - bes_Delta / 2.,
            special.j0(bes_Omega *
           (res_begin - times - bes_Delta / 2.) ),
           1)))
    return bes_A * b


def exp_decay(times, tau, start):
    dex = np.where(times - start <= 0, MIN_FLOAT,
            np.exp( - (times - start) / (tau + MIN_FLOAT)))
    return dex

def convolution_gaussian(times, start, scale, sigma, tau):
    s = np.mean(times)
    conv  = convolve(gaussian_pulse(times, s, 1, sigma),
                    exp_decay(times,tau,start), 'same')
    return scale * conv



if __name__ == '__main__':
    pass
