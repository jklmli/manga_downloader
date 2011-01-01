#!/usr/bin/env python


#####################

from MangaFoxParser import MangaFoxParser
from MangaReaderParser import MangaReaderParser
from OtakuWorksParser import OtakuWorksParser

#####################

class SiteParserFactory():
	"""
	Chooses the right subclass function to call.
	"""
	@staticmethod
	def getInstance(options):
		ParserClass = {
			'MangaFox' 	: MangaFoxParser,
			'MangaReader' 	: MangaReaderParser,
			'OtakuWorks' 	: OtakuWorksParser
			
		}.get(options.site, None)
		
		if not ParserClass:
			raise NotImplementedError( "Site Not Supported" )
		
		return ParserClass(options)