#!/usr/bin/env python

##########

import re
import urllib
import zipfile
import os
import sys
import shutil
import imghdr
import string

##########

def checkValidity(chapter_start, chapter_end, total_chapters):
	if total_chapters == 0:
		print('Manga not found: it doesn\'t exist, has been removed, or cannot be resolved by autocorrect.')
		sys.exit()
	if (chapter_end > total_chapters) or (chapter_start < 0) or (chapter_end < chapter_start):
		print('Incorrect chapter start/end - most recent chapter is ' + str(total_chapters))
		sys.exit()
	
def cleanTmp():
	if os.path.exists('mangadl_tmp'):
		shutil.rmtree('mangadl_tmp')
	os.mkdir('mangadl_tmp')

def compress(manga_chapter_prefix, download_path, max_pages, download_format):
	print('Compressing...')
	z = zipfile.ZipFile( os.path.join('mangadl_tmp', manga_chapter_prefix + download_format), 'a')
	for page in range(1, max_pages + 1):
		z.write( os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(page).zfill(3)), manga_chapter_prefix + '_' + str(page).zfill(3) + '.' + imghdr.what(os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(page).zfill(3))))
	z.close()
	shutil.move( os.path.join('mangadl_tmp', manga_chapter_prefix + download_format), download_path)
	cleanTmp()
	
def downloadImage(img_url, download_location):
	while True:
		try:
			ret = urllib.urlretrieve(img_url, download_location)
		except IOError:
			pass
		else:
			break
	return ret
	
def fixFormatting(s):
	for i in string.punctuation:
		s = s.replace(i, "")
	return s.lower().replace(' ', '_')

def getSourceCode(url):
	while True:
		try:
			ret = urllib.urlopen(url).read()
		except IOError:
			pass
		else:
			break
	return ret

##########

def pickSite(manga):
#	total_chapters = []
	keywords = []
	misc = []
	websites = ['OtakuWorks']

	#OtakuWorks check
	url = 'http://www.otakuworks.com/search/%s' % '+'.join(manga.split())
	source_code = getSourceCode(url)	
	try:
		matchedManga = re.compile('>([^>]*?) \(Manga\)').search(source_code).group(1)
		if(matchedManga.lower() != manga.lower()):
			print('Did you mean: %s? (y/n)' % matchedManga)
			answer = raw_input();
			if (answer != 'y'):
				print('Please retype your query.\n')
				sys.exit()
#		print(siteHome)
#		print('done finding keyword')
	except AttributeError:
#		total_chapters.append(0)
		keywords.append('')
		print('Manga not found: it doesn\'t exist, has been removed, or cannot be resolved by autocorrect.')
		sys.exit()
		
	else:
		url = re.compile('a href="([^>]*?)"[^<]*? \(Manga\)').search(source_code).group(1)
#		print(url)
#		url = re.sub('series', 'track', url)
		source_code = getSourceCode(url)
		chapters = re.compile('a href="([^>]*%s[^>]*)">([^<]*#[^<]*)</a>' % '-'.join(matchedManga.lower().split())).findall(source_code)
#		print(chapters)
		chapters.reverse()
		for i in range(0, len(chapters)):
#			chapters[i][0] = 'http://www.otakuworks.com/' + chapters[i][0]
			print('(%i) %s' % (i + 1, chapters[i][1]))
		chapter_list_array_decrypted = []
		chapter_list_string = ''
		if(all_chapters_FLAG == False):
			chapter_list_string = raw_input('\nDownload which chapters?\n')
		if(all_chapters_FLAG == True or chapter_list_string.lower() == 'all'):
			print('\nDownloading all chapters...')
			for i in range(0, len(chapters)):
				chapter_list_array_decrypted.append(i)
		else:
			chapter_list_array = chapter_list_string.split(',')
		
			for i in chapter_list_array:
				iteration = re.search('([0-9]*)-([0-9]*)', i)
				if(iteration != None):
					for j in range((int)(iteration.group(1)), (int)(iteration.group(2)) + 1):
						chapter_list_array_decrypted.append(j - 1)
	#					print(j)
				else:
					chapter_list_array_decrypted.append((int)(i) - 1)
	#				print((int)(i))
			
		keywords.append(matchedManga)
		misc.append('http://www.otakuworks.com/' + chapters[len(chapters) - 1][0])
#		print(re.compile('Chapter #%i</title><link>([^<]*?)</link>' % max_chapters).search(source_code).group(1))
#	print('Finished OtakuWorks check.')
	

	
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
#		manga = re.compile('a href="http://manga.animea.net/(.*?).html"').search(source_code).group(1)
#		url = siteHome
#		source_code = urllib.urlopen(url).read()	
#		total_chapters.append(int(re.compile('http://manga.animea.net/' + manga + '-chapter-(.*?).html').search(source_code).group(1)))
#		keywords.append(manga)
	
