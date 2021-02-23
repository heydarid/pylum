"""
Purpose:        Different models for the index of refraction 
                of MgO-doped LN.
Based off:      Code from Marc Jankowski
Copyright:      (c) Jan 2021 David Heydari
"""

import numpy as np

"""
        O. Gayer (2008): Only valid from T = 20-200°C, λ0 = 0.5~4µm.
"""
def sellmeier_Jundt(wavl, T, f, a, b):
        n = np.sqrt(a[0] + b[0]*f 
                + (a[1] + b[1]*f)/(wavl**2 - (a[2] + b[2]*f)**2)
                + (a[3] + b[3]*f)/(wavl**2 - a[4]**2)
                - a[5]*wavl**2)
        return n**2

def gayer2008_e(wavl, T):  # T in Kelvin
        f = (T-273.15 - 24.5)*(T-273.15 + 570.82)
        a = [5.756, 0.0983, 0.2020, 189.32, 12.52, 1.32e-2]
        b = [2.86e-6, 4.7e-8, 6.113e-8, 1.516e-4]
        return sellmeier_Jundt(wavl*1e6, T, f, a, b)

def gayer2008_o(wavl, T):  # T in Kelvin
        f = (T-273.15 - 24.5)*(T-273.15 + 570.82)
        a = [5.653, 0.1185, 0.2091, 89.61, 10.85, 1.97e-2]
        b = [7.941e-7, 3.134e-8, -4.641e-9, -2.188e-6]
        return sellmeier_Jundt(wavl*1e6, T, f, a, b)
