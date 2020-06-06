"""
Purpose:    Creates custom materials into the Lumerical material database
            from data ported from RefractiveIndex.info database.
Structure:  Ridge-waveguide composed of cladding, core, substrate
            Simulation region is cross-section of waveguide in xy, at some z-slice
Copyright:   (c) June 2020 David Heydari
"""

# TODO: include RII db

# Common Lumerical materials
silicon = 'Si (Silicon) - Palik'
silica = 'SiO2 (Glass) - Palik'