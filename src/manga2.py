import argparse

from redux.metasite import MetaSite
from redux.site.mangafox import MangaFox
from redux.site.mangahere import MangaHere
from redux.site.mangapanda import MangaPanda
from redux.site.mangareader import MangaReader


def main():
    parser = argparse.ArgumentParser(description='Download manga.')
    subparsers = parser.add_subparsers()
    add_list_subparser(subparsers)
    add_download_subparser(subparsers)

    args = parser.parse_args()
    args.func(args)


def add_list_subparser(subparsers):
    parser = subparsers.add_parser('list', help='list all chapters')
    parser.add_argument('series', help='series name')
    parser.set_defaults(func=itemize)


def add_download_subparser(subparsers):
    parser = subparsers.add_parser('download', help='download some chapters')
    parser.add_argument('series', help='series name')
    parser.add_argument('chapters', help='a quoted string of comma delimited numbers or ranges')
    parser.set_defaults(func=download)


def itemize(args):
    chapters = MetaSite([MangaFox, MangaHere, MangaPanda, MangaReader])\
        .series(args.series).chapters

    for chapter_number, meta_chapter in chapters.items():
        print("(%s) %s" % (chapter_number, meta_chapter.title))


def download(args):
    return


if __name__ == '__main__':
    main()