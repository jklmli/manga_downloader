#!/usr/bin/env python

##########

import optparse
import os
import sys

##########

from MangaXmlParser import MangaXmlParser
import SiteParser

##########

VERSION = 'v0.6.8'

siteDict = {
		''  : 'MangaFox',
		'1' : 'MangaFox',
		'2' : 'OtakuWorks',
		'3' : 'MangaReader'
					}

##########

class InvalidSite(Exception):
	pass

def main():

	# for easier parsing, adds free --help and --version
	parser = optparse.OptionParser(	usage='usage: %prog [options] <manga name>', 
					version=('Manga Downloader %s' % VERSION)									)
					
	parser.set_defaults(	all_chapters_FLAG = False, 
				download_format = '.cbz', 
				download_path = '.', 
				overwrite_FLAG = False,
				auto = False													)
				
	parser.add_option(	'--all', 
				action = 'store_true', 
				dest = 'all_chapters_FLAG', 
				help = 'Download all available chapters.'											)
				
	parser.add_option(	'-d', '--directory', 
				dest = 'download_path', 
				help = 'The destination download directory.  Defaults to the directory of the script.'					)
				
	parser.add_option(	'--overwrite', 
				action = 'store_true', 
				dest = 'overwrite_FLAG', 
				help = 'Overwrites previous copies of downloaded chapters.'								)
				
	parser.add_option(	'-s','--subdirectory', 
				action = 'store_const', 
				dest = 'download_path', 
				const = 'CURRENT_DIRECTORY', 
				help = 'Creates a new subdirectory inside the directory of the script using the name of the manga.'			)
				
	parser.add_option(	'-x','--xml', 
				dest = 'xmlfile_path', 
				help = 'Parses the .xml file and downloads all chapters newer than the last chapter downloaded for the listed mangas.'	)
				
	parser.add_option(	'-z', '--zip', 
				action = 'store_const', 
				dest = 'download_format', 
				const = '.zip', 
				help = 'Downloads using .zip compression.  Omitting this option defaults to %default.'					)
	
	(options, args) = parser.parse_args()
	
	if(len(args) == 0):
		parser.error('Manga not specified.')
	
	if(len(args) > 1):
		parser.error('Possible multiple mangas specified, please select one.  (Did you forget to put quotes around a multi-word manga?)')
	
	options.manga = args[0]
	
	# Changes the working directory to the script location
	if (os.path.dirname(sys.argv[0]) != ""):
		os.chdir(os.path.dirname(sys.argv[0]))

	if options.xmlfile_path != None:
		xmlParser = MangaXmlParser(options.xmlfile_path)
		xmlParser.overwrite_FLAG = options.overwrite_FLAG
		xmlParser.downloadManga()
	else:
		print('\nWhich site?\n(1) MangaFox\n(2) OtakuWorks\n(3) MangaReader\n')
		site = raw_input()
		
		try:
			siteParser = SiteParser.SiteParserFactory.getInstance(siteDict[site])
		except KeyError:
			raise InvalidSite('Site selection invalid.')
		
		# we clean here instead of before every prepareDownload (same result, less wasted cycles)
		siteParser.cleanTmp()
		
		if (options.download_path == 'CURRENT_DIRECTORY'):
			options.download_path = ('./' + SiteParser.fixFormatting(options.manga)) 
		options.download_path = os.path.realpath(options.download_path) + os.sep
			
		if not(os.path.exists(options.download_path)):
			os.mkdir(options.download_path)
		
		siteParser.setOpts(options)
		
		siteParser.parseSite()
		
		siteParser.downloadChapters()

if __name__ == "__main__":
	main()
	

