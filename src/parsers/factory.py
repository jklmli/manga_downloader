#!/usr/bin/env python

#####################

from mangafox import MangaFox
from mangareader import MangaReader
from otakuworks import OtakuWorks

#####################

class SiteParserFactory():
	"""
	Chooses the right subclass function to call.
	"""
	@staticmethod
	def getInstance(options):
		ParserClass = {
			'MangaFox' 		: MangaFox,
			'MangaReader' 	: MangaReader,
			'OtakuWorks' 	: OtakuWorks
			
		}.get(options.site, None)
		
		if not ParserClass:
			raise NotImplementedError( "Site Not Supported" )
		
		return ParserClass(options)