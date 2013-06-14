import re
import string

from src.new.util.util import Util
from src.new.base.image import Image
from src.new.util.hasurl import HasUrl


@Util.post_hookable
class Noez:
    @classmethod
    def series(cls, name):
        return cls.Series(name)

    @classmethod
    def post_hook(cls):
        cls.Chapter.SITE = cls.Series.SITE = cls

    class Chapter(HasUrl):
        URL_REGEX = NotImplemented
        TOTAL_PAGES_REGEX = NotImplemented
        SITE = None

        def __init__(self, series, url):
            self.series = series
            self.url = url

        @property
        @Util.memoize
        def volume(self):
            match = self.URL_REGEX.match(self.url)
            return match.group('volume').lstrip('0') if match is not None else None

        @property
        @Util.memoize
        def chapter(self):
            match = self.URL_REGEX.match(self.url)
            return match.group('chapter').lstrip('0') if match is not None else None

        @property
        @Util.memoize
        def pages(self):
            total_pages = int(self.TOTAL_PAGES_REGEX.search(self.source).group('count'))
            return [self.SITE.Page(self, '{}/{}.html'.format(self.url, index)) for index in range(1, total_pages + 1)]

    class Page(HasUrl):
        IMAGE_REGEX = NotImplemented

        def __init__(self, chapter, url):
            self.chapter = chapter
            self.url = url

        @property
        @Util.memoize
        def image(self):
            return Image(self.IMAGE_REGEX.search(self.source).group('link'))

    class Series(HasUrl):
        SITE_BASE_URL = NotImplemented
        CHAPTER_BASE_URL = NotImplemented
        SITE = None

        def __init__(self, name):
            self.name = name

        @property
        @Util.memoize
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
        @Util.memoize
        def url(self):
            return self.SITE_BASE_URL.format(self.normalized_name)

        @property
        @Util.memoize
        def chapters(self):
            chapter_regex = re.compile(self.CHAPTER_BASE_URL.format(self.normalized_name))

            ret = [self.SITE.Chapter(self, match.group('url')) for match in chapter_regex.finditer(self.source)]
            ret.reverse()

            return ret
