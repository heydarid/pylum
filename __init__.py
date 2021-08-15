"""
__init__.py for highest level in pylum hierarchy.

Copyright:   (c) May 2020 David Heydari
"""

# TODO: Linux: adapt for updated versions of Lumerical (not just 2019)

import sys, os
from os import path
from glob import glob
import platform

platform_os = platform.system()
if platform_os == 'Windows':
	if path.isdir(path.normpath( 'C:/Program Files/Lumerical')):
		dirc = min([path.normpath(x) for x in glob('c:/Program Files/Lumerical'+'/*')])
		sys.path.append( path.normpath( dirc + '\\api\\python\\' ) )
	else:
		raise Exception( 'ERROR: Cannot find Windows Lumerical API directory!' )
elif platform_os == 'Linux':
	if path.isdir('/opt/lumerical/v212'):
		sys.path.append('/opt/lumerical/v212/api/python/')
	elif path.isdir('/opt/lumerical/mode/api'):
		sys.path.append('/opt/lumerical/mode/api/python/')
	else:
		raise Exception('ERROR: Cannot find Linux Lumerical API directory!' )
import lumapi