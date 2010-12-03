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
from xml.dom import minidom

##########

class NoUpdates(Exception):
	pass
	
class MangaNotFound(Exception):
	pass

##########

def cleanTmp():
	if os.path.exists(mangdl_tmp_path):
		shutil.rmtree(mangdl_tmp_path)
	os.mkdir(mangdl_tmp_path)

def compress(manga_chapter_prefix, download_path, max_pages, download_format):
	print('Compressing...')
	z = zipfile.ZipFile( os.path.join(mangdl_tmp_path, manga_chapter_prefix + download_format), 'a')
	for page in range(1, max_pages + 1):	
		temp_path = os.path.join(mangdl_tmp_path, manga_chapter_prefix + '_' + str(page).zfill(3))
		
		if imghdr.what(temp_path) != None:
			z.write( temp_path, manga_chapter_prefix + '_' + str(page).zfill(3) + '.' + imghdr.what(temp_path))
	z.close()
	shutil.move( os.path.join(mangdl_tmp_path, manga_chapter_prefix + download_format), download_path)
	cleanTmp()
	
def downloadImages(page, pageUrl, manga_chapter_prefix, stringQuery):
	while True:
		try:
			source_code = getSourceCode(pageUrl)
			img_url = re.compile(stringQuery).search(source_code).group(1)
		except AttributeError:
			pass
		else:
			break
			
	print(img_url)
	while True:
		try:
			temp_path = os.path.join(mangdl_tmp_path, manga_chapter_prefix + '_' + str(page).zfill(3))
			urllib.urlretrieve(img_url, temp_path)
		except IOError:
			pass
		else:
			break
	
def fixFormatting(s):
	for i in string.punctuation:
		if(i != '-' and i != '.'):
			s = s.replace(i, "")
	return s.lower().lstrip('.').strip().replace(' ', '_')

def getSourceCode(url):
	while True:
		try:
			ret = urllib.urlopen(url).read()
		except IOError:
			pass
		else:
			break
	return ret
	
def prepareDownload(manga, chapters, current_chapter, download_path, queryString):
	manga_chapter_prefix = fixFormatting(manga) + '_' + fixFormatting(chapters[current_chapter][1])
	if (os.path.exists(download_path + manga_chapter_prefix + '.cbz') or os.path.exists(download_path + manga_chapter_prefix + '.zip')) and overwrite_FLAG == False:
		print(chapters[current_chapter][1] + ' already downloaded, skipping to next chapter...')
		return (None, None, None)
	while True:
		try:
			url = chapters[current_chapter][0]
			print(url)
			source_code = getSourceCode(url)
			max_pages = int(re.compile(queryString).search(source_code).group(1))
		except AttributeError:
			pass
		else:
			break
	return (manga_chapter_prefix, url, max_pages)

def selectChapters(chapters):
	chapter_list_array_decrypted = []
	chapter_list_string = ''
	if(all_chapters_FLAG == False):
		chapter_list_string = raw_input('\nDownload which chapters?\n')
	if(all_chapters_FLAG == True or chapter_list_string.lower() == 'all'):
		print('\nDownloading all chapters...')
		for i in range(0, len(chapters)):
			chapter_list_array_decrypted.append(i)
	else:
		chapter_list_array = chapter_list_string.replace(' ', '').split(',')
	
		for i in chapter_list_array:
			iteration = re.search('([0-9]*)-([0-9]*)', i)
			if(iteration != None):
				for j in range((int)(iteration.group(1)), (int)(iteration.group(2)) + 1):
					chapter_list_array_decrypted.append(j - 1)
			else:
				chapter_list_array_decrypted.append((int)(i) - 1)
	return chapter_list_array_decrypted

