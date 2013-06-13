import re

from src.new.mangafox.mangafoxpage import MangaFoxPage
from src.new.util.util import Util
from src.new.util.hasurl import HasUrl

class MangaFoxChapter(HasUrl):
    VOLUME_REGEX = re.compile('http://mangafox.me/manga/[^/]*/v([^/]*)/c[^/]*')
    CHAPTER_REGEX = re.compile('http://mangafox.me/manga/[^/]*/v[^/]*/c([^/]*)')
    TOTAL_PAGES_REGEX = re.compile('var total_pages=([^;]*?);')

    def __init__(self, series, url):
        self.series = series
        self.url = url

    @property
    @Util.memoize
    def volume(self):
        match = MangaFoxChapter.VOLUME_REGEX.findall(self.url)
        return match[0].lstrip('0') if len(match) != 0 else None

    @property
    @Util.memoize
    def chapter(self):
        match = MangaFoxChapter.CHAPTER_REGEX.findall(self.url)
        return match[0].lstrip('0') if len(match) != 0 else None

    @property
    @Util.memoize
    def pages(self):
        total_pages = int(MangaFoxChapter.TOTAL_PAGES_REGEX.findall(self.source)[0])
        return [MangaFoxPage(self, '{}/{}.html'.format(self.url, index)) for index in range(1, total_pages + 1)]

