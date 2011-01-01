#!/usr/bin/env python

####################################################################
# For more detailed commnets look at MangaFoxParser
#
# The code for this sites is similar enough to not need
# explanation, but dissimilar enough to not warrant any further OOP
####################################################################

####################

import re

#####################

from SiteParserBase import SiteParserBase
from helper import *
from ProgressBar.ThreadProgressBar import *

#####################

class AnimeaParser(SiteParserBase):

	##########
	#Animea check
	#	url = 'http://www.google.com/search?q=site:manga.animea.net+' + '+'.join(manga.split())
	#	source_code = urllib.urlopen(url).read()
	#	try:
	#		siteHome = re.compile('a href="(http://manga.animea.net/.*?.html)"').search(source_code).group(1)
	#	except AttributeError:
	#		total_chapters.append(0)
	#		keywords.append('')
	#	else:
	#		manga = re.compile('a href="http://manga.animea.net/(.*?).html"').search(source_code).group(1)
	#		url = siteHome
	#		source_code = urllib.urlopen(url).read()			
	#		total_chapters.append(int(re.compile('http://manga.animea.net/' + manga + '-chapter-(.*?).html').search(source_code).group(1)))
	#		keywords.append(manga)
	
	#	print('Finished Animea check.')
	#return (site, total_chapters)
	
	#	winningIndex = 1
	#	winningIndex = 0
	#	return (websites[0], keywords[winningIndex], misc[0])
	#	return (websites[winningIndex], keywords[winningIndex], chapters, chapter_list_array_decrypted)		
	##########

	def downloadAnimea(self, manga, chapter_start, chapter_end, download_path, download_format):
		for current_chapter in range(chapter_start, chapter_end + 1):	
			manga_chapter_prefix = manga.lower().replace('-', '_') + '_' + str(current_chapter).zfill(3)
			if (os.path.exists(download_path + manga_chapter_prefix + '.cbz') or os.path.exists(download_path + manga_chapter_prefix + '.zip')) and overwrite_FLAG == False:
				print('Chapter ' + str(current_chapter) + ' already downloaded, skipping to next chapter...')
				continue;
			url = 'http://manga.animea.net/'+ manga + '-chapter-' + str(current_chapter) + '-page-1.html'
			source_code = getSourceCode(url)
			max_pages = int(re.compile('of (.*?)</title>').search(source_code).group(1))
		
			for page in range(1, max_pages + 1):
				url = 'http://manga.animea.net/'+ manga + '-chapter-' + str(current_chapter) + '-page-' + str(page) + '.html'
				source_code = getSourceCode(url)
				img_url = re.compile('img src="(http.*?.[jp][pn]g)"').search(source_code).group(1)
				print('Chapter ' + str(current_chapter) + ' / ' + 'Page ' + str(page))
				print(img_url)
				downloadImage(img_url, os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(page).zfill(3)))

			compress(manga_chapter_prefix, download_path, max_pages, download_format)