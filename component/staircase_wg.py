"""
Purpose:    General purpose ridge waveguide environment constructor.
            All units SI unless otherwise specified.
Structure:  Staircase-like waveguide structure composed of cladding (cap), core, substrate
            Simulation region is cross-section of waveguide in xy, at some z-slice
            Assumes etching is performed, at each step in the lithography, symmetrically
            around the core waveguide.
Copyright:   (c) November 2020 David Heydari
"""

"""
Example of material_params argument:
    material_params = OrderedDict([
        ('subs_mat', dielectrics.silica),
        ('core_mat', dielectrics.silicon_nasa),
        ('cap_mat', dielectrics.silica),
        ])
width2: total extension width
width1: central core
"""

class Staircase:
    def __init__(self, width, width2, height, etch1, etch2):
        self.width1 = width
        self.width2 = width2
        self.width = self.width1 + self.width2
        self.height = height
        self.etch = etch1
        self.etch2 = etch2

class StaircaseWaveguide:
    def __init__(self, wg, material_params):
        self.wg = wg
        self.material_params = material_params

    def _create_substrate(self, program):  # run first
        program.addrect()
        program.set("name", "substrate")

    def _create_flanks(self, program):
        program.addrect()
        program.set("name", "flank_l")
        program.addrect()
        program.set("name", "flank_r")
    
    def _create_pedestals(self, program):
        program.addrect()
        program.set("name", "pedestal_l")
        program.addrect()
        program.set("name", "pedestal_r")

    def _create_claddings(self, program):
        program.addrect()
        program.set("name", "cladding_core")
        program.addrect()
        program.set("name", "clad_pedestal_l")
        program.addrect()
        program.set("name", "clad_pedestal_r")
        program.addrect()
        program.set("name", "clad_flank_l")
        program.addrect()
        program.set("name", "clad_flank_r")

    def _create_core(self, program):
        program.addrect()
        program.set("name", "guide")

    def create_structures(self, program):
        self._create_substrate(program)
        self._create_flanks(program)
        self._create_pedestals(program)
        self._create_claddings(program)
        self._create_core(program)

    def _add_to_core_group(self, program, name):
        program.select("guide")
        program.shiftselect("pedestal_l")
        program.shiftselect("pedestal_r")
        program.shiftselect("flank_l")
        program.shiftselect("flank_r")
        program.shiftselect("cladding_core")
        program.shiftselect("clad_pedestal_l")
        program.shiftselect("clad_pedestal_r")
        program.shiftselect("clad_flank_l")
        program.shiftselect("clad_flank_r")
        program.addtogroup(name)

    def _set_substrate_material(self, program, subs_material):
        program.setnamed("substrate", "material", subs_material)

    def _set_core_material(self, program, core_material, name):
        program.setnamed(name + "::guide", "material", core_material)
        program.setnamed(name + "::pedestal_l", "material", core_material)
        program.setnamed(name + "::pedestal_r", "material", core_material)
        program.setnamed(name + "::flank_l", "material", core_material)
        program.setnamed(name + "::flank_r", "material", core_material)

    def _set_cap_material(self, program, cap_material, name):
        program.setnamed(name + "::cladding_core", "material", cap_material)
        program.setnamed(name + "::clad_pedestal_l", "material", cap_material)
        program.setnamed(name + "::clad_pedestal_r", "material", cap_material)
        program.setnamed(name + "::clad_flank_l", "material", cap_material)
        program.setnamed(name + "::clad_flank_r", "material", cap_material)

    def set_group_material(self, program, name):
        subs_material = self.material_params['subs_mat']
        core_material = self.material_params['core_mat']
        cap_material = self.material_params['cap_mat']
        self._set_substrate_material(program, subs_material)
        self._set_cap_material(program, cap_material, name)
        self._set_core_material(program, core_material, name)

    def set_mesh_orders(self, program, name):
        program.select(name + "::cladding_core")
        program.set("override mesh order from material database", True)
        program.set("mesh order", 4)
        program.select(name + "::clad_flank_l")
        program.set("override mesh order from material database", True)
        program.set("mesh order", 5)
        program.select(name + "::clad_flank_r")
        program.set("override mesh order from material database", True)
        program.set("mesh order", 5)
        program.select(name + "::clad_pedestal_l")
        program.set("override mesh order from material database", True)
        program.set("mesh order", 6)
        program.select(name + "::clad_pedestal_r")
        program.set("override mesh order from material database", True)
        program.set("mesh order", 6)
        program.select(name + "::guide")
        program.set("override mesh order from material database", True)
        program.set("mesh order", 1)
        program.select(name + "::flank_l")
        program.set("override mesh order from material database", True)
        program.set("mesh order", 2)
        program.select(name + "::flank_r")
        program.set("override mesh order from material database", True)
        program.set("mesh order", 2)
        program.select(name + "::pedestal_l")
        program.set("override mesh order from material database", True)
        program.set("mesh order", 3)
        program.select(name + "::pedestal_r")
        program.set("override mesh order from material database", True)
        program.set("mesh order", 3)

    def _set_substrate_geometry(self, program, wavl, x_core, subs_thickness):
        program.switchtolayout()
        program.setnamed("substrate", "x", x_core)  
        program.setnamed("substrate", "x span", 20*wavl)
        program.setnamed("substrate", "y min", -subs_thickness)
        program.setnamed("substrate", "y max", 0)

    def _set_core_geometry(self, program, name, x_core, cap_thickness):
        program.switchtolayout()
        program.setnamed(name + "::guide", "x", x_core)
        program.setnamed(name + "::guide", "x span", self.wg.width1)
        program.setnamed(name + "::guide", "y min", 0)
        program.setnamed(name + "::guide", "y max", self.wg.height)

    def _set_pedestal_geometry(self, program, name, wavl, x_core):
        program.switchtolayout()
        program.setnamed(name + "::pedestal_l", "x min", -10*wavl)
        program.setnamed(name + "::pedestal_l", "x max", x_core)
        program.setnamed(name + "::pedestal_l", "y min", 0)
        program.setnamed(name + "::pedestal_l", "y max", self.wg.height - self.wg.etch)
        program.setnamed(name + "::pedestal_r", "x min", x_core)
        program.setnamed(name + "::pedestal_r", "x max", 10*wavl)
        program.setnamed(name + "::pedestal_r", "y min", 0)
        program.setnamed(name + "::pedestal_r", "y max", self.wg.height - self.wg.etch)

    def _set_flank_geometry(self, program, name, x_core):
        program.switchtolayout()
        program.setnamed(name + "::flank_l", "x min", -self.wg.width/2)
        program.setnamed(name + "::flank_l", "x max", x_core)
        program.setnamed(name + "::flank_l", "y min", 0)
        program.setnamed(name + "::flank_l", "y max", self.wg.height - self.wg.etch2)
        program.setnamed(name + "::flank_r", "x min", x_core)
        program.setnamed(name + "::flank_r", "x max", self.wg.width/2)
        program.setnamed(name + "::flank_r", "y min", 0)
        program.setnamed(name + "::flank_r", "y max", self.wg.height - self.wg.etch2)
    
    def _set_cladding_geometry(self, program, name, x_core, wavl, cap_thickness):
        program.switchtolayout()
        program.setnamed(name + "::cladding_core", "x", x_core)
        program.setnamed(name + "::cladding_core", "x span", self.wg.width1 + cap_thickness)
        program.setnamed(name + "::cladding_core", "y min", 0)
        program.setnamed(name + "::cladding_core", "y max", self.wg.height + cap_thickness)
        program.setnamed(name + "::clad_pedestal_l", "x min", -10*wavl)
        program.setnamed(name + "::clad_pedestal_l", "x max", x_core)
        program.setnamed(name + "::clad_pedestal_l", "y min", 0)
        program.setnamed(name + "::clad_pedestal_l", "y max", self.wg.height - self.wg.etch + cap_thickness)
        program.setnamed(name + "::clad_pedestal_r", "x min", x_core)
        program.setnamed(name + "::clad_pedestal_r", "x max", 10*wavl)
        program.setnamed(name + "::clad_pedestal_r", "y min", 0)
        program.setnamed(name + "::clad_pedestal_r", "y max", self.wg.height - self.wg.etch + cap_thickness)

        program.setnamed(name + "::clad_flank_l", "x min", -self.wg.width/2)
        program.setnamed(name + "::clad_flank_l", "x max", x_core)
        program.setnamed(name + "::clad_flank_l", "y min", 0)
        program.setnamed(name + "::clad_flank_l", "y max", self.wg.height - self.wg.etch2 + cap_thickness)
        program.setnamed(name + "::clad_flank_r", "x min", x_core)
        program.setnamed(name + "::clad_flank_r", "x max", self.wg.width/2)
        program.setnamed(name + "::clad_flank_r", "y min", 0)
        program.setnamed(name + "::clad_flank_r", "y max", self.wg.height - self.wg.etch2 + cap_thickness)

    def _enable_pedestal(self, program, name, left, right):
        program.switchtolayout()
        program.setnamed(name + "::pedestal_l", "enabled", left)
        program.setnamed(name + "::pedestal_r", "enabled", right)
        program.setnamed(name + "::clad_pedestal_l", "enabled", left)
        program.setnamed(name + "::clad_pedestal_r", "enabled", right)

    def set_geometry(self, program, wavl, x_core, name, 
            subs_thickness, cap_thickness, left, right):
        self._set_substrate_geometry(program, wavl, x_core, subs_thickness)
        self._set_pedestal_geometry(program, name, wavl, x_core)
        self._set_flank_geometry(program, name, x_core)
        self._set_cladding_geometry(program, name, x_core, wavl, cap_thickness)
        self._set_core_geometry(program, name, x_core, cap_thickness)
        self._enable_pedestal(program, name, left, right)

    def produce_component(self, program, wavl, x_core, core_name, 
            cap_thickness, subs_thickness, left, right):
        program.deleteall()
        self.create_structures(program)
        self._add_to_core_group(program, core_name)
        self.set_group_material(program, core_name)
        self.set_geometry(program, wavl, x_core, core_name, subs_thickness, 
            cap_thickness, left, right)
        self.set_mesh_orders(program, core_name)

    def save_file(self, program, path):
        program.save(path)
    def _close_application(self, program):
        program.exit(True)