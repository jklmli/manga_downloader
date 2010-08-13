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
		print('Manga not found: it doesn\'t exist, has been removed, or cannot be resolved by autocorrect.')
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
		z.write( os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(page).zfill(3)), manga_chapter_prefix + '_' + str(page).zfill(3) + '.jpg')
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
	total_chapters = []
	keywords = []
	misc = []
	websites = ['MangaVolume', 'CloudManga', 'OtakuWorks']
	
	#MangaVolume check
	url = 'http://www.google.com/search?q=site:mangavolume.com+manga+' + '+'.join(manga.split())
	source_code = getSourceCode(url)
	try:
		siteHome = re.compile('mangavolume.com/.*?/mangas-(.*?)/').search(source_code).group(0)
	except:
		total_chapters.append(0)
		keywords.append('')
	else:	
		manga = re.compile('mangavolume.com/.*?/mangas-(.*?)/').search(source_code).group(1)
		url = 'http://www.' + siteHome
		source_code = getSourceCode(url)
		try:
			intermediate = re.compile('>(?!<a href)(.*?)</a> </td>').search(source_code).group(1)
#			print(intermediate)
			total_chapters.append(int(intermediate[len(manga): ]))
#			print(int(intermediate[len(manga): ]))
		except AttributeError:
			total_chapters.append(0)
		keywords.append(manga)
	misc.append('')
	
	print('Finished MangaVolume check.')
	
	#CloudManga check
	url = 'http://www.google.com/search?q=site:cloudmanga.com+manga+' + '+'.join(manga.split())
	source_code = getSourceCode(url)
#	print('done downloading google search code')
	try:
		manga = re.compile('cloudmanga.com/(.*?)/').search(source_code).group(1)
#		print('done finding keyword')
	except AttributeError:
		total_chapters.append(0)
		keywords.append('')
	else:
		url = 'http://www.cloudmanga.com/' + manga
		source_code = getSourceCode(url)
#		print('done downloading cloudmanga code')
		total_chapters.append(int(re.compile(manga + '/([0-9]*?)/\'"').search(source_code).group(1)))
#		print(int(re.compile(manga + '/([0-9]*?)/\'"').search(source_code).group(1)))
		keywords.append(manga)
	misc.append('')
	print('Finished CloudManga check.')

	#OtakuWorks check
	url = 'http://www.google.com/search?q=site:otakuworks.com+manga+' + '+'.join(manga.split())
	source_code = getSourceCode(url)	
	try:
		siteHome = re.compile('(otakuworks.com/series/[0-9]*?)/([^/]*?)"').search(source_code).group(1)
#		print(siteHome)
#		print('done finding keyword')
	except AttributeError:
		total_chapters.append(0)
		keywords.append('')
	else:
		manga = re.compile('(otakuworks.com/series/[0-9]*?)/([^/]*?)"').search(source_code).group(2)
		url = 'http://www.' + siteHome
		source_code = getSourceCode(url)
#		print(url)
		total_chapters.append(int(re.compile('"/view/(.*?)chp-(\d{1,3})(.*?)"').search(source_code).group(2)))
#		print(int(re.compile('"http://www.otakuworks.com/view/.*?chp-(.*?)"').search(source_code).group(1)))
#		print(manga)
		keywords.append(manga)
		misc.append('http://www.otakuworks.com' + re.compile('"(/view/.*?chp-\d{1,3}.*?)"').search(source_code).group(1))
#	print('http://www.otakuworks.com/' + re.compile('"/view/(.*?)chp-(\d{1,3})(.*?)"').search(source_code).group(1))
	print('Finished OtakuWorks check.')
	

	
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
	
	winningIndex = total_chapters.index(max(total_chapters))
	return (websites[winningIndex], max(total_chapters), keywords[winningIndex], misc[winningIndex])
	
	
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

		compress(manga_chapter_prefix, current_chapter, download_path, max_pages, download_format)
		
