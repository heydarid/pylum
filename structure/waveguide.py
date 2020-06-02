"""
Purpose:     General purpose waveguide constructor for use in
                any Lumerical simulation.
Copyright:   (c) May 2020 David Heydari, Edwin Ng
"""
class Waveguide:
    def __init__(self, width, height, etch):
        self.width = width*1e-6
        self.height = height*1e-6
        self.etch = etch*1e-6