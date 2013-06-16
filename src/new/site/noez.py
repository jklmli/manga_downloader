import re
import string

from src.new.base.image import Image
from mangasite import MangaSite


class Noez(MangaSite):
    class Chapter(MangaSite.Chapter):
        @property
        def volume(self):
            match = self.VOLUME_AND_CHAPTER_FROM_URL_REGEX.match(self.url)
            return match.group('volume').lstrip('0') if (match is not None and match.group('volume') is not None) else None

        @property
        def chapter(self):
            match = self.VOLUME_AND_CHAPTER_FROM_URL_REGEX.match(self.url)
            return match.group('chapter').lstrip('0') if (match is not None and match.group('chapter') is not None) else None

        @property
        def pages(self):
            total_pages = int(self.TOTAL_PAGES_FROM_SOURCE_REGEX.search(self.source).group('count'))
            return [self.series.site.Page(self, '{}/{}.html'.format(self.url, index)) for index in range(1, total_pages + 1)]

    class Page(MangaSite.Page):
        @property
        def image(self):
            return Image(self.IMAGE_FROM_SOURCE_REGEX.search(self.source).group('link'))

    class Series(MangaSite.Series):
        @property
        def normalized_name(self):
            def fixFormatting(s):
                for i in string.punctuation:
                    s = s.replace(i, " ")
                p = re.compile('\s+')
                s = p.sub(' ', s)
                s = s.lower().strip().replace(' ', '_')
                return s

            return fixFormatting(self.name)

        @property
        def url(self):
            return self.TEMPLATE_URL.format(name=self.normalized_name)

        @property
        def chapters(self):
            ret = [self.site.Chapter(self, match.group('url')) for match in self.CHAPTER_FROM_SOURCE_REGEX.finditer(self.source)]
            ret.reverse()

            return ret
