#!/usr/bin/env python

#####################

from parsers.mangafox import MangaFox
from parsers.mangareader import MangaReader
from parsers.mangapanda import MangaPanda
from parsers.mangahere import MangaHere
from parsers.eatmanga import EatManga
try:
	from bs4 import BeautifulSoup
	from parsers.batoto import Batoto
except ImportError:
	Batoto = None

#####################

class SiteParserFactory():
	"""
	Chooses the right subclass function to call.
	"""
	@staticmethod
	def getInstance(options):
		ParserClass = {
				'[mf]'        : MangaFox,
				'[mr]'        : MangaReader,
				'[mp]'        : MangaPanda,
				'[mh]'        : MangaHere,
				'[em]'        : EatManga,
				'[bt]'        : Batoto,
				'MangaFox'    : MangaFox,
				'MangaReader' : MangaReader,
				'MangaPanda'  : MangaPanda,
				'MangaHere'   : MangaHere,
				'EatManga'    : EatManga,
				'Batoto'      : Batoto,

				}.get(options.site, None)

		if not ParserClass:
			raise NotImplementedError( "Site Not Supported" )

		return ParserClass(options)
