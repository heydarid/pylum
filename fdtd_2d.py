"""
Purpose:    FDTD solver that collects relevant data from Lumerical(R) FDTD(TM)
            FDTD simulation instance simulating longitudinal cross-section.
            Units are SI unless otherwise noted.
Useful links:
https://support.lumerical.com/hc/en-us/articles/360034917233-MODE-Finite-Difference-Eigenmode-FDE-solver-introduction
https://support.lumerical.com/hc/en-us/articles/360034382674-PML-boundary-conditions-in-FDTD-and-MODE#toc_2
https://support.lumerical.com/hc/en-us/articles/360034382694-Symmetric-and-anti-symmetric-BCs-in-FDTD-and-MODE
Copyright:   (c) August 2020 David Heydari
"""
import sys, os
fileDir = os.path.dirname(os.path.abspath(__file__))
parentDir = os.path.dirname(fileDir)
import lumapi

import scipy.constants as sc
import numpy as np
pi = np.pi
c0 = sc.physical_constants["speed of light in vacuum"][0]
mu0 = sc.mu_0
eps0 = sc.epsilon_0
Z0 = 1/np.sqrt(eps0/mu0)

class FDTD2DSimulator:
    def __init__(self, environment):
        self.environment = environment
        self.fdtd = environment.fdtd
        self.fdtd.switchtolayout()
    @property
    def xaxis(self):
        return self.mode.getdata("FDE::data::material", "x")[:,0]
    @property
    def yaxis(self):
        return self.mode.getdata("FDE::data::material", "y")[:,0]
    @property
    def index(self):
        return self.mode.getdata("FDE::data::material", "index_y")[:,:,0,0]

    def _add_2d_fdtd(self):
        self.fdtd.addfdtd()
        self.fdtd.set("dimension", 1)  # 1: 2D, 2: 3D
    def _add_mesh(self):
        self.fdtd.addmesh()
    
    
        

    def _close_application(self):
        print("Emergency close!")
        self.mode.close(True)