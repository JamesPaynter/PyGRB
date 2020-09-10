import numpy as np
import matplotlib.pyplot as plt

import scipy.integrate as integrate
from scipy.optimize import fsolve
import math

import matplotlib as mpl
from matplotlib import rc
mpl.rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}']
rc('font',**{'family':'DejaVu Sans','serif':['Computer Modern'], 'size':12})
rc('text', usetex=True)

from scipy.stats import poisson

cols = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']

dlambda = 1e-6
llambda = np.linspace(dlambda, 10, int(10/dlambda))
p = poisson.pmf(1, llambda)
prior = 1 / np.sqrt(llambda)
p2 = prior * p
norm_p = p2 / np.sum(p2 * dlambda)

fig, ax = plt.subplots(figsize = (8,5))
ax.plot(llambda, norm_p, c = 'k')

threshold = 8e-6/8e-5
zeds = [0.05, 0.5, 1, 2, 5]
lums = [1e43, 1e44, 1e45, 1e46, 1e47]
omegas = [.333, 3.22e-3, 5.4e-5, 3e-6, 1e-6] #lum
omegas = [1.8e-2, 3e-4, 1.5e-4, 8e-5, 6e-5] # z l = 1e45
# omegas = [1.8e-2, 3e-4, 1.5e-4, 8e-5, 6e-5] #z l = 1e44.5
for i, (z, omega, l) in enumerate(zip(zeds, omegas, lums)):
    threshold = 8e-6 / omega

    credibility = np.sum(dlambda * p2[llambda < threshold])
    print(f'At <L> = {l} a globular cluster is excluded at {100*(1-credibility):.3f}% credibility')
    # print(f'At <z_s> = {z} a globular cluster is excluded at {100*(1-credibility):.3f}% credibility')
    ax.axvline(threshold, color = cols[i], linestyle = ':',
        label = f'$\\Omega_\\text{{gc}}/\\Omega_l$ for $\\left<z_s\\right>\\sim{z}$')
ax.set_xscale('log')
ax.set_xlabel(r'$X\sim$ Poisson$(N=1)$')
ax.set_ylabel('Probability Density')
ax.legend(loc = 'upper left')
# plt.show()

const_G = 6.6741e-11 # SI units
const_c = 299792458.  # m/s
omega_m = 0.286
omega_v = 0.714
H_0     = 69600. #/ 3.086e22    # m/s / Mpc
MPC_2_M = 3.086e22

GRB_LUMINOSITY = 10**44.5 # Watts
ENERGY_TO_GAMMA = 1.602e-14 # Watts to 100 kev phot / sec
PHI_0 = 0.3 # photons / cm^2 / sec (BATSE minimum detectable photon flux)
LENS_MASS = 6e4 * 2e30 # kg
MIN_TIME_DELAY = 1e-2 # second
MAX_TIME_DELAY = 240 # second
SOURCE_REDSHIFT = 5

# not used
# def pd(z_l, z_s):
#     return (vector_pd(z_s) - vector_pd(z_l)) / (1 + z_s)
def efficiency(phi):
    phi_0 = 0.21  # photons / sec / cm^2
    alpha = 0.105 # photons / sec / cm^2
    return np.where(phi < phi_0, 0, 1 - np.exp(- (phi - phi_0) / alpha))
def cross_section(mass, z_l, z_s):
    return np.pi * einstein(mass, z_l, z_s)
def einstein(mass, z_l, z_s):
    dist = ((1 + z_l) * (vector_pd(z_s) - vector_pd(z_l)) /
            (vector_pd(z_s) * vector_pd(z_l))               )
    return np.sqrt(4 * const_G * mass * 2e30 / math.pow(const_c, 2) * dist / MPC_2_M)

def proper_distance(z):
    ''' Returns proper distance in Mpc '''
    ### uses angular diameter distances from dodelson
    integral, err = integrate.quad(lambda x:  math.pow(math.pow((1 + x), 3)
                                            * omega_m + omega_v, -0.5), 0, z)
    return const_c / H_0 * integral

def vector_pd(z):
    ''' Vectorizes the proper distance '''
    vfunc = np.vectorize(proper_distance)
    return vfunc(z)

def vector_angular_diameter_distance(z):
    """ Return angular diameeter distance, can take vectors. """
    return vector_pd(z) / (1 + z)

def magnification_y(y):
    return (math.log( math.sqrt(math.pow(y,2) + 4) + y) -
            math.log( math.sqrt(math.pow(y,2) + 4) - y) )

def vector_magnification_y(y):
    vfunc = np.vectorize(magnification_y)
    return vfunc(y)

def y_function(y):
    return (y/2 * math.sqrt(math.pow(y,2) + 4) + vector_magnification_y(y))

