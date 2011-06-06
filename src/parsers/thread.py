#!/usr/bin/env python

#####################

import datetime
import threading
import time

#####################

from base import SiteParserBase
from ConvertPackage.ConversionQueue import ConversionQueue
from factory import SiteParserFactory
from util import isImageLibAvailable, updateNode

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
			print ("Manga ("+self.manga+") up-to-date.")
		print '\n'	
			
	def run (self):
		success = False
		if (self.uptodate_FLAG):
			return		
			
		try:
			for current_chapter in self.siteParser.chapters:
				#print "Current Chapter =" + str(current_chapter[0])
				iLastChap = current_chapter[1]
		
			success = self.siteParser.download()
			
		except SiteParserBase.MangaNotFound as Instance:
			print "Error: Manga ("+self.manga+")"
			print Instance 
			print "\n"
			return 
		
		# Update the XML File only when all the chapters successfully download. If 1 of n chapters failed 
		# to download, the next time the script is run the script will try to download all n chapters. However,
		# autoskipping (unless the user specifies the --overwrite Flag) should skip the chapters that were already
		# downloaded so little additional time should be added.
			
		if self.xmlfile_path != None and success:
			updateNode(self.dom, self.node, 'LastChapterDownloaded', str(iLastChap))
			self.updateTimestamp()	
		
	def updateTimestamp(self):
		t = datetime.datetime.today()
		timeStamp = "%d-%02d-%02d %02d:%02d:%02d" % (t.year, t.month, t.day, t.hour, t.minute, t.second)
		
		updateNode(self.dom, self.node, 'timeStamp', timeStamp)
	
	@staticmethod
	def waitForThreads(threadPool, conversionOptions):
		while (len(threadPool) > 0):
			thread = threadPool.pop()
			while (thread.isAlive()):
				processedItems = SiteParserThread.processConversionList(conversionOptions) 
				if (processedItems == 0):
					# Yields execution to whatever another thread
					time.sleep(0)
		
		# This is to avoid a race condition where the last SiteParserThread adds a compressionFile 
		# to the list and then dies. Therefore thread.isAlive would be false but there would still
		# be a compression file to process
		SiteParserThread.processConversionList(conversionOptions)			
	
	@staticmethod
	def processConversionList(conversionOptions):
		i = 0
		if (conversionOptions.conversion_FLAG):
			if (not isImageLibAvailable()):
				print "PIL (Python Image Library) not available."
			else:	
				from ConvertPackage.ConvertFile import convertFile
				
				convertFileObj = convertFile()
				compressedFile, outputPath = ConversionQueue.pop()
				while (compressedFile != None and outputPath != None):
					i = i + 1
					convertFileObj.convert(compressedFile, outputPath, conversionOptions.device, conversionOptions.verbose_FLAG)
					compressedFile, outputPath = ConversionQueue.pop()
		
		return i			