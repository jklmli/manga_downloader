from src.new.util.util import Util


class HasUrl(object):
    @property
    @Util.memoize
    def source(self):
        return Util.getSourceCode(self.url)
