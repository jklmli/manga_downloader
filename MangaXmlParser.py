from xml.dom import minidom
from SiteParser import SiteParserFactory

class MangaXmlParser:
	def __init__(self, xmlPath):
		self.xmlFile = xmlPath
		self.overwrite_FLAG = False
		self.download_format = '.cbz'
		self.ConversionFlag = False
		self.Device = "Kindle 3"
	
	@staticmethod 
	def ImportConversionLib():
		try:
			from ConvertFile import convertFile
		except ImportError:
			return False
		else:
			return True
	
	@staticmethod
	def getText(nodelist):
		rc = []
		for node in nodelist:
			if node.nodeType == node.TEXT_NODE:
				rc.append(node.data)
		
		return ''.join(rc)

	@staticmethod
	def setText(nodelist, text):
		for node in nodelist:
			if node.nodeType == node.TEXT_NODE:
				node.data = text
				
	def downloadManga(self):
		print("parsing XML File")
		dom = minidom.parse(self.xmlFile)
		
		for node in dom.getElementsByTagName("MangaSeries"):
			iLastChap = 0;
			name = MangaXmlParser.getText(node.getElementsByTagName('name')[0].childNodes)
			site = 	MangaXmlParser.getText(node.getElementsByTagName('HostSite')[0].childNodes)
			lastChapterDownloaded =	MangaXmlParser.getText(node.getElementsByTagName('LastChapterDownloaded')[0].childNodes)
			download_path =	MangaXmlParser.getText(node.getElementsByTagName('downloadPath')[0].childNodes)
			
			
			siteParser = SiteParserFactory.getInstance(site)
			
			siteParser.overwrite_FLAG = self.overwrite_FLAG
			siteParser.all_chapters_FLAG = False
		
			try:
				siteParser.ParseSite(name, True, lastChapterDownloaded)
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
				siteParser.downloadChapters(download_path, self.download_format)
				print "\n"
			except:
				print "Unknown Error - ("+name+")\n"
				continue
			
			#print iLastChap
			MangaXmlParser.setText(node.getElementsByTagName('LastChapterDownloaded')[0].childNodes, str(iLastChap))
			
			if (self.ConversionFlag):
				if (not MangaXmlParser.ImportConversionLib()):
					print "PIL (Python Image Library) not available."
				else:	
					from ConvertFile import convertFile
					
					convertFileObj = convertFile()
					for compressedFile in siteParser.CompressedFiles:
						convertFileObj.convert(compressedFile, download_path, self.Device)	
			
		f = open(self.xmlFile, 'w')
		f.write(dom.toxml())       	    