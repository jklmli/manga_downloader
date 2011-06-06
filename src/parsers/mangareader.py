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
from util import getSourceCode

#####################

class MangaReader(SiteParserBase):

	re_getSeries = re.compile('<li><a href="([^"]*)">([^<]*)</a>')
	re_getChapters = re.compile('<a href="([^"]*)">([^<]*)</a>([^<]*)</td>')
	re_getPage = re.compile("<option value=\"([^']*?)\"[^>]*>\s*(\d*)</option>")
	re_getImage = re.compile('img id="img" .* src="([^"]*)"')
	re_getMaxPages = re.compile('</select> of (\d*)(\s)*</div>')

	def parseSite(self):
		print('Beginning MangaReader check: %s' % self.manga)
		
		url = 'http://www.mangareader.net/alphabetical'

		source = getSourceCode(url)
		allSeries = MangaReader.re_getSeries.findall(source[source.find('series_col'):])

		keyword = self.selectFromResults(allSeries)

		url = 'http://www.mangareader.net%s' % keyword
		source = getSourceCode(url)

		self.chapters = MangaReader.re_getChapters.findall(source)
		
		lowerRange = 0
	
		for i in range(0, len(self.chapters)):
			self.chapters[i] = ('http://www.mangareader.net%s' % self.chapters[i][0], '%s%s' % (self.chapters[i][1], self.chapters[i][2]))
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
			if (lowerRange == upperRange):
				raise self.NoUpdates
			
			for i in range (lowerRange, upperRange):
				self.chapters_to_download .append(i)
		return 
	
	def downloadChapter(self, max_pages, url, manga_chapter_prefix, current_chapter):
		pageIndex = 0
		for page in MangaReader.re_getPage.findall(getSourceCode(url)):
			if (self.verbose_FLAG):
				print(self.chapters[current_chapter][1] + ' | ' + 'Page %s / %i' % (page[1], max_pages))

			pageUrl = 'http://www.mangareader.net' + page[0]
			self.downloadImage(page[1], pageUrl, manga_chapter_prefix)
			pageIndex = pageIndex + 1