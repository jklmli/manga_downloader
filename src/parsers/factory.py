#!/usr/bin/env python

#####################

from parsers.mangafox import MangaFox
from parsers.mangareader import MangaReader
from parsers.otakuworks import OtakuWorks

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
			'MangaFox'    : MangaFox,
			'MangaReader' : MangaReader,
			'OtakuWorks'  : OtakuWorks
			
		}.get(options.site, None)
		
		if not ParserClass:
			raise NotImplementedError( "Site Not Supported" )
		
		return ParserClass(options)
