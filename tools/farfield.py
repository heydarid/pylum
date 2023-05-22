"""
Purpose:    Computes far field of a given FDFD data set by way of Fraunhofer (Fourier)      
            transform.  Formalism is described in notes.
            Can also increase the resolution of the FFT 
            by zero-padding the data.
Copyright:   (c) Jan 2021 David Heydari
"""

import numpy as np
from numpy.fft import fft, fft2, fftshift, fftfreq
π = np.pi

def farfield(fde_sim_data_i, d_farfield, pad_number=3000):
    λ0 = fde_sim_data_i.wavl
    k = 2*np.pi/λ0
    new_E = np.pad(fde_sim_data_i.E_field[0], pad_number, mode="constant")
    dx = np.diff(fde_sim_data_i.xaxis).min()
    dy = np.diff(fde_sim_data_i.yaxis).min()
    X, Y = fftfreq(new_E.shape[0], dx)*(λ0*d_farfield), fftfreq(new_E.shape[1], dy)*(λ0*d_farfield)
    XXpf, YYpf =  np.meshgrid(X,Y)
    prefactor = 1J * np.exp(-1J*k*d_farfield) * np.exp( -1J*π* (XXpf**2+YYpf**2) / (λ0*d_farfield) )
    farfield = dx * dy / (λ0 * d_farfield) * abs(prefactor * fftshift(fft2(new_E.T)))
    return fftshift(XXpf), fftshift(YYpf), farfield