##########

def useCloudManga(manga, chapter_start, chapter_end, download_path, download_format, misc):
	manga_prefix = 'http://www.cloudmanga.com/' + manga + '/'
	
	url = manga_prefix + str(chapter_start) + '/'
	source_code = getSourceCode(url)
#	num_Pages = re.compile('option value').findall(source_code[source_code.find("Discussion"):])
#	print(len(num_Pages))
	img_url = re.compile('src="(http://.*?/.*?/.*?/)(.*?).jpg"').search(source_code)
	img_url_prefix = img_url.group(1)
	current_chapter_img_index = int(img_url.group(2))
	noSkips = False
	
	for current_chapter in range(chapter_start, chapter_end + 1):
		manga_chapter_prefix = manga.lower().replace('-', '_') + '_' + str(current_chapter).zfill(3)
		if (os.path.exists(download_path + manga_chapter_prefix + '.cbz') or os.path.exists(download_path + manga_chapter_prefix + '.zip')) and overwrite_FLAG == False:
			print('Chapter ' + str(current_chapter) + ' already downloaded, skipping to next chapter...')
			noSkips = False
			continue;
		if noSkips == True:
			current_chapter_img_index = next_chapter_img_index
		else:
			url = manga_prefix + str(current_chapter) + '/'
			source_code = getSourceCode(url)
			current_chapter_img_index = int(re.compile('src="(http://.*?/.*?/.*?/)(.*?).jpg"').search(source_code).group(2))
		if (current_chapter != total_chapters):	
			url = manga_prefix + str(current_chapter + 1) + '/'
			source_code = getSourceCode(url)
			next_chapter_img_index = int(re.compile('src="(http://.*?/.*?/.*?/)(.*?).jpg"').search(source_code).group(2))
			max_pages = next_chapter_img_index - current_chapter_img_index
					
			for page in range(1, max_pages + 1):
				print('Chapter ' + str(current_chapter) + ' / ' + 'Page ' + str(page))
				print(img_url_prefix + str(current_chapter_img_index + page - 1) + '.jpg')
				downloadImage(img_url_prefix + str(current_chapter_img_index + page - 1) + '.jpg', os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(page).zfill(3)))

		else:
			page = 0
			nextPage = True
			while nextPage == True:
				page +=1
				print('Chapter ' + str(current_chapter) + ' / ' + 'Page ' + str(page))
				print(img_url_prefix + str(current_chapter_img_index + page - 1) + '.jpg')				
				downloadImage(img_url_prefix + str(current_chapter_img_index + page - 1) + '.jpg', os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(page).zfill(3)))
				if imghdr.what(os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(page).zfill(3))) == None:
					nextPage = False
			max_pages = page - 1
		compress(manga_chapter_prefix, current_chapter, download_path, max_pages, download_format)
#		current_chapter_img_index = (next_chapter_img_index, current_chapter + 1)

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

###########

def useMangaVolume(manga, chapter_start, chapter_end, download_path, download_format, misc):
	for current_chapter in range(chapter_start, chapter_end + 1):
		manga_chapter_prefix = manga.lower().replace('-', '_') + '_' + str(current_chapter).zfill(3)
		if (os.path.exists(download_path + manga_chapter_prefix + '.cbz') or os.path.exists(download_path + manga_chapter_prefix + '.zip')) and overwrite_FLAG == False:
			print('Chapter ' + str(current_chapter) + ' already downloaded, skipping to next chapter...')
			continue;
		url = 'http://www.mangavolume.com/index.php?serie=' + manga + '&chapter=' + manga + '-' + str(current_chapter) + '&page_nr=' + str(1)
		source_code = getSourceCode(url)
		max_pages = int(re.compile('of <b>(.*?)</b>').search(source_code).group(1))
		
		img_url = re.compile('img src="(http.*?.jpg)"').search(source_code).group(1)
		current_chapter_img_index = int(re.compile('http.*?_(.*?).jpg').search(img_url).group(1))
		img_url_prefix = img_url[0:img_url.find('_') + 1]
		
		for page in range(1, max_pages + 1):
			print('Chapter ' + str(current_chapter) + ' / ' + 'Page ' + str(page))
			print(img_url_prefix + str(current_chapter_img_index + page - 1) + '.jpg')
			downloadImage(img_url_prefix + str(current_chapter_img_index + page - 1) + '.jpg', os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(page).zfill(3)))

		compress(manga_chapter_prefix, current_chapter, download_path, max_pages, download_format)
		
