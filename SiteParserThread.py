#!/usr/bin/env python

#####################

import threading
import time
import datetime

from SiteParser import SiteParserFactory
from helper import *
#####################

class SiteParserThread( threading.Thread ):

	def __init__ ( self, optDict, dom, node ):
		threading.Thread.__init__(self)
		for elem in vars(optDict):
			setattr(self, elem, getattr(optDict, elem))
			
		self.dom = dom
		self.node = node

	def UpdateTimestamp(self):
		t = datetime.datetime.today()
		timeStamp = "%d-%02d-%02d %02d:%02d:%02d" % (t.year, t.month, t.day, t.hour, t.minute, t.second)
		
		UpdateNode(self.dom, self.node, 'timeStamp', timeStamp)
			
	def run (self):
		siteParser = SiteParserFactory.getInstance(self)
		try:
			siteParser.parseSite()		
			for current_chapter in siteParser.chapters:
				#print "Current Chapter =" + str(current_chapter[0])
				iLastChap = current_chapter[1]
		
			siteParser.downloadChapters()
			print "\n"
			
		except siteParser.NoUpdates:
			print ("Manga ("+self.manga+") up-to-date.\n")
			return
		except Exception, (Instance):
			print "Error: Manga ("+self.manga+")"
			print Instance 
			print "\n"
			return 
			
		if self.xmlfile_path != None:
			UpdateNode(self.dom, self.node, 'LastChapterDownloaded', str(iLastChap))
			self.UpdateTimestamp()	
		
		if (self.conversion_FLAG):
			if (not isImageLibAvailable()):
				print "PIL (Python Image Library) not available."
			else:	
				from ConvertFile import convertFile
					
				convertFileObj = convertFile()
				for compressedFile in siteParser.CompressedFiles:
					convertFileObj.convert(compressedFile, self.download_path, self.Device)	