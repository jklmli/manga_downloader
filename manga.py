#!/usr/bin/env python

##########

import sys
import os

from SiteParser import SiteParserFactory
from MangaXmlParser import MangaXmlParser

def main():
	download_path = './'
	download_format = '.cbz'
	all_chapters_FLAG = False
	overwrite_FLAG = False
	xmlfile_path = ''


	options = {
		'-a' : 'all_chapters_FLAG = True',
		'-d' : 'download_path = sys.argv[index + 1]',
		'-f' : 'download_path = "CURRENT_DIRECTORY"',
		'-n' : 'manga = sys.argv[index + 1]',
		'-o' : 'overwrite_FLAG = True',
		'-z' : 'download_format = ".zip"',
		'-x' : 'xmlfile_path = sys.argv[index + 1]'
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

	# Changes the working directory to the script location
	if (os.path.dirname(sys.argv[0]) != ""):
		os.chdir(os.path.dirname(sys.argv[0]))

	if xmlfile_path != "":
		xmlParser = MangaXmlParser(xmlfile_path)
		xmlParser.overwrite_FLAG = overwrite_FLAG
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
			download_path = './' + siteParser.fixFormatting(manga)
			if not(os.path.exists(download_path)):
				os.mkdir(download_path)
					
		download_path = os.path.realpath(download_path) + os.sep
	
		siteParser.downloadChapters(download_path, download_format)

if __name__ == "__main__":
	main()
	

