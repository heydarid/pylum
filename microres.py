"""
Purpose:    Computes the coupling efficiency between different bus and curved 
            waveguide microring resonator structures, using a largely analytical approach.
            Based off of Bahadori, et. al. JLT 10.1109/JLT.2018.2821359
            Units are SI unless otherwise noted.
Copyright:   (c) May 2020 David Heydari
"""

import sys, os
fileDir = os.path.dirname(os.path.abspath(__file__))
parentDir = os.path.dirname(fileDir)
print(fileDir)
import lumapi

import scipy.constants as sc
import numpy as np
pi = np.pi
c0 = sc.physical_constants["speed of light in vacuum"][0]
mu0 = sc.mu_0
eps0 = sc.epsilon_0
Z0 = 1/np.sqrt(eps0/mu0)

# wg = structure.Waveguide()
def get_Delta_n(wg, gap, wavl_oper):
    return None