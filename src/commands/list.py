from mangopi.metasite import MetaSite
from mangopi.site.mangafox import MangaFox
from mangopi.site.mangahere import MangaHere
from mangopi.site.mangapanda import MangaPanda
from mangopi.site.mangareader import MangaReader

from .command import Command


class List(Command):
    @staticmethod
    def add_parser(context):
        parser = context.add_parser('list', help='list all chapters')
        parser.add_argument('series', help='series name')
        parser.set_defaults(func=List.action)

    @staticmethod
    def action(args):
        chapters = MetaSite([MangaFox, MangaHere, MangaPanda, MangaReader]) \
            .series(args.series)\
            .chapters

        for chapter_number, meta_chapter in chapters.items():
            print("(%s) %s" % (chapter_number, meta_chapter.title))
