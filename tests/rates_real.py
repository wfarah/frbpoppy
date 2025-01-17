"""Calculate the real frb detection rates."""
from scipy.stats import chi2, norm
from scipy.integrate import quad
import matplotlib.pyplot as plt
import numpy as np

EXPECTED = {'htru': [9, 24 * 0.551 / 1549],  # N_frbs, scaling to get frbs/day
            'apertif': [1, 1 / 7],
            'askap-fly': [20, 24 / 32840 * 8],
            'utmost': [0, 0],
            'chime': [0, 0],
            'palfa': [1, 1 / 24.1],
            'guppi': [0.4, 1 / 81]  # 0.4 is my own assumption
            }

SURVEYS = ('palfa', 'htru', 'askap-fly')
ALPHAS = np.around(np.linspace(-0.2, -2.5, 7), decimals=2)


def poisson_interval(k, sigma=1):
    """
    Use chi-squared info to get the poisson interval.

    Give a number of observed events, which range of observed events would have
    been just as likely given a particular interval?

    Based off https://stackoverflow.com/questions/14813530/
    poisson-confidence-interval-with-numpy
    """
    gauss = norm(0, 1).pdf
    a = 1 - quad(gauss, -sigma, sigma, limit=1000)[0]
    low, high = (chi2.ppf(a/2, 2*k) / 2, chi2.ppf(1-a/2, 2*k + 2) / 2)
    if k == 0:
        low = 0.0

    return low, high


def real_rates(surveys=SURVEYS):
    """Calculate the EXPECTED rates (all scaled by HTRU)."""
    rates = {}

    for surv in surveys:
        # Plot EXPECTED rate
        exp_n = EXPECTED[surv][0]
        exp_scaling = EXPECTED[surv][1]

        norm = 1 / (EXPECTED['htru'][0] * EXPECTED['htru'][1])

        exp_min, exp_max = poisson_interval(exp_n, sigma=2)

        exp = exp_n * exp_scaling * norm
        exp_min *= exp_scaling * norm
        exp_max *= exp_scaling * norm

        rates[surv] = (exp, exp_min, exp_max)

    return rates


def main():

    rates = real_rates()

    for surv in rates:
        middle, top, bottom = rates[surv]
        left = min(ALPHAS)
        right = max(ALPHAS)
        x = [left, right, right, left]
        y = [top, top, bottom, bottom]
        plt.fill(x, y, alpha=0.25)
        plt.plot([left, right], [middle]*2, label=surv, linestyle='dashed')

        plt.xlabel(r'$\alpha$')
        plt.ylabel(r'Events / htru')
        plt.yscale('log')
        plt.legend()
        plt.gca().invert_xaxis()
        plt.tight_layout()
        plt.savefig('./plots/real_rates.pdf')


if __name__ == '__main__':
    main()
