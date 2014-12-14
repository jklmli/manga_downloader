#!/usr/bin/env python

#####################

import imghdr
import os
import re
import shutil
import tempfile
import threading
import time
import zipfile

#####################

try:
	import urllib
except ImportError:
	import urllib.parse as urllib

#####################

from util import * 

#####################

class SiteParserBase:

#####	
	# typical misspelling of title and/or manga removal
	class MangaNotFound(Exception):
		
		def __init__(self, errorMsg=''):
			self.errorMsg = 'Manga not found. %s' % errorMsg
		
		def __str__(self):
			return self.errorMsg
	
	# XML file config reports nothing to do
	class NoUpdates(Exception):

		def __init__(self, errorMsg=''):
			self.errorMsg = 'No updates. %s' % errorMsg

		def __str__(self):
			return self.errorMsg
		
#####

	def __init__(self,optDict):
		for elem in vars(optDict):
			setattr(self, elem, getattr(optDict, elem))
		self.chapters = []
		self.chapters_to_download = []
		self.tempFolder = tempfile.mkdtemp()
		self.garbageImages = {}
		
		# should be defined by subclasses
		self.re_getImage = None
		self.re_getMaxPages = None
		self.isPrependMangaName = False

	# this takes care of removing the temp directory after the last successful download
	def __del__(self):
		try:
			shutil.rmtree(self.tempFolder)
		except:
			pass
		if len(self.garbageImages) > 0:
			print('\nSome images were not downloaded due to unavailability on the site or temporary ip banning:\n')
			for elem in self.garbageImages.keys():
				print('Manga keyword: %s' % elem)
				print('Pages: %s' % self.garbageImages[elem])
#####	
		
	def downloadChapter(self):
		raise NotImplementedError('Should have implemented this')		
		
	def parseSite(self):
		raise NotImplementedError('Should have implemented this')
#####
	
	def compress(self, mangaChapterPrefix, max_pages):
		"""
		Looks inside the temporary directory and zips up all the image files.
		"""
		if self.verbose_FLAG:
			print('Compressing...')
		
		compressedFile = os.path.join(self.tempFolder, mangaChapterPrefix) + self.downloadFormat
			
		z = zipfile.ZipFile( compressedFile, 'w')
		
		for page in range(1, max_pages + 1):	
			tempPath = os.path.join(self.tempFolder, mangaChapterPrefix + '_' + str(page).zfill(3))
			# we got an image file
			if os.path.exists(tempPath) is True and imghdr.what(tempPath) != None:
				z.write( tempPath, mangaChapterPrefix + '_' + str(page).zfill(3) + '.' + imghdr.what(tempPath))
			# site has thrown a 404 because image unavailable or using anti-leeching
			else:
				if mangaChapterPrefix not in self.garbageImages:
					self.garbageImages[mangaChapterPrefix] = [page]
				else:
					self.garbageImages[mangaChapterPrefix].append(page)
				
		z.close()
		
		if self.overwrite_FLAG == True:
			priorPath = os.path.join(self.downloadPath, mangaChapterPrefix) + self.downloadFormat
			if os.path.exists(priorPath):
				os.remove(priorPath)
		
		shutil.move(compressedFile, self.downloadPath)
		
		# The object conversionQueue (singleton) stores the path to every compressed file that  
		# has been downloaded. This object is used by the conversion code to convert the downloaded images
		# to the format specified by the Device errorMsg
		
		compressedFile = os.path.basename(compressedFile)
		compressedFile = os.path.join(self.downloadPath, compressedFile)
		return compressedFile
	
	def downloadImage(self, downloadThread, page, pageUrl, manga_chapter_prefix):
		"""
		Given a page URL to download from, it searches using self.imageRegex
		to parse out the image URL, and downloads and names it using 
		manga_chapter_prefix and page.
		"""

		# while loop to protect against server denies for requests
		# note that disconnects are already handled by getSourceCode, we use a 
		# regex to parse out the image URL and filter out garbage denies
		maxRetries = 5
		waitRetryTime = 5
		while True:
			try:
				if (self.verbose_FLAG):
					print(pageUrl)
				source_code = getSourceCode(pageUrl, self.proxy)
				img_url = self.__class__.re_getImage.search(source_code).group(1)
				if (self.verbose_FLAG):
					print("Image URL: %s" % img_url)
			except AttributeError:
				if (maxRetries == 0):
					if (not self.verbose_FLAG):
						self.outputMgr.updateOutputObj( downloadThread.outputIdx )
					return	
				else:
					# random dist. for further protection against anti-leech
					# idea from wget
					time.sleep(random.uniform(0.5*waitRetryTime, 1.5*waitRetryTime))
					maxRetries -= 1
			else:
				break

		# Remove the 'http://' before encoding, otherwise the '://' would be 
		# encoded as well				
