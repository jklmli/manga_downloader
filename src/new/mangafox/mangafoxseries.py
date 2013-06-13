import re
import string

from src.new.util.util import Util
from src.new.mangafox.mangafoxchapter import MangaFoxChapter
from src.new.util.hasurl import HasUrl


class MangaFoxSeries(HasUrl):
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
        return 'http://mangafox.me/manga/%s/' % self.normalized_name

    @property
    @Util.memoize
    def chapters(self):
        chapter_regex = re.compile('a href="(http://.*?mangafox.*?/manga/%s/v[\d]+/c[\d]+)/[^"]*?" title' % self.normalized_name)

        ret = [MangaFoxChapter(self, url) for url in chapter_regex.findall(self.source)]
        ret.reverse()

        return ret