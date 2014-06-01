import abc


class Command(object):
    __metaclass__ = abc.ABCMeta

    @staticmethod
    @abc.abstractmethod
    def add_parser(self):
        pass

    @staticmethod
    @abc.abstractmethod
    def action(args):
        pass
