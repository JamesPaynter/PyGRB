from scipy.stats import gamma

def get_Poisson_CI(delta, N):
    """ Get Poisson confidence interval (frequentist) for counts, N and
        significance threshold, delta.

    Parameters
    ----------

    delta: float
        The significance threshold. The probability tails are equally
        distributed between the upper and lower side, such that the total
        probability contained within them is equal to delta. Each tail contains
        delta / 2 probability.
    N: int
        The number of observed counts to calculate confidence intervals for.

    Returns
    -------

    lower, upper: float
        The lower and upper limits of the confidence interval given having
        observed N counts for the specified significance threshold.

    """
    lower = gamma.ppf(    delta / 2, a = N,     scale = 1)
    upper = gamma.ppf(1 - delta / 2, a = N + 1, scale = 1)
    return lower, upper


if __name__ == '__main__':
    # print(get_Poisson_CI(0.418, 5))
    pass
