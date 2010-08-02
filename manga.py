#!/usr/bin/env python

import re
import urllib
import zipfile
import os
import sys

index = 1

while index < len(sys.argv):
	if sys.argv[index] == '-n':
		manga = sys.argv[index + 1]
		index += 1
	elif sys.argv[index] == '-s':
		current_chapter = int(sys.argv[index + 1])
		index += 1
	elif sys.argv[index] == '-e':
		chapter_end = int(sys.argv[index + 1])
		index += 1
	elif sys.argv[index] == '-d':
		download_path = sys.argv[index + 1]
		index += 1
	index += 1

current_page = 1
download_path = '/'

os.system('rm *.jpg')

def useMangaVolume(manga, current_chapter, chapter_end, download_path, current_page):
	while (current_chapter <= chapter_end):
		print('Chapter ' + str(current_chapter) + ' / ' + 'Page ' + str(current_page))
		url = "http://www.mangavolume.com/index.php?serie=" + str(manga).lower().replace(" ", "-") + "&chapter=" + str(manga).lower().replace(" ", "-") + "-" + str(current_chapter) + "&page_nr=" + str(current_page)
		source_code = urllib.urlopen(url).read()
		img_url = re.compile('http(.*).jpg').search(source_code).group(0)
		urllib.urlretrieve(img_url, str(current_page) + '.jpg')
		if(source_code.find('page_nr=' + str(current_page + 1)) != -1):
			current_page += 1
			print img_url
		else:
			print('Compressing...')
			i = 1
			z = zipfile.ZipFile(str(manga).replace(' ', '_') + '_' + str(current_chapter) + '.cbz', 'a')
			while i <= current_page:
				z.write(str(i) + '.jpg')
				i += 1
			if download_path != '/':
				os.system('mv ' + str(manga).replace(' ', '_') + '_' + str(current_chapter) + '.cbz ' + download_path)
			current_page = 1
			current_chapter += 1
			os.system('rm *.jpg')

useMangaVolume(manga, current_chapter, chapter_end, download_path, current_page)
