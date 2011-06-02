#!/usr/bin/env python

####################################################################
# For more detailed comments look at MangaFoxParser
#
# The code for this sites is similar enough to not need
# explanation, but dissimilar enough to not warrant any further OOP
####################################################################

####################

import re

#####################

from base import SiteParserBase
from progressbar.threaded import ThreadProgressBar
from util import fixFormatting, getSourceCode

#####################

class OtakuWorks(SiteParserBase):
	
	re_getMangas = re.compile('a href="([^"]*?)"[^>]*?>([^<]*?) \(Manga\)')
	
	def parseSite(self):
		print('Beginning OtakuWorks check: %s' % self.manga)
		url = 'http://www.otakuworks.com/search/%s' % '+'.join(self.manga.split())

		source = getSourceCode(url)
		
		info = OtakuWorks.re_getMangas.findall(source)
		
		# we either have 0 search results or we have already been redirected to the manga homepage
		if len(info) != 0:
			keyword = self.selectFromResults(info)
			source = getSourceCode(keyword)
	
		if(source.find('has been licensed and as per request all releases under it have been removed.') != -1):
			raise self.MangaNotFound('It has been removed.')
		
		# can't pre-compile this because relies on class name
		self.chapters = re.compile('a href="([^>]*%s[^>]*)">([^<]*#[^<]*)</a>' % '-'.join(fixFormatting(self.manga).replace('_', ' ').split())).findall(source)
		self.chapters.reverse()

		lowerRange = 0
		
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

		isDisplayLocked = False
			
		if (not self.verbose_FLAG):
			# Function Tries to acquire the lock if it succeeds it initialize the progress bar
			isDisplayLocked = ThreadProgressBar.acquireDisplayLock(manga_chapter_prefix,max_pages + 1, False )	
				
		for page in range(1, max_pages + 1):
			if (self.verbose_FLAG):
				print(self.chapters[current_chapter][1] + ' | ' + 'Page %i / %i' % (page, max_pages))
					
			pageUrl = '%s/%i' % (url, page)
			self.downloadImage(page, pageUrl, manga_chapter_prefix, 'img src="(http://static.otakuworks.net/viewer/[^"]*)"')

			if (not self.verbose_FLAG):
				if (not isDisplayLocked):
					isDisplayLocked = ThreadProgressBar.acquireDisplayLock(manga_chapter_prefix,max_pages + 1, False )
											
				if (isDisplayLocked):
					ThreadProgressBar.updateProgressBar(page+1)
			
		if (isDisplayLocked):
			ThreadProgressBar.releaseDisplayLock()
		else:
			if (not self.verbose_FLAG):
				ThreadProgressBar.acquireDisplayLock(manga_chapter_prefix,max_pages + 1, True )
				ThreadProgressBar.updateProgressBar(max_pages + 1)
				ThreadProgressBar.releaseDisplayLock()
					
		self.postDownloadProcessing(manga_chapter_prefix, max_pages)