##########

def useOtakuWorks(manga, chapter_start, chapter_end, download_path, download_format, misc):
	for current_chapter in range(chapter_start, chapter_end + 1):
		manga_chapter_prefix = manga.lower().replace('-', '_') + '_' + str(current_chapter).zfill(3)
		if (os.path.exists(download_path + manga_chapter_prefix + '.cbz') or os.path.exists(download_path + manga_chapter_prefix + '.zip')) and overwrite_FLAG == False:
			print('Chapter ' + str(current_chapter) + ' already downloaded, skipping to next chapter...')
			continue;
#		print('beginning download....')
		source_code = getSourceCode(misc)
#		print('dl complete')
#		print('http://www.otakuworks.com/(.*?)chp-' + str(current_chapter).zfill(3))\
#		print(misc)
		url = re.compile('view/[^/]*?/[^/]*?/[^/]*?chp-' + str(current_chapter).zfill(3)).search(source_code).group(0) + '/read'
#		print(url)
		url = 'http://www.otakuworks.com/' + url
		source_code = getSourceCode(url)
		max_pages = 0
		for page in re.compile('"([^"]*?)" rel="lightbox').findall(source_code):
			max_pages += 1
			print('Chapter ' + str(current_chapter) + ' / ' + 'Page ' + str(max_pages))
			print(page)
			downloadImage(page, os.path.join('mangadl_tmp', manga_chapter_prefix + '_' + str(max_pages).zfill(3)))
			
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

options = {	'-a' : 'all_chapters_FLAG = True',
		'-d' : 'download_path = sys.argv[index + 1]',
		'-e' : 'chapter_end = int(sys.argv[index + 1])',
		'-f' : 'download_path = "CURRENT_DIRECTORY"',
		'-n' : 'manga = sys.argv[index + 1]',
		'-s' : 'chapter_start = int(sys.argv[index + 1])',
		'-o' : 'overwrite_FLAG = True',
		'-z' : 'download_format = ".zip"'	}
		
for index in range(1, len(sys.argv)):

	try:
		exec(options[sys.argv[index]] )
	except KeyError:
		pass

print('Selecting optimal site for download...')

#info = pickSite(manga)


site, total_chapters, manga, misc = pickSite(manga)
#site = info[0]
#total_chapters = info[1]
#manga = info[2]
#misc = info[3]

if download_path == 'CURRENT_DIRECTORY':
	download_path = './' + manga.lower().replace('-', '_')
	if not(os.path.exists(download_path)):
		os.mkdir(download_path)
		

if download_path.endswith('/') == False and download_path.find('\\') == -1:
	download_path += '/'

if download_path.endswith('\\') == False and download_path.find('/') == -1:
	download_path += '\\'

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

#useAnimea(manga, chapter_start, chapter_end, download_path, download_format, misc)
#useMangaReader(manga, chapter_start, chapter_end, download_path, download_format, misc)
#useMangaVolume(manga, chapter_start, chapter_end, download_path, download_format, misc)
#useCloudManga(manga, chapter_start, chapter_end, download_path, download_format, misc)
#useOtakuWorks(manga, chapter_start, chapter_end, download_path, download_format, misc)
exec( 'use' + site + '(manga, chapter_start, chapter_end, download_path, download_format, misc)')
