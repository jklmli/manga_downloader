#!/usr/bin/env python

####################

import re
import string
import time

#####################

from parsers.base import SiteParserBase
from util import fixFormatting, getSourceCode

#####################

class MangaHere(SiteParserBase):
	re_getSeries = re.compile('a href="http://.*?mangahere.*?/manga/([^/]*)/[^"]*?" class=[^>]*>([^<]*)</a>')
	#re_getSeries = re.compile('a href="/manga/([^/]*)/[^"]*?" class=[^>]*>([^<]*)</a>')
	#re_getChapters = re.compile('"(.*?Ch.[\d.]*)[^"]*","([^"]*)"')
	re_getImage = re.compile('<img src="([^"]*.jpg)[^"]*"')
	re_getMaxPages = re.compile('var total_pages = ([^;]*?);')

	def fixFormatting(self, s):

		for i in string.punctuation:
			s = s.replace(i, " ")

		p = re.compile( '\s+')
		s = p.sub( ' ', s )

		s = s.lower().strip().replace(' ', '_')
		return s

	def chapter_compare(self, x, y):
		non_decimal = re.compile(r'[^\d.]+')

		x_vol = float(non_decimal.sub('', x[0]))
		y_vol = float(non_decimal.sub('', y[0]))
		if x_vol != y_vol:
			return 1 if x_vol > y_vol else -1

		x_chapter = float(non_decimal.sub('', x[1]))
		y_chapter = float(non_decimal.sub('', y[1]))
		if x_chapter != y_chapter:
			return 1 if x_chapter > y_chapter else -1

		return 0

	def parseSite(self):
		"""
		Parses list of chapters and URLs associated with each one for the given manga and site.
		"""

		print('Beginning MangaHere check: %s' % self.manga)

		# jump straight to expected URL and test if manga removed
		url = 'http://www.mangahere.com/manga/%s/' % self.fixFormatting( self.manga )
		if self.verbose_FLAG:
			print(url)
		source = getSourceCode(url, self.proxy)

		if (source is None or 'the page you have requested can' in source):
			# do a 'begins-with' search, then a 'contains' search
			url = 'http://www.mangahere.com/search.php?name=%s' % '+'.join(self.manga.split())
			if self.verbose_FLAG:
				print(url)

			try:
				source = getSourceCode(url, self.proxy)
				if('Sorry you have just searched, please try 5 seconds later.' in source):
					print('Searched too soon, waiting 5 seconds...')
					time.sleep(5)
				seriesResults = MangaHere.re_getSeries.findall(source)

				seriesResults = []
				if source is not None:
					seriesResults = MangaHere.re_getSeries.findall(source)

				if (0 == len(seriesResults) ):
					url = 'http://www.mangahere.com/search.php?name=%s' % '+'.join(self.manga.split())
					if self.verbose_FLAG:
						print(url)
					source = getSourceCode(url, self.proxy)
					if source is not None:
						seriesResults = MangaHere.re_getSeries.findall(source)

			# 0 results
			except AttributeError:
				raise self.MangaNotFound('It doesn\'t exist, or cannot be resolved by autocorrect.')
			else:
				keyword = self.selectFromResults(seriesResults)
				if self.verbose_FLAG:
					print ("Keyword: %s" % keyword)
				url = 'http://www.mangahere.com/manga/%s/' % keyword
				if self.verbose_FLAG:
					print(url)
				source = getSourceCode(url, self.proxy)

		else:
			# The Guess worked
			keyword = self.fixFormatting( self.manga )
			if self.verbose_FLAG:
				print ("Keyword: %s" % keyword)


		# other check for manga removal if our initial guess for the name was wrong
		if('it is not available in.' in source):
			raise self.MangaNotFound('It has been removed.')

		# that's nice of them
		#url = 'http://www.mangahere.com/cache/manga/%s/chapters.js' % keyword
		#source = getSourceCode(url, self.proxy)

		# chapters is a 2-tuple
		# chapters[0] contains the chapter URL
		# chapters[1] contains the chapter title

		isChapterOnly = False

		# can't pre-compile this because relies on class name
		re_getChapters = re.compile('a.*?href="http://.*?mangahere.*?/manga/%s/(v[\d]+)/(c[\d]+(\.[\d]+)?)/[^"]*?"' % keyword)
		self.chapters = re_getChapters.findall(source)
		if not self.chapters:
			if self.verbose_FLAG:
				print ("Trying chapter only regex")
			isChapterOnly = True
			re_getChapters = re.compile('a.*?href="http://.*?mangahere.*?/manga/%s/(c[\d]+(\.[\d]+)?)/[^"]*?"' % keyword)
			self.chapters = re_getChapters.findall(source)

		#Sort chapters by volume and chapter number. Needed because next chapter isn't always accurate.
		self.chapters = sorted(self.chapters, cmp=self.chapter_compare)

		# code used to both fix URL from relative to absolute as well as verify last downloaded chapter for XML component
		lowerRange = 0

		if isChapterOnly:
			for i in range(0, len(self.chapters)):
				if self.verbose_FLAG:
					print("%s" % self.chapters[i][0])
				if (self.auto):
					if (self.lastDownloaded == self.chapters[i][0]):
						lowerRange = i + 1

				self.chapters[i] = ('http://www.mangahere.com/manga/%s/%s' % (keyword, self.chapters[i][0]), self.chapters[i][0], self.chapters[i][0])

		else:
			for i in range(0, len(self.chapters)):
				if self.verbose_FLAG:
					print("%s %s" % (self.chapters[i][0], self.chapters[i][1]))
				self.chapters[i] = ('http://www.mangahere.com/manga/%s/%s/%s' % (keyword, self.chapters[i][0], self.chapters[i][1]), self.chapters[i][0] + "." + self.chapters[i][1], self.chapters[i][1])
				if (self.auto):
					if (self.lastDownloaded == self.chapters[i][1]):
						lowerRange = i + 1

		# this might need to be len(self.chapters) + 1, I'm unsure as to whether python adds +1 to i after the loop or not
		upperRange = len(self.chapters)

		# Validate whether the last chapter is a
		if (self.verbose_FLAG):
			print(self.chapters[upperRange - 1])
			print("Validating chapter: %s" % self.chapters[upperRange - 1][0])
		source = getSourceCode(self.chapters[upperRange - 1][0], self.proxy)

		if ('not available yet' in source):
			# If the last chapter is not available remove it from the list
			del self.chapters[upperRange - 1]
			upperRange = upperRange - 1;


		# which ones do we want?
		if (not self.auto):
			for i in range(0, upperRange):
				if isChapterOnly:
					print('(%i) %s' % (i + 1, self.chapters[i][0]))
				else:
					print('(%i) %s' % (i + 1, self.chapters[i][1]))

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
