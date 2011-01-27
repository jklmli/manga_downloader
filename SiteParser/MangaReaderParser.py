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

class MangaReaderParser(SiteParserBase):

	def parseSite(self):
		print('Beginning MangaReader check: %s' % self.manga)
		
		url = 'http://www.mangareader.net/alphabetical'

		source_code = getSourceCode(url)
		info = re.compile('<li><a href="([^"]*)">([^<]*)</a>').findall(source_code[source_code.find('series_col'):])

		keyword = self.selectFromResults(info)

		url = 'http://www.mangareader.net%s' % keyword
		source_code = getSourceCode(url)

		self.chapters = re.compile('<a href="([^"]*)">([^<]*)</a>([^<]*)</td>').findall(source_code)
		
		lowerRange = 0
		upperRange = 0
	
		for i in range(0, len(self.chapters)):
			self.chapters[i] = ('http://www.mangareader.net' + self.chapters[i][0], '%s%s' % (self.chapters[i][1], self.chapters[i][2]))
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
				self.chapters_to_download .append(i)
		return 
	
	def downloadChapter(self, current_chapter):
		if (self.verbose_FLAG):
			print "Manga Reader - Download Chapter"
		
		manga_chapter_prefix, url, max_pages = self.prepareDownload(current_chapter, '</select> of (\d*)(\s)*</div>')

		if url == None:
			return

		hasDisplayLock = False
			
		if (not self.verbose_FLAG):
			# Function Tries to acquire the lock if it succeeds it initialize the progress bar
			hasDisplayLock = ThreadProgressBar.AcquireDisplayLock(manga_chapter_prefix,max_pages + 1, False )	
		
		pageIndex = 0

		for page in re.compile("<option value=\"([^']*?)\"[^>]*>\s*(\d*)</option>").findall(getSourceCode(url)):

			if (self.verbose_FLAG):
				print(self.chapters[current_chapter][1] + ' | ' + 'Page %s / %i' % (page[1], max_pages))

			pageUrl = 'http://www.mangareader.net' + page[0]
			self.downloadImage(page[1], pageUrl, manga_chapter_prefix, 'img id="img" .* src="([^"]*)"')
			
			pageIndex = pageIndex + 1
			if (not self.verbose_FLAG):
				if (not hasDisplayLock):
					hasDisplayLock = ThreadProgressBar.AcquireDisplayLock(manga_chapter_prefix,max_pages + 1, False )
											
				if (hasDisplayLock):
					ThreadProgressBar.UpdateProgressBar(pageIndex+ 1)
			
		if (hasDisplayLock):
			ThreadProgressBar.ReleaseDisplayLock()
		else:
			if (not self.verbose_FLAG):
				ThreadProgressBar.AcquireDisplayLock(manga_chapter_prefix,max_pages + 1, True )
				ThreadProgressBar.UpdateProgressBar(max_pages + 1)
				ThreadProgressBar.ReleaseDisplayLock()

		self.postDownloadProcessing(manga_chapter_prefix, max_pages)		