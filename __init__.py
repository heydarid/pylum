"""
__init__.py for highest level in lumpy hierarchy.
Adapted from code from Gavin West and Dodd Gray (2019)

Copyright:   (c) May 2020 David Heydari
"""

import sys, re, h5py, pickle, os
from os import path
from glob import glob

import scipy.constants as sc
import numpy as np
import scipy as sp
# import pint

from collections import OrderedDict
import matplotlib.pyplot as plt
from time import sleep
from pathlib import Path
import itertools as it
from copy import deepcopy
import platform
from inspect import isclass

################################################################################
################################################################################
##              Find and import Lumerical Python api library                  ##
##                  based on current system platform used                     ##
################################################################################
################################################################################
platform_os = platform.system()
if platform_os == 'Windows':
	if path.isdir(path.normpath( 'C:/Program Files/Lumerical')):
		dir_list=[path.normpath(x) for x in glob('c:/Program Files/Lumerical'+'/*')]
		latest_lum_dir = min( dir_list )  # The other dir, FlexLM, has a longer string name
		sys.path.append( path.normpath( latest_lum_dir + '\\api\\python\\' ) )
	else:
		raise Exception( 'ERROR: Cannot find Windows Lumerical API directory.' )
elif platform_os == 'Linux':
	if path.isdir('/opt/lumerical/2019b'):
		sys.path.append('/opt/lumerical/2019b/api/python/')
	elif path.isdir('/opt/lumerical/mode/api'):
		sys.path.append('/opt/lumerical/mode/api/python/')
	else:
		raise Exception('ERROR: Cannot find Linux Lumerical API directory.' )

import lumapi