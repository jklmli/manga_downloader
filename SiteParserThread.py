#!/usr/bin/env python

#####################

import threading
import time
import datetime

from SiteParser import *
from helper import *
#####################

class SiteParserThread( threading.Thread ):

	def __init__ ( self, optDict, dom, node ):
		threading.Thread.__init__(self)
		self.uptodate_FLAG = False
		
		for elem in vars(optDict):
			setattr(self, elem, getattr(optDict, elem))
			
		self.dom = dom
		self.node = node
		self.siteParser = SiteParserFactory.getInstance(self)
		try:
			self.siteParser.parseSite()	
		except self.siteParser.NoUpdates:
			self.uptodate_FLAG = True

	def UpdateTimestamp(self):
		t = datetime.datetime.today()
		timeStamp = "%d-%02d-%02d %02d:%02d:%02d" % (t.year, t.month, t.day, t.hour, t.minute, t.second)
		
		UpdateNode(self.dom, self.node, 'timeStamp', timeStamp)
			
	def run (self):
		if (self.uptodate_FLAG):
			print ("Manga ("+self.manga+") up-to-date.\n")
			return		
			
		try:
			for current_chapter in self.siteParser.chapters:
				#print "Current Chapter =" + str(current_chapter[0])
				iLastChap = current_chapter[1]
		
			self.siteParser.downloadChapters()
			print "\n"
			
		except Exception, (Instance):
			print "Error: Manga ("+self.manga+")"
			print Instance 
			print "\n"
			return 
			
		if self.xmlfile_path != None:
			UpdateNode(self.dom, self.node, 'LastChapterDownloaded', str(iLastChap))
			self.UpdateTimestamp()	
		

	
	@staticmethod
	def WaitForThreads(threadPool, conversionOptions):
		while (len(threadPool) > 0):
			thread = threadPool.pop()
			while (thread.isAlive()):
				if (SiteParserThread.ProcessConversionList(conversionOptions) == 0):
					time.sleep(2)
		
		# This is to avoid a race condition where the last SiteParserThreads adds a compressionFile 
		# to the list and then dies. Therfore thread.isAlive would be false but there would still
		# be a compression File to process
		SiteParserThread.ProcessConversionList(conversionOptions)			
	
	@staticmethod
	def ProcessConversionList(conversionOptions):
		i = 0
		if (conversionOptions.conversion_FLAG):
			if (not isImageLibAvailable()):
				print "PIL (Python Image Library) not available."
			else:	
				from ConvertFile import convertFile
				
				convertFileObj = convertFile()
				compressedFile, outputPath = SiteParserBase.PopCoversionFileEntry()
				while (compressedFile != None and outputPath != None):
					i = i + 1
					convertFileObj.convert(compressedFile, outputPath, conversionOptions.Device)
					compressedFile, outputPath = SiteParserBase.PopCoversionFileEntry()
		
		return i			