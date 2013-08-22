import re

from redux.site.noez import Noez


class MangaHere(Noez):
    class Chapter(Noez.Chapter):
        VOLUME_AND_CHAPTER_FROM_URL_REGEX = re.compile(
            'http://www.mangahere.com/manga/[^/]*/(v(?P<volume>[^/]*)/)?c(?P<chapter>[^/]*)')
        TOTAL_PAGES_FROM_SOURCE_REGEX = re.compile('var total_pages = (?P<count>[^;]*?);')

    class Page(Noez.Page):
        IMAGE_FROM_SOURCE_REGEX = re.compile('<img src="(?P<link>[^"]*.jpg)[^"]*"')

    class Series(Noez.Series):
        CHAPTER_FROM_SOURCE_REGEX = re.compile(
            '0077" href="(?P<url>[^"]*)" >.*?<span class="mr6">[^<]*?</span>(?P<title>.*?)</span>',
            re.DOTALL)
        TEMPLATE_URL = 'http://www.mangahere.com/manga/{name}/'
