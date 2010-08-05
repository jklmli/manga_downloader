#!/usr/bin/env python

##########

import re
import urllib
import zipfile
import os
import sys
import shutil
import imghdr

##########

def checkValidity(chapter_start, chapter_end, total_chapters):
	if total_chapters == 0:
		print('Manga not found: it doesn\'t exist, has been removed, or is spelled incorrectly.')
		sys.exit()
	if (chapter_end > total_chapters) or (chapter_start < 0) or (chapter_end < chapter_start):
		print('Incorrect chapter start/end - most recent chapter is ' + str(total_chapters))
		sys.exit()
	
def cleanTmp():
	if os.path.exists('mangadl_tmp'):
		shutil.rmtree('mangadl_tmp')
	os.mkdir('mangadl_tmp')

def compress(manga_chapter_prefix, current_chapter, download_path, max_pages, download_format):
	print('Compressing...')
	z = zipfile.ZipFile( os.path.join('mangadl_tmp', manga_chapter_prefix + download_format), 'a')
	for page in range(1, max_pages + 1):
		z.write( os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(page).zfill(3) + '.jpg'), manga_chapter_prefix + '_' + str(page).zfill(3) + '.jpg')
	z.close()
	shutil.move( os.path.join('mangadl_tmp', manga_chapter_prefix + download_format), download_path)
	cleanTmp()

def pickSite(manga):
	total_chapters = []
	keywords = []
	websites = ['MangaVolume', 'CloudManga', 'Animea']
	
	#MangaVolume check
	url = 'http://www.google.com/search?q=site:mangavolume.com+' + '+'.join(manga.split())
	source_code = urllib.urlopen(url).read()
	try:
		siteHome = re.compile('mangavolume.com/.*?/mangas-(.*?)/').search(source_code).group(0)
	except:
		total_chapters.append(0)
		keywords.append('')
	else:	
		siteKeyword = re.compile('mangavolume.com/.*?/mangas-(.*?)/').search(source_code).group(1)
		url = 'http://www.' + siteHome
		source_code = urllib.urlopen(url).read()
		try:
			intermediate = re.compile('>(?!<a href)(.*?)</a> </td>').search(source_code).group(1)
#			print(intermediate)
			total_chapters.append(int(intermediate[len(siteKeyword): ]))
#			print(int(intermediate[len(siteKeyword): ]))
		except AttributeError:
			total_chapters.append(0)
		keywords.append(siteKeyword)
	
	print('Finished MangaVolume check.')

	#CloudManga check
	url = 'http://www.google.com/search?q=site:cloudmanga.com+' + '+'.join(manga.split())
	source_code = urllib.urlopen(url).read()
#	print('done downloading google search code')
	try:
		siteKeyword = re.compile('cloudmanga.com/(.*?)/').search(source_code).group(1)
#		print('done finding keyword')
	except AttributeError:
		total_chapters.append(0)
		keywords.append('')
	else:
		url = 'http://www.cloudmanga.com/' + siteKeyword
		source_code = urllib.urlopen(url).read()
#		print('done downloading cloudmanga code')
		total_chapters.append(int(re.compile(siteKeyword + '/(.*?)/\'"').search(source_code).group(1)))
#		print(int(re.compile(siteKeyword + '/(.*?)/\'"').search(source_code).group(1)))
		keywords.append(siteKeyword)
	
	print('Finished CloudManga check.')
	
	#MangaReader check
#	url = 'http://www.bing.com/search?q=site:mangareader.net+' + str(manga).lower().replace(' ', '-')
#	source_code = urllib.urlopen(url).read()
#	try:
#		prefix_Number = int(re.compile('net/.{1,4}?/').search(source_code).group(0)[4:-1])
#	except AttributeError:
#		total_chapters.append(0)
#	else:
#		url = 'http://www.mangareader.net/' + str(prefix_Number) + '/' + str(manga).lower().replace(' ', '-') + '.html'
#		source_code = urllib.urlopen(url).read()
#		total_chapters.append(int(re.compile('Chapter ' + '(.{1,4}?)</a> :' ).search(source_code).group(0)[8:-6]))
	
	#Animea check
