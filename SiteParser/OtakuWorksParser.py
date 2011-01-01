#!/usr/bin/env python

####################################################################
# For more detailed commnets look at MangaFoxParser
#
# The code for this sites is similar enough to not need
# explanation, but dissimilar enough to not warrant any further OOP
####################################################################

####################

import re

#####################

from SiteParserBase import SiteParserBase
from helper import *
from ProgressBar.ThreadProgressBar import *

#####################

class OtakuWorksParser(SiteParserBase):
	
	def parseSite(self):
		print('Beginning OtakuWorks check: %s' % self.manga)
		url = 'http://www.otakuworks.com/search/%s' % '+'.join(self.manga.split())

		source_code = getSourceCode(url)

		info = re.compile('a href="([^"]*?)"[^>]*?>([^<]*?) \(Manga\)').findall(source_code)
		
		# we either have 0 search results or we have already been redirected to the manga homepage
		if len(info) != 0:
			keyword = self.selectFromResults(info)
			source_code = getSourceCode(keyword)
	
		if(source_code.find('has been licensed and as per request all releases under it have been removed.') != -1):
			raise self.MangaNotFound('It has been removed.')
		
		self.chapters = re.compile('a href="([^>]*%s[^>]*)">([^<]*#[^<]*)</a>' % '-'.join(fixFormatting(self.manga).replace('_', ' ').split())).findall(source_code)
		self.chapters.reverse()

		lowerRange = 0
		upperRange = 0
		for i in range(0, len(self.chapters)):
			self.chapters[i] = ('http://www.otakuworks.com' + self.chapters[i][0] + '/read', self.chapters[i][1])
			if (not self.auto):
				print('(%i) %s' % (i + 1, self.chapters[i][1]))
			else:
				if (self.lastDownloaded == self.chapters[i][1]):
					lowerRange = i + 1
		
		# this might need to be len(self.chapters) + 1, I'm unsure as to whether python adds +1 to i after the loop or not
		upperRange = len(self.chapters)	
	
		if (not self.auto):
			self.chapters_to_download = self.selectChapters(self.chapters)
		else:
			if ( lowerRange == upperRange):
				raise self.NoUpdates
			for i in range (lowerRange, upperRange):
				self.chapters_to_download.append(i)
		return 
		
	def downloadChapter(self, current_chapter):
		
		manga_chapter_prefix, url, max_pages = self.prepareDownload(current_chapter, '<strong>(\d*)</strong>')
 
		if url == None:
			return

		hasDisplayLock = False
			
		if (not self.verbose_FLAG):
			# Function Tries to acquire the lock if it succeeds it initialize the progress bar
			hasDisplayLock = ThreadProgressBar.AcquireDisplayLock(manga_chapter_prefix,max_pages + 1, False )	
				
		for page in range(1, max_pages + 1):
			if (self.verbose_FLAG):
				print(self.chapters[current_chapter][1] + ' | ' + 'Page %i / %i' % (page, max_pages))
					
			pageUrl = '%s/%i' % (url, page)
			self.downloadImage(page, pageUrl, manga_chapter_prefix, 'img src="(http://static.otakuworks.net/viewer/[^"]*)"')

			if (not self.verbose_FLAG):
				if (not hasDisplayLock):
					hasDisplayLock = ThreadProgressBar.AcquireDisplayLock(manga_chapter_prefix,max_pages + 1, False )
											
				if (hasDisplayLock):
					ThreadProgressBar.UpdateProgressBar(page+1)
			
		if (hasDisplayLock):
			ThreadProgressBar.ReleaseDisplayLock()
		else:
			if (not self.verbose_FLAG):
				ThreadProgressBar.AcquireDisplayLock(manga_chapter_prefix,max_pages + 1, True )
				ThreadProgressBar.UpdateProgressBar(max_pages + 1)
				ThreadProgressBar.ReleaseDisplayLock()
					
		self.postDownloadProcessing(manga_chapter_prefix, max_pages)