#		img_url = 'http://' + urllib.quote(img_url.split('//')[1])
		
		if self.verbose_FLAG:
			print(img_url)
		
		# Loop to protect against server denies for requests and/or minor disconnects
		while True:
			try:
				temp_path = os.path.join(self.tempFolder, manga_chapter_prefix + '_' + str(page).zfill(3))
				urllib.urlretrieve(img_url, temp_path)
			except IOError:
				pass
			else:
				break
		if (not self.verbose_FLAG):
			self.outputMgr.updateOutputObj( downloadThread.outputIdx )
	
	def processChapter(self, downloadThread, current_chapter):
		"""
		Calculates prefix for filenames, creates download directory if
		nonexistent, checks to see if chapter previously downloaded, returns
		data critical to downloadChapter()
		"""
		
		# Do not need to ZeroFill the manga name because this should be consistent 
		# MangaFox already prepends the manga name
		if self.useShortName_FLAG:
			if (not self.isPrependMangaName):
				manga_chapter_prefix = fixFormatting(self.manga, self.spaceToken)+ self.spaceToken + zeroFillStr(fixFormatting(self.chapters[current_chapter][2], self.spaceToken), 3)
			else:	
				manga_chapter_prefix = zeroFillStr(fixFormatting(self.chapters[current_chapter][2], self.spaceToken), 3)
		else:
			manga_chapter_prefix = fixFormatting(self.manga, self.spaceToken) + '.' +  self.site + '.' + zeroFillStr(fixFormatting(self.chapters[current_chapter][1].decode('utf-8'), self.spaceToken), 3)

		
		# we already have it
		if os.path.exists(os.path.join(self.downloadPath, manga_chapter_prefix) + self.downloadFormat) and self.overwrite_FLAG == False:
			print(self.chapters[current_chapter][1].decode('utf-8') + ' already downloaded, skipping to next chapter...')
			return

		SiteParserBase.DownloadChapterThread.acquireSemaphore()
		if (self.timeLogging_FLAG):
			print(manga_chapter_prefix + " (Start Time): " + str(time.time()))
		# get the URL of the chapter homepage
		url = self.chapters[current_chapter][0]
		
		# mangafox .js sometimes leaves up invalid chapters
		if (url == None):
			print('Failed to find '+ self.chapters[current_chapter][1].decode('utf-8')+', skipping to next chapter...')
			return
		
		if (self.verbose_FLAG):
			print("PrepareDownload: " + url)
		
		source = getSourceCode(url, self.proxy)
		max_page_search = self.__class__.re_getMaxPages.search(source)
		
		# MangaHere sometimes leaves up links to invalid chapter and
		# the max page search fails
		if (max_page_search == None):
			print('Failed to find '+ self.chapters[current_chapter][1].decode('utf-8')+', skipping to next chapter...')
			return

		max_pages = int(max_page_search.group(1))
		
		if (self.verbose_FLAG):
				print ("Pages: "+ str(max_pages))
		if (not self.verbose_FLAG):
			downloadThread.outputIdx = self.outputMgr.createOutputObj(manga_chapter_prefix, max_pages)

		self.downloadChapter(downloadThread, max_pages, url, manga_chapter_prefix, current_chapter)
		
		# Post processing 
		# Release locks/semaphores
		# Zip Them up
		self.postDownloadProcessing(manga_chapter_prefix, max_pages)	
	
	def selectChapters(self, chapters):
		"""
		Prompts user to select list of chapters to be downloaded from total list.
		"""
		
		# this is the array form of the chapters we want
		chapterArray = []
		
		if(self.all_chapters_FLAG == False):
			inputChapterString = raw_input('\nDownload which chapters?\n')
			
		if(self.all_chapters_FLAG == True or inputChapterString.lower() == 'all'):
			print('\nDownloading all chapters...')
			for i in range(0, len(chapters)):
				chapterArray.append(i)
		else:
			# parsing user input
			
			# ignore whitespace, split using comma delimiters
			chapter_list_array = inputChapterString.replace(' ', '').split(',')
			
			for i in chapter_list_array:
				iteration = re.search('([0-9]*)-([0-9]*)', i)
				
				# it's a range
				if(iteration is not None):
					for j in range((int)(iteration.group(1)), (int)(iteration.group(2)) + 1):
						chapterArray.append(j - 1)
				# it's a single chapter
				else:
					chapterArray.append((int)(i) - 1)
		return chapterArray
	
	def selectFromResults(self, results):
		"""
		Basic error checking for manga titles, queries will return a list of all mangas that 
		include the query, case-insensitively.
		"""
		
		found = False
		
		# Translate the manga name to lower case
		# Need to handle if it contains NonASCII characters
		actualName = (self.manga.decode('utf-8')).lower()
		
		# each element in results is a 2-tuple
		# elem[0] contains a keyword or string that needs to be passed back (generally the URL to the manga homepage)
		# elem[1] contains the manga name we'll be using
		# When asking y/n, we pessimistically only accept 'y'
		
		for elem in results:
			proposedName = (elem[1].decode('utf-8')).lower()
			
			if actualName in proposedName:
				# manual mode
				if (not self.auto):
					print(elem[1])
				
				# exact match
				if proposedName == actualName:
					self.manga = elem[1]
					keyword = elem[0]
					found = True
					break
				else:
					# only request input in manual mode
					if (not self.auto):
						print('Did you mean: %s? (y/n)' % elem[1])
						answer = raw_input();
	
						if (answer == 'y'):
							self.manga = elem[1]
							keyword = elem[0]
							found = True
							break
		if (not found):
			raise self.MangaNotFound('No strict match found. Check query.')
		return keyword
	
	chapterThreadSemaphore = None
	
	class DownloadChapterThread( threading.Thread ):
		def __init__ ( self, siteParser, chapter):
			threading.Thread.__init__(self)
			self.siteParser = siteParser
			self.chapter = chapter
			self.isThreadFailed = False
			self.outputIdx = -1
			
		@staticmethod
		def initSemaphore(value):
			global chapterThreadSemaphore
			chapterThreadSemaphore = threading.Semaphore(value)
			
		@staticmethod
		def acquireSemaphore():
			global chapterThreadSemaphore
			
			if (chapterThreadSemaphore == None):
				raise FatalError('Semaphore not initialized')
				
			chapterThreadSemaphore.acquire()
			
		@staticmethod
		def releaseSemaphore():	
			global chapterThreadSemaphore
			
			if (chapterThreadSemaphore == None):
				raise FatalError('Semaphore not initialized')
				
			chapterThreadSemaphore.release()
			
		def run (self):
			try:
				self.siteParser.processChapter(self, self.chapter)	
			except Exception as exception:
				# Assume semaphore has not been release
				# This assumption could be faulty if the error was thrown in the compression function
				# The worst case is that releasing the semaphore would allow one more thread to 
				# begin downloading than it should
				#
				# If the semaphore was not released before the exception, it could cause deadlock
				chapterThreadSemaphore.release()
				self.isThreadFailed = True
				raise FatalError("Thread crashed while downloading chapter: %s" % str(exception))
	
	def download(self):
		threadPool = []
		isAllPassed = True
		SiteParserBase.DownloadChapterThread.initSemaphore(self.maxChapterThreads)
		if (self.verbose_FLAG):
			print("Number of Threads: %d " % self.maxChapterThreads)
		"""
		for loop that goes through the chapters we selected.
		"""
		
		for current_chapter in self.chapters_to_download:
			thread = SiteParserBase.DownloadChapterThread(self, current_chapter)
			threadPool.append(thread)
			thread.start()
				
		while (len(threadPool) > 0):
			thread = threadPool.pop()
			while (thread.isAlive()):
				# Yields control to whomever is waiting 
				time.sleep(0)
			if (isAllPassed and thread.isThreadFailed):
				isAllPassed = False
		
		return isAllPassed

	def postDownloadProcessing(self, manga_chapter_prefix, max_pages):
		if (self.timeLogging_FLAG):
			print("%s (End Time): %s" % (manga_chapter_prefix, str(time.time())))

		SiteParserBase.DownloadChapterThread.releaseSemaphore()
		compressedFile = self.compress(manga_chapter_prefix, max_pages)
		self.convertChapter( compressedFile )	
	
	def convertChapter(self, compressedFile):
		# Check if the conversion flag is set
		if ( self.conversion_FLAG ):
			if (not isImageLibAvailable()):
				print("PIL (Python Image Library) not available.")
			else:	
				from ConvertPackage.ConvertFile import convertFile
				if (self.verbose_FLAG):
					print ("Compressed File "+str(compressedFile))							
				
				if (compressedFile != None and self.outputDir != None):
					convertFile.convert(self.outputMgr, compressedFile, self.outputDir, self.device, self.verbose_FLAG)