##########
def parseMangaFox(manga, auto, lastDownloaded):
	chapter_list_array_decrypted = []
	print('Beginning MangaFox check...')
	url = 'http://www.mangafox.com/search.php?name=%s' % '+'.join(manga.split())
	try:
		source_code = getSourceCode(url)
		info = re.compile('a href="/manga/([^/]*)/[^"]*?" class=[^>]*>([^<]*)</a>').findall(source_code)
	except AttributeError:
		print('Manga not found: it doesn\'t exist, or cannot be resolved by autocorrect.')
		raise MangaNotFound
	else:
		found = False
		for notes in info:
			if (not auto):
				print(notes[1])
			
			if notes[1].lower() == manga.lower():
				matchedManga = notes[1]
				keyword = notes[0]
				found = True
				break
			else:
				if (not auto):
					print('Did you mean: %s? (y/n)' % notes[1])
					answer = raw_input();
				else:
					answer = 'n'
				
				if (answer == 'y'):
					matchedManga = notes[1]
					keyword = notes[0]
					found = True
					break
		if found == False:	
			print('No strict match found; please retype your query.\n')
			raise MangaNotFound
			
		url = 'http://www.mangafox.com/manga/%s/' % keyword
		source_code = getSourceCode(url)
		if(source_code.find('it is not available in Manga Fox.') != -1):
			print('Manga not found: it has been removed')
			raise MangaNotFound
		
		url = 'http://www.mangafox.com/cache/manga/%s/chapters.js' % keyword
		source_code = getSourceCode(url)
		
		chapters = re.compile('"(.*?Ch.[\d.]*)[^"]*","([^"]*)"').findall(source_code)

		lowerRange = 0
		upperRange = 0
		
		for i in range(0, len(chapters)):
			chapters[i] = ('http://www.mangafox.com/manga/%s/' % keyword + chapters[i][1], chapters[i][0])
			if (not auto):
				print('(%i) %s' % (i + 1, chapters[i][1]))
			
			if (lastDownloaded == chapters[i][1]):
				lowerRange = i + 1
				
		upperRange = i + 1
		
		#print str(lowerRange) +" - "+str(upperRange)
		
		if (not auto):
			chapter_list_array_decrypted = selectChapters(chapters)
		else:
			if ( lowerRange == upperRange):
				raise NoUpdates
				
			for i in range (lowerRange, upperRange):
				chapter_list_array_decrypted.append(i)
			
		return ('MangaFox', matchedManga, chapters, chapter_list_array_decrypted)

##########

def parseMangaReader(manga, auto, lastDownloaded):
	chapter_list_array_decrypted = []
	print('Beginning MangaReader check...')
	url = 'http://www.mangareader.net/alphabetical'
	try:
		source_code = getSourceCode(url)
		
		info = re.compile('<li><a href="([^"]*)">([^<]*)</a>').findall(source_code[source_code.find('series_col'):])
		found = False
		
		for notes in info:
			if notes[1].lower().find(manga.lower()) != -1:
				if (not auto):
					print(notes[1])
			
				if notes[1].lower() == manga.lower():
					matchedManga = notes[1]
					keyword = notes[0]
					found = True
					break
				else:
					if (not auto):
						print('Did you mean: %s? (y/n)' % notes[1])
						answer = raw_input();
					else:
						answer = 'n'
				
					if (answer == 'y'):
						matchedManga = notes[1]
						keyword = notes[0]
						found = True
					break
						
		if (not found):
			if (not auto):
				print('No strict match found; please retype your query.\n')
				sys.exit()
			else:
				raise MangaNotFound
					
	except AttributeError:
		if (not auto):
			print('Manga not found: it doesn\'t exist, has been removed, or cannot be resolved by autocorrect.')
			sys.exit()
		else:
			raise MangaNotFound
	else:
		url = 'http://www.mangareader.net%s' % keyword
		source_code = getSourceCode(url)
#		print(url)
		
		chapters = re.compile('<tr><td><a href="([^"]*)" class="chico">([^<]*)</a>([^<]*)</td>').findall(source_code)
		
		lowerRange = 0
		upperRange = 0
		
		for i in range(0, len(chapters)):
			chapters[i] = ('http://www.mangareader.net' + chapters[i][0], '%s%s' % (chapters[i][1], chapters[i][2]))
			if (not auto):
				print('(%i) %s' % (i + 1, chapters[i][1]))

			if (lastDownloaded == chapters[i][1]):
				lowerRange = i + 1
				
		upperRange = i + 1
						
		if (not auto):
			chapter_list_array_decrypted = selectChapters(chapters)
		else:
			if ( lowerRange == upperRange):
				raise NoUpdates
				
			for i in range (lowerRange, upperRange):
				chapter_list_array_decrypted.append(i)
				
		return ('MangaReader', matchedManga, chapters, chapter_list_array_decrypted)

