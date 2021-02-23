"""
Purpose:    General purpose waveguide constructor.
            All units SI unless otherwise specified.
Copyright:   (c) May 2020 David Heydari, Edwin Ng
"""
class Waveguide:
    def __init__(self, width, height, etch1, 
                etch2=None, width2=None):
        self.width = width
        self.height = height
        self.width2 = width2
        if width2 !=None:
            self.width1 = width
            self.width = width + width2
        self.etch = etch1
        self.etch2 = etch2