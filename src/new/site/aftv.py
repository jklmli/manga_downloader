import re
import urllib2

from src.new.base.image import Image
from mangasite import MangaSite


class Aftv(MangaSite):
    class Chapter(MangaSite.Chapter):
        @property
        def volume(self):
            return None

        @property
        def chapter(self):
            match = self.VOLUME_AND_CHAPTER_FROM_URL_REGEX.match(self.url)
            return match.group('chapter').lstrip('0') if match is not None else None

        @property
        def pages(self):
            total_pages = int(self.TOTAL_PAGES_FROM_SOURCE_REGEX.search(self.source).group('count'))

            if (self.url.endswith('.html')):
                page_base_url = re.sub('(\d+)-(\d+)-(\d+)', '\\1-\\2-{}', self.url)
            else:
                page_base_url = self.url + '/{}'

            return [self.series.site.Page(self, page_base_url.format(index)) for index in range(1, total_pages + 1)]

    class Page(MangaSite.Page):
        @property
        def image(self):
            return Image(self.IMAGE_FROM_SOURCE_REGEX.search(self.source).group('link'))

    class Series(MangaSite.Series):
        @property
        def normalized_name(self):
            url = self.TEMPLATE_URL.format('/actions/search/?q={}'.format(self.name.replace(' ', '+')))

            lines = urllib2.urlopen(url)
            first_result = lines.readline()

            return first_result.split('|')[-2]

        @property
        def url(self):
            return self.TEMPLATE_URL.format(self.normalized_name)

        @property
        def chapters(self):
            ret = [self.site.Chapter(self, self.TEMPLATE_URL.format(match.group('url'))) for match in self.CHAPTER_FROM_SOURCE_REGEX.finditer(self.source)]

            return ret
