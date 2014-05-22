#!/usr/bin/python

import re
from bs4 import BeautifulSoup

from parsers.base import SiteParserBase
from util import getSourceCode
from collections import OrderedDict

class EatManga(SiteParserBase):

    re_getChapters = re.compile('<a href="([^"]*)" title="([^"]*)">([^<]*)</a>([^<]*)</th>')
    re_getMaxPages = re.compile('</select> of (\d*)')
    re_getPage = re.compile("<option value=\"([^']*?)\"[^>]*>\s*(\d*)</option>")
    re_getImage = re.compile('img id="eatmanga_image.*" src="([^"]*)')

    def fixFormatting(self, s):
        p = re.compile( '\s+')
        s = p.sub( ' ', s )

        s = s.strip().replace(' ', '-')
        return s

    def parseSite(self):
        print('Beginning EatManga check: %s' % self.manga)
        url = 'http://eatmanga.com/Manga-Scan/%s' % self.fixFormatting( self.manga )
        if self.verbose_FLAG:
            print(url)

        source = getSourceCode(url, self.proxy)

        self.chapters = EatManga.re_getChapters.findall(source)
        self.chapters.reverse()

        if not self.chapters:
            raise self.MangaNotFound

        lowerRange = 0

        for i in range(0, len(self.chapters)):
            if 'upcoming' in self.chapters[i][0]:
                #Skip not available chapters
                del self.chapters[i]
                continue

            self.chapters[i] = ('http://eatmanga.com%s' % self.chapters[i][0], self.chapters[i][2], self.chapters[i][2])
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

        self.isPrependMangaName = True

        return

    def downloadChapter(self, downloadThread, max_pages, url, manga_chapter_prefix, current_chapter):
        pageIndex = 0
        pages = EatManga.re_getPage.findall(getSourceCode(url, self.proxy))

        #Remove duplicate pages if any and ensure order
        pages = list(OrderedDict.fromkeys(pages))

        for page in pages:
            if (self.verbose_FLAG):
                print(self.chapters[current_chapter][1] + ' | ' + 'Page %s / %i' % (page[1], max_pages))

            pageUrl = 'http://eatmanga.com%s' % page[0]
            self.downloadImage(downloadThread, page[1], pageUrl, manga_chapter_prefix)
            pageIndex = pageIndex + 1

