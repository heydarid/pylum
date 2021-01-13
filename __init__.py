"""
__init__.py for highest level in lumpy hierarchy.
Adapted from code from Gavin West and Dodd Gray (2019)

Copyright:   (c) May 2020 David Heydari
"""

# TODO: adapt for updated versions of Lumerical (not just 2019)

import sys, os
from os import path
from glob import glob
import platform

platform_os = platform.system()
if platform_os == 'Windows':
	if path.isdir(path.normpath( 'C:/Program Files/Lumerical')):
		dir_list=[path.normpath(x) for x in glob('c:/Program Files/Lumerical'+'/*')]
		latest_lum_dir = min( dir_list )  # The other dir, FlexLM, has a longer string name
		sys.path.append( path.normpath( latest_lum_dir + '\\api\\python\\' ) )
		import lumapi
	else:
		raise Exception( 'ERROR: Cannot find Windows Lumerical API directory.' )
elif platform_os == 'Linux':
	if path.isdir('/opt/lumerical/2019b'):
		sys.path.append('/opt/lumerical/2019b/api/python/')
		import lumapi
	elif path.isdir('/opt/lumerical/mode/api'):
		sys.path.append('/opt/lumerical/mode/api/python/')
		import lumapi
	else:
		raise Exception('ERROR: Cannot find Linux Lumerical API directory.' )