def vec_y_function(y):
    vfunc = np.vectorize(y_function)
    return vfunc(y)

def time_delay_function(mass, z_l, y):
    return 4 * (1 + z_l) * const_G * mass * vec_y_function(y) / (const_c ** 3)

def y_max(z_s, phi_emit, **kwargs):
    """ phi_emit is in units of Watts"""
    phi_emit/= ENERGY_TO_GAMMA # convert Joules / sec into photons / sec
    phi_emit/= 1e4 # convert / m^2 to cm^2
    phi_0    = kwargs.pop('phi_0', PHI_0)
    phi_peak = phi_emit / (4 * np.pi * (vector_pd(z_s) * (1 + z_s) * MPC_2_M)**2)
    return  ( np.power(1 + phi_peak / phi_0,  0.25)
            - np.power(1 + phi_peak / phi_0, -0.25))

def y_from_Delta_t(z_l, Delta_t, Mass_lens):
    def func(y):
        return Delta_t - time_delay_function(Mass_lens, z_l, y)
    y = fsolve(func, 100)
    return y

def vector_y_from_Delta_t(z_l, Delta_t, Mass_lens):
    vfunc = np.vectorize(y_from_Delta_t)
    return vfunc(z_l, Delta_t, Mass_lens)

def hubble(z):
    h = np.power(np.power((1 + z), 3) * omega_m + omega_v, -0.5)
    return h

def redshift_integral(z, **kwargs):
    """ Note that sometimes the integral fails for small z
    resulting in an array of zeroes for the optical depth."""
    # integral, err = integrate.quad(lambda x: (1 + x) ** 2 * proper_distance(x) ** 3 *
    integral, err = integrate.quad(lambda x: (1 + x) ** 2 * proper_distance(x) *
    (proper_distance(z) - proper_distance(x)) /
    hubble(x) *
    y_bounds(x, z, **kwargs), 0, z, points = [0, 1e-100, 1e-50, 1e-20, 1e-10, 1e-5, 1, z])
    return integral

def vector_redshift_integral(z, **kwargs):
    vfunc = np.vectorize(redshift_integral)
    return vfunc(z, **kwargs)

def y_bounds(z_l, z_s, bounds = False, **kwargs):
    Delta_t_min = kwargs.pop('Delta_t_min', MIN_TIME_DELAY)
    Delta_t_max = kwargs.pop('Delta_t_max', MAX_TIME_DELAY)
    Mass_lens   = kwargs.pop('Mass_lens', LENS_MASS)
    luminosity  = kwargs.pop('luminosity', GRB_LUMINOSITY)
    phi_0       = kwargs.pop('phi_0', PHI_0)
    y_a = y_max(z_s, phi_emit = luminosity, phi_0 = phi_0)
    y_b = vector_y_from_Delta_t(z_l = z_l, Delta_t = Delta_t_max, Mass_lens = Mass_lens)
    yymax = np.minimum.reduce([y_a,y_b])
    yymin = vector_y_from_Delta_t(z_l = z_l, Delta_t = Delta_t_min, Mass_lens = Mass_lens)
    if bounds:
        return yymin, yymax, y_a, y_b
    else:
        teo =  (yymax**2 - yymin**2) * np.heaviside(yymax - yymin, 0)
        return teo

def vec_optical_depth(mass_density, source_redshift, **kwargs):
    integral = vector_redshift_integral(source_redshift, **kwargs)
    return 3 * H_0 * mass_density * integral / (2 * const_c * vector_pd(source_redshift))

