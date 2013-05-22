#!/usr/bin/env python

#####################

from parsers.mangafox import MangaFox
from parsers.mangareader import MangaReader
from parsers.mangapanda import MangaPanda
from parsers.mangahere import MangaHere
from parsers.batoto import Batoto

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
			        '[bt]'        : Batoto,
				'MangaFox'    : MangaFox,
				'MangaReader' : MangaReader,
				'MangaPanda'  : MangaPanda,
				'MangaHere'   : MangaHere,
			        'Batoto'      : Batoto,

				}.get(options.site, None)

		if not ParserClass:
			raise NotImplementedError( "Site Not Supported" )

		return ParserClass(options)
