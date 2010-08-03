#!/usr/bin/env python

##########

import re
import urllib
import zipfile
import os
import sys
import shutil

##########

def checkValidity(chapter_start, chapter_end, total_chapters):
	if total_chapters == 0:
		print('Manga not found: it doesn\'t exist, has been removed, or is spelled incorrectly.')
		sys.exit()
	if (chapter_end > total_chapters) or (chapter_start < 0) or (chapter_end < chapter_start):
		print('Incorrect chapter start/end: most recent chapter is ' + str(total_chapters))
		sys.exit()
	
def cleanTmp():
	if os.path.exists('mangadl_tmp'):
		shutil.rmtree('mangadl_tmp')
	os.mkdir('mangadl_tmp')

def compress(manga_chapter_prefix, current_chapter, download_path, max_pages, download_format):
	print('Compressing...')
	z = zipfile.ZipFile('mangadl_tmp/' + manga_chapter_prefix + download_format, 'a')
	for page in range(1, max_pages + 1):
		z.write('mangadl_tmp/' + manga_chapter_prefix + '_' + str(page).zfill(3) + '.jpg', manga_chapter_prefix + '_' + str(page).zfill(3) + '.jpg')
	shutil.move('mangadl_tmp/' + manga_chapter_prefix + download_format, download_path)
	cleanTmp()

def pickSite(manga):
	total_chapters = []
	websites = ['MangaVolume', 'Animea']
	
	#MangaVolume check
	url = 'http://www.mangavolume.com/index.php?serie=' + str(manga).lower().replace(' ', '-') + '&chapter=' + str(manga).lower().replace(' ', '-') + '-1&page_nr=1'
	source_code = urllib.urlopen(url).read()
	try:
		total_chapters.append(int(re.compile('Total Chapters:</span>(.*?)</li>').search(source_code).group(0)[23:-5]))
	except AttributeError:
		total_chapters.append(0)
		
	#Animea check
	url = 'http://manga.animea.net/'+ str(manga).lower().replace(' ', '-') + '-chapter-1-page-1.html'
	source_code = urllib.urlopen(url).read()
	try:
		total_chapters.append(int(re.compile('<option value="-chapter-(.*?)">').search(source_code).group(0)[24:-2]))
	except AttributeError:
		total_chapters.append(0)
	
	#return (site, total_chapters)
	return (websites[total_chapters.index(max(total_chapters))], max(total_chapters))

###########

def useMangaVolume(manga, chapter_start, chapter_end, download_path, download_format):
	for current_chapter in range(chapter_start, chapter_end + 1):
		manga_chapter_prefix = str(manga).replace(' ', '_') + '_' + str(current_chapter).zfill(3)
		if (os.path.exists(download_path + manga_chapter_prefix + '.cbz') or os.path.exists(download_path + manga_chapter_prefix + '.zip')) and overwrite_FLAG == False:
			print('Chapter ' + str(current_chapter) + ' already downloaded, skipping to next chapter')
			continue;
		url = 'http://www.mangavolume.com/index.php?serie=' + str(manga).lower().replace(' ', '-') + '&chapter=' + str(manga).lower().replace(' ', '-') + '-' + str(current_chapter) + '&page_nr=' + str(1)
		source_code = urllib.urlopen(url).read()
		max_pages = int(re.compile('of <b>(.*?)</b>').search(source_code).group(0)[6:-4])
		
		img_url = re.compile('img src="http(.*?).jpg"').search(source_code).group(0)[9:-1]
		chapter_base_CODE = int(img_url[img_url.find('_') + 1 : -4]) - 1
		img_url = img_url[0:img_url.find('_')]
		
		for page in range(1, max_pages + 1):
			print('Chapter ' + str(current_chapter) + ' / ' + 'Page ' + str(page))
			print(img_url + '_' + str(chapter_base_CODE + page) + '.jpg')
			urllib.urlretrieve(img_url + '_' + str(chapter_base_CODE + page) + '.jpg', 'mangadl_tmp/' + manga_chapter_prefix + '_' + str(page).zfill(3) + '.jpg')

		compress(manga_chapter_prefix, current_chapter, download_path, max_pages, download_format)

##########

