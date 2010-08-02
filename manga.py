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
		chapter_start = int(sys.argv[index + 1])
		index += 1
	elif sys.argv[index] == '-e':
		chapter_end = int(sys.argv[index + 1])
		index += 1
	index += 1
current_chapter = chapter_start
current_page = 1
os.system('rm *.jpg')
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
			z.write(str(current_page) + '.jpg')
			i += 1
		current_page = 1
		current_chapter += 1
		os.system('rm *.jpg')
