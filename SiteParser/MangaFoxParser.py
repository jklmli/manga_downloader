#!/usr/bin/env python

####################

import re

#####################

from SiteParserBase import SiteParserBase
from helper import *
from ProgressBar.ThreadProgressBar import *

#####################

class MangaFoxParser(SiteParserBase):
	
	def parseSite(self):
		"""
		Parses list of chapters and URLs associated with each one for the given manga and site.
		"""
		
		print('Beginning MangaFox check: %s' % self.manga)
		
		url = 'http://www.mangafox.com/manga/%s/' % fixFormatting(self.manga)
		source_code = getSourceCode(url)
		
		# jump straight to expected URL and test if manga removed
		if(source_code.find('it is not available in Manga Fox.') != -1):
			raise self.MangaNotFound('It has been removed')
		
		# do a search
		url = 'http://www.mangafox.com/search.php?name=%s' % '+'.join(self.manga.split())
		try:
			source_code = getSourceCode(url)
			info = re.compile('a href="/manga/([^/]*)/[^"]*?" class=[^>]*>([^<]*)</a>').findall(source_code)
		# 0 results
		except AttributeError:
			raise self.MangaNotFound('It doesn\'t exist, or cannot be resolved by autocorrect.')
		else:	
			keyword = self.selectFromResults(info)
			url = 'http://www.mangafox.com/manga/%s/' % keyword
			source_code = getSourceCode(url)
			# other check for manga removal if our initial guess for the name was wrong
			if(source_code.find('it is not available in Manga Fox.') != -1):
				raise self.MangaNotFound('It has been removed')
		
			# that's nice of them
			url = 'http://www.mangafox.com/cache/manga/%s/chapters.js' % keyword
			source_code = getSourceCode(url)
		
			# chapters is a 2-tuple
			# chapters[0] contains the chapter URL
			# chapters[1] contains the chapter title
			self.chapters = re.compile('"(.*?Ch.[\d.]*)[^"]*","([^"]*)"').findall(source_code)

			# code used to both fix URL from relative to absolute as well as verify last downloaded chapter for XML component
			lowerRange = 0
			upperRange = 0
		
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
		manga_chapter_prefix, url, max_pages = self.prepareDownload(current_chapter, 'var total_pages=([^;]*?);')
			
		# more or less due to the MangaFox js script sometimes leaving up chapter names and taking down URLs
		# also if we already have the chapter
		if url == None:
			return
				
		hasDisplayLock = False
			
		if (not self.verbose_FLAG):
			# Function Tries to acquire the lock if it succeeds it initialize the progress bar
			hasDisplayLock = ThreadProgressBar.AcquireDisplayLock(manga_chapter_prefix,max_pages + 1, False )			
				
		for page in range(1, max_pages + 1):

			if (self.verbose_FLAG):
				print(self.chapters[current_chapter][1] + ' | ' + 'Page %i / %i' % (page, max_pages))

			pageUrl = '%s/%i.html' % (url, page)
			self.downloadImage(page, pageUrl, manga_chapter_prefix, ';"><img src="([^"]*)"')
				
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
				
		# Post Processing 
		# Release locks/semaophores
		# Zip Them up
		self.postDownloadProcessing(manga_chapter_prefix, max_pages)	