def main(**kwargs):
    z_s = kwargs.get('source_redshift', SOURCE_REDSHIFT)
    Delta_t_min = kwargs.get('Delta_t_min', MIN_TIME_DELAY)
    Delta_t_max = kwargs.get('Delta_t_max', MAX_TIME_DELAY)
    l = kwargs.get('luminosity', GRB_LUMINOSITY)
    m = kwargs.get('mass', LENS_MASS)
    phi = kwargs.get('detection_counts', PHI_0)

    fig, ax = plt.subplots()
    fig2, ax2 = plt.subplots()
    # lenses = [2e33, 2e34, 2e35, 2e36, 2e40]
    lums = [1e43, 1e44, 1e45, 1e46, 1e47]
    zeds = [0.05, 0.5, 1., 2., 5.]#, 10.]
    cols = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']
    ls = ['-', '-.']
    # for i, m in enumerate(lenses):
    phis = [0.3]#[300, 1500]
    for k, phi in enumerate(phis):
        # for i, l in enumerate(lums):
        for i, z_s in enumerate(zeds):
            plot_y_bounds(axes = ax2, colour = cols[i], Mass_lens = m, z_s = z_s)
            mass_density = np.geomspace(1e-6,5e-1, 1000)
            optical_depth = vec_optical_depth(mass_density, z_s,
                                                Mass_lens = m,
                                                luminosity = l,
                                                Delta_t_min = Delta_t_min,
                                                Delta_t_max = Delta_t_max,
                                                phi_0 = phi)
            ax.plot(mass_density, 1 - np.exp(- optical_depth),
                    c = cols[i], linestyle = ls[k],
                    label = f'$z_s = {z_s}$',
                    # , $\\varphi_0 = {phi}$',
                    # label = f'$M = {m/2e30:.0f} M_\odot$'
                    # label = f'$L = 10^{{{np.log10(l):.0f}}}$ Watts',
                    )
            omega = mass_density[np.argmin(np.abs(optical_depth - 1/2700))]
            # print(f'For GRB luminosity L = {l} the lens density is Omega = {omega:.6f}')
            print(f'For source redshift <z> = {z_s} the lens density is Omega = {omega:.6f}')
    ax.axhline(1/2700, color = 'k',
    label = r'Estimated lens probability $P(\tau)\sim 1/2700$')
    ax.axvline(1/2700, color = 'k', linestyle = '-.',
    label = r'Na\"ive density estimate, $\Omega\sim\tau$')
    ax.axvline(8e-6, color = 'k', linestyle = ':',
    label = r'Estimated globular cluster density, $\Omega_\text{gc}$')
    ax.set_xlabel(r'Lens Density, $\Omega_l$')
    ax.set_ylabel(r'Lens Probability, $P(\tau) = 1 - e^{-\tau}$')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(right = np.max(mass_density))
    ax.set_ylim(bottom = 1e-4)
    ax.legend()
    plt.show()







# ============================================================================ #
# ============================================================================ #

def plot_y_bounds(**kwargs):
    z_s = kwargs.pop('z_s', SOURCE_REDSHIFT)
    ax = kwargs.pop('axes', None)
    colour = kwargs.pop('colour', 'tab:blue')
    if ax is None:
        fig, ax = plt.subplots()

    N = int(2e2)

    # z = np.geomspace(0.01, z_s, N)
    # z_l = z / 2
    # y_low, y_high, y_a, y_b = y_bounds(z_l, z, bounds = True, **kwargs)

    z = z_s * np.ones(N)
    z_l = np.geomspace(1e-2, z_s, N)
    y_low, y_high, y_a, y_b = y_bounds(z_l = z_l, z_s = z, bounds = True, **kwargs)
    ax.plot(z_l, y_low, label = f'$z_s={z_s}$', c = colour)
    ax.plot(z_l, y_b, c = colour, linestyle = ':') # label = 'upper y bound time',
    ax.plot(z_l, y_a, c = colour, linestyle = '-.')
    ax.fill_between(z_l, y_high, y_low, color = colour, alpha = 0.20, where = y_high > y_low)
    ax.set_xlabel('Lens redshift, $z_l$')
    ax.set_ylabel('Lensing cross-section annulus\n $y=\\beta/\\theta_E$ bounds')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend()



def plot_redshift_integral_with_z():
    """ Plot redshift integral from paper (complex) """
    z = np.linspace(1e-1,12,1000)
    F_of_z = vector_redshift_integral(z)
    plt.plot(z, F_of_z)
    plt.show()

def plot_y_max_with_redshift():
    x = np.geomspace(1e-12,1e1, 10000)
    y = vector_y_from_Delta_t(x)
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_xlabel('Redshift, z')
    ax.set_ylabel('y max')
    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.show()

def plot_einstein_radius_with_lens_redshift():
    x = np.linspace(1e0,1e1, 10000)
    y = einstein(1e6, 1, x)
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_xlabel('Redshift, z')
    ax.set_ylabel('Cross section')
    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.show()

def plot_angular_diameter_distance_with_redshift():
    x = np.linspace(1e-1,1e2, 10000)
    y = vector_angular_diameter_distance(x)
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_xlabel('Redshift, z')
    ax.set_ylabel('Proper Distance (Mpc)')
    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.show()

def plot_proper_distance_with_redshift_proper_dist():
    x = np.linspace(1e-4,1e2, 10000)
    y = vector_pd(x)
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_xlabel('Redshift, z')
    ax.set_ylabel('Proper Distance (Mpc)')
    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.show()

def plot_efficiency_with_photon_flux():
    photon_flux = np.linspace(1e-1,1e2, 10000)
    trigger_eff = efficiency(photon_flux)
    fig, ax = plt.subplots()
    ax.plot(photon_flux, trigger_eff)
    ax.set_xlabel('Photon flux / sec / cm^2')
    ax.set_ylabel('Detection (trigger) efficiency')
    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.show()





# ============================================================================ #
# ============================================================================ #

if __name__ == '__main__':
    main()
    # print(pd(0.39,1.41))
