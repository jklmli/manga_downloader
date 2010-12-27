#!/usr/bin/env python

##########

import optparse
import os
import sys

##########

from MangaXmlParser import MangaXmlParser
import helper
import SiteParser

##########

VERSION = 'v0.7.1'

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
	# optparse (v2.3-v2.7) was chosen over argparse (v2.7+) for compatibility (and relative similarity) reasons and over getopt(v?) for additional functionality
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
	
	# subdirectory option flagged
	if (options.download_path == 'CURRENT_DIRECTORY'):
		options.download_path = ('./' + SiteParser.fixFormatting(options.manga))
		
	options.download_path = os.path.realpath(options.download_path) + os.sep
	
	# Changes the working directory to the script location
	if (os.path.dirname(sys.argv[0]) != ""):
		os.chdir(os.path.dirname(sys.argv[0]))

	# xmlfile option flagged
	if options.xmlfile_path != None:
		xmlParser = MangaXmlParser(options)
	else:
		# site selection
		print('\nWhich site?\n(1) MangaFox\n(2) OtakuWorks\n(3) MangaReader\n')
		site = raw_input()
		
		try:
			options.site = siteDict[site]
			siteParser = SiteParser.SiteParserFactory.getInstance(options)
		except KeyError:
			raise InvalidSite('Site selection invalid.')
		
		# pass over command-line args
#		siteParser.setOpts(options)
		
		# basic processing
		siteParser.parseSite()
		
		# download
		siteParser.downloadChapters()

if __name__ == "__main__":
	main()
	

