"""
Purpose:        FDTD solver that collects relevant data from Lumerical(R) FDTD(TM).
                Units are SI unless otherwise noted.
Assumptions:    Propagation in z direction (if 3d).  Cross-section in x-y plane.     
Copyright:      (c) August 2020 David Heydari
"""
import scipy.constants as consts
import numpy as np
pi = np.pi
c0 = consts.c
mu0 = consts.mu_0
eps0 = consts.epsilon_0
Z0 = 1/np.sqrt(eps0/mu0)
import enum
from enum import IntEnum
import lumapi

"""
TODO: 
"""

class MonitorType(IntEnum):
    POINT = 1
    LINEARX = 2
    LINEARY = 3
    LINEARZ = 4
    XNORMAL2D = 5
    YNORMAL2D = 6
    ZNORMAL2D = 7
    a3D = 8

class FDTDSimulation:
    def __init__(self, component, hideGUI=True):
        self.fdtd = lumapi.FDTD(hide=hideGUI)
        self.component = component
        self.fdtd.switchtolayout()
    @property
    def xaxis(self):
        return self.fdtd.getdata("FDTD::data::material", "x")[:,0]
    @property
    def yaxis(self):
        return self.fdtd.getdata("FDTD::data::material", "y")[:,0]
    @property
    def index(self):
        return self.fdtd.getdata("FDTD::data::material", "index_y")[:,:,0,0]

    def _add_fdtd(self, dim):
        self.fdtd.addfdtd()
        self.fdtd.set("dimension", dim)  # 1: 2D, 2: 3D
    def _modify_mesh(self, dx_mesh, dy_mesh, dz_mesh):
        self.fdtd.set("override x mesh", True)
        self.fdtd.set("dx", dx_mesh)
        self.fdtd.set("override y mesh", True)
        self.fdtd.set("dy", dy_mesh)
        self.fdtd.set("override z mesh", dz_mesh != 0)
        self.fdtd.set("dz", dz_mesh)

    def _set_sim_region(self, dim, wavl, mesh, dx_mesh, dy_mesh, 
            boundary_cds, dz_mesh):
        self._add_fdtd(dim)
        self.fdtd.addmesh()
        self._modify_mesh(dx_mesh, dy_mesh, dz_mesh=0)
        if 'PML' in boundary_cds:
            self.fdtd.setnamed("FDE", "y", self.component.wg.height/2.)
            self.fdtd.setnamed("FDE", "y span", self.component.wg.height + wavl)
            self.fdtd.setnamed("FDE", "x", 0)
            self.fdtd.setnamed("FDE", "x span", self.component.wg.width + wavl)
        elif 'Metal' in boundary_cds:
            self.fdtd.setnamed("FDE", "y", self.component.wg.height/2.)
            self.fdtd.setnamed("FDE", "y span", 3.5*(self.component.wg.height + wavl))
            self.fdtd.setnamed("FDE", "x", 0)
            self.fdtd.setnamed("FDE", "x span", 3.5*(self.component.wg.width + wavl))
        self.fdtd.setnamed("FDE", "mesh refinement", "conformal variant 0")  
            # acceptable for sims involving non-metals.
        self.fdtd.setnamed("mesh", "y", self.component.wg.height/2.)
        self.fdtd.setnamed("mesh", "y span", 1.05*self.component.wg.height)
        self.fdtd.setnamed("mesh", "x", 0)
        self.fdtd.setnamed("mesh", "x span", 1.05*self.component.wg.width)
        self.fdtd.setnamed("mesh", "enabled", mesh)
        if dim == 2:
            self._modify_mesh(dx_mesh, dy_mesh, dz_mesh)
            if 'PML' in boundary_cds:
                self.fdtd.setnamed("FDE", "z", self.component.wg.height/2.)
                self.fdtd.setnamed("FDE", "z span", self.component.wg.height + wavl)
            elif 'Metal' in boundary_cds:
                self.fdtd.setnamed("FDE", "z", self.component.wg.height/2.)
                self.fdtd.setnamed("FDE", "z span", 3.5*(self.component.wg.height + wavl))
            self.fdtd.setnamed("mesh", "z", self.component.wg.height/2.)
            self.fdtd.setnamed("mesh", "z span", 1.05*self.component.wg.height)

    def _set_boundary_cds(self, symmetry, boundary_cds):
        if symmetry:
            self.fdtd.setnamed("FDE", "x min bc", "Anti-Symmetric")
        else:
            self.fdtd.setnamed("FDE", "x min bc", boundary_cds[0])
        self.fdtd.setnamed("FDE", "x max bc", boundary_cds[1])
        self.fdtd.setnamed("FDE", "y min bc", boundary_cds[2])
        self.fdtd.setnamed("FDE", "y max bc", boundary_cds[3])

    def setup_sim(self, dim, wavl, x_core=0, core_name="structure", symmetry=True,
        cap_thickness=0.5e-6, subs_thickness=3e-6, left=True, right=True, mesh=False,
        dx_mesh=10e-9, dy_mesh=10e-9, dz_mesh=10e-9, boundary_cds=['PML','PML','PML','PML']):
        self.fdtd.switchtolayout()
        self.component.produce_environment(wavl, x_core, core_name, 
            cap_thickness, subs_thickness, left, right)
        self._set_sim_region(wavl, dim, mesh, dx_mesh, dy_mesh, boundary_cds, dz_mesh)
        self._set_boundary_cds(symmetry, boundary_cds)

    def _add_dft_monitor(self, name, Type, x, y, z, xspan, yspan, zspan):
        self.fdtd.addpower()
        self.fdtd.set("name", name)
        self.fdtd.set("monitor type", Type)
        self.fdtd.set("x", x)
        self.fdtd.set("y", y)
        self.fdtd.set("z", z)
        self.fdtd.set("x span", xspan)
        self.fdtd.set("y span", yspan)
        self.fdtd.set("z span", zspan)



    ### Application
    def _close_application(self):
        print("Emergency close!")
        self.fdtd.close(True)