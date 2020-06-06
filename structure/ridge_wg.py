"""
Purpose:    General purpose ridge waveguide environment constructor.
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

class RidgeWaveguideEnvironment:
    default_params = OrderedDict([
    ## default ridge waveguide material settings
        ('subs_mat', materials.silica),
        ('core_mat', materials.silicon),
        ('cap_mat', materials.silica),
        ])
    def __init__(self, wg, hideGUI=True):
        self.mode = lumapi.MODE(hide=hideGUI)
        self.wg = wg

    def _create_structures(self): # run first
        self.mode.addrect()
        self.mode.set("name", "guide")
        self.mode.addrect()
        self.mode.set("name", "pedestal")
        self.mode.addrect()
        self.mode.set("name", "substrate")
        self.mode.addrect()
        self.mode.set("name", "cladding")
        self.mode.selectall()
        self.mode.addtogroup("structure")

    def _set_substrate_material(self, subs_material):
        self.mode.setnamed("structure::substrate", "material", subs_material)

    def _set_core_material(self, core_material):
        self.mode.setnamed("structure::guide", "material", core_material)
        self.mode.setnamed("structure::pedestal", "material", core_material)

    def _set_cap_material(self, cap_material):
        self.mode.setnamed("structure::cladding", "material", cap_material)

    def _set_group_material(self, params=default_params):
        subs_material = params['subs_mat']
        core_material = params['core_mat']
        cap_material = params['cap_mat']
        self._set_cap_material(cap_material)
        self._set_core_material(core_material)
        self._set_substrate_material(subs_material)

    def _set_mesh_orders(self):
        self.mode.select("structure::cladding")
        self.mode.set("override mesh order from material database", True)
        self.mode.set("mesh order", 4)
        self.mode.select("structure::guide")
        self.mode.set("override mesh order from material database", True)
        self.mode.set("mesh order", 3)
        self.mode.select("structure::pedestal")
        self.mode.set("override mesh order from material database", True)
        self.mode.set("mesh order", 2)

    def _set_geometry(self, wg, wavl, cap_thickness, subs_thickness):
        self.mode.switchtolayout()
        self.mode.setnamed("structure::guide", "x", 0)
        self.mode.setnamed("structure::pedestal", "x", 0)
        self.mode.setnamed("structure::cladding", "x", 0)
        self.mode.setnamed("structure::substrate", "x", 0)
        self.mode.setnamed("structure::cladding", "x span", self.wg.width + cap_thickness)
        self.mode.setnamed("structure::guide", "x span", self.wg.width)
        self.mode.setnamed("structure::guide", "y min", 0)
        self.mode.setnamed("structure::guide", "y max", self.wg.height)
        self.mode.setnamed("structure::pedestal", "x span", 20*wavl)
        self.mode.setnamed("structure::cladding", "y min", 0)
        self.mode.setnamed("structure::cladding", "y max", self.wg.height + cap_thickness)
        self.mode.setnamed("structure::pedestal", "y min", 0)
        self.mode.setnamed("structure::pedestal", "y max", self.wg.height - self.wg.etch)
        self.mode.setnamed("structure::substrate", "x span", 20*wavl)
        self.mode.setnamed("structure::substrate", "y min", -subs_thickness)
        self.mode.setnamed("structure::substrate", "y max", 0)
    
    def produce_environment(self, wg, wavl, cap_thickness=0.5e-6, subs_thickness=3e-6):
        self._create_structures()
        self._set_group_material()
        self._set_geometry(wg, wavl, cap_thickness, subs_thickness)
        self._set_mesh_orders()

    def save_file(self, path):
        self.mode.save(path)
    def _close_application(self):
        self.mode.exit(True)