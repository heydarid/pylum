"""
Purpose:     FDFD eigenmode (FDE) mode-solver that collects relevant data from Lumerical MODE
                FDE mode simulation instance simulating a pre-defined structure.
Structure:   Ridge-waveguide composed of air-Si-SiO2-Si(substrate)
             Simulation region is cross-section of waveguide in xy, at some z-slice
             Pre-selects the TE mode (highly Ex) for our nonlinear optics project preferences.

            Units are SI unless otherwise noted.
Useful links:
https://support.lumerical.com/hc/en-us/articles/360034917233-MODE-Finite-Difference-Eigenmode-FDE-solver-introduction
https://support.lumerical.com/hc/en-us/articles/360034382674-PML-boundary-conditions-in-FDTD-and-MODE#toc_2
https://support.lumerical.com/hc/en-us/articles/360034382694-Symmetric-and-anti-symmetric-BCs-in-FDTD-and-MODE
Copyright:   (c) May 2020 David Heydari, Edwin Ng
"""
import sys, os
fileDir = os.path.dirname(os.path.abspath(__file__))
parentDir = os.path.dirname(fileDir)
print(fileDir)
import lumapi

import scipy.constants as sc
import numpy as np
pi = np.pi
c0 = sc.physical_constants["speed of light in vacuum"][0]
mu0 = sc.mu_0
eps0 = sc.epsilon_0
Z0 = 1/np.sqrt(eps0/mu0)

