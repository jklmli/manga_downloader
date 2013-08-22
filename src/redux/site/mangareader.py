import re

from redux.site.aftv import Aftv


class MangaReader(Aftv):
    class Chapter(Aftv.Chapter):
        VOLUME_AND_CHAPTER_FROM_URL_REGEX = re.compile(
            'http://www.mangareader.net/((\d+)-(\d+)-(\d+)/)?[^/]+/(chapter-)?(?P<chapter>\d+)(\
            .html)?')
        TOTAL_PAGES_FROM_SOURCE_REGEX = re.compile('</select> of (?P<count>\d*)(\s)*</div>')

    class Page(Aftv.Page):
        IMAGE_FROM_SOURCE_REGEX = re.compile('img id="img" .*? src="(?P<link>[^"]*)"')

    class Series(Aftv.Series):
        TEMPLATE_URL = 'http://www.mangareader.net{path}'
