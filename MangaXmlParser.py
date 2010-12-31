#!/usr/bin/env python

######################
import os
import time

from xml.dom import minidom
from SiteParser import SiteParserFactory
from SiteParserThread import SiteParserThread
from helper import *

######################

class MangaXmlParser:
	def __init__(self, optDict):
		self.options = optDict
		for elem in vars(optDict):
			setattr(self, elem, getattr(optDict, elem))

	def downloadManga(self):
		print("Parsing XML File...")
		dom = minidom.parse(self.xmlfile_path)
		
		threadPool = []
		self.options.auto = True
					
		for node in dom.getElementsByTagName("MangaSeries"):
			iLastChap = 0;
			name = getText(node.getElementsByTagName('name')[0])
			site = getText(node.getElementsByTagName('HostSite')[0])
			
			try:
				lastDownloaded = getText(node.getElementsByTagName('LastChapterDownloaded')[0])
			except IndexError:
				lastDownloaded = ""
			
			try:
				download_path =	getText(node.getElementsByTagName('downloadPath')[0])
			except IndexError:
				download_path = ('./' + SiteParser.fixFormatting(name))
			
			self.options.site = site
			self.options.manga = name
			self.options.download_path = download_path
			self.options.lastDownloaded = lastDownloaded
			
			threadPool.append(SiteParserThread(self.options, dom, node))
		
		for thread in threadPool: 
			thread.start()
		
		while (len(threadPool) > 0):
			thread = threadPool.pop()
			while (thread.isAlive()):
				time.sleep(3)
		
		#print dom.toxml()		
		f = open(self.xmlfile_path, 'w')
		f.write(dom.toxml())       	    
