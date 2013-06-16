from redux.helper.decorators import memoize
from redux.helper.util import Util


class HasUrl(object):
    @property
    @memoize
    def source(self):
        return Util.getSourceCode(self.url)
