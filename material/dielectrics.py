"""
Purpose:    Creates custom materials into the Lumerical material database
            from data ported from RefractiveIndex.info database.
Structure:  Ridge-waveguide composed of cladding, core, substrate
            Simulation region is cross-section of waveguide in xy, at some z-slice
Copyright:   (c) June 2020 David Heydari
"""

import scipy.constants as sc
import numpy as np
pi = np.pi
c0 = sc.c
mu0 = sc.mu_0
eps0 = sc.epsilon_0
Z0 = 1/np.sqrt(eps0/mu0)

import numpy as np
# TODO: include RII db

# Common Lumerical materials (listed)
air = 'etch'
silicon = 'Si (Silicon) - Palik'
silica = 'SiO2 (Glass) - Palik'

# Materials from Sellmeier
#### Silicon ####
def make_Si_nasa(solver, T=295, fit_coefs=10):
    from .indexmodels import Si
    name = 'Si (Silicon) - NASA'
    wavls = np.linspace(1, 4, 1000)*1e-6
    eps = Si.NASA(wavls, T)
    solver.setmaterial(solver.addmaterial("Sampled data"), "name", name)
    solver.setmaterial(name, "max coefficients", fit_coefs) 
    solver.setmaterial(name, "sampled data", np.array([c0 / wavls, eps]).T)
    return name
silicon_nasa = 'Si (Silicon) - NASA'

# Anisotropic materials
#### MgO:LiNbO3 ####
def make_LN_gayer(solver, T=295, fit_coefs=10):
    from .indexmodels import MgOLN
    name = 'MgO:LN - Gayer'
    wavls = np.linspace(0.5, 4, 1000)*1e-6
    eps_o = MgOLN.gayer2008_o(wavls, T)
    eps_e = MgOLN.gayer2008_e(wavls, T)
    solver.setmaterial(solver.addmaterial("Sampled data"), "name", name)
    solver.setmaterial(name, "Anisotropy", 1)
    solver.setmaterial(name, "max coefficients", fit_coefs) 
    solver.setmaterial(name, "sampled data", 
        np.array([c0 / wavls, eps_o, eps_o, eps_e]).T)
    return name
gayer_LN = 'MgO:LN - Gayer'