"""
Purpose:    Fits a Gaussian to a given FDFD mode set (FDEModeSimData).  
            Useful for fiber mode matching calculations.  
Copyright:  (c) Jan 2021 David Heydari
"""

from scipy.optimize import curve_fit
import numpy as np
π = np.pi

def w(z, w0, λ0):
    zR = np.pi * w0**2 / λ0
    return w0 * np.sqrt(1 + (z/zR)**2)

def gaussbeam(λ0, x, x0, w0, d_farfield=0.):
    p = [x0, w0]
    return (p[1]/w(d_farfield, p[1], λ0))*np.exp(-2 * ((x-p[0])/p[1])**2)

# p0 = [0., 3.]  # units: [μm]
# fit, tmp = curve_fit(gaussbeam, fde_sim_data_i.xaxis*1e6,
#                      np.real(fde_sim_data_i.E_field[0].T[cut_inds[1]]), p0=p0)