def useAnimea(manga, chapter_start, chapter_end, download_path, download_format):
	for current_chapter in range(chapter_start, chapter_end + 1):
		manga_chapter_prefix = str(manga).replace(' ', '_') + '_' + str(current_chapter).zfill(3)
		if (os.path.exists(download_path + manga_chapter_prefix + '.cbz') or os.path.exists(download_path + manga_chapter_prefix + '.zip')) and overwrite_FLAG == False:
			print('Chapter ' + str(current_chapter) + ' already downloaded, skipping to next chapter')
			continue;
		url = 'http://manga.animea.net/'+ str(manga).lower().replace(' ', '-') + '-chapter-' + str(current_chapter) + '-page-1.html'
		source_code = urllib.urlopen(url).read()
		max_pages = int(re.compile('of (.*?)</title>').search(source_code).group(0)[3:-8])
		
		for page in range(1, max_pages + 1):
			url = 'http://manga.animea.net/'+ str(manga).lower().replace(' ', '-') + '-chapter-' + str(current_chapter) + '-page-' + str(page) + '.html'
			source_code = urllib.urlopen(url).read()
			img_url = re.compile('img src="http(.*?).jpg"').search(source_code).group(0)[9:-1]
			print('Chapter ' + str(current_chapter) + ' / ' + 'Page ' + str(page))
			print(img_url)
			urllib.urlretrieve(img_url, 'mangadl_tmp/' + manga_chapter_prefix + '_' + str(page).zfill(3) + '.jpg')

		compress(manga_chapter_prefix, current_chapter, download_path, max_pages, download_format)

##########

def useMangaReader(manga, chapter_start, chapter_end, download_path, download_format):
	for current_chapter in range(chapter_start, chapter_end + 1):
		manga_chapter_prefix = str(manga).replace(' ', '_') + '_' + str(current_chapter).zfill(3)
		if (os.path.exists(download_path + manga_chapter_prefix + '.cbz') or os.path.exists(download_path + manga_chapter_prefix + '.zip')) and overwrite_FLAG == False:
			print('Chapter ' + str(current_chapter) + ' already downloaded, skipping to next chapter')
			continue;	
		noPage = False
		page = 0
		while noPage == False:
			page += 1
			img_url = 'http://img1.mangareader.net/manga/' + str(manga).lower().replace(' ', '-') + '/' + str(current_chapter) + '-' + str(page) + '.jpg'
			print('Chapter ' + str(current_chapter) + ' / ' + 'Page ' + str(page))
			print(img_url)
			urllib.urlretrieve(img_url, 'mangadl_tmp/' + manga_chapter_prefix + '_' + str(page).zfill(3) + '.jpg')
		compress(manga_chapter_prefix, current_chapter, download_path, page - 1, download_format)
		
##########

download_path = './'
download_format = '.cbz'
chapter_start = 0
chapter_end = 0
all_chapters_FLAG = False
overwrite_FLAG = False

for index in range(1, len(sys.argv)):
	options = {	'-a' : 'all_chapters_FLAG = True',
			'-d' : 'download_path = sys.argv[index + 1]',
			'-e' : 'chapter_end = int(sys.argv[index + 1])',
			'-n' : 'manga = sys.argv[index + 1]',
			'-s' : 'chapter_start = int(sys.argv[index + 1])',
			'-o' : 'overwrite_FLAG = True',
			'-z' : 'download_format = ".zip"'	}
	try:
		exec(options[sys.argv[index]] )
	except KeyError:
		pass

if download_path.endswith('/') == False and download_path.find('\\') == -1:
	download_path += '/'

if download_path.endswith('\\') == False and download_path.find('/') == -1:
	download_path += '\\'

print('Selecting optimal site for download...')
info = pickSite(manga)
site = info[0]
total_chapters = info[1]
print('Site found!\nUsing: ' + site)

if all_chapters_FLAG == True or (chapter_start == 0 and chapter_end == 0):
	chapter_start = 1
	chapter_end = total_chapters

if chapter_start == 0 and chapter_end != 0:
	chapter_start = 1
	
if chapter_start != 0 and chapter_end == 0:
	chapter_end = total_chapters


checkValidity(chapter_start, chapter_end, total_chapters)

cleanTmp()
#useMangaReader(manga, chapter_start, chapter_end, download_path, download_format)
exec( 'use' + site + '(manga, chapter_start, chapter_end, download_path, download_format)')
