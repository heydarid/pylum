"""
Purpose:    Computes the coupling efficiency between different bus and curved 
            waveguide microring resonator structures, using a largely analytical approach.
            Based off of Bahadori, et. al. JLT 10.1109/JLT.2018.2821359
            Units are SI unless otherwise noted.
Copyright:   (c) May 2020 David Heydari
"""

import lumapi

import scipy.constants as sc
import numpy as np
pi = np.pi
c0 = sc.physical_constants["speed of light in vacuum"][0] 
mu0 = sc.mu_0
eps0 = sc.epsilon_0
Z0 = 1/np.sqrt(eps0/mu0)

from pylum.fdemode import FDEModeSimulator

class FDECoupledModeSimulator(FDEModeSimulator):
    def __init__(self, environment):
        self.environment = environment
        self.mode.switchtolayout()
    @property
    def xaxis(self):
        return self.mode.getdata("FDE::data::material", "x")[:,0]
    @property
    def yaxis(self):
        return self.mode.getdata("FDE::data::material", "y")[:,0]
    @property
    def index(self):
        return self.mode.getdata("FDE::data::material", "index_y")[:,:,0,0]

    def setup_sim(self, pml_wavl, cap_thickness=0.5e-6, subs_thickness=3e-6, mesh=False):
        self.mode.switchtolayout()
        self.environment.produce_environment(pml_wavl, subs_thickness, cap_thickness)
        super()._set_sim_region(pml_wavl, mesh)
        super()._set_boundary_cds(symmetry=False)
    
    def solve_modes()

class FDECoupledModeSimData:
    def __init__(self):
        self.xaxis = xaxis
        self.yaxis = yaxis
        self.wavl = wavel
        self.index = index
    @property
    def even_mode(self):
        self.E_field = E_field
        self.H_field = H_field
        self.n_grps = n_grp
        self.n_effs = n_eff
    @property
    def odd_mode(self):
        self.E_field = E_field
        self.H_field = H_field
        self.n_grps = n_grp
        self.n_effs = n_eff

    def get_Delta_n(self):
        return np.abs(np.real(self.even_mode.n_effs - self.odd_mode.n_effs))

class CouplingRegion:
    