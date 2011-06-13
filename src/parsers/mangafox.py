#!/usr/bin/env python

####################

import re

#####################

from base import SiteParserBase
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
		
		# jump straight to expected URL and test if manga removed
		url = 'http://www.mangafox.com/manga/%s/' % self.manga.lower().strip().replace(' ', '_')
		source = getSourceCode(url)
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
	
	def downloadChapter(self, max_pages, url, manga_chapter_prefix, current_chapter):
		for page in range(1, max_pages + 1):
			if (self.verbose_FLAG):
				print(self.chapters[current_chapter][1] + ' | ' + 'Page %i / %i' % (page, max_pages))

			pageUrl = '%s/%i.html' % (url, page)
			self.downloadImage(page, pageUrl, manga_chapter_prefix)
