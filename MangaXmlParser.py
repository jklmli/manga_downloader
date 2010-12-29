#!/usr/bin/env python

######################
import os

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
	def getText(nodelist):
#		rc = []
#		for node in nodelist:
#			if node.nodeType == node.TEXT_NODE:
#				rc.append(node.data)
#		
#		
#		return ''.join(rc)
		return ''.join([node.data for node in nodelist if node.nodeType == node.TEXT_NODE])

	@staticmethod
	def setText(nodelist, text):
		for node in nodelist:
			if node.nodeType == node.TEXT_NODE:
				node.data = text
		# could apply list comprehension as well, but this way's maybe more readable?
					
	def downloadManga(self):
		print("Parsing XML File...")
		dom = minidom.parse(self.xmlfile_path)
		
		for node in dom.getElementsByTagName("MangaSeries"):
			iLastChap = 0;
			name = MangaXmlParser.getText(node.getElementsByTagName('name')[0].childNodes)
			site = 	MangaXmlParser.getText(node.getElementsByTagName('HostSite')[0].childNodes)
			lastDownloaded = MangaXmlParser.getText(node.getElementsByTagName('LastChapterDownloaded')[0].childNodes)
			download_path =	MangaXmlParser.getText(node.getElementsByTagName('downloadPath')[0].childNodes)
			
			self.options.site = site
			self.options.manga = name
			self.options.download_path = download_path
			self.options.lastDownloaded = lastDownloaded
			self.options.auto = True
		
			try:		
				# create download directory if not found
				if os.path.exists(self.options.download_path) is False:
					os.mkdir(self.options.download_path)
			except OSError:
				print "Manga ("+name+"):"				
				print 'Unable to create download directory: there may be a file with the same name, or you may not have permissions to write there.'
		
			siteParser = SiteParserFactory.getInstance(self.options)
	
			try:
				siteParser.parseSite()
			except siteParser.MangaNotFound:
				print ("Manga ("+name+") Missing. Check if still available\n")
				continue
			
			except siteParser.NoUpdates:
				print ("Manga ("+name+") up-to-date.\n")
				continue
		
			for current_chapter in siteParser.chapters:
				#print "Current Chapter =" + str(current_chapter[0])
				iLastChap = current_chapter[1]
		
			try:
				siteParser.downloadChapters()
				print "\n"
			except:
				print "Unknown Error - ("+name+")\n"
				continue
			
			#print iLastChap
			MangaXmlParser.setText(node.getElementsByTagName('LastChapterDownloaded')[0].childNodes, str(iLastChap))
			
			if (self.conversion_FLAG):
				if (not isImageLibAvailable()):
					print "PIL (Python Image Library) not available."
				else:	
					from ConvertFile import convertFile
					
					convertFileObj = convertFile()
					for compressedFile in siteParser.CompressedFiles:
						convertFileObj.convert(compressedFile, download_path, self.Device)	
			
		f = open(self.xmlfile_path, 'w')
		f.write(dom.toxml())       	    
