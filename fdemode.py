"""
Purpose:    FDFD eigenmode (FDE) mode-solver that collects relevant data from Lumerical(R) MODE(TM)
            FDE mode simulation instance simulating a ridge-waveguide.
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
import lumapi


import scipy.constants as sc
import numpy as np
pi = np.pi
c0 = sc.physical_constants["speed of light in vacuum"][0]
mu0 = sc.mu_0
eps0 = sc.epsilon_0
Z0 = 1/np.sqrt(eps0/mu0)

# environment = RidgeWaveguideEnvironment(wg, hideGUI)
class FDEModeSimulator:
    def __init__(self, environment):
        self.environment = environment
        self.mode = environment.mode
        self.wg = environment.wg
        self.mode.switchtolayout()
    @property
    def xaxis(self):
        return self.mode.getdata("FDE::data::material", "x")[:,0]
    @property
    def yaxis(self):
        return self.mode.getdata("FDE::data::material", "y")[:,0]
    @property
    def index(self):
        return self.mode.getdata("FDE::data::material", "index_y")[:,:,0,0]

    def _add_fde(self):
        self.mode.addfde()
    def _add_mesh(self, dx_mesh, dy_mesh):
        self.mode.addmesh()
        self.mode.set("override x mesh", 1)
        self.mode.set("dx", dx_mesh)
        self.mode.set("override y mesh", 1)
        self.mode.set("dy", dy_mesh)

    def _close_application(self):
        print("Emergency close!")
        self.mode.close(True)

    def _set_sim_region(self, wavl, mesh, dx_mesh, dy_mesh):
        print("Setting simulation region...")
        self._add_fde()
        self._add_mesh(dx_mesh, dy_mesh)
        self.mode.setnamed("FDE", "y min", -4.5*self.wg.height)
        self.mode.setnamed("FDE", "y max", 4.5*self.wg.height)
        self.mode.setnamed("FDE", "x", 0)
        self.mode.setnamed("FDE", "x span", 3*wavl)
        self.mode.setnamed("FDE", "mesh refinement", "conformal variant 0")
        self.mode.setnamed("mesh", "y min", -1.5*wavl)
        self.mode.setnamed("mesh", "y max", 1.5*wavl)
        self.mode.setnamed("mesh", "x", 0)
        self.mode.setnamed("mesh", "x span", 2*self.wg.width)
        self.mode.setnamed("mesh", "enabled", mesh)

    def _set_boundary_cds(self, symmetry, boundary_cds):
        print("Setting boundary conditions...")
        if symmetry:
            self.mode.setnamed("FDE", "x min bc", "Anti-Symmetric")
        else:
            self.mode.setnamed("FDE", "x min bc", boundary_cds[0])
        self.mode.setnamed("FDE", "x max bc", boundary_cds[1])
        self.mode.setnamed("FDE", "y min bc", boundary_cds[2])
        self.mode.setnamed("FDE", "y max bc", boundary_cds[3])

    def setup_sim(self, wavl, x_core=0, core_name="structure", symmetry=True,
        cap_thickness=0.5e-6, subs_thickness=3e-6, left=True, right=True, mesh=False,
        dx_mesh=10e-9, dy_mesh=10e-9, boundary_cds=['PML','PML','PML','PML']):
        self.mode.switchtolayout()
        self.environment.produce_environment(self.wg, wavl, x_core, core_name, 
            cap_thickness, subs_thickness, left, right)
        self._set_sim_region(wavl, mesh, dx_mesh, dy_mesh)
        self._set_boundary_cds(symmetry, boundary_cds)

    def _find_modes(self, wavl, trial_modes):
        print("Solving modes...")
        self.mode.switchtolayout()
        self.mode.setnamed("FDE", "wavelength", wavl)
        self.mode.setanalysis("number of trial modes", trial_modes)
        return self.mode.findmodes()

    def filtered_modes(self, pol_thres, pol):
        mode_ids = [s.split("::")[2] for s in self.mode.getresult().split('\n')
            if 'mode' in s]
        return [i for i in mode_ids
            if self.mode.getdata(i, pol+" polarization fraction") > pol_thres]

    # Depreciated 10/29/2020
    def select_mode(self, mode_id):
        self.mode.selectmode(mode_id)

    def package_data(self, mode_id):
        wavl = c0 / self.mode.getdata(mode_id, "f")
        E_field = [self.mode.getdata(mode_id, s)[:,:,0,0] 
            for s in ("Ex","Ey","Ez")]
        n_eff = [self.mode.getdata(mode_id, "neff")][0]
        H_field = [self.mode.getdata(mode_id, s)[:,:,0,0] 
            for s in ("Hx","Hy","Hz")]
        n_grp = [self.mode.getdata(mode_id, "ng")][0]
        return FDEModeSimData(self.xaxis, self.yaxis, self.index, wavl, E_field, H_field, n_grp, n_eff)

    def solve_mode(self, wavl, trial_modes=4, pol_thres=0.96, pol="TE", mode_ind=0):
        # Run simulation
        self._find_modes(wavl, trial_modes)
        mode_id = self.filtered_modes(pol_thres, pol)[mode_ind]
        self.select_mode(mode_id)
        # Package simulation data
        wavl = c0 / self.mode.getdata(mode_id, "f")
        E_field = [self.mode.getdata(mode_id, s)[:,:,0,0] 
            for s in ("Ex","Ey","Ez")]
        n_eff = [self.mode.getdata(mode_id, "neff")][0][0][0]
        H_field = [self.mode.getdata(mode_id, s)[:,:,0,0] 
            for s in ("Hx","Hy","Hz")]
        n_grp = [self.mode.getdata(mode_id, "ng")][0]
        return FDEModeSimData(self.xaxis, self.yaxis, self.index, wavl, E_field, H_field, n_grp, n_eff)


    ## This sweep function has been depreciated (29/06/2020). ##
    def run_lumer_sweep(self, wavl_start, wavl_span, N_sweep, trial_modes=4, pol_thres=0.96, pol="TE", mode_ind=0):
        # Find starting mode
        self._find_modes(wavl_start, trial_modes)
        self.select_mode(self.filtered_modes(pol_thres,pol)[mode_ind])
        # Run sweep
        self.mode.setanalysis("track selected mode", True)
        self.mode.setanalysis("stop wavelength", wavl_start + wavl_span)
        self.mode.setanalysis("number of points", N_sweep)
        self.mode.setanalysis("number of test modes", 3) # Recommended
        self.mode.setanalysis("detailed dispersion calculation", True)
        self.mode.setanalysis("store mode profiles while tracking", True)
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
        return FDEModeSimData(self.xaxis, self.yaxis, self.index, wavls, E_fields, H_fields, c0/vgs, n_effs)

    def run_sweep(self, wavl_center, wavl_span, N_sweep, trial_modes=4, pol_thres=0.96, pol="TE", mode_ind=0):
        # Package simulation data
        wavls = []
        E_fields = []
        H_fields = []
        n_effs = []
        n_grps = []
        # Perform sweep
        wavl_start = wavl_center - wavl_span/2
        wavl_stop = wavl_center + wavl_span/2
        for wavl_i in np.linspace(wavl_start, wavl_stop, N_sweep):
            self._find_modes(wavl_i, trial_modes)
            mode_id = self.filtered_modes(pol_thres, pol)[mode_ind]
            self.select_mode(mode_id)
            E_field = [self.mode.getdata(mode_id, s)[:,:,0,0] 
                for s in ("Ex","Ey","Ez")]
            n_eff = [self.mode.getdata(mode_id, "neff")][0]
            H_field = [(Z0/n_eff)*self.mode.getdata(mode_id, s)[:,:,0,0] 
                for s in ("Hx","Hy","Hz")]  # converting Lumerical to our normalization
            n_grp = [self.mode.getdata(mode_id, "ng")][0]
            E_fields.append(E_field)
            H_fields.append(H_field)
            n_effs.append(n_eff)
            n_grps.append(n_grp)
            wavls.append(wavl_i)
        return FDEModeSimData(self.xaxis, self.yaxis, self.index, wavls, np.array(E_fields), 
            np.array(H_fields), np.array(n_grps), np.array(n_effs))


class FDEModeSimData:
    def __init__(self, xaxis, yaxis, index, wavel, E_field, H_field, n_grp, n_eff):
        self.xaxis = xaxis
        self.yaxis = yaxis
        self.wavl = wavel
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
    
    @staticmethod
    def _compute_Aeff(E, H, dA):
        S = np.real(E[0]*np.conj(H[1]) - E[1]*np.conj(H[0]))
        return (S*dA).sum()
    
    def compute_Aeff(self):
        if isinstance(self.wavl,(list,np.ndarray)):
            return [self._compute_Aeff(E,H, self.dxdy)
                for E,H in zip(self.E_field,self.H_field)]
        return self._compute_Aeff(self.E_field,self.H_field,self.dxdy)

    def clip_fields(self, x, y):
        mask_x = (x[0] < self.xaxis) & (self.xaxis < x[-1])
        mask_y = (y[0] < self.yaxis) & (self.yaxis < y[-1])
        if isinstance(self.wavl,(list,np.ndarray)):
            E_field = [[Ek[mask_x,:][:,mask_y] for Ek in E] for E in self.E_field]
            H_field = [[Hk[mask_x,:][:,mask_y] for Hk in H] for H in self.H_field]
        else:
            E_field = [Ek[mask_x,:][:,mask_y] for Ek in self.E_field]
            H_field = [Hk[mask_x,:][:,mask_y] for Hk in self.H_field]
        return FDEModeSimData(self.xaxis[mask_x], self.yaxis[mask_y],
            self.index, self.wavl, E_field, H_field, self.n_grps, self.n_effs)
