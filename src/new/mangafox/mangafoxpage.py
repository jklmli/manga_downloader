import re

from src.new.util.util import Util
from src.new.base.image import Image
from src.new.util.hasurl import HasUrl


class MangaFoxPage(HasUrl):
    IMAGE_REGEX = re.compile('"><img src="([^"]*)"')

    def __init__(self, chapter, url):
        self.chapter = chapter
        self.url = url

    @property
    @Util.memoize
    def image(self):
        return Image(MangaFoxPage.IMAGE_REGEX.findall(self.source)[0])
