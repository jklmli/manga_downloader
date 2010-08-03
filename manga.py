#!/usr/bin/env python



import re
import urllib
import zipfile
import os
import sys
import shutil




1
def cleanTmp():
	if os.path.exists('mangadl_tmp'):
		shutil.rmtree('mangadl_tmp')
	os.mkdir('mangadl_tmp')

def compress(mangaChapterPrefix, current_chapter, download_path, current_page, download_format):
	print('Compressing...')
	z = zipfile.ZipFile('mangadl_tmp/' + mangaChapterPrefix + download_format, 'a')
	for page in range(1, current_page + 1):
		z.write('mangadl_tmp/' + mangaChapterPrefix + '_' + str(page).zfill(3) + '.jpg')
	if download_path != '/':
		shutil.move('mangadl_tmp/' + mangaChapterPrefix + download_format, download_path)
	cleanTmp()

def useMangaVolume(manga, chapter_start, chapter_end, download_path, download_format):
	for current_chapter in range(chapter_start, chapter_end + 1):
		mangaChapterPrefix = str(manga).replace(' ', '_') + '_' + str(current_chapter).zfill(3)
		if os.path.exists(download_path + mangaChapterPrefix + '.cbz') or os.path.exists(download_path + mangaChapterPrefix + '.zip') and overwrite == False:
			print('Chapter ' + str(current_chapter) + ' already downloaded, skipping to next chapter')
			current_chapter += 1
			continue;
		nextPage = True	
		current_page = 1
		while nextPage == True:
			print('Chapter ' + str(current_chapter) + ' / ' + 'Page ' + str(current_page))
			url = "http://www.mangavolume.com/index.php?serie=" + str(manga).lower().replace(" ", "-") + "&chapter=" + str(manga).lower().replace(" ", "-") + "-" + str(current_chapter) + "&page_nr=" + str(current_page)
			source_code = urllib.urlopen(url).read()
			img_url = re.compile('http(.*).jpg').search(source_code)
			if img_url == None:
				print('Manga not found: has been removed or spelled incorrectly.')
				sys.exit()
			else:
				img_url = img_url.group(0)
			urllib.urlretrieve(img_url, 'mangadl_tmp/' + mangaChapterPrefix + '_' + str(current_page).zfill(3) + '.jpg')
			if(source_code.find('page_nr=' + str(current_page + 1)) != -1):
				current_page += 1
				print img_url
			else:
				compress(mangaChapterPrefix, current_chapter, download_path, current_page, download_format)
				nextPage = False





download_path = '/'
download_format = '.cbz'
overwrite = False

for index in range(1, len(sys.argv)):
	if sys.argv[index] == '-d':
		download_path = sys.argv[index + 1]
		index += 1
	elif sys.argv[index] == '-e':
		chapter_end = int(sys.argv[index + 1])
		index += 1
	elif sys.argv[index] == '-n':
		manga = sys.argv[index + 1]
		index += 1
	elif sys.argv[index] == '-s':
		chapter_start = int(sys.argv[index + 1])
		index += 1
	elif sys.argv[index] == '-o':
		overwrite = True
	elif sys.argv[index] == '-z':
		download_format = '.zip'

if download_path.endswith('/') == False:
	download_path += '/'

cleanTmp()

useMangaVolume(manga, chapter_start, chapter_end, download_path, download_format)
