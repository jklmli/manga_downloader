import re
import urllib2

from redux.helper.decorators import memoize
from mangasite import MangaSite


class Aftv(MangaSite):
    class Chapter(MangaSite.Chapter):
        @property
        def volume(self):
            return None

        @property
        def pages(self):
            if (self.url.endswith('.html')):
                page_base_url = re.sub('(\d+)-(\d+)-(\d+)', '\\1-\\2-{}', self.url)
            else:
                page_base_url = self.url + '/{}'

            return [self.series.site.Page(self, page_base_url.format(index)) for index in range(1, self.number_of_pages + 1)]

    class Series(MangaSite.Series):
        class Metadata(object):
            def __init__(self, name1, picture_link, name2, author_name, path, id):
                self.name = name1
                self.picture_link = picture_link
                self.author_name = author_name
                self.path = path
                self.id = id

        @property
        def normalized_name(self):
            return self.metadata.name

        @property
        def chapters(self):
            ret = [self.site.Chapter(self, self.TEMPLATE_URL.format(path=match.group('path'))) for match in self.CHAPTER_FROM_SOURCE_REGEX.finditer(self.source)]

            return ret

        @property
        def url(self):
            return self.TEMPLATE_URL.format(path=self.metadata.path)

        @property
        @memoize
        def metadata(self):
            url = self.TEMPLATE_URL.format(path=('/actions/search/?q={}'.format(self.name.replace(' ', '+'))))

            lines = urllib2.urlopen(url)
            first_result = lines.readline()

            return self.Metadata(*first_result.split('|'))