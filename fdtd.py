"""
Purpose:    FDTD solver that collects relevant data from Lumerical(R) FDTD(TM).
            Units are SI unless otherwise noted.
Useful links:
https://support.lumerical.com/hc/en-us/articles/360034917233-MODE-Finite-Difference-Eigenmode-FDE-solver-introduction
https://support.lumerical.com/hc/en-us/articles/360034382674-PML-boundary-conditions-in-FDTD-and-MODE#toc_2
https://support.lumerical.com/hc/en-us/articles/360034382694-Symmetric-and-anti-symmetric-BCs-in-FDTD-and-MODE
Copyright:   (c) August 2020 David Heydari
"""
import scipy.constants as sc
import numpy as np
pi = np.pi
c0 = sc.physical_constants["speed of light in vacuum"][0]
mu0 = sc.mu_0
eps0 = sc.epsilon_0
Z0 = 1/np.sqrt(eps0/mu0)

class FDTDSimulator:
    def __init__(self, environment):
        self.environment = environment
        self.fdtd = environment.fdtd
        self.fdtd.switchtolayout()
    @property
    def xaxis(self):
        return self.fdtd.getdata("FDE::data::material", "x")[:,0]
    @property
    def yaxis(self):
        return self.fdtd.getdata("FDE::data::material", "y")[:,0]
    @property
    def index(self):
        return self.fdtd.getdata("FDE::data::material", "index_y")[:,:,0,0]

    def _add_fdtd(self, dim=1):
        self.fdtd.addfdtd()
        self.fdtd.set("dimension", dim)  # 1: 2D, 2: 3D
    def _add_mesh(self, dx_mesh, dy_mesh, dz_mesh):
        self.fdtd.addmesh()
        self.fdtd.set("override x mesh", True)
        self.fdtd.set("dx", dx_mesh)
        self.fdtd.set("override y mesh", True)
        self.fdtd.set("dy", dy_mesh)
        self.fdtd.set("override z mesh", dz_mesh != 0)
        self.fdtd.set("dz", dy_mesh)
    
    ### 2d routines
    def _set_sim_region_2d(self, wavl, mesh, dx_mesh, dy_mesh):
        self._add_fdtd()
        self._add_mesh(dx_mesh, dy_mesh, dz_mesh=0)
        self.fdtd.setnamed("FDE", "y min", -4.5*self.environment.wg.height)
        self.fdtd.setnamed("FDE", "y max", 4.5*self.environment.wg.height)
        self.fdtd.setnamed("FDE", "x", 0)
        self.fdtd.setnamed("FDE", "x span", 3*wavl)
        self.fdtd.setnamed("FDE", "mesh refinement", "conformal variant 0")
        self.fdtd.setnamed("mesh", "y min", -0.5e-6)
        self.fdtd.setnamed("mesh", "y max", 2.5*self.environment.wg.height)
        self.fdtd.setnamed("mesh", "x", 0)
        self.fdtd.setnamed("mesh", "x span", 2.5*self.environment.wg.width)
        self.fdtd.setnamed("mesh", "enabled", mesh)
    
    def _set_boundary_cds(self, symmetry, boundary_cds):
        if symmetry:
            self.fdtd.setnamed("FDE", "x min bc", "Anti-Symmetric")
        else:
            self.fdtd.setnamed("FDE", "x min bc", boundary_cds[0])
        self.fdtd.setnamed("FDE", "x max bc", boundary_cds[1])
        self.fdtd.setnamed("FDE", "y min bc", boundary_cds[2])
        self.fdtd.setnamed("FDE", "y max bc", boundary_cds[3])

    def setup_sim(self, wavl, x_core=0, core_name="structure", symmetry=True,
        cap_thickness=0.5e-6, subs_thickness=3e-6, left=True, right=True, mesh=False,
        dx_mesh=10e-9, dy_mesh=10e-9, boundary_cds=['PML','PML','PML','PML']):
        self.fdtd.switchtolayout()
        self.environment.produce_environment(wavl, x_core, core_name, 
            cap_thickness, subs_thickness, left, right)
        self._set_sim_region(wavl, mesh, dx_mesh, dy_mesh)
        self._set_boundary_cds(symmetry, boundary_cds)

    ### 3d routines
    def _set_sim_region_3d(self, wavl, mesh, dx_mesh, dy_mesh):
        pass

    ### Application
    def _close_application(self):
        print("Emergency close!")
        self.fdtd.close(True)