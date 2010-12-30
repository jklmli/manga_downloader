#!/usr/bin/env python

####################

import string
import urllib
import re
####################

# something seriously wrong happened
class FatalError(Exception):
	pass

def ZeroFillStr(inputString, numOfZeros):
	startIndex = []
	endIndex = []
	
	outputString = inputString
	
	for m in re.finditer('\d+', outputString):
		startIndex.append(m.start())
		endIndex.append(m.end())
	
	# Starting from the end converts the found substrings to their zero filled counterparts
	# 
	# Converting from the end of the string will not move the locations of
	# any of the prior substrings (Thoses in the string before the one 
	# currently being converted. 
	while ((len(startIndex) > 0) and (len(endIndex))):
		startIdx = startIndex.pop()
		endIdx = endIndex.pop()
		outputString = outputString[:startIdx] + outputString[startIdx:endIdx].zfill(numOfZeros) + outputString[endIdx:]	
	
	return outputString	

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
