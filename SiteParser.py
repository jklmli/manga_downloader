import urllib
import re
import string
import os
import shutil
import sys
import zipfile
import imghdr

class SiteParserBase:

	class AppURLopener(urllib.FancyURLopener):
		version = 'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.14 Safari/534.3'
	
	class NoUpdates(Exception):
		pass
	
	class MangaNotFound(Exception):
		pass


	def __init__(self):
		urllib._urlopener = SiteParserBase.AppURLopener()
		self.mangdl_tmp_path = "mangadl_tmp" 
		self.all_chapters_FLAG = False
		self.overwrite_FLAG = False
		self.chapters = []
		self.chapters_to_download = []
		self.Manga = None
	
	def ParseSite(self, manga, auto, lastDownloaded):
		raise NotImplementedError( "Should have implemented this" )
	
	def downloadChapters(self, manga, chapter_start, chapter_end, download_path, download_format):
		raise NotImplementedError( "Should have implemented this" )

	def fixFormatting(self, s):
		for i in string.punctuation:
			if(i != '-' and i != '.'):
				s = s.replace(i, "")
		return s.lower().lstrip('.').strip().replace(' ', '_')
	
	def getSourceCode(self, url):
		while True:
			try:
				ret = urllib.urlopen(url).read()
			except IOError:
				pass
			else:
				break
		return ret
	
	def cleanTmp(self):
		if os.path.exists(self.mangdl_tmp_path):
			shutil.rmtree(self.mangdl_tmp_path)
		os.mkdir(self.mangdl_tmp_path)
	
	def selectChapters(self, chapters):
		chapter_list_array_decrypted = []
		chapter_list_string = ''
		if(self.all_chapters_FLAG == False):
			chapter_list_string = raw_input('\nDownload which chapters?\n')
		if(self.all_chapters_FLAG == True or chapter_list_string.lower() == 'all'):
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
		
	def prepareDownload(self, manga, chapters, current_chapter, download_path, queryString):
		self.cleanTmp()
		manga_chapter_prefix = self.fixFormatting(manga) + '_' + self.fixFormatting(chapters[current_chapter][1])
		if (os.path.exists(download_path + manga_chapter_prefix + '.cbz') or os.path.exists(download_path + manga_chapter_prefix + '.zip')) and self.overwrite_FLAG == False:
			print(chapters[current_chapter][1] + ' already downloaded, skipping to next chapter...')
			return (None, None, None)
		while True:
			try:
				url = chapters[current_chapter][0]
				print(url)
				source_code = self.getSourceCode(url)
				max_pages = int(re.compile(queryString).search(source_code).group(1))
			except AttributeError:
				pass
			else:
				break
		return (manga_chapter_prefix, url, max_pages)
	
	def downloadImages(self, page, pageUrl, manga_chapter_prefix, stringQuery):
		while True:
			try:
				source_code = self.getSourceCode(pageUrl)
				img_url = re.compile(stringQuery).search(source_code).group(1)
			except AttributeError:
				pass
			else:
				break
			
		print(img_url)
		while True:
			try:
				temp_path = os.path.join(self.mangdl_tmp_path, manga_chapter_prefix + '_' + str(page).zfill(3))
				urllib.urlretrieve(img_url, temp_path)
			except IOError:
				pass
			else:
				break
				
	def compress(self, manga_chapter_prefix, download_path, max_pages, download_format):
		print('Compressing...')
		
		zipPath = os.path.join(self.mangdl_tmp_path, manga_chapter_prefix + download_format)
	
		# Modified for compatibilities issue with Python2.5, 
		# Option a would throw an error if the file did not exist.
		if os.path.exists(zipPath):
			z = zipfile.ZipFile( zipPath, 'a')
		else:
			z = zipfile.ZipFile( zipPath, 'w')
		
		
		for page in range(1, max_pages + 1):	
			temp_path = os.path.join(self.mangdl_tmp_path, manga_chapter_prefix + '_' + str(page).zfill(3))
		
			if imghdr.what(temp_path) != None:
				z.write( temp_path, manga_chapter_prefix + '_' + str(page).zfill(3) + '.' + imghdr.what(temp_path))
		z.close()
		shutil.move( os.path.join(self.mangdl_tmp_path, manga_chapter_prefix + download_format), download_path)
		self.cleanTmp()
	

########################################
class SiteParserFactory():
	@staticmethod
	def getInstance(site):
		ParserClass = {
			'MangaFox' : MangaFoxParser,
			'MangaReader' : MangaReaderParser,
			'OtakuWorks' : OtakuWorksParser
		}.get(site, None)
		
		if not ParserClass:
			raise NotImplementedError( "Site Not Supported" )
		
		return ParserClass()


