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

class CoupledWaveguide(Waveguide):
    def __init__(self, gap, gap_etch, width_l, width_r, 
        height, etch_l, etch_r):
        self.gap = gap
        self.gap_etch = gap_etch
        self.width_l = width_l
        self.width_r = width_r
        self.height = height
        self.etch_l = etch_l
        self.etch_r = etch_r
    def left_wg(self):
        return super().__init__(self.width_l, self.height, self.etch_l)
    def right_wg(self):
        return super().__init__(self.width_r, self.height, self.etch_r)

class CoupledRidgeWaveguideEnvironment(RidgeWaveguideEnvironment):
    default_params = OrderedDict([
    ## default ridge waveguide material settings
        ('subs_mat', materials.silica),
        ('core_mat', materials.silicon),
        ('cap_mat', materials.silica),
        ])
    def __init__(self, coupled_wg, hideGUI=True):
        super().__init__(coupled_wg)
        self.coupled_wg = coupled_wg

    def _create_gap_pedestal(self, cap_thickness):
        self.mode.switchtolayout()
        self.mode.addrect()
        self.mode.set("name", "gap")
        self.mode.setnamed("gap", "x", 0)
        self.mode.setnamed("gap", "x span", self.coupled_wg.gap)
        self.mode.setnamed("gap", "y min", 0)
        self.mode.setnamed("gap", "y max", self.coupled_wg.height - self.coupled_wg.gap_etch)

        self.mode.addrect()
        self.mode.set("name", "gap_clad")
        self.mode.setnamed("gap_clad", "x", 0)
        self.mode.setnamed("gap_clad", "x span", self.coupled_wg.gap)
        self.mode.setnamed("gap_clad", "y min", 0)
        self.mode.setnamed("gap_clad", "y max", self.coupled_wg.height - self.coupled_wg.gap_etch + cap_thickness)

    def _set_gap_geometry(self, params=default_params):
        self.mode.setnamed("gap", "material", params['core_mat'])
        self.mode.setnamed("gap_clad", "material", params['cap_mat'])

    def _set_gap_mesh_order(self):
        self.mode.select("gap_clad")
        self.mode.set("override mesh order from material database", True)
        self.mode.set("mesh order", 4)
        self.mode.select("gap")
        self.mode.set("override mesh order from material database", True)
        self.mode.set("mesh order", 3)

    def create_structures(self):
        super()._create_pedestals()
        super()._create_claddings()
        super()._create_core()

    def create_coupled_guides(self, wavl, subs_thickness, cap_thickness, params=default_params):
        super()._create_substrate()
        self.create_structures()
        super()._add_to_core_group("left_guide")
        super().set_group_material("left_guide", params)
        super().set_geometry(wavl, self.coupled_wg.left_wg(), name="left_guide", 
            subs_thickness=subs_thickness, cap_thickness=cap_thickness, 
            x_core=-(self.coupled_wg.gap + self.coupled_wg.width_l)/2, left=True, right=False)
        super().set_mesh_orders("left_guide")

        self.create_structures()
        super()._add_to_core_group("right_guide")
        super().set_group_material("right_guide", params)
        super().set_geometry(wavl, self.coupled_wg.right_wg(), name="right_guide", 
            subs_thickness=subs_thickness, cap_thickness=cap_thickness, 
            x_core=(self.coupled_wg.gap + self.coupled_wg.width_r)/2, left=False, right=True)
        super().set_mesh_orders("right_guide")

        self._create_gap_pedestal(cap_thickness)
        self._set_gap_geometry(params)

    def produce_environment(self):
        pass