"""
Purpose:        General purpose grating on waveguide constructor.
                Non-apodized grating.  Meant for 2d cross section 
                longitudinal simulation in FDTD.
                Follows very closely Lumerical supplied code.
Structure:      Grating composed of cladding (cap), core, substrate
                Parameters include material, target length, total height,
                etch depth (here means etch into grating, NOT transverse direction), 
                duty cycle, pitch, input, and output length
                Grating is built based off of supplied 'wg' Waveguide object
                (associated with total height parameters).
Assumptions:    Grating begins after a sufficient tapering with default z_span
                of 50um (transverse direction to propagation).  Input mode fully
                occupies the wide space in both transverse directions (e.g. there is no
                notion of "etch depth" in this sense.)
Copyright:      (c) August 2020 David Heydari
"""

from collections import OrderedDict

import sys, os, math
fileDir = os.path.dirname(os.path.abspath(__file__))
parentDir = os.path.dirname(fileDir)
import lumapi

import pylum.material.materials as materials

# TODO: use regex to simplify the code

class GratingEnvironment:
    default_params = OrderedDict([
    ## default ridge waveguide material settings
        ('subs_mat', materials.silicon_nasa),
        ('core_mat', materials.silicon_nasa),
        ('cap_mat', materials.silica),
        ])
    def __init__(self, core_thickness, hideGUI=True):
        self.fdtd = lumapi.FDTD(hide=hideGUI)
        self.h_total = core_thickness
        materials.make_Si_nasa(self.fdtd)

    def _create_substrate(self):  # run first
        self.fdtd.addrect()
        self.fdtd.set("name", "substrate")

    def _grating_section(self, grating_length, pitch, dc):
        n_periods = math.ceil(grating_length/pitch)
        etch_width = pitch*(1 - dc)
        L_gra = n_periods*pitch + etch_width
        return n_periods, etch_width, L_gra

    def _set_substrate_geometry(self, input_length, output_length, L_gra, subs_thickness, z_span):
        self.fdtd.switchtolayout()
        self.fdtd.setnamed("substrate", "x min", -input_length)
        self.fdtd.setnamed("substrate", "x max", L_gra + output_length)
        self.fdtd.setnamed("substrate", "y min", -subs_thickness)
        self.fdtd.setnamed("substrate", "y max", 0)
        self.fdtd.setnamed("substrate", "z", 0)
        self.fdtd.setnamed("substrate", "z span", z_span)

    def _set_cladding_geometry(self, input_length, output_length, L_gra, 
            bottom_clad_thickness, top_clad_thickness, z_span):
        self.fdtd.switchtolayout()
        self.fdtd.setnamed("clad_bottom", "x min", -input_length)  
        self.fdtd.setnamed("clad_bottom", "x max", L_gra + output_length)
        self.fdtd.setnamed("clad_bottom", "y min", 0)
        self.fdtd.setnamed("clad_bottom", "y max", bottom_clad_thickness)
        self.fdtd.setnamed("clad_bottom", "x min", -input_length)  
        self.fdtd.setnamed("clad_bottom", "x max", L_gra + output_length)
        self.fdtd.setnamed("clad_bottom", "z", 0)
        self.fdtd.setnamed("clad_bottom", "z span", z_span)
        self.fdtd.setnamed("clad_top", "x min", -input_length)
        self.fdtd.setnamed("clad_top", "x max", L_gra + output_length)
        self.fdtd.setnamed("clad_top", "y min", 0)
        self.fdtd.setnamed("clad_top", "y max", bottom_clad_thickness + top_clad_thickness + self.h_total)
        self.fdtd.setnamed("clad_top", "z", 0)
        self.fdtd.setnamed("clad_top", "z span", z_span)
        self.fdtd.select("clad_top")
        self.fdtd.set("override mesh order from material database", True)
        self.fdtd.set("mesh order", 3)

    def _create_cladding(self):
        self.fdtd.addrect()
        self.fdtd.set("name", "clad_bottom")
        self.fdtd.addrect()
        self.fdtd.set("name", "clad_top")

    def _input_waveguide(self, input_length, bottom_clad_thickness):
        self.fdtd.addrect()
        self.fdtd.set("name", "input waveguide")
        self.fdtd.set("x min", -input_length)
        self.fdtd.set("x max", 0)
        self.fdtd.set("y min", bottom_clad_thickness)
        self.fdtd.set("y max", bottom_clad_thickness + self.h_total)

    def _output_waveguide(self, output_length, L_gra, bottom_clad_thickness):
        self.fdtd.addrect()
        self.fdtd.set("name", "output waveguide")
        self.fdtd.set("x min", L_gra)
        self.fdtd.set("x max", L_gra + output_length)
        self.fdtd.set("y min", bottom_clad_thickness)
        self.fdtd.set("y max", bottom_clad_thickness + self.h_total)

    def _create_grating(self, n_periods, pitch, etch_width, L_gra, etch_depth,
        input_length, output_length, z_span, bottom_clad_thickness):
        if etch_depth > self.h_total: 
            etch_depth = self.h_total 
        else:
            # lower layer below grating
            self.fdtd.addrect()
            self.fdtd.set("name","lower layer")
            self.fdtd.set("x min", 0)
            self.fdtd.set("x max", L_gra)
            self.fdtd.set("y min", bottom_clad_thickness)
            self.fdtd.set("y max", bottom_clad_thickness + self.h_total - etch_depth)
        # add grating
        for i in range(1, n_periods):
            self.fdtd.addrect()
            self.fdtd.set("name", "post")
            self.fdtd.set("x min", pitch*(i-1) + etch_width)
            self.fdtd.set("x max", pitch*i)
            self.fdtd.set("y min", bottom_clad_thickness + self.h_total - etch_depth)
            self.fdtd.set("y max", bottom_clad_thickness + self.h_total)
        # add ending waveguide
        self._output_waveguide(output_length, L_gra, bottom_clad_thickness)
        # set z span for all structures
        self.fdtd.selectall()
        self.fdtd.set("z", 0)
        self.fdtd.set("z span", z_span)
       
    def _grating_group(self, name='grating'):
        self.fdtd.select("input waveguide")
        self.fdtd.shiftselect("output waveguide")
        self.fdtd.shiftselect("lower layer")
        self.fdtd.shiftselect("post")
        self.fdtd.addtogroup(name)

    def create_structures(self, pitch, etch_depth, grating_length, dc, 
            z_span, input_length, output_length, subs_thickness, bottom_clad_thickness, top_clad_thickness):
        n_periods, etch_width, L_gra = self._grating_section(grating_length, pitch, dc)
        self._create_substrate()
        self._set_substrate_geometry(input_length, output_length, L_gra, subs_thickness, z_span)
        self._input_waveguide(input_length, bottom_clad_thickness)
        self._create_grating(n_periods, pitch, etch_width, L_gra, etch_depth, input_length, output_length, z_span, bottom_clad_thickness)
        self._grating_group()
        self._create_cladding()
        self._set_cladding_geometry(input_length, output_length, L_gra, bottom_clad_thickness, top_clad_thickness, z_span)

    def _set_substrate_material(self, subs_material):
        self.fdtd.setnamed("substrate", "material", subs_material)

    def _set_grating_core_material(self, core_material):
        self.fdtd.setnamed("grating::post", "material", core_material)
        self.fdtd.setnamed("grating::output waveguide", "material", core_material)
        self.fdtd.setnamed("grating::input waveguide", "material", core_material)
        self.fdtd.setnamed("grating::lower layer", "material", core_material)

    def _set_cap_material(self, cap_material):
        self.fdtd.setnamed("clad_bottom", "material", cap_material)
        self.fdtd.setnamed("clad_top", "material", cap_material)

    def _set_group_material(self, params=default_params):
        subs_material = params['subs_mat']
        core_material = params['core_mat']
        cap_material = params['cap_mat']
        self._set_substrate_material(subs_material)
        self._set_cap_material(cap_material)
        self._set_grating_core_material(core_material)

    def produce_environment(self, pitch, etch_depth, grating_length, dc, 
            z_span=50e-6, input_length=20e-6, output_length=40e-6, subs_thickness=50e-6, bottom_clad_thickness=2e-6, top_clad_thickness=1e-6):
        self.fdtd.deleteall()
        self.create_structures(pitch, etch_depth, grating_length, dc, 
            z_span, input_length, output_length, subs_thickness, bottom_clad_thickness, top_clad_thickness)
        self._set_group_material()