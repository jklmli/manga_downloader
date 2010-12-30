#!/usr/bin/env python

######################
import os
import datetime

from xml.dom import minidom
from SiteParser import SiteParserFactory
from helper import *

######################

class MangaXmlParser:
	def __init__(self, optDict):
		self.options = optDict
		for elem in vars(optDict):
			setattr(self, elem, getattr(optDict, elem))
	
	@staticmethod
	def getText(node):
		rc = []
		for node in node.childNodes:
			if node.nodeType == node.TEXT_NODE:
				rc.append(node.data)		
		
		return ''.join(rc)
#		return ''.join([node.data for node in nodelist if node.nodeType == node.TEXT_NODE])

	@staticmethod
	def setText(dom, node, text):
		
		for currNode in node.childNodes:
			if currNode.nodeType == currNode.TEXT_NODE:
				currNode.data = text
				return

		# If this code is executed, it means that the loop failed to find a text node
		# A new text needs to be created and appended to this node
		textNode = dom.createTextNode(text) 	
		node.appendChild(textNode)
	
	@staticmethod
	def UpdateNode(dom, node, tagName, text):
		if (len(node.getElementsByTagName(tagName)) > 0):
			updateNode = node.getElementsByTagName(tagName)[0]
		else:
			# Node Currently Does have a timeStamp Node Must add one
			updateNode = dom.createElement(tagName)
			node.appendChild(updateNode)
			
		MangaXmlParser.setText(dom, updateNode, text)  		
	
	@staticmethod
	def UpdateTimestamp(dom, node):
		t = datetime.datetime.today()
		timeStamp = "%d-%02d-%02d %02d:%02d:%02d" % (t.year, t.month, t.day, t.hour, t.minute, t.second)
		
		MangaXmlParser.UpdateNode(dom, node, 'timeStamp', timeStamp)

	def downloadManga(self):
		print("Parsing XML File...")
		dom = minidom.parse(self.xmlfile_path)
		
		for node in dom.getElementsByTagName("MangaSeries"):
			iLastChap = 0;
			name = MangaXmlParser.getText(node.getElementsByTagName('name')[0])
			site = 	MangaXmlParser.getText(node.getElementsByTagName('HostSite')[0])
			
			try:
				lastDownloaded = MangaXmlParser.getText(node.getElementsByTagName('LastChapterDownloaded')[0])
			except IndexError:
				lastDownloaded = ""
			
			try:
				download_path =	MangaXmlParser.getText(node.getElementsByTagName('downloadPath')[0])
			except IndexError:
				download_path = "./"
			
			self.options.site = site
			self.options.manga = name
			self.options.download_path = download_path
			self.options.lastDownloaded = lastDownloaded
			self.options.auto = True
		
			siteParser = SiteParserFactory.getInstance(self.options)
	
			try:
				siteParser.parseSite()		
				for current_chapter in siteParser.chapters:
					#print "Current Chapter =" + str(current_chapter[0])
					iLastChap = current_chapter[1]
		
				siteParser.downloadChapters()
				print "\n"
			
			except siteParser.NoUpdates:
				print ("Manga ("+name+") up-to-date.\n")
				continue	
			except Exception, (Instance):
				print "Error: Manga ("+name+")"
				print Instance 
				print "\n"
				continue
			
			MangaXmlParser.UpdateNode(dom, node, 'LastChapterDownloaded', str(iLastChap))
			MangaXmlParser.UpdateTimestamp(dom, node)
			
			if (self.conversion_FLAG):
				if (not isImageLibAvailable()):
					print "PIL (Python Image Library) not available."
				else:	
					from ConvertFile import convertFile
					
					convertFileObj = convertFile()
					for compressedFile in siteParser.CompressedFiles:
						convertFileObj.convert(compressedFile, download_path, self.Device)	
			
		#print dom.toxml()
		
		f = open(self.xmlfile_path, 'w')
		f.write(dom.toxml())       	    