#	print('Finished Animea check.')
	#return (site, total_chapters)
	
#	winningIndex = total_chapters.index(max(total_chapters))
	winningIndex = 0
#	return (websites[0], keywords[winningIndex], misc[0])
	return (websites[winningIndex], keywords[winningIndex], misc[winningIndex], chapters, chapter_list_array_decrypted)
	
	
##########

def useAnimea(manga, chapter_start, chapter_end, download_path, download_format, misc):
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
		
##########

def useMangaReader(manga, chapter_start, chapter_end, download_path, download_format, misc):
	
	for current_chapter in range(chapter_start, chapter_end + 1):
		manga_chapter_prefix = manga.lower().replace('-', '_') + '_' + str(current_chapter).zfill(3)
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
			downloadImage(img_url, os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(page).zfill(3)))
			if imghdr.what(os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(page).zfill(3) + '.jpg')) == None:
				nextPage = False
		compress(manga_chapter_prefix, current_chapter, download_path, page - 1, download_format)
		
##########

def useOtakuWorks(manga, chapters, chapters_to_download, download_path, download_format, misc):
	for current_chapter in chapters_to_download:
		manga_chapter_prefix = fixFormatting(manga) + '_' + fixFormatting(chapters[current_chapter][1])
		if (os.path.exists(download_path + manga_chapter_prefix + '.cbz') or os.path.exists(download_path + manga_chapter_prefix + '.zip')) and overwrite_FLAG == False:
			print(chapters[current_chapter][1] + ' already downloaded, skipping to next chapter...')
			continue;
#		print('beginning download....')
		
#		print('dl complete')
#		print('http://www.otakuworks.com/(.*?)chp-' + str(current_chapter).zfill(3))\
#		print(misc)
		url = 'http://www.otakuworks.com/' + chapters[current_chapter][0]
		source_code = getSourceCode(url)
		max_pages = 0
		for page in re.compile('"([^"]*?)" rel="lightbox').findall(source_code):
			max_pages += 1
			print(chapters[current_chapter][1] + ' / ' + 'Page ' + str(max_pages))
			print(page)
			downloadImage(page, os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(max_pages).zfill(3)))
			
		compress(manga_chapter_prefix, download_path, max_pages, download_format)
##########


download_path = './'
download_format = '.cbz'
#chapter_start = 0
#chapter_end = 0
all_chapters_FLAG = False
overwrite_FLAG = False

class AppURLopener(urllib.FancyURLopener):
	version = 'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.14 Safari/534.3'

urllib._urlopener = AppURLopener()

options = {
		'-a' : 'all_chapters_FLAG = True',
		'-d' : 'download_path = sys.argv[index + 1]',
#		'-e' : 'chapter_end = int(sys.argv[index + 1])',
		'-f' : 'download_path = "CURRENT_DIRECTORY"',
		'-n' : 'manga = sys.argv[index + 1]',
#		'-s' : 'chapter_start = int(sys.argv[index + 1])',
		'-o' : 'overwrite_FLAG = True',
		'-z' : 'download_format = ".zip"'	
									}
		
for index in range(1, len(sys.argv)):

	try:
		exec(options[sys.argv[index]] )
	except KeyError:
		pass

print('Selecting optimal site for download...')

#info = pickSite(manga)


site, manga, misc, chapters, chapters_to_download = pickSite(manga)
#site = info[0]
#total_chapters = info[1]
#manga = info[2]
#misc = info[3]

if download_path == 'CURRENT_DIRECTORY':
	download_path = './' + fixFormatting(manga)
	if not(os.path.exists(download_path)):
		os.mkdir(download_path)
		

if download_path.endswith('/') == False and download_path.find('\\') == -1:
	download_path += '/'

if download_path.endswith('\\') == False and download_path.find('/') == -1:
	download_path += '\\'

#print('Site found!\nUsing: ' + site)

#if all_chapters_FLAG == True or (chapter_start == 0 and chapter_end == 0):
#	chapter_start = 1
#	chapter_end = total_chapters

#if chapter_start == 0 and chapter_end != 0:
#	chapter_start = 1
	
#if chapter_start != 0 and chapter_end == 0:
#	chapter_end = total_chapters


#checkValidity(chapter_start, chapter_end, total_chapters)

cleanTmp()

#useAnimea(manga, chapter_start, chapter_end, download_path, download_format, misc)
#useMangaReader(manga, chapter_start, chapter_end, download_path, download_format, misc)
#useOtakuWorks(manga, chapter_start, chapter_end, download_path, download_format, misc)
exec( 'use' + site + '(manga, chapters, chapters_to_download, download_path, download_format, misc)')
