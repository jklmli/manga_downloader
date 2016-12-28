#!/usr/bin/env python

####################

import re
import string

#####################

from parsers.base import SiteParserBase
from util import fixFormatting, getSourceCode

#####################

class MangaFox(SiteParserBase):
	re_getSeries = re.compile('a href="http://.*?mangafox.*?/manga/([^/]*)/[^"]*?" class=[^>]*>([^<]*)</a>')
	#re_getSeries = re.compile('a href="/manga/([^/]*)/[^"]*?" class=[^>]*>([^<]*)</a>')
	#re_getChapters = re.compile('"(.*?Ch.[\d.]*)[^"]*","([^"]*)"')
	re_getImage = re.compile('<img src="([^"]*)".*?id="image"')
	re_getMaxPages = re.compile('var total_pages=([^;]*?);')
	
	def fixFormatting(self, s):
		
		for i in string.punctuation:
			s = s.replace(i, " ")
		
		p = re.compile( '\s+')
		s = p.sub( ' ', s )
		
		s = s.lower().strip().replace(' ', '_')
		return s
		
	def parseSite(self):
		"""
		Parses list of chapters and URLs associated with each one for the given manga and site.
		"""
		
		print('Beginning MangaFox check: %s' % self.manga)

		# jump straight to expected URL and test if manga removed
		url = 'http://mangafox.me/manga/%s/' % self.fixFormatting( self.manga )
		if self.verbose_FLAG:
			print(url)
		
		source, redirectURL = getSourceCode(url, self.proxy, True)

		if (redirectURL != url or source is None or 'the page you have requested cannot be found' in source):
			# Could not find the manga page by guessing 
			# Use the website search
			url = 'http://mangafox.me/search.php?name_method=bw&name=%s&is_completed=&advopts=1' % '+'.join(self.manga.split())
			if self.verbose_FLAG:
				print(url)
			try:
				source = getSourceCode(url, self.proxy)
				seriesResults = []
				if source is not None:
					seriesResults = MangaFox.re_getSeries.findall(source)
				
				if ( 0 == len(seriesResults) ):
					url = 'http://mangafox.me/search.php?name_method=cw&name=%s&is_completed=&advopts=1' % '+'.join(self.manga.split())
					if self.verbose_FLAG:
						print(url)
					source = getSourceCode(url, self.proxy)
					if source is not None:
						seriesResults = MangaFox.re_getSeries.findall(source)
					
			# 0 results
			except AttributeError:
				raise self.MangaNotFound('It doesn\'t exist, or cannot be resolved by autocorrect.')
			else:	
				keyword = self.selectFromResults(seriesResults)
				if self.verbose_FLAG:
					print ("Keyword: %s" % keyword)
				url = 'http://mangafox.me/manga/%s/' % keyword	
				if self.verbose_FLAG:
					print ("URL: %s" % url)				
				source = getSourceCode(url, self.proxy)
				
				if (source is None):
					raise self.MangaNotFound('Search Failed to find Manga.')		
		else:
			# The Guess worked
			keyword = self.fixFormatting( self.manga )
			if self.verbose_FLAG:
				print ("Keyword: %s" % keyword)
		

		if('it is not available in Manga Fox.' in source):
			raise self.MangaNotFound('It has been removed.')
			

		# that's nice of them
		#url = 'http://mangafox.me/cache/manga/%s/chapters.js' % keyword
		#source = getSourceCode(url, self.proxy)
		
		# chapters is a 2-tuple
		# chapters[0] contains the chapter URL
		# chapters[1] contains the chapter title
			
		isChapterOnly = False
		
		# can't pre-compile this because relies on class name
		re_getChapters = re.compile('a href="http://.*?mangafox.*?/manga/%s/(v[\d|(TBD)]+)/(c[\d\.]+)/[^"]*?" title' % keyword)
		self.chapters = re_getChapters.findall(source)
		if not self.chapters:
			if self.verbose_FLAG:
				print ("Trying chapter only regex")
			isChapterOnly = True
			re_getChapters = re.compile('a href="http://.*?mangafox.*?/manga/%s/(c[\d\.]+)/[^"]*?" title' % keyword)
			self.chapters = re_getChapters.findall(source)
			
		self.chapters.reverse()
			
		# code used to both fix URL from relative to absolute as well as verify last downloaded chapter for XML component
		lowerRange = 0
			
		if isChapterOnly:
			for i in range(0, len(self.chapters)):
				if self.verbose_FLAG:
					print("%s" % self.chapters[i])
				if (not self.auto):
					print('(%i) %s' % (i + 1, self.chapters[i]))
				else:
					if (self.lastDownloaded == self.chapters[i]):
						lowerRange = i + 1
												
				self.chapters[i] = ('http://mangafox.me/manga/%s/%s' % (keyword, self.chapters[i]), self.chapters[i], self.chapters[i])

		else:				
			for i in range(0, len(self.chapters)):
				if self.verbose_FLAG:
					print("%s %s" % (self.chapters[i][0], self.chapters[i][1]))
				self.chapters[i] = ('http://mangafox.me/manga/%s/%s/%s' % (keyword, self.chapters[i][0], self.chapters[i][1]), self.chapters[i][0] + "." + self.chapters[i][1], self.chapters[i][1])
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
	
	def downloadChapter(self, downloadThread, max_pages, url, manga_chapter_prefix, current_chapter):
		for page in range(1, max_pages + 1):
			if (self.verbose_FLAG):
				print(self.chapters[current_chapter][1] + ' | ' + 'Page %i / %i' % (page, max_pages))

			pageUrl = '%s/%i.html' % (url, page)
			self.downloadImage(downloadThread, page, pageUrl, manga_chapter_prefix)
