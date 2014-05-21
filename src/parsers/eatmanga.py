#!/usr/bin/python

import re
from bs4 import BeautifulSoup

from parsers.base import SiteParserBase
from util import getSourceCode

class EatManga(SiteParserBase):

    re_getChapters = re.compile('<a href="([^"]*)" title="([^"]*)">([^<]*)</a>([^<]*)</th>')

    def fixFormatting(self, s):
        p = re.compile( '\s+')
        s = p.sub( ' ', s )

        s = s.strip().replace(' ', '-')
        return s

    def parseSite(self):
        print('Beginning EatManga check: %s' % self.manga)
        url = 'http://eatmanga.com/Manga-Scan/%s/' % self.fixFormatting( self.manga )
        if self.verbose_FLAG:
            print(url)

        source = getSourceCode(url, self.proxy)

        self.chapters = EatManga.re_getChapters.findall(source)
        self.chapters[0]


    def downloadChapter(self, downloadThread, max_pages, url, manga_chapter_prefix, current_chapter):
        pass

