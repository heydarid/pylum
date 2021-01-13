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
c0 = sc.physical_constants["speed of light in vacuum"][0]
mu0 = sc.mu_0
eps0 = sc.epsilon_0
Z0 = 1/np.sqrt(eps0/mu0)

import n_Si
import numpy as np

# TODO: include RII db

# Common Lumerical materials
silicon = 'Si (Silicon) - Palik'
silica = 'SiO2 (Glass) - Palik'

# Materials from Sellmeier
#### Silicon ####
#TODO: Make this function work!
def make_Si_nasa(mode_object):
    m = mode_object
    T = 295 # room temperature, Kelvin
    wavls = np.linspace(1, 4, 300)*1e-6
    f = c0 / wavls
    eps = (n_Si.n_Si(wavls, T))**2
    sampledData = np.array([f, eps]).T
    matName = 'Si (Silicon) - NASA'
    temp = m.addmaterial("Sampled data")
    m.setmaterial(temp, "name", matName)
    m.setmaterial(matName, "max coefficients", 2) 
    m.setmaterial(matName, "sampled data", sampledData)
    return silicon_nasa
silicon_nasa = 'Si (Silicon) - NASA'