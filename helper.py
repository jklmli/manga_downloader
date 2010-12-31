#!/usr/bin/env python

####################

import string
import urllib
import re
from xml.dom import minidom
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

#=========================
#
# XML Helper Functions
#
#=========================

def getText(node):
	rc = []
	for node in node.childNodes:
		if node.nodeType == node.TEXT_NODE:
			rc.append(node.data)		
			
		return ''.join(rc)
#		return ''.join([node.data for node in nodelist if node.nodeType == node.TEXT_NODE])			

def setText(dom, node, text):
		
	for currNode in node.childNodes:
		if currNode.nodeType == currNode.TEXT_NODE:
			currNode.data = text
			return

	# If this code is executed, it means that the loop failed to find a text node
	# A new text needs to be created and appended to this node
	textNode = dom.createTextNode(text) 	
	node.appendChild(textNode)

def UpdateNode(dom, node, tagName, text):
	if (len(node.getElementsByTagName(tagName)) > 0):
		updateNode = node.getElementsByTagName(tagName)[0]
	else:
		# Node Currently Does have a timeStamp Node Must add one
		updateNode = dom.createElement(tagName)
		node.appendChild(updateNode)
		
	setText(dom, updateNode, text) 	
	