#	url = 'http://www.google.com/search?q=site:manga.animea.net+' + '+'.join(manga.split())
#	source_code = urllib.urlopen(url).read()
#	try:
#		siteHome = re.compile('a href="(http://manga.animea.net/.*?.html)"').search(source_code).group(1)
#	except AttributeError:
#		total_chapters.append(0)
#		keywords.append('')
#	else:
#		siteKeyword = re.compile('a href="http://manga.animea.net/(.*?).html"').search(source_code).group(1)
#		url = siteHome
#		source_code = urllib.urlopen(url).read()	
#		total_chapters.append(int(re.compile('http://manga.animea.net/' + siteKeyword + '-chapter-(.*?).html').search(source_code).group(1)))
#		keywords.append(siteKeyword)
	
#	print('Finished Animea check.')
	#return (site, total_chapters)
	
	winningIndex = total_chapters.index(max(total_chapters))
	return (websites[winningIndex], max(total_chapters), keywords[winningIndex])
	
	
##########

def useAnimea(manga, chapter_start, chapter_end, download_path, download_format, siteKeyword):
	for current_chapter in range(chapter_start, chapter_end + 1):
		manga_chapter_prefix = siteKeyword + '_' + str(current_chapter).zfill(3)
		if (os.path.exists(download_path + manga_chapter_prefix + '.cbz') or os.path.exists(download_path + manga_chapter_prefix + '.zip')) and overwrite_FLAG == False:
			print('Chapter ' + str(current_chapter) + ' already downloaded, skipping to next chapter...')
			continue;
		url = 'http://manga.animea.net/'+ siteKeyword + '-chapter-' + str(current_chapter) + '-page-1.html'
		source_code = urllib.urlopen(url).read()
		max_pages = int(re.compile('of (.*?)</title>').search(source_code).group(1))
		
		for page in range(1, max_pages + 1):
			url = 'http://manga.animea.net/'+ siteKeyword + '-chapter-' + str(current_chapter) + '-page-' + str(page) + '.html'
			source_code = urllib.urlopen(url).read()
			img_url = re.compile('img src="(http.*?.[jp][pn]g)"').search(source_code).group(1)
			print('Chapter ' + str(current_chapter) + ' / ' + 'Page ' + str(page))
			print(img_url)
			urllib.urlretrieve(img_url, os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(page).zfill(3) + '.jpg'))

		compress(manga_chapter_prefix, current_chapter, download_path, max_pages, download_format)
		
##########

def useCloudManga(manga, chapter_start, chapter_end, download_path, download_format, siteKeyword):
	manga_prefix = 'http://www.cloudmanga.com/' + siteKeyword + '/'
	
	url = manga_prefix + str(chapter_start) + '/'
	source_code = urllib.urlopen(url).read()
#	num_Pages = re.compile('option value').findall(source_code[source_code.find("Discussion"):])
#	print(len(num_Pages))
	img_url = re.compile('src="(http://.*?/.*?/.*?/)(.*?).jpg"').search(source_code)
	img_url_prefix = img_url.group(1)
	current_chapter_img_index = int(img_url.group(2))
	
	for current_chapter in range(chapter_start, chapter_end + 1):
		manga_chapter_prefix = str(manga).replace(' ', '_') + '_' + str(current_chapter).zfill(3)
		if (os.path.exists(download_path + manga_chapter_prefix + '.cbz') or os.path.exists(download_path + manga_chapter_prefix + '.zip')) and overwrite_FLAG == False:
			print('Chapter ' + str(current_chapter) + ' already downloaded, skipping to next chapter...')
			url = manga_prefix + str(current_chapter + 1) + '/'
			source_code = urllib.urlopen(url).read()
			current_chapter_img_index = int(re.compile('src="(http://.*?/.*?/.*?/)(.*?).jpg"').search(source_code).group(2))
			continue;
		if (current_chapter != total_chapters):	
			url = manga_prefix + str(current_chapter + 1) + '/'
			source_code = urllib.urlopen(url).read()
			next_chapter_img_index = int(re.compile('src="(http://.*?/.*?/.*?/)(.*?).jpg"').search(source_code).group(2))
			max_pages = next_chapter_img_index - current_chapter_img_index
					
			for page in range(1, max_pages + 1):
				print('Chapter ' + str(current_chapter) + ' / ' + 'Page ' + str(page))
				print(img_url_prefix + str(current_chapter_img_index + page - 1) + '.jpg')
				urllib.urlretrieve(img_url_prefix + str(current_chapter_img_index + page - 1) + '.jpg', os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(page).zfill(3) + '.jpg'))
		else:
			page = 0
			nextPage = True
			while nextPage == True:
				page +=1
				print('Chapter ' + str(current_chapter) + ' / ' + 'Page ' + str(page))
				print(img_url_prefix + str(current_chapter_img_index + page - 1) + '.jpg')				
				urllib.urlretrieve(img_url_prefix + str(current_chapter_img_index + page - 1) + '.jpg', os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(page).zfill(3) + '.jpg'))
				if imghdr.what(os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(page).zfill(3) + '.jpg')) == None:
					nextPage = False
			max_pages = page - 1
		compress(manga_chapter_prefix, current_chapter, download_path, max_pages, download_format)
		current_chapter_img_index = next_chapter_img_index

