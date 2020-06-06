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
        # super().
        pass