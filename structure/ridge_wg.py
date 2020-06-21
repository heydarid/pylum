"""
Purpose:    General purpose ridge waveguide environment constructor.
            All units SI unless otherwise specified.
Structure:  Ridge-waveguide composed of cladding (cap), core, substrate
            Simulation region is cross-section of waveguide in xy, at some z-slice
            Assumes etching is performed, at each step in the lithography, symmetrically
            around the core waveguide.
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

    def _create_substrate(self):  # run first
        self.mode.addrect()
        self.mode.set("name", "substrate")

    def _create_pedestals(self):
        self.mode.addrect()
        self.mode.set("name", "pedestal_l")
        self.mode.addrect()
        self.mode.set("name", "pedestal_r")

    def _create_core(self):
        self.mode.addrect()
        self.mode.set("name", "guide")
        self.mode.addrect()
        self.mode.set("name", "cladding")

    def create_structures(self):
        self._create_substrate()
        self._create_pedestals()
        self._create_core()

    def _add_to_core_group(self, name):
        self.mode.select("guide")
        self.mode.select("cladding")
        self.mode.select("pedestal_l")
        self.mode.select("pedestal_r")
        self.mode.addtogroup(name)

    def _set_substrate_material(self, subs_material):
        self.mode.setnamed("substrate", "material", subs_material)

    def _set_core_material(self, core_material, name):
        self.mode.setnamed(name + "::guide", "material", core_material)
        self.mode.setnamed(name + "pedestal_l", "material", core_material)
        self.mode.setnamed(name + "pedestal_r", "material", core_material)

    def _set_cap_material(self, cap_material, name):
        self.mode.setnamed(name + "::cladding", "material", cap_material)

    def set_group_material(self, name, params=default_params):
        subs_material = params['subs_mat']
        core_material = params['core_mat']
        cap_material = params['cap_mat']
        self._set_cap_material(cap_material, name)
        self._set_core_material(core_material, name)
        self._set_substrate_material(subs_material)

    def set_mesh_orders(self, name):
        self.mode.select(name + "::cladding")
        self.mode.set("override mesh order from material database", True)
        self.mode.set("mesh order", 4)
        self.mode.select(name + "::guide")
        self.mode.set("override mesh order from material database", True)
        self.mode.set("mesh order", 3)
        self.mode.select(name + "::pedestal_l")
        self.mode.set("override mesh order from material database", True)
        self.mode.set("mesh order", 2)
        self.mode.select(name + "::pedestal_r")
        self.mode.set("override mesh order from material database", True)
        self.mode.set("mesh order", 2)

    def _set_substrate_geometry(self, wavl, subs_thickness):
        self.mode.switchtolayout()
        self.mode.setnamed("substrate", "x", 0)  
        self.mode.setnamed("substrate", "x span", 20*wavl)
        self.mode.setnamed("substrate", "y min", -subs_thickness)
        self.mode.setnamed("substrate", "y max", 0)

    def _set_pedestal_geometry(self, wavl, wg, name, left, right):
        self.mode.switchtolayout()
        self.mode.setnamed(name + "::pedestal_l", "x min", 10*wavl)
        self.mode.setnamed(name + "::pedestal_l", "x max", 0)
        self.mode.setnamed(name + "::pedestal_l", "y min", 0)
        self.mode.setnamed(name + "::pedestal_l", "y max", self.wg.height - self.wg.etch)

        self.mode.setnamed(name + "::pedestal_r", "x min", 0)
        self.mode.setnamed(name + "::pedestal_r", "x max", 10*wavl)
        self.mode.setnamed(name + "::pedestal_r", "y min", 0)
        self.mode.setnamed(name + "::pedestal_r", "y max", self.wg.height - self.wg.etch)

        self.mode.setnamed(name + "::pedestal_l", "enabled", left)
        self.mode.setnamed(name + "::pedestal_r", "enabled", right)
    
    def _set_core_geometry(self, wg, cap_thickness, x_core):
        self.mode.switchtolayout()
        self.mode.setnamed("structure::guide", "x", x_core)
        self.mode.setnamed("structure::guide", "x span", self.wg.width)
        self.mode.setnamed("structure::guide", "y min", 0)
        self.mode.setnamed("structure::guide", "y max", self.wg.height)
        
        self.mode.setnamed("structure::cladding", "x", x_core)
        self.mode.setnamed("structure::cladding", "x span", self.wg.width + cap_thickness)
        self.mode.setnamed("structure::cladding", "y min", 0)
        self.mode.setnamed("structure::cladding", "y max", self.wg.height + cap_thickness)

    def set_geometry(self, wavl, wg, name, subs_thickness, cap_thickness, 
        x_core, left, right):
        self._set_substrate_geometry(wavl, subs_thickness)
        self._set_pedestal_geometry(wavl, wg, name, left, right)
        self._set_core_geometry(wg, cap_thickness, x_core)

    def produce_environment(self, wg, wavl, x_core=0, core_name="structure", 
            cap_thickness=0.5e-6, subs_thickness=3e-6, left=True, right=True):
        self.create_structures()
        self._add_to_core_group(core_name)
        self.set_group_material(core_name)
        self.set_geometry(wavl, wg, core_name, subs_thickness, cap_thickness, 
            x_core, left, right)
        self.set_mesh_orders(core_name)

    def save_file(self, path):
        self.mode.save(path)
    def _close_application(self):
        self.mode.exit(True)