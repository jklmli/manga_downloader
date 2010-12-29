#!/usr/bin/env python

####################

import string
import urllib

####################

# something seriously wrong happened
class FatalError(Exception):
	pass

def isImageLibAvailable():
	try:
		from ConvertFile import convertFile
	except ImportError:
		return False
	else:
		return True

def fixFormatting(s):
	"""
	Special character fix for filesystem paths.
	"""
	
	for i in string.punctuation:
		if(i != '-' and i != '.'):
			s = s.replace(i, '')
	return s.lower().lstrip('.').strip().replace(' ', '_')

def getSourceCode(url):
	"""
	While loop to get around server denies for info or minor disconnects.
	"""
	
	while True:
		try:
			ret = urllib.urlopen(url).read()
		except IOError:
			pass
		else:
			break
	return ret
