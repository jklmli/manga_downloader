from src.new.util.util import Util


class HasUrl:
    @property
    @Util.memoize
    def source(self):
        return Util.getSourceCode(self.url)
