"""
Purpose:    Generates the index of refraction data for Silicon
            from the Sellmeier equation with parameters, from the 
            NASA paper "Temperature-dependent refractive index of
            silicon and germanium" (Frey, 2006)
Copyright:   (c) June 2020 David Heydari
"""

import numpy as np

def n_Si(wavl, T):  # T in Kelvin
    wavl_um = wavl*1e6
    T_pow = np.arange(0,5)
    S1 = [10.4907, -2.0802e-4, 4.21694e-6, -5.82298e-9, 3.44688e-12]
    S2 = [-1346.61, 29.1664, -0.278724, 1.05939e-3, -1.35089e-6]
    S3 = [4.42827e7, -1.76213e6, -7.61575e4, 678.414, 103.243]

    S_ij = np.array([S1, S2, S3], dtype=np.float64)
    l1 = [0.299713, -1.14234e-5, 1.67134e-7, -2.51049e-10, 2.32484e-14]
    l2 = [-3.51710e3, 42.3892, -0.357957, 1.17504e-3, -1.13212e-6]
    l3 = [1.714e6, -1.4498e5, -6.90744e3, -39.3699, 23.577]

    l_ij = np.array([l1, l2, l3], dtype=np.float64)
    S = np.array([[0, 0, 0]], dtype=np.float64).T
    l = np.array([[0, 0, 0]], dtype=np.float64).T

    for ind_res in np.arange(0,3):
        for ind_T in np.arange(0,5):
            S[ind_res] = S[ind_res] + S_ij[ind_res,ind_T] * T ** T_pow[ind_T]
            l[ind_res] = l[ind_res] + l_ij[ind_res,ind_T] * T ** T_pow[ind_T]
    n_2_minus_1 = sum(S * wavl_um**2 / ( np.ones((3,1)) * wavl_um**2 - l**2 * np.ones((1,np.size(wavl_um))) ), 0)
    n = np.sqrt(n_2_minus_1 + 1)
    return n