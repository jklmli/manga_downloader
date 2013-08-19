import abc
from abc import ABCMeta

from redux.helper.decorators import memoize
from redux.helper.image import Image
from redux.helper.traits.hasurl import HasUrl


class MangaSite(object):
    __metaclass__ = ABCMeta

    @classmethod
    def series(cls, name):
        return cls.Series(cls, name)

    class Chapter(HasUrl):
        __metaclass__ = ABCMeta

        VOLUME_AND_CHAPTER_FROM_URL_REGEX = NotImplemented
        TOTAL_PAGES_FROM_SOURCE_REGEX = NotImplemented
        CHAPTER_TITLE_FROM_SOURCE_REGEX = NotImplemented

        def __init__(self, series, title, url):
            """
            :type series: Series
            :type title: str
            :type url: str
            """
            self.series = series
            self.title = title
            self.url = url

        @property
        @memoize
        def volume(self):
            """
            :rtype: str or None
            """
            match = self.VOLUME_AND_CHAPTER_FROM_URL_REGEX.match(self.url)
            return match.group('volume').lstrip('0') if (match is not None and match.group('volume') is not None) else None

        @property
        @memoize
        def chapter(self):
            """
            :rtype: str
            """
            match = self.VOLUME_AND_CHAPTER_FROM_URL_REGEX.match(self.url)
            return match.group('chapter').lstrip('0') if (match is not None and match.group('chapter') is not None) else None

        @property
        @memoize
        def number_of_pages(self):
            """
            :rtype: int
            """
            return int(self.TOTAL_PAGES_FROM_SOURCE_REGEX.search(self.source).group('count'))

        @abc.abstractproperty
        @memoize
        def pages(self):
            """
            :rtype: list of Page
            """
            pass

    class Page(HasUrl):
        __metaclass__ = ABCMeta

        IMAGE_FROM_SOURCE_REGEX = NotImplemented

        def __init__(self, chapter, url):
            """
            :type chapter: Chapter
            :type url: str
            """
            self.chapter = chapter
            self.url = url

        @property
        @memoize
        def image(self):
            """
            :rtype: Image
            """
            return Image(self.IMAGE_FROM_SOURCE_REGEX.search(self.source).group('link'))

    class Series(HasUrl):
        __metaclass__ = ABCMeta

        CHAPTER_FROM_SOURCE_REGEX = NotImplemented
        TEMPLATE_URL = NotImplemented

        def __init__(self, site, name):
            """
            :type site: MangaSite
            :type name: str
            """
            self.site = site
            self.name = name

        @property
        @memoize
        def url(self):
            """
            :rtype: str
            """
            return self.TEMPLATE_URL.format(name=self.normalized_name)

        @abc.abstractproperty
        @memoize
        def normalized_name(self):
            """
            :rtype: str
            """
            pass

        @abc.abstractproperty
        @memoize
        def chapters(self):
            """
            :rtype: list of Chapter
            """
            pass