##########

def parseOtakuWorks(manga, auto, lastDownloaded):
	i = 0
	chapter_list_array_decrypted = []
	
	print('Beginning OtakuWorks check...')
	url = 'http://www.otakuworks.com/search/%s' % '+'.join(manga.split())
	
	try:
		source_code = getSourceCode(url)
		info = re.compile('>([^>]*?) \(Manga\)').findall(source_code)
		
		found = False
		
		for notes in info:
			i = i + 1
			if (not auto):
				print(notes)
				
			if notes.lower() == manga.lower():
				matchedManga = notes
				found = True
				break
			else:
				if (not auto):
					print('Did you mean: %s? (y/n)' % notes)
					answer = raw_input();
				else:
					answer = 'n'
				
				if (answer == 'y'):
					matchedManga = notes
					found = True
					break
					
		if (not found):
			if (not auto):
				print('No strict match found; please retype your query.\n')
				sys.exit()
			else:
				raise MangaNotFound
					
	except AttributeError:
		if (not auto):
			print('Manga not found: it doesn\'t exist, has been removed, or cannot be resolved by autocorrect.')
			sys.exit()
		else:
			raise MangaNotFound
		
#	else:
	try:
		FoundURLs = re.compile('a href="([^>]*?)"[^<]*? \(Manga\)').findall(source_code)
		source_code = getSourceCode(FoundURLs[i-1])
		
	except AttributeError:
		pass
	except IndexError:
		pass
	
	chapters = re.compile('a href="([^>]*%s[^>]*)">([^<]*#[^<]*)</a>' % '-'.join(fixFormatting(matchedManga).replace('_', ' ').split())).findall(source_code)
	chapters.reverse()

	lowerRange = 0
	upperRange = 0
	for i in range(0, len(chapters)):
		chapters[i] = ('http://www.otakuworks.com' + chapters[i][0] + '/read', chapters[i][1])
		if (not auto):
			print('(%i) %s' % (i + 1, chapters[i][1]))
		if (lastDownloaded == chapters[i][1]):
			lowerRange = i + 1
			
	upperRange = i + 1	
	
	if (not auto):
		chapter_list_array_decrypted = selectChapters(chapters)
	else:
		if ( lowerRange == upperRange):
			raise NoUpdates
			
		for i in range (lowerRange, upperRange):
			chapter_list_array_decrypted.append(i)
			
	return ('OtakuWorks', matchedManga, chapters, chapter_list_array_decrypted)
	
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

def downloadAnimea(manga, chapter_start, chapter_end, download_path, download_format):
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

def downloadMangaFox(manga, chapters, chapters_to_download, download_path, download_format):
	for current_chapter in chapters_to_download:
		manga_chapter_prefix, url, max_pages = prepareDownload(manga, chapters, current_chapter, download_path, 'var total_pages=([^;]*?);')
		if url == None:
			continue
			
		for page in range(1, max_pages + 1):
			print(chapters[current_chapter][1] + ' / ' + 'Page ' + str(page))
			pageUrl = '%s/%i.html' % (url, page)
			downloadImages(page, pageUrl, manga_chapter_prefix, ';"><img src="([^"]*)"')
			
		compress(manga_chapter_prefix, download_path, page, download_format)
		
##########

def downloadMangaReader(manga, chapters, chapters_to_download, download_path, download_format):
	
	for current_chapter in chapters_to_download:
	
		manga_chapter_prefix, url, max_pages = prepareDownload(manga, chapters, current_chapter, download_path, '</select> of (\d*)            </div>')
		
		manga_chapter_prefix = fixFormatting(chapters[current_chapter][1])
		if url == None:
			continue
			
		for page in re.compile("<option value='([^']*?)'[^>]*> (\d*)</option>").findall(getSourceCode(url)):
			print(chapters[current_chapter][1] + ' / ' + 'Page ' + page[1])
			pageUrl = 'http://www.mangareader.net' + page[0]
			downloadImages(page[1], pageUrl, manga_chapter_prefix, 'img id="img" src="([^"]*)"')
			
		compress(manga_chapter_prefix, download_path, (int)(page[1]), download_format)
		
