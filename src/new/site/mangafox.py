import re

from noez import Noez
from src.new.util.util import Util


@Util.post_hookable
class MangaFox(Noez):
    class Chapter(Noez.Chapter):
        URL_REGEX = re.compile('http://mangafox.me/manga/[^/]*/(v(?P<volume>[^/]*/))?c(?P<chapter>[^/]*)')
        TOTAL_PAGES_REGEX = re.compile('var total_pages=(?P<count>[^;]*?);')

    class Page(Noez.Page):
        IMAGE_REGEX = re.compile('"><img src="(?P<link>[^"]*)"')

    class Series(Noez.Series):
        CHAPTER_BASE_URL = 'a href="(?P<url>http://.*?mangafox.*?/manga/{}/[^/]*(/[^/]*)?)/[^"]*?" title'
        SITE_BASE_URL = 'http://mangafox.me/manga/{}/'