class ModeSimulator:
    def __init__(self, wg, hideGUI=True):
        self.mode = lumapi.MODE(fileDir + '/template/waveguide_get_modes.lms',
            hide=hideGUI)
        self.wg = wg
        self.mode.switchtolayout()
        self.mode.setactivesolver("FDE")
    
    @property
    def xaxis(self):
        return self.mode.getdata("FDE::data::material", "x")[:,0]
    @property
    def yaxis(self):
        return self.mode.getdata("FDE::data::material", "y")[:,0]
    @property
    def index(self):
        return self.mode.getdata("FDE::data::material", "index_y")[:,:,0,0]
    
    def set_sim_region(self, wavl):
        # PMLs general rule of thumb, ~1.5λ from edges of the waveguide core
        self.mode.switchtolayout()
        self.mode.setnamed("FDE", "y min", -1e-6)
        self.mode.setnamed("FDE", "y max", self.wg.height + 1e-6)
        self.mode.setnamed("FDE", "x", 0)
        self.mode.setnamed("FDE", "x span", self.wg.width + 2*1.5*wavl)
        self.mode.setnamed("mesh", "x", 0)
        self.mode.setnamed("mesh", "x span", self.wg.width + 2*1.5*wavl)

    def set_boundary_cds(self):
        self.mode.setnamed("FDE", "x min bc", "Anti-Symmetric")
        self.mode.setnamed("FDE", "x max bc", "PML")
        self.mode.setnamed("FDE", "y min bc", "Metal")
        self.mode.setnamed("FDE", "y max bc", "Metal")

    def set_geometry(self):
        self.mode.switchtolayout()
        self.mode.setnamed("structure::guide", "x", 0)
        self.mode.setnamed("structure::pedestal", "x", 0)
        self.mode.setnamed("structure::guide", "x span", self.wg.width)
        self.mode.setnamed("structure::guide", "y min", 0)
        self.mode.setnamed("structure::guide", "y max", self.wg.height)
        self.mode.setnamed("structure::pedestal", "y min", 0)
        self.mode.setnamed("structure::pedestal", "y max", self.wg.height - self.wg.etch)

    def _find_modes(self, wavl, trial_modes):
        self.set_geometry()
        self.set_sim_region(wavl)
        self.set_boundary_cds()
        self.mode.run()
        self.mode.switchtolayout()
        self.mode.set("wavelength", wavl)
        self.mode.setanalysis("number of trial modes", trial_modes)
        self.mode.findmodes()

    def filtered_modes(self, pol_thres, pol):
        mode_ids = [s.split("::")[2] for s in self.mode.getresult().split('\n')
            if 'mode' in s] # Is there a better way?
        return [i for i in mode_ids
            if self.mode.getdata(i, pol+" polarization fraction") > pol_thres]

    def select_mode(self, mode_id):
        self.mode.selectmode(mode_id)

    def solve_mode(self, wavl, trial_modes=4, pol_thres=0.96, pol="TE", mode_ind=0):
        # Run simulation
        self._find_modes(wavl, trial_modes)
        mode_ids = self.filtered_modes(pol_thres, pol)
        self.select_mode(mode_ids[mode_ind]) # Can this take FDE::data::mode1?
        mode_id = "FDE::data::"+mode_ids[0]
        # Package simulation data
        wavl = c0 / self.mode.getdata(mode_id, "f")
        E_field = np.expand_dims([self.mode.getdata(mode_id, s)[:,:,0,0] 
            for s in ("Ex","Ey","Ez")], axis=0)
        H_field = np.expand_dims([self.mode.getdata(mode_id, s)[:,:,0,0] 
            for s in ("Hx","Hy","Hz")], axis=0)
        n_grp = [self.mode.getdata(mode_id, "ng")][0]
        n_eff = [self.mode.getdata(mode_id, "neff")][0]
        return SimulationData(self.wg, self.xaxis, self.yaxis, self.index,
            wavl, E_field, H_field, n_grp, n_eff)

    def run_sweep(self, wavl_start, wavl_span, N_sweep, trial_modes=4, pol_thres=0.96, pol="TE", mode_ind=0):
        # Find starting mode
        self._find_modes(wavl_start, trial_modes)
        self.select_mode(self.filtered_modes(pol_thres,pol)[mode_ind])
        # Run sweep
        self.mode.setanalysis("track selected mode", 1) # Can this use True?
        self.mode.setanalysis("stop wavelength", wavl_start + wavl_span)
        self.mode.setanalysis("number of points", N_sweep)
        self.mode.setanalysis("number of test modes", 3) # Recommended
        self.mode.setanalysis("detailed dispersion calculation", 1)
        self.mode.setanalysis("store mode profiles while tracking", 1)
        self.mode.frequencysweep()
        # Package sweep data
        wavls = c0 / self.mode.getdata("FDE::data::frequencysweep", "f")
        E_temp = [self.mode.getdata("FDE::data::frequencysweep", s)
            for s in ("Ex","Ey","Ez")]
        H_temp = [self.mode.getdata("FDE::data::frequencysweep", s)
            for s in ("Hx","Hy","Hz")]
        E_fields = [[E[:,:,0,ind,0] for E in E_temp] for ind in range(N_sweep)]
        H_fields = [[H[:,:,0,ind,0] for H in H_temp] for ind in range(N_sweep)]
        vgs = np.real(self.mode.getdata("FDE::data::frequencysweep", "vg"))
        n_effs = np.real(self.mode.getdata("FDE::data::frequencysweep", "neff"))
        return SimulationData(self.wg, self.xaxis, self.yaxis, self.index,
            wavls, E_fields, H_fields, c0/vgs, n_effs)

class SimulationData:
    def __init__(self, wg, xaxis, yaxis, index, wavel, E_field, H_field, n_grp, n_eff):
        self.waveguide = wg
        self.wavelength = wavel
        self.xaxis = xaxis
        self.yaxis = yaxis
        self.index = index
        self.E_field = E_field
        self.H_field = H_field
        self.n_grps = n_grp
        self.n_effs = n_eff

    @property
    def dxdy(self):
        xax = np.expand_dims(np.diff(self.xaxis, prepend=0),axis=1)
        yax = np.expand_dims(np.diff(self.yaxis, prepend=0),axis=1)
        return xax*np.transpose(yax)

    def compute_Aeff(self):
        dA = self.dxdy
        wavl_size = np.shape(np.array(self.wavelength).reshape(np.size(self.wavelength),1))[0]
        e = [self.E_field[i] for i in range(wavl_size)]
        h = [self.H_field[i] for i in range(wavl_size)]
        Sxy = [(1/2)*np.real(E[0]*np.conj(H[1]) - E[1]*np.conj(H[0]))
            for E in e for H in h]
        A_eff = [(Sxy[i]*dA).sum() for i in range(wavl_size)]
        return np.expand_dims(A_eff, axis=1)