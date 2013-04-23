#!/usr/bin/env python

#####################

import datetime
import threading
import time
import os
import socks
import socket
#####################

from parsers.base import SiteParserBase
from parsers.factory import SiteParserFactory
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
			# create download directory if not found
			try:
				if os.path.exists(self.downloadPath) is False:
					os.mkdir(self.downloadPath)
			except OSError:
				print("""Unable to create download directory. There may be a file 
					with the same name, or you may not have permissions to write 
					there.""")
				raise

		except self.siteParser.NoUpdates:
			self.uptodate_FLAG = True
			print ("Manga ("+self.manga+") up-to-date.")
		print('\n')
			
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
			print("Error: Manga ("+self.manga+")")
			print(Instance)
			print("\n")
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