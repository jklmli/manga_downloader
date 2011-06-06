#!/usr/bin/env python

####################

import re

#####################

from base import SiteParserBase
from progressbar.threaded import ThreadProgressBar
from util import fixFormatting, getSourceCode

#####################

class MangaFox(SiteParserBase):
	
	re_getSeries = re.compile('a href="/manga/([^/]*)/[^"]*?" class=[^>]*>([^<]*)</a>')
	re_getChapters = re.compile('"(.*?Ch.[\d.]*)[^"]*","([^"]*)"')
	re_getImage = re.compile(';"><img src="([^"]*)"')
	re_getMaxPages = re.compile('var total_pages=([^;]*?);')
	
	def parseSite(self):
		"""
		Parses list of chapters and URLs associated with each one for the given manga and site.
		"""
		
		print('Beginning MangaFox check: %s' % self.manga)
		
		url = 'http://www.mangafox.com/manga/%s/' % fixFormatting(self.manga)
		source = getSourceCode(url)
		
		# jump straight to expected URL and test if manga removed
		if('it is not available in Manga Fox.' in source):
			raise self.MangaNotFound('It has been removed.')
		
		# do a 'begins-with' search, then a 'contains' search
		url = 'http://www.mangafox.com/search.php?name_method=bw&name=%s' % '+'.join(self.manga.split())
		try:
			source = getSourceCode(url)
			seriesResults = MangaFox.re_getSeries.findall(source)
			if (0 == len(seriesResults) ):
				url = 'http://www.mangafox.com/search.php?name=%s' % '+'.join(self.manga.split())
				source = getSourceCode(url)
				seriesResults = MangaFox.re_getSeries.findall(source)
				
		# 0 results
		except AttributeError:
			raise self.MangaNotFound('It doesn\'t exist, or cannot be resolved by autocorrect.')
		else:	
			keyword = self.selectFromResults(seriesResults)
			url = 'http://www.mangafox.com/manga/%s/' % keyword
			source = getSourceCode(url)
			# other check for manga removal if our initial guess for the name was wrong
			if('it is not available in Manga Fox.' in source):
				raise self.MangaNotFound('It has been removed.')
		
			# that's nice of them
			url = 'http://www.mangafox.com/cache/manga/%s/chapters.js' % keyword
			source = getSourceCode(url)
		
			# chapters is a 2-tuple
			# chapters[0] contains the chapter URL
			# chapters[1] contains the chapter title
			self.chapters = MangaFox.re_getChapters.findall(source)

			# code used to both fix URL from relative to absolute as well as verify last downloaded chapter for XML component
			lowerRange = 0
		
			for i in range(0, len(self.chapters)):
				self.chapters[i] = ('http://www.mangafox.com/manga/%s/' % keyword + self.chapters[i][1], self.chapters[i][0])
				if (not self.auto):
					print('(%i) %s' % (i + 1, self.chapters[i][1]))
				else:
					if (self.lastDownloaded == self.chapters[i][1]):
						lowerRange = i + 1

			# this might need to be len(self.chapters) + 1, I'm unsure as to whether python adds +1 to i after the loop or not
			upperRange = len(self.chapters)
			
			# which ones do we want?
			if (not self.auto):
				self.chapters_to_download = self.selectChapters(self.chapters)
			# XML component
			else:
				if ( lowerRange == upperRange):
					raise self.NoUpdates
				
				for i in range (lowerRange, upperRange):
					self.chapters_to_download.append(i)
			return 		
	
	def downloadChapter(self, current_chapter):
		manga_chapter_prefix, url, max_pages = self.processChapter(current_chapter)
			
		# more or less due to the MangaFox js script sometimes leaving up chapter names and taking down URLs
		# also if we already have the chapter
		if url == None:
			return
				
		isDisplayLocked = False
			
		if (not self.verbose_FLAG):
			# Function Tries to acquire the lock if it succeeds it initialize the progress bar
			isDisplayLocked = ThreadProgressBar.acquireDisplayLock(manga_chapter_prefix,max_pages + 1, False )			
				
		for page in range(1, max_pages + 1):

			if (self.verbose_FLAG):
				print(self.chapters[current_chapter][1] + ' | ' + 'Page %i / %i' % (page, max_pages))

			pageUrl = '%s/%i.html' % (url, page)
			self.downloadImage(page, pageUrl, manga_chapter_prefix)
				
			if (not self.verbose_FLAG):
				if (not isDisplayLocked):
					isDisplayLocked = ThreadProgressBar.acquireDisplayLock(manga_chapter_prefix,max_pages + 1, False )
											
				if (isDisplayLocked):
					ThreadProgressBar.updateProgressBar(page+1)
			
		if (isDisplayLocked):
			ThreadProgressBar.releaseDisplayLock()
		else:
			if (not self.verbose_FLAG):
				ThreadProgressBar.acquireDisplayLock(manga_chapter_prefix, max_pages + 1, True )
				ThreadProgressBar.updateProgressBar(max_pages + 1)
				ThreadProgressBar.releaseDisplayLock()
				
		# Post Processing 
		# Release locks/semaophores
		# Zip Them up
		self.postDownloadProcessing(manga_chapter_prefix, max_pages)	