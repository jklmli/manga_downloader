#!/usr/bin/env python

######################

from xml.dom import minidom
from SiteParser import SiteParserFactory

######################

class MangaXmlParser:
	def __init__(self, xmlPath):
		# now uses setOpts
		pass
	
	@staticmethod
	def getText(nodelist):
#		rc = []
#		for node in nodelist:
#			if node.nodeType == node.TEXT_NODE:
#				rc.append(node.data)
#		
#		
#		return ''.join(rc)
		
		# untested code, but should work
		return ''.join([node.data for node in nodelist if node.nodeType == node.TEXT_NODE])

	@staticmethod
	def setText(nodelist, text):
		for node in nodelist:
			if node.nodeType == node.TEXT_NODE:
				node.data = text
		# could apply list comprehension as well, but this way's maybe more readable?
	
	def setOpts(self, optDict):
		"""
		sets attributes for the object, passed from the arguments to manga.py
		"""
		for elem in vars(optDict):
			setattr(self, elem, getattr(optDict, elem))
	#			print(elem, getattr(optDict, elem))	
					
	def downloadManga(self):
		print("Parsing XML File...")

		dom = minidom.parse(self.xmlFile)
		
		for node in dom.getElementsByTagName("MangaSeries"):
			iLastChap = 0;
			name = MangaXmlParser.getText(node.getElementsByTagName('name')[0].childNodes)
			site = 	MangaXmlParser.getText(node.getElementsByTagName('HostSite')[0].childNodes)
			lastDownloaded = MangaXmlParser.getText(node.getElementsByTagName('LastChapterDownloaded')[0].childNodes)
			download_path =	MangaXmlParser.getText(node.getElementsByTagName('downloadPath')[0].childNodes)
			
			
			siteParser = SiteParserFactory.getInstance(site)
			
#			siteParser.overwrite_FLAG = self.overwrite_FLAG
#			siteParser.all_chapters_FLAG = False
#			siteParser.auto = True
#			siteParser.lastDownloaded = lastChapterDownloaded

			# should be able to replace above code
			siteParser.setOpts(vars(self))
		
			try:
				siteParser.ParseSite()
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

		f = open(self.xmlFile, 'w')
		f.write(dom.toxml())       	    
