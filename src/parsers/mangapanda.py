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

from parsers.base import SiteParserBase
from util import getSourceCode

#####################

class MangaPanda(SiteParserBase):

	re_getSeries = re.compile('<li><a href="([^"]*)">([^<]*)</a>')
	re_getChapters = re.compile('<a href="([^"]*)">([^<]*)</a>([^<]*)</td>')
	re_getPage = re.compile("<option value=\"([^']*?)\"[^>]*>\s*(\d*)</option>")
	re_getImage = re.compile('img id="img" .* src="([^"]*)"')
	re_getMaxPages = re.compile('</select> of (\d*)(\s)*</div>')

	def parseSite(self):
		print('Beginning MangaPanda check: %s' % self.manga)
		
		url = 'http://www.mangapanda.com/alphabetical'

		source = getSourceCode(url)
		allSeries = MangaPanda.re_getSeries.findall(source[source.find('series_col'):])

		keyword = self.selectFromResults(allSeries)

		url = 'http://www.mangapanda.com%s' % keyword
		source = getSourceCode(url)

		self.chapters = MangaPanda.re_getChapters.findall(source)
		
		lowerRange = 0
	
		for i in range(0, len(self.chapters)):
			self.chapters[i] = ('http://www.mangapanda.com%s' % self.chapters[i][0], '%s%s' % (self.chapters[i][1], self.chapters[i][2]), self.chapters[i][1])
			if (not self.auto):
				print('(%i) %s' % (i + 1, self.chapters[i][1]))
			else:
				if (self.lastDownloaded == self.chapters[i][1]):
					lowerRange = i + 1
		
		# this might need to be len(self.chapters) + 1, I'm unsure as to whether python adds +1 to i after the loop or not
		upperRange = len(self.chapters)
		self.isPrependMangaName = False				
		if (not self.auto):
			self.chapters_to_download = self.selectChapters(self.chapters)
		else:
			if (lowerRange == upperRange):
				raise self.NoUpdates
			
			for i in range (lowerRange, upperRange):
				self.chapters_to_download .append(i)
		
		self.isPrependMangaName = True
		
		return 
	
	def downloadChapter(self, downloadThread, max_pages, url, manga_chapter_prefix, current_chapter):
		pageIndex = 0
		for page in MangaPanda.re_getPage.findall(getSourceCode(url)):
			if (self.verbose_FLAG):
				print(self.chapters[current_chapter][1] + ' | ' + 'Page %s / %i' % (page[1], max_pages))

			pageUrl = 'http://www.mangapanda.com' + page[0]
			self.downloadImage(downloadThread, page[1], pageUrl, manga_chapter_prefix)
			pageIndex = pageIndex + 1
