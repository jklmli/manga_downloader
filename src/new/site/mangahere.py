import re

from noez import Noez


class MangaHere(Noez):
    class Chapter(Noez.Chapter):
        URL_REGEX = re.compile('http://mangahere.com/manga/[^/]*/(v(?P<volume>[^/]*/))?c(?P<chapter>[^/]*)')
        TOTAL_PAGES_REGEX = re.compile('var total_pages = (?P<count>[^;]*?);')

    class Page(Noez.Page):
        IMAGE_REGEX = re.compile('<img src="(?P<link>[^"]*.jpg)[^"]*"')

    class Series(Noez.Series):
        CHAPTER_BASE_URL = 'a.*?href="(?P<url>http://.*?mangahere.*?/manga/{}/[^/]*(/[^/]*)?)/"'
        SITE_BASE_URL = 'http://mangahere.com/manga/{}/'

MangaHere.post_initialize()
