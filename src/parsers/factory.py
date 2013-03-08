#!/usr/bin/env python

#####################

from parsers.mangafox import MangaFox
from parsers.mangareader import MangaReader
from parsers.otakuworks import OtakuWorks
from parsers.mangapanda import MangaPanda

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
				'[ow]'        : OtakuWorks,
				'[mp]'        : MangaPanda,
				'MangaFox'    : MangaFox,
				'MangaReader' : MangaReader,
				'OtakuWorks'  : OtakuWorks,
				'MangaPanda'  : MangaPanda

				}.get(options.site, None)

		if not ParserClass:
			raise NotImplementedError( "Site Not Supported" )

		return ParserClass(options)
