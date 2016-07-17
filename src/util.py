#!/usr/bin/env python

####################

import gzip
import io
import random
import re
import string
import time
try:
	import socks
	NO_SOCKS = False
except ImportError:
	NO_SOCKS = True
import socket
###################

try:
	import urllib2
except ImportError:
	import urllib.request as urllib2

####################

UA = """Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36"""
# overwrite user agent for spoofing, enable GZIP
urlReqHeaders = {'User-agent': UA, 'Accept-encoding': 'gzip'}

####################

# something seriously wrong happened
class FatalError(Exception):
	pass

def fixFormatting(s, spaceToken):
	"""
	Special character fix for filesystem paths.
	"""
	s = s.decode('utf-8').encode('ascii', 'ignore')
	for i in string.punctuation:
		if(i != '-' and i != spaceToken):
			s = s.replace(i, '')
	return s.lower().lstrip(spaceToken).strip().replace(' ', spaceToken)

def getSourceCode(url, proxy, returnRedirctUrl = False, maxRetries=1, waitRetryTime=1):
	"""
	Loop to get around server denies for info or minor disconnects.
	"""
	if (proxy is not None):
		if (NO_SOCKS):
			raise FatalError('socks library required to use proxy (e.g. SocksiPy)')
		proxySettings = proxy.split(':')
		socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS4, proxySettings[0], int(proxySettings[1]), True)
		socket.socket = socks.socksocket
				
	global urlReqHeaders
	
	ret = None
	request = urllib2.Request(url, headers=urlReqHeaders) 
	
	while (ret == None): 
		try:
			f = urllib2.urlopen(request)
			encoding = f.headers.get('Content-Encoding')
					
			if encoding == None:
				ret = f.read()
			else:
				if encoding.upper() == 'GZIP': 
					compressedstream = io.BytesIO(f.read()) 
					gzipper = gzip.GzipFile(fileobj=compressedstream)
					ret = gzipper.read()
				else:
					raise FatalError('Unknown HTTP Encoding returned')
		except urllib2.URLError:
			if (maxRetries == 0):
				break
			else:
				# random dist. for further protection against anti-leech
				# idea from wget
				time.sleep(random.uniform(0.5*waitRetryTime, 1.5*waitRetryTime))
				maxRetries -= 1

	if returnRedirctUrl:
		return ret, f.geturl()
	else:
		return ret

def isImageLibAvailable():
	try:
		from ConvertPackage.ConvertFile import convertFile
		return True
	except ImportError:
		return False

def zeroFillStr(inputString, numOfZeros):
	return re.sub(	'\d+', 
					lambda matchObj:
						# string formatting trick to zero-pad 
						('%0' + str(numOfZeros) + 'i') % int(matchObj.group(0)), 
					inputString	)

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

def updateNode(dom, node, tagName, text):
	text = text.decode('utf-8')
	if (len(node.getElementsByTagName(tagName)) > 0):
		updateNode = node.getElementsByTagName(tagName)[0]
	else:
		# Node Currently Does have a timeStamp Node Must add one
		updateNode = dom.createElement(tagName)
		node.appendChild(updateNode)
		
	setText(dom, updateNode, text) 	
	
