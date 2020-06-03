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
Copyright:   (c) May 2020 David Heydari
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
    def __init__(self, wg, wavl_0, wavl_bw, is_TE=True, trial_modes=4, N_sweep=10, hideGUI=True):        
        self.mode = lumapi.MODE(fileDir + '/template/waveguide_get_modes.lms', hide=hideGUI)
        self.wg = wg
        self.wavl_0 = wavl_0*1e-6
        self.wavl_bw = wavl_bw*1e-6
        self.is_TE = is_TE
        self.trial_modes = trial_modes
        self.te_threshold = 0.96
        self.mode.switchtolayout()
        self.mode.setactivesolver("FDE")
        self.N_sweep = N_sweep
        
    def set_sim_region(self, wavl):
        self.mode.switchtolayout()
        self.mode.setnamed("FDE", "y min", -1.0e-6)
        self.mode.setnamed("FDE", "y max", self.wg.height + 1.0e-6)
        self.mode.setnamed("FDE", "x", 0)
        self.mode.setnamed("FDE", "x span", self.wg.width + 2*1.5*wavl)
        self.mode.setnamed("mesh", "x", 0)
        self.mode.setnamed("mesh", "x span", self.wg.width + 2*1.5*wavl)  
            # PMLs general rule of thumb, ~1.5λ from edges of the waveguide core.

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

    def solve_modes(self, wavl, trial_modes=4):
        self.set_geometry()
        self.set_sim_region(wavl)
        self.set_boundary_cds()
        self.mode.run()
        self.mode.switchtolayout()
        self.mode.set("wavelength", wavl)
        self.mode.setanalysis("number of trial modes", trial_modes)
        self.mode.findmodes()
        data = self.select_mode()
        return data

    def select_mode(self, is_TE=True, te_threshold=0.96):
        mode_list = [str for str in self.mode.getresult().split('\n') if 'mode' in str]
        pol_TE = dict([(j,self.mode.getdata(j, "TE polarization fraction")) for j in 
                        [i.split('::')[2] for i in mode_list]])
        if is_TE:
            filtered_TE_pol = {key:te for key, te in pol_TE.items() if te > te_threshold}
            self.mode.selectmode(list(filtered_TE_pol.keys())[0])
        else:
            filtered_TE_pol = {key:te for key, te in pol_TE.items() if te < 1 - te_threshold}
            self.mode.selectmode(list(filtered_TE_pol.keys())[0])
        return filtered_TE_pol

    def sweep(self, wavl, wavl_bw, trial_modes, N_sweep):
        self.mode.switchtolayout()
        wavl_start = wavl
        wavl_end   = wavl + wavl_bw
        self.mode.set("wavelength", wavl_start)
        self.solve_modes(wavl, trial_modes)
        self.mode.setanalysis("track selected mode", 1)
        self.mode.setanalysis("stop wavelength", wavl_end)
        self.mode.setanalysis("number of points", N_sweep)
        self.mode.setanalysis("number of test modes", 3)  # recommended by Lumerical
        self.mode.setanalysis("detailed dispersion calculation", 1)
        self.mode.setanalysis("store mode profiles while tracking", 1)
        self.mode.frequencysweep()
        E_temp = [self.mode.getdata("FDE::data::frequencysweep", s) for s in ("Ex","Ey","Ez")]
        H_temp = [self.mode.getdata("FDE::data::frequencysweep", s) for s in ("Hx","Hy","Hz")]
        lambdas = c0 / self.mode.getdata("FDE::data::frequencysweep", "f")
        n_effs = np.real(self.mode.getdata("FDE::data::frequencysweep", "neff"))
        n_grps = c0 / np.real(self.mode.getdata("FDE::data::frequencysweep", "vg"))
        return n_effs, n_grps, lambdas, E_temp, H_temp


    def return_wg_data(self):
        if self.wavl_bw != 0:
            sim = self.return_wg_sweep_data()
            dxdy = self.get_dxdy(sim)
            sim.store_dxdy(dxdy)
            A_eff = self.compute_Aeff(sim)
            sim.store_A_eff(A_eff)
        else:
            filtered_modes = self.solve_modes()
            keys = [j for j in filtered_modes.keys()]
            lambda_0 = c0 / self.mode.getdata("FDE::data::"+keys[0], "f")
            E_field = [self.mode.getdata("FDE::data::"+keys[0], s)[:,:,0,0] for s in ("Ex","Ey","Ez")]
            H_field = [self.mode.getdata("FDE::data::"+keys[0], s)[:,:,0,0] for s in ("Hx","Hy","Hz")]
            n_grp = [self.mode.getdata("FDE::data::"+keys[0], "neff")][0]
            n_eff = [self.mode.getdata("FDE::data::"+keys[0], "ng")][0]
            xaxis = self.mode.getdata("FDE::data::material", "x")[:,0] 
            yaxis = self.mode.getdata("FDE::data::material", "y")[:,0] 
            index = self.mode.getdata("FDE::data::material", "index_y")[:,:,0,0]
            sim = SimulationData(self.wg,xaxis,yaxis,index,lambda_0,E_field,H_field,n_grp,n_eff)
            dxdy = self.get_dxdy(sim)
            sim.store_dxdy(dxdy)
            A_eff = self.compute_Aeff(sim)
            sim.store_A_eff(A_eff)
        return sim

    def return_wg_sweep_data(self):
        n_effs, n_grps, lambdas, E_temp, H_temp = self.sweep()
        xaxis = self.mode.getdata("FDE::data::material", "x")[:,0] 
        yaxis = self.mode.getdata("FDE::data::material", "y")[:,0] 
        index = self.mode.getdata("FDE::data::material", "index_y")[:,:,0,0]
        E_sweep = [[E[:,:,0,ind,0] for E in E_temp] for ind in range(self.N_sweep)]
        H_sweep = [[H[:,:,0,ind,0] for H in H_temp] for ind in range(self.N_sweep)]
        
        sim_s = SimulationData(self.wg,xaxis,yaxis,index,lambdas,E_sweep,H_sweep,n_grps,n_effs)
        return sim_s

class SimulationData:
    def __init__(self, wg, xaxis, yaxis, index, lambdas, E_fields, H_fields, n_grps, n_effs):
        self.waveguide = wg
        self.lambdas = lambdas
        self.xaxis = xaxis
        self.yaxis = yaxis
        self.index = index
        self.E_fields = E_fields  # Ordering: [lambdas, (x,y,z)-comp, field matrix]
        self.H_fields = H_fields
        self.n_grps = n_grps
        self.n_effs = n_effs
    def get_dxdy(self):
        xax = np.diff(self.xaxis).reshape(len(np.diff(self.xaxis)),1)
        yax = np.diff(self.yaxis).reshape(len(np.diff(self.yaxis)),1)
        coordmat = xax*np.transpose(yax)
        realcoordmat = np.zeros(np.shape(self.E_fields))
        realcoordmat[:,:,:coordmat.shape[0],:coordmat.shape[1]] = coordmat
        return realcoordmat
    def compute_Aeff(self, sim_data):
        dA = self.get_dxdy(sim_data)
        e = [sim_data.E_fields[i] for i in range(np.shape(sim_data.lambdas)[0])]
        h = [sim_data.H_fields[i] for i in range(np.shape(sim_data.lambdas)[0])]
        Sxy = [(1/2)*np.real(E[0]*np.conj(H[1]) - E[1]*np.conj(H[0])) for E in e for H in h]
        A_eff = np.array([(Sxy[i]*dA[i][0]).sum() for i in range(np.shape(sim_data.lambdas)[0])])
        return np.expand_dims(A_eff, axis=1)
    def store_dxdy(self, dxdy):
        self.dxdy = dxdy
    def store_A_eff(self,A_eff):
        self.A_eff = A_eff