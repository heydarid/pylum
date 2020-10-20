"""
Purpose:    General purpose waveguide constructor.
            All units SI unless otherwise specified.
Copyright:   (c) May 2020 David Heydari, Edwin Ng
"""
class Waveguide:
    def __init__(self, width, height, etch):
        self.width = width
        self.height = height
        self.etch = etch