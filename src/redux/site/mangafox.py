import re

from redux.site.noez import Noez


class MangaFox(Noez):
    class Chapter(Noez.Chapter):
        VOLUME_AND_CHAPTER_FROM_URL_REGEX = re.compile(
            'http://mangafox.me/manga/[^/]*/(v(?P<volume>[^/]*)/)?c(?P<chapter>[^/]*)')
        TOTAL_PAGES_FROM_SOURCE_REGEX = re.compile('var total_pages=(?P<count>[^;]*?);')

    class Page(Noez.Page):
        IMAGE_FROM_SOURCE_REGEX = re.compile('"><img src="(?P<link>[^"]*)"')

    class Series(Noez.Series):
        CHAPTER_FROM_SOURCE_REGEX = re.compile(
            'a href="(?P<url>[^"]*)" title=.*?(title nowrap">(?P<title>[^<]*))?<\/span>', re.DOTALL)
        TEMPLATE_URL = 'http://mangafox.me/manga/{name}/'
