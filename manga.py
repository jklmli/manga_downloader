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


#!/usr/bin/env python

##########

import sys
import os

from SiteParser import SiteParserFactory
from MangaXmlParser import MangaXmlParser

def DisplayVersion():
	print "Version Number: 0.6.3a\n"

def ImportConversionLibs():
		try:
			from ConvertFile import convertFile
		except ImportError:
			return False
		else:
			return True

def printHelp():
	helpOptions = [
		'-a\t\t\tDownload all of the relevant manga chapters.',
		'-d <download path>\tSet the download path.',
		'-f\t\t\tSet the download path to the "CURRENT_DIRECTORY"',
		'-n <manga name>\t\tSet the manga name',
		'-o\t\t\tScript overwrites the compressed file (.cbz/zip) \n\t\t\tif already present.',
		'-z\t\t\tSet the download_format to Zip. (Default cbz)"',
		'-x <xmlFile>\t\tReads the xmlFile and updates the corresponding mangas.',
		'-v\t\t\tDisplay the program version number',		
		'-c\t\t\tScript coverts downloaded Manga to the <Device> specific\n\t\t\tformat.',
		'-Device <DeviceName>\tSpecify the device for the conversion process.\n\t\t\t(Default: Kindle3).',
		'-convertDir\t\tSpecifies the program should convert a directory of\n\t\t\tpictures the Device Specific Format.',
	 	'-iDir <Input Path>\tPath that contains the manga to convert.',		
    	'-oDir <Output Path>\tPath to store the converted manga files.'
    	]
    
	for helpString in helpOptions:
		print helpString
	print "\n"	
	sys.exit()	
    
def printLicenseInfo():
		print "Program: Copyright (c) 2010. GPL v3 (http://www.gnu.org/licenses/gpl.html)."
		print "Icon:\tCopyright (c) 2006. GNU Free Document License v1.2 (Author:Kasuga) ."
		print "\thttp://ja.wikipedia.org/wiki/%E5%88%A9%E7%94%A8%E8%80%85:Kasuga\n"
  
def main():
	printLicenseInfo()
	
	download_path = './'
	download_format = '.cbz'
	all_chapters_FLAG = False
	overwrite_FLAG = False
	version_FLAG = False
	xmlfile_path = ''

	ConversionFlag = False
	ConvertDir = False
	displayHelp = False
	
	Device = 'Kindle 3'
	InputDir = ''
	OutputDir = ''
   
	options = {
		'-a' : 'all_chapters_FLAG = True',
		'-d' : 'download_path = sys.argv[index + 1]',
		'-f' : 'download_path = "CURRENT_DIRECTORY"',
		'-n' : 'manga = sys.argv[index + 1]',
		'-o' : 'overwrite_FLAG = True',
		'-z' : 'download_format = ".zip"',
		'-x' : 'xmlfile_path = sys.argv[index + 1]',
		'-v' : 'version_FLAG = True',
		'-h' : 'displayHelp = True',
		
		'-c' : 'ConversionFlag = True',
    	'-oDir' : 'OutputDir = sys.argv[index + 1]',
    	'-iDir' : 'InputDir = sys.argv[index + 1]',
		'-Device' : 'Device = sys.argv[index + 1]',
		'-convertDir' : 'ConvertDir = True'
				}
				
	siteDict = {
		''  : 'MangaFox',
		'1' : 'MangaFox',
		'2' : 'OtakuWorks',
		'3' : 'MangaReader'
					}
		
	for index in range(1, len(sys.argv)):
		try:
			exec(options[sys.argv[index]] )
		except KeyError:
			pass
			
	if (version_FLAG):	
		DisplayVersion()
		sys.exit()	
	
	if (displayHelp):
		printHelp()

	if ((not ImportConversionLibs())  and (ConversionFlag or ConvertDir)):
		print "\nConversion Functionality Not available.\nMust install the PIL (Python Image Library)"
		sys.exit()
	#else: 
	#	print "PIL Available"
	
	from ConvertFile import convertFile
	
	# Changes the working directory to the script location
	if (os.path.dirname(sys.argv[0]) != ""):
		os.chdir(os.path.dirname(sys.argv[0]))

	if (ConvertDir):
		convertFileObj = convertFile()
		convertFileObj.convert(InputDir, OutputDir, Device)		
		sys.exit()
	
	if xmlfile_path != "":
		xmlParser = MangaXmlParser(xmlfile_path)
		xmlParser.overwrite_FLAG = overwrite_FLAG
		xmlParser.ConversionFlag = ConversionFlag
		xmlParser.Device = Device

		xmlParser.downloadManga()
	else:
		print('\nWhich site?\n(1) MangaFox\n(2) OtakuWorks\n(3) MangaReader\n')
		site = raw_input()
	
		siteParser = SiteParserFactory.getInstance(siteDict[site])
		siteParser.overwrite_FLAG = overwrite_FLAG
		siteParser.all_chapters_FLAG = all_chapters_FLAG
		siteParser.download_format = download_format
		
		try:
			siteParser.ParseSite(manga, False, 1)
		except KeyError:
			print('Invalid selection. Now exiting...')
			sys.exit()

		if download_path == 'CURRENT_DIRECTORY':
			download_path = './' + fixFormatting(manga)
			if not(os.path.exists(download_path)):
				os.mkdir(download_path)
					
		download_path = os.path.realpath(download_path) + os.sep
	
		siteParser.downloadChapters(download_path, download_format)
		
		if (ConversionFlag):
			convertFileObj = convertFile()
			for compressedFile in siteParser.CompressedFiles:
				convertFileObj.convert(compressedFile, OutputDir, Device)	

if __name__ == "__main__":
	main()
	