##########

def useMangaReader(manga, chapter_start, chapter_end, download_path, download_format, siteKeyword):
	
	for current_chapter in range(chapter_start, chapter_end + 1):
		manga_chapter_prefix = str(manga).replace(' ', '_') + '_' + str(current_chapter).zfill(3)
		if (os.path.exists(download_path + manga_chapter_prefix + '.cbz') or os.path.exists(download_path + manga_chapter_prefix + '.zip')) and overwrite_FLAG == False:
			print('Chapter ' + str(current_chapter) + ' already downloaded, skipping to next chapter...')
			continue;	
		nextPage = True
		page = 0
		while nextPage == True:
			page += 1
			img_url = 'http://img1.mangareader.net/manga/' + str(manga).title() + '/' + str(current_chapter) + '-' + str(page) + '.jpg'
			print('Chapter ' + str(current_chapter) + ' / ' + 'Page ' + str(page))
			print(img_url)
			urllib.urlretrieve(img_url, os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(page).zfill(3) + '.jpg'))
			if imghdr.what(os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(page).zfill(3) + '.jpg')) == None:
				nextPage = False
		compress(manga_chapter_prefix, current_chapter, download_path, page - 1, download_format)

###########

def useMangaVolume(manga, chapter_start, chapter_end, download_path, download_format, siteKeyword):
	for current_chapter in range(chapter_start, chapter_end + 1):
		manga_chapter_prefix = str(siteKeyword).replace('-', '_') + '_' + str(current_chapter).zfill(3)
		if (os.path.exists(download_path + manga_chapter_prefix + '.cbz') or os.path.exists(download_path + manga_chapter_prefix + '.zip')) and overwrite_FLAG == False:
			print('Chapter ' + str(current_chapter) + ' already downloaded, skipping to next chapter...')
			continue;
		url = 'http://www.mangavolume.com/index.php?serie=' + siteKeyword + '&chapter=' + siteKeyword + '-' + str(current_chapter) + '&page_nr=' + str(1)
		source_code = urllib.urlopen(url).read()
		max_pages = int(re.compile('of <b>(.*?)</b>').search(source_code).group(1))
		
		img_url = re.compile('img src="(http.*?.jpg)"').search(source_code).group(1)
		current_chapter_img_index = int(re.compile('http.*?_(.*?).jpg').search(img_url).group(1))
		img_url_prefix = img_url[0:img_url.find('_') + 1]
		
		for page in range(1, max_pages + 1):
			print('Chapter ' + str(current_chapter) + ' / ' + 'Page ' + str(page))
			print(img_url_prefix + str(current_chapter_img_index + page - 1) + '.jpg')
			urllib.urlretrieve(img_url_prefix + str(current_chapter_img_index + page - 1) + '.jpg', os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(page).zfill(3) + '.jpg'))

		compress(manga_chapter_prefix, current_chapter, download_path, max_pages, download_format)
		
##########

download_path = './'
download_format = '.cbz'
chapter_start = 0
chapter_end = 0
all_chapters_FLAG = False
overwrite_FLAG = False

class AppURLopener(urllib.FancyURLopener):
	version = 'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.14 Safari/534.3'

urllib._urlopener = AppURLopener()

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
siteKeyword = info[2]
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

#useAnimea(manga, chapter_start, chapter_end, download_path, download_format, siteKeyword)
#useMangaReader(manga, chapter_start, chapter_end, download_path, download_format, siteKeyword)
#useMangaVolume(manga, chapter_start, chapter_end, download_path, download_format, siteKeyword)
#useCloudManga(manga, chapter_start, chapter_end, download_path, download_format, siteKeyword)
exec( 'use' + site + '(manga, chapter_start, chapter_end, download_path, download_format, siteKeyword)')