########################################
class MangaFoxParser(SiteParserBase):
	
	def ParseSite(self, manga, auto, lastDownloaded):
		print('Beginning MangaFox check...')
		url = 'http://www.mangafox.com/search.php?name=%s' % '+'.join(manga.split())
		try:
			source_code = self.getSourceCode(url)
			info = re.compile('a href="/manga/([^/]*)/[^"]*?" class=[^>]*>([^<]*)</a>').findall(source_code)
		except AttributeError:
			print('Manga not found: it doesn\'t exist, or cannot be resolved by autocorrect.')
			raise self.MangaNotFound
		else:
			found = False
			for notes in info:
				if (not auto):
					print(notes[1])
			
				if notes[1].lower() == manga.lower():
					self.Manga = notes[1]
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
						self.Manga = notes[1]
						keyword = notes[0]
						found = True
						break
			if found == False:	
				print('No strict match found; please retype your query.\n')
				raise self.MangaNotFound
			
			url = 'http://www.mangafox.com/manga/%s/' % keyword
			source_code = self.getSourceCode(url)
			if(source_code.find('it is not available in Manga Fox.') != -1):
				print('Manga not found: it has been removed')
				raise self.MangaNotFound
		
			url = 'http://www.mangafox.com/cache/manga/%s/chapters.js' % keyword
			source_code = self.getSourceCode(url)
		
			self.chapters = re.compile('"(.*?Ch.[\d.]*)[^"]*","([^"]*)"').findall(source_code)

			lowerRange = 0
			upperRange = 0
		
			for i in range(0, len(self.chapters)):
				self.chapters[i] = ('http://www.mangafox.com/manga/%s/' % keyword + self.chapters[i][1], self.chapters[i][0])
				if (not auto):
					print('(%i) %s' % (i + 1, self.chapters[i][1]))
			
				if (lastDownloaded == self.chapters[i][1]):
					lowerRange = i + 1
				
			upperRange = i + 1
		
			#print str(lowerRange) +" - "+str(upperRange)
		
			if (not auto):
				self.chapters_to_download = self.selectChapters(self.chapters)
			else:
				if ( lowerRange == upperRange):
					raise self.NoUpdates
				
				for i in range (lowerRange, upperRange):
					self.chapters_to_download.append(i)
			
			return 
		
	
	def downloadChapters(self, download_path, download_format):
	
		if (self.Manga == None):
			raise self.MangaNotFound
			
		for current_chapter in self.chapters_to_download:
			manga_chapter_prefix, url, max_pages = self.prepareDownload(self.Manga, self.chapters, current_chapter, download_path, 'var total_pages=([^;]*?);')
			if url == None:
				continue
			
			for page in range(1, max_pages + 1):
				print(self.chapters[current_chapter][1] + ' / ' + 'Page ' + str(page))
				pageUrl = '%s/%i.html' % (url, page)
				self.downloadImages(page, pageUrl, manga_chapter_prefix, ';"><img src="([^"]*)"')
			
		self.compress(manga_chapter_prefix, download_path, max_pages, download_format)	
			


#############################################################		
class MangaReaderParser(SiteParserBase):

	def ParseSite(self, manga, auto, lastDownloaded):
		print('Beginning MangaReader check...')
		url = 'http://www.mangareader.net/alphabetical'
		try:
			source_code = self.getSourceCode(url)
		
			info = re.compile('<li><a href="([^"]*)">([^<]*)</a>').findall(source_code[source_code.find('series_col'):])
			found = False
		
			for notes in info:
				if notes[1].lower().find(manga.lower()) != -1:
					if (not auto):
						print(notes[1])
			
					if notes[1].lower() == manga.lower():
						self.Manga = notes[1]
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
							self.Manga = notes[1]
							keyword = notes[0]
							found = True
						break
						
			if (not found):
				if (not auto):
					print('No strict match found; please retype your query.\n')
					sys.exit()
				else:
					raise self.MangaNotFound
					
		except AttributeError:
			if (not auto):
				print('Manga not found: it doesn\'t exist, has been removed, or cannot be resolved by autocorrect.')
				sys.exit()
			else:
				raise self.MangaNotFound
		else:
			url = 'http://www.mangareader.net%s' % keyword
			source_code = self.getSourceCode(url)
			# print(url)
			
			self.chapters = re.compile('<tr><td><a href="([^"]*)" class="chico">([^<]*)</a>([^<]*)</td>').findall(source_code)
			
			lowerRange = 0
			upperRange = 0
			
			for i in range(0, len(self.chapters)):
				self.chapters[i] = ('http://www.mangareader.net' + self.chapters[i][0], '%s%s' % (self.chapters[i][1], self.chapters[i][2]))
				if (not auto):
					print('(%i) %s' % (i + 1, self.chapters[i][1]))

				if (lastDownloaded == self.chapters[i][1]):
					lowerRange = i + 1
				
			upperRange = i + 1
							
			if (not auto):
				self.chapters_to_download = self.selectChapters(self.chapters)
			else:
				if ( lowerRange == upperRange):
					raise self.NoUpdates
				
				for i in range (lowerRange, upperRange):
					self.chapters_to_download .append(i)
				
			return 
	
	
	
	def downloadChapters(self, download_path, download_format):
		if (self.Manga == None):
			raise self.MangaNotFound
				
		for current_chapter in self.chapters_to_download:
	
			manga_chapter_prefix, url, max_pages = self.prepareDownload(self.Manga, self.chapters, current_chapter, download_path, '</select> of (\d*)            </div>')
		
			manga_chapter_prefix = self.fixFormatting(self.chapters[current_chapter][1])
			if url == None:
				continue
			
			for page in re.compile("<option value='([^']*?)'[^>]*> (\d*)</option>").findall(self.getSourceCode(url)):
				print(self.chapters[current_chapter][1] + ' / ' + 'Page ' + page[1])
				pageUrl = 'http://www.mangareader.net' + page[0]
				self.downloadImages(page[1], pageUrl, manga_chapter_prefix, 'img id="img" src="([^"]*)"')
				
		self.compress(manga_chapter_prefix, download_path, max_pages, download_format)	



#############################################################			
class OtakuWorksParser(SiteParserBase):
	
	def ParseSite(self, manga, auto, lastDownloaded):
		i = 0
		
		print('Beginning OtakuWorks check...')
		url = 'http://www.otakuworks.com/search/%s' % '+'.join(manga.split())
	
		try:
			source_code = self.getSourceCode(url)
			info = re.compile('>([^>]*?) \(Manga\)').findall(source_code)
		
			found = False
		
			for notes in info:
				i = i + 1
				if (not auto):
					print(notes)
				
				if notes.lower() == manga.lower():
					self.Manga = notes
					found = True
					break
				else:
					if (not auto):
						print('Did you mean: %s? (y/n)' % notes)
						answer = raw_input();
					else:
						answer = 'n'
				
					if (answer == 'y'):
						self.Manga = notes
						found = True
						break
					
			if (not found):
				if (not auto):
					print('No strict match found; please retype your query.\n')
					sys.exit()
				else:
					raise self.MangaNotFound
					
		except AttributeError:
			if (not auto):
				print('Manga not found: it doesn\'t exist, has been removed, or cannot be resolved by autocorrect.')
				sys.exit()
			else:
				raise MangaNotFound
		
	#	else:
		try:
			FoundURLs = re.compile('a href="([^>]*?)"[^<]*? \(Manga\)').findall(source_code)
			source_code = self.getSourceCode(FoundURLs[i-1])
		
		except AttributeError:
			pass
		except IndexError:
			pass
	
		self.chapters = re.compile('a href="([^>]*%s[^>]*)">([^<]*#[^<]*)</a>' % '-'.join(self.fixFormatting(self.Manga).replace('_', ' ').split())).findall(source_code)
		self.chapters.reverse()

		lowerRange = 0
		upperRange = 0
		for i in range(0, len(self.chapters)):
			self.chapters[i] = ('http://www.otakuworks.com' + self.chapters[i][0] + '/read', self.chapters[i][1])
			if (not auto):
				print('(%i) %s' % (i + 1, self.chapters[i][1]))
			if (lastDownloaded == self.chapters[i][1]):
				lowerRange = i + 1
			
		upperRange = i + 1	
	
		if (not auto):
			self.chapters_to_download = self.selectChapters(self.chapters)
		else:
			if ( lowerRange == upperRange):
				raise self.NoUpdates
			
			for i in range (lowerRange, upperRange):
				self.chapters_to_download.append(i)
			
		return 
		
		
	def downloadChapters(self, download_path, download_format):

		if (self.Manga == None):
			raise self.MangaNotFound

		for current_chapter in self.chapters_to_download:
		
			manga_chapter_prefix, url, max_pages = self.prepareDownload(self.Manga, self.chapters, current_chapter, download_path, '<strong>(\d*)</strong>')
			if url == None:
				continue
		
			for page in range(1, max_pages + 1):
				print(self.chapters[current_chapter][1] + ' / ' + 'Page ' + str(page))
				pageUrl = '%s/%i' % (url, page)
				self.downloadImages(page, pageUrl, manga_chapter_prefix, 'img src="(http://static.otakuworks.net/viewer/[^"]*)"')
		
		self.compress(manga_chapter_prefix, download_path, max_pages, download_format)
			


#############################################################				
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