##########

def downloadOtakuWorks(manga, chapters, chapters_to_download, download_path, download_format):
	for current_chapter in chapters_to_download:
		
		manga_chapter_prefix, url, max_pages = prepareDownload(manga, chapters, current_chapter, download_path, '<strong>(\d*)</strong>')
		if url == None:
			continue
		
		for page in range(1, max_pages + 1):
			print(chapters[current_chapter][1] + ' / ' + 'Page ' + str(page))
			pageUrl = '%s/%i' % (url, page)
			downloadImages(page, pageUrl, manga_chapter_prefix, 'img src="(http://static.otakuworks.net/viewer/[^"]*)"')
			
		compress(manga_chapter_prefix, download_path, max_pages, download_format)
		
##########

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

############

def setText(nodelist, text):
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            node.data = text

##########

def ParseXMLFile(xmlFile):
	
	dom = minidom.parse(xmlFile)
	for node in dom.getElementsByTagName("MangaSeries"):
		iLastChap = 0;
		name = getText(node.getElementsByTagName('name')[0].childNodes)
		site = 	getText(node.getElementsByTagName('HostSite')[0].childNodes)
		lastChapterDownloaded =	getText(node.getElementsByTagName('LastChapterDownloaded')[0].childNodes)
		download_path =	getText(node.getElementsByTagName('downloadPath')[0].childNodes)
		
		execString = "site, manga, chapters, chapters_to_download = parse"+site+"(\""+name+"\", True, \""+lastChapterDownloaded+"\")"
		
		#print execString
		
		try:
			exec(execString)
		except MangaNotFound:
			print ("Manga ("+name+") Missing. Check if still available")
			continue
			
		except  NoUpdates:
			print ("Manga ("+name+") up-to-date.\n")
			continue
		
		
		for current_chapter in chapters:
			#print "Current Chapter =" + str(current_chapter[0])
			iLastChap = current_chapter[1]
		
		try:
			execString = 'download' + site + '(manga, chapters, chapters_to_download, download_path, download_format)'
		
			exec(execString)
		except:
			print "Error"
			continue
			
		#print iLastChap
		setText(node.getElementsByTagName('LastChapterDownloaded')[0].childNodes, str(iLastChap))

	f = open(xmlFile, 'w')
	f.write(dom.toxml())
	
##########
download_path = './'
download_format = '.cbz'
all_chapters_FLAG = False
overwrite_FLAG = False
xmlfile_path = ''
mangdl_tmp_path = "mangadl_tmp" 

class AppURLopener(urllib.FancyURLopener):
	version = 'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.14 Safari/534.3'

urllib._urlopener = AppURLopener()

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
cleanTmp()

if xmlfile_path != "":
	print("parsing XML File")
	ParseXMLFile(xmlfile_path)
else:
	print('\nWhich site?\n(1) MangaFox\n(2) OtakuWorks\n(3) MangaReader\n')
	site = raw_input()
	
	try:
		exec('site, manga, chapters, chapters_to_download = parse' + siteDict[site] + '(manga, False, 1)')
	except KeyError:
		print('Invalid selection. Now exiting...')
		sys.exit()

	if download_path == 'CURRENT_DIRECTORY':
		download_path = './' + fixFormatting(manga)
		if not(os.path.exists(download_path)):
			os.mkdir(download_path)
					
	download_path = os.path.realpath(download_path) + os.sep
	

	cleanTmp()

	#useAnimea(manga, chapter_start, chapter_end, download_path, download_format, misc)
	#useMangaReader(manga, chapter_start, chapter_end, download_path, download_format, misc)
	#useOtakuWorks(manga, chapter_start, chapter_end, download_path, download_format, misc)
	exec( 'download' + site + '(manga, chapters, chapters_to_download, download_path, download_format)')
