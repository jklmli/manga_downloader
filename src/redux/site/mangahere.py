import re

from noez import Noez


class MangaHere(Noez):
    class Chapter(Noez.Chapter):
        VOLUME_AND_CHAPTER_FROM_URL_REGEX = re.compile('http://www.mangahere.com/manga/[^/]*/(v(?P<volume>[^/]*/))?c(?P<chapter>[^/]*)')
        TOTAL_PAGES_FROM_SOURCE_REGEX = re.compile('var total_pages = (?P<count>[^;]*?);')

    class Page(Noez.Page):
        IMAGE_FROM_SOURCE_REGEX = re.compile('<img src="(?P<link>[^"]*.jpg)[^"]*"')

    class Series(Noez.Series):
        CHAPTER_FROM_SOURCE_REGEX = re.compile('a.*?href="(?P<url>[^"]*)"[^>]*>[^<]*</a>[^<]*<span class="mr6"')
        TEMPLATE_URL = 'http://www.mangahere.com/manga/{name}/'
