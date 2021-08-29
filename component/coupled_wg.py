"""
Purpose:    General purpose coupled-ridge waveguide environment constructor.
            All units SI unless otherwise specified.
Structure:  Ridge-waveguide composed of cladding (cap), core, substrate
            Simulation region is cross-section of waveguide in xy, at some z-slice
Copyright:  (c) June 2020 David Heydari
"""

"""
Example of material_params argument:
    material_params = OrderedDict([
        ('subs_mat', dielectrics.silica),
        ('core_mat', dielectrics.silicon_nasa),
        ('cap_mat', dielectrics.silica),
        ])
"""

from .ridge_wg import Waveguide
from .ridge_wg import RidgeWaveguide

class CoupledWaveguide:
    def __init__(self, gap, gap_etch, width_l, width_r, 
                height, etch_l, etch_r):
        self.height = height
        self.gap = gap
        self.gap_etch = gap_etch
        self.width = width_l + width_r + gap  # for simulation purposes only
        self.left_wg = Waveguide(width_l, self.height, etch_l)
        self.right_wg = Waveguide(width_r, self.height, etch_r)

class CoupledRidgeWaveguide:
    def __init__(self, coupled_wg, material_params, hideGUI=True):
        self.wg = coupled_wg
        self.material_params = material_params

    def _create_ridges(self, program, wavl, cap_thickness, subs_thickness):
        left = RidgeWaveguide(self.wg.left_wg, self.material_params)
        x_left_core = -(self.wg.left_wg.width + self.wg.gap)/2
        left.produce_component(program, wavl, x_core=x_left_core, core_name="left_guide", 
                                cap_thickness=cap_thickness, subs_thickness=subs_thickness, 
                                left=True, right=False, cleanup=True)
        x_right_core = (self.wg.right_wg.width + self.wg.gap)/2
        right = RidgeWaveguide(self.wg.right_wg, self.material_params)
        right.produce_component(program, wavl, x_core=x_right_core, core_name="right_guide", 
                                cap_thickness=cap_thickness, subs_thickness=subs_thickness, 
                                left=False, right=True, cleanup=False)

    def component_switch(self, program, left, right, gap, name):
        program.switchtolayout()
        program.setnamed(name + "::gap", "enabled", gap)
        program.setnamed(name + "::gap_clad", "enabled", gap)
        program.setnamed(name + "::left_guide", "enabled", left)
        program.setnamed(name + "::right_guide", "enabled", right)

    def _create_gap_pedestal(self, program):
        program.addrect()
        program.set("name", "gap")
    def _create_gap_cladding(self, program):
        program.addrect()
        program.set("name", "gap_clad")

    def _set_gap_geometry(self, program):
        program.switchtolayout()
        program.set("name", "gap")
        program.setnamed("gap", "x", 0)
        program.setnamed("gap", "x span", self.wg.gap)
        program.setnamed("gap", "y min", 0)
        program.setnamed("gap", "y max", self.wg.height - self.wg.gap_etch)
    def _set_gap_clad_geometry(self, program, cap_thickness):
        program.switchtolayout()
        program.set("name", "gap_clad")
        program.setnamed("gap_clad", "x", 0)
        program.setnamed("gap_clad", "x span", self.wg.gap)
        program.setnamed("gap_clad", "y min", 0)
        program.setnamed("gap_clad", "y max", self.wg.height - self.wg.gap_etch 
                            + cap_thickness)
    def set_geometry(self, program, cap_thickness):
        self._set_gap_geometry(program)
        self._set_gap_clad_geometry(program, cap_thickness)

    def _set_gap_core_material(self, program, core_material, name):
        program.setnamed(name + "::gap", "material", core_material)
    def _set_gap_cap_material(self, program, cap_material, name):
        program.setnamed(name + "::gap_clad", "material", cap_material)
    def set_gap_materials(self, program, name):
        core_material = self.material_params['core_mat']
        cap_material = self.material_params['cap_mat']
        self._set_gap_core_material(program, core_material, name)
        self._set_gap_cap_material(program, cap_material, name)

    def set_mesh_orders(self, program, name):
        program.select(name + "::gap")
        program.set("override mesh order from material database", True)
        program.set("mesh order", 3)
        program.select(name + "::gap_clad")
        program.set("override mesh order from material database", True)
        program.set("mesh order", 4)

    def _add_to_core_group(self, program, name):
        program.selectall()
        program.addtogroup(name)

    def produce_component(self, program, wavl, x_core, name, 
                            cap_thickness, subs_thickness):
        self._create_ridges(program, wavl, cap_thickness, subs_thickness)
        self._create_gap_pedestal(program)
        self._create_gap_cladding(program)
        self.set_geometry(program, cap_thickness)
        self._add_to_core_group(program, name)
        self.set_mesh_orders(program, name)
        self.set_gap_materials(program, name)

    def save_file(self, program, path):
        program.save(path)
    def _close_application(self, program):
        program.exit(True)