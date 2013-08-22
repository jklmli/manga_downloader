from collections import OrderedDict

from underscore import _

from redux.helper.decorators import memoize
from redux.helper.util import Util


class MetaSite(object):
    def __init__(self, modules=[], options={}):
        self.modules = modules
        self.options = options

    @memoize
    def series(self, name):
        """
        :type name: str
        :rtype: MetaSeries
        """
        return MetaSite.MetaSeries(self, name)

    class MetaSeries(object):
        def __init__(self, site, name):
            """
            :type site: MetaSite
            :type name: str
            """
            self.site = site
            self.name = name

        @property
        @memoize
        def chapters(self):
            """
            :rtype: OrderedDict of (str, MetaChapter)
            """
            all_chapters = _.flatten([
                site.series(self.name).chapters for site in self.site.modules
            ])

            chapter_map = OrderedDict(
                Util.natural_sort(
                    _.groupBy(all_chapters, lambda chapter, index: chapter.chapter).items(),
                    key=lambda t: t[0]
                )
            )

            return OrderedDict(
                (chapter, MetaSite.MetaChapter(self, chapter, choices)) for chapter, choices in
                chapter_map.items())

    class MetaChapter(object):
        def __init__(self, series, chapter, choices):
            """
            :type series: MetaSeries
            :type chapter: str
            :type choices: list of redux.site.mangasite.MangaSite.Chapter
            """
            self.series = series
            self.chapter = chapter
            self.choices = choices

        @property
        @memoize
        def title(self):
            """
            :rtype: str
            """
            return (_(self.choices).chain()
                    .map(lambda chapter, *args: chapter.title)
                    .sortBy(lambda title, *args: len(title))
                    .last().value()
            )

        @property
        @memoize
        def first_available_choice(self):
            """
            :rtype: redux.site.mangasite.MangaSite.Chapter
            """
            return _(self.choices).find(
                lambda chapter, *args: (_(chapter.pages).chain()
                                        .map(lambda page, *args: page.image)
                                        .all(lambda image, *args: image is not None).value()
                )
            )

        @property
        @memoize
        def pages(self):
            """
            :rtype: list of redux.site.mangasite.MangaSite.Page
            """
            return self.first_available_choice.pages
