#!/usr/bin/env python

# Copyright (C) 2010  
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

##########

import optparse
import os
import sys
try:
	import socks
	NO_SOCKS = False
except ImportError:
	NO_SOCKS = True
import socket

##########

from parsers.thread import SiteParserThread
from util import fixFormatting, isImageLibAvailable
from xmlparser import MangaXmlParser
from outputManager.progressBarManager import progressBarManager
##########

VERSION = 'v0.8.8'

siteDict = {
		''  : '[mf]',
		'1' : '[mf]',
		'2' : '[mr]',
		'3' : '[mp]',
		'4' : '[mh]'
					}

##########

class InvalidSite(Exception):
	pass

def printLicenseInfo():
		print( "\nProgram: Copyright (c) 2010. GPL v3 (http://www.gnu.org/licenses/gpl.html)." )
		print( "Icon:      Copyright (c) 2006. GNU Free Document License v1.2 (Author:Kasuga)." )
		print( "           http://ja.wikipedia.org/wiki/%E5%88%A9%E7%94%A8%E8%80%85:Kasuga\n" )
		
##########
		
def main():
	printLicenseInfo()
	
	# for easier parsing, adds free --help and --version
	# optparse (v2.3-v2.7) was chosen over argparse (v2.7+) for compatibility (and relative similarity) reasons 
	# and over getopt(v?) for additional functionality
	parser = optparse.OptionParser(	usage='usage: %prog [options] <manga name>', 
					version=('Manga Downloader %s' % VERSION)									)
					
	parser.set_defaults(	
				all_chapters_FLAG = False,
				auto = False,
				conversion_FLAG = False,
				convert_Directory = False,
				device = 'Kindle 3',
				downloadFormat = '.cbz', 
				downloadPath = 'DEFAULT_VALUE', 
				inputDir = None,
				outputDir = 'DEFAULT_VALUE',
				overwrite_FLAG = False,
				verbose_FLAG = False,
				timeLogging_FLAG = False,
				maxChapterThreads = 3,
				useShortName = False,
				spaceToken = '.',
				proxy = None	
				)
				
	parser.add_option(	'--all', 
				action = 'store_true', 
				dest = 'all_chapters_FLAG', 
				help = 'Download all available chapters.'										)
				
	parser.add_option(	'-d', '--directory', 
				dest = 'downloadPath', 
				help = 'The destination download directory.  Defaults to the directory of the script.'					)
				
	parser.add_option(	'--overwrite', 
				action = 'store_true', 
				dest = 'overwrite_FLAG', 
				help = 'Overwrites previous copies of downloaded chapters.'								)

	parser.add_option(	'--verbose', 
				action = 'store_true', 
				dest = 'verbose_FLAG', 
				help = 'Verbose Output.'								)
				
	parser.add_option(	'-x','--xml', 
				dest = 'xmlfile_path', 
				help = 'Parses the .xml file and downloads all chapters newer than the last chapter downloaded for the listed mangas.'	)
	
	parser.add_option(	'-c', '--convertFiles', 
				action = 'store_true', 
				dest = 'conversion_FLAG', 
				help = 'Converts downloaded files to a Format/Size acceptable to the device specified by the --device parameter.'				)

	parser.add_option( 	'--device', 
				dest = 'device', 
				help = 'Specifies the conversion device. Omitting this option default to %default.'				)
	
	parser.add_option( 	'--convertDirectory', 
				action = 'store_true', 
				dest = 'convert_Directory', 
				help = 'Converts the image files stored in the directory specified by --inputDirectory. Stores the converted images in the directory specified by --outputDirectory'	)
	
	parser.add_option( 	'--inputDirectory', 
				dest = 'inputDir', 
				help = 'The directory containing the images to convert when --convertDirectory is specified.'					)
	
	parser.add_option( 	'--outputDirectory', 
				dest = 'outputDir', 
				help = 'The directory to store the images when --convertDirectory is specified.'					)				
											
	parser.add_option(	'-z', '--zip', 
				action = 'store_const', 
				dest = 'downloadFormat', 
				const = '.zip', 
				help = 'Downloads using .zip compression.  Omitting this option defaults to %default.'					)
	
	parser.add_option(	'-t', '--threads', 
				dest = 'maxChapterThreads', 
				help = 'Limits the number of chapter threads to the value specified.'					)
	
	parser.add_option(	'--timeLogging', 
				action = 'store_true', 
				dest = 'timeLogging_FLAG', 
				help = 'Output time logging.'					)	

	parser.add_option(	'--useShortName', 
				action = 'store_true', 
				dest = 'useShortName_FLAG', 
				help = 'To support devices that limit the size of the filename, this parameter uses a short name'				)				

	parser.add_option( 	'--spaceToken', 
				dest = 'spaceToken', 
				help = 'Specifies the character used to replace spaces in the manga name.'				)				
	
	parser.add_option( 	'--proxy', 
				dest = 'proxy', 
				help = 'Specifies the proxy.'				)				
					
	(options, args) = parser.parse_args()
	
	try:
		options.maxChapterThreads = int(options.maxChapterThreads)
	except:
		options.maxChapterThreads = 2
	
	if (options.maxChapterThreads <= 0):
		options.maxChapterThreads = 2;
		
	if(len(args) == 0 and ( not (options.convert_Directory or options.xmlfile_path != None) )):
		parser.error('Manga not specified.')
	
	#if(len(args) > 1):
	#	parser.error('Possible multiple mangas specified, please select one.  (Did you forget to put quotes around a multi-word manga?)')
	
	SetDownloadPathToName_Flag = False
	SetOutputPathToDefault_Flag = False
	if(len(args) > 0):
		
		# Default Directory is the ./MangaName
		if (options.downloadPath == 'DEFAULT_VALUE'):
			SetDownloadPathToName_Flag = True

			
		# Default outputDir is the ./MangaName
		if (options.outputDir == 'DEFAULT_VALUE'):
			SetOutputPathToDefault_Flag = True


	PILAvailable = isImageLibAvailable()
	# Check if PIL Library is available if either of convert Flags are set 
	if ((not PILAvailable)  and (options.convert_Directory or options.conversion_FLAG)):
		print ("\nConversion Functionality Not available.\nMust install the PIL (Python Image Library)")
		sys.exit()
	else:
		if (PILAvailable):
			from ConvertPackage.ConvertFile import convertFile
	
	if (options.convert_Directory):	
		options.inputDir = os.path.abspath(options.inputDir)
	
	# Changes the working directory to the script location
	if (os.path.dirname(sys.argv[0]) != ""):
		os.chdir(os.path.dirname(sys.argv[0]))

	options.outputMgr = progressBarManager()
	options.outputMgr.start()
	try:
		if (options.convert_Directory):
			if ( options.outputDir == 'DEFAULT_VALUE' ):
				options.outputDir = '.'
			print("Converting Files: %s" % options.inputDir)	
			convertFile.convert(options.outputMgr, options.inputDir, options.outputDir, options.device, options.verbose_FLAG)
	
		elif options.xmlfile_path != None:
			xmlParser = MangaXmlParser(options)
			xmlParser.downloadManga()
		else:
			threadPool = []
			for manga in args:
				print( manga )
				options.manga = manga
			
				if SetDownloadPathToName_Flag:		
					options.downloadPath = ('./' + fixFormatting(options.manga, options.spaceToken))
			
				if SetOutputPathToDefault_Flag:	
					options.outputDir = options.downloadPath 
			
				options.downloadPath = os.path.realpath(options.downloadPath) + os.sep
				
			
				# site selection
				print('\nWhich site?\n(1) MangaFox\n(2) MangaReader\n(3) MangaPanda\n(4) MangaHere\n')
	
				# Python3 fix - removal of raw_input()
				try:
					site = raw_input()
				except NameError:
					site = input()

				try:
					options.site = siteDict[site]
				except KeyError:
					raise InvalidSite('Site selection invalid.')	
			
				threadPool.append(SiteParserThread(options, None, None))
			
			for thread in threadPool: 
				thread.start()
				thread.join()
	finally:
		# Must always stop the manager
		options.outputMgr.stop()
		
		
if __name__ == '__main__':
	main()
