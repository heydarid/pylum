"""
Purpose:    General purpose coupled-ridge waveguide environment constructor.
            All units SI unless otherwise specified.
Structure:  Ridge-waveguide composed of cladding (cap), core, substrate
            Simulation region is cross-section of waveguide in xy, at some z-slice
Copyright:   (c) June 2020 David Heydari
"""

from collections import OrderedDict

import sys, os
fileDir = os.path.dirname(os.path.abspath(__file__))
parentDir = os.path.dirname(fileDir)
print(fileDir)
import lumapi

import pylum.material.materials as materials
from pylum.structure.ridge_wg import RidgeWaveguideEnvironment
from pylum.structure.waveguide import Waveguide

class CoupledWaveguide:
    def __init__(self, width_l, width_r, height, etch_l, etch_r):
        self.width_l = width_l
        self.width_r = width_r
        self.height = height
        self.etch_l = etch_l
        self.etch_r = etch_r

class CoupledRidgeWaveguideEnvironment(RidgeWaveguideEnvironment):
    default_params = OrderedDict([
    ## default ridge waveguide material settings
        ('subs_mat', materials.silica),
        ('core_mat', materials.silicon),
        ('cap_mat', materials.silica),
        ])
    def __init__(self, wg, hideGUI=True):
        super().__init__(wg, hideGUI)
        self.mode = lumapi.MODE(hide=hideGUI)
        self.wg = wg

    def _create_coupled_guides(self):
        super()._create_structures()
        
    def produce_environment(self):
