"""Plot intensity profile of theoretical beam patterns."""
import matplotlib.pyplot as plt
import numpy as np
from frbpoppy.survey import Survey

PATTERNS = ['perfect', 'gaussian', 'airy-0', 'airy-4']
SURVEY = 'apertif'
MIN_Y = 1e-6
n = 500000

for pattern in PATTERNS:

    n_sidelobes = 1
    p = pattern
    z = 0
    if pattern.startswith('airy'):
        n_sidelobes = int(pattern[-1])
        p = 'airy'
        if n_sidelobes == 0:
            z = 10

    s = Survey(SURVEY, gain_pattern=p, n_sidelobes=n_sidelobes)
    int_pro, offset = s.intensity_profile(n_gen=n)

    # Sort the values
    sorted_int = np.argsort(offset)
    int_pro = int_pro[sorted_int]
    offset = offset[sorted_int]

    # Clean up lower limit
    offset = offset[int_pro > MIN_Y]
    int_pro = int_pro[int_pro > MIN_Y]

    # Offset in degrees
    offset = offset/60.

    print(s.beam_size_fwhm, s.beam_size)

    plt.plot(offset, int_pro, label=pattern, zorder=z)


plt.xlabel(f'Offset ($\degree$)')
plt.ylabel('Intensity Profile')
plt.yscale('log')
plt.legend()
plt.tight_layout()
plt.savefig('plots/int_pro_theory.pdf')
