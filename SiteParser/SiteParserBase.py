#!/usr/bin/env python

#####################

import imghdr
import os
import re
import shutil
import sys
import urllib
import zipfile
import tempfile
import threading
import time

#####################

from helper import *
from ThreadProgressBar import *
from ConversionQueue import ConversionQueue

#####################


class SiteParserBase:

	# overwrite default user-agent so we can download
	class AppURLopener(urllib.FancyURLopener):
		version = 'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.14 Safari/534.3'
	
#####	
	# typical misspelling of title and/or manga removal
	class MangaNotFound(Exception):
		
		def __init__(self, str=""):
			if (str == ""):
				self.parameter = "Manga Not Found."
			else:
				self.parameter = "Manga Not Found: "+str	
		
		def __str__(self):
			return self.parameter
	
	# XML file config reports nothing to do
	class NoUpdates(Exception):

		def __init__(self, str=""):
			if (str == ""):
				self.parameter = "No Updates."
			else:
				self.parameter = "No Updates: "+str	
 
		def __str__(self):
			return self.parameter
		
	# Script Failed to Create Download path folder	
	class NonExistantDownloadPath(Exception):
		def __init__(self, str=""):
			if (str == ""):
				self.parameter = "Download Path does not exist."
			else:
				self.parameter = "Download Path does not exist: "+str	
 
		def __str__(self):
			return self.parameter
		
#####

	def __init__(self,optDict):
		urllib._urlopener = SiteParserBase.AppURLopener()
		for elem in vars(optDict):
			setattr(self, elem, getattr(optDict, elem))
		self.chapters = []
		self.chapters_to_download = []
		self.mangadl_tmp_path = tempfile.mkdtemp()
		self.garbageImages = {}

	# this takes care of removing the temp directory after the last successful download
	def __del__(self):
		try:
			shutil.rmtree(self.mangadl_tmp_path)
		except:
			pass
		if len(self.garbageImages) > 0:
			print('\nSome images were not downloaded due to unavailability on the site or temporary ip banning:\n')
			for elem in self.garbageImages.keys():
				print('Manga keyword: %s' % elem)
				print('Pages: %s' % self.garbageImages[elem])
#####	
		
	def downloadChapter(self):
		raise NotImplementedError( 'Should have implemented this' )		
		
	def parseSite(self):
		raise NotImplementedError( 'Should have implemented this' )
#####
	
	
	def compress(self, manga_chapter_prefix, max_pages):
		"""
		Looks inside the temporary directory and zips up all the image files.
		"""
		if self.verbose_FLAG:
			print('Compressing...')
		
		compressedFile = os.path.join(self.mangadl_tmp_path, manga_chapter_prefix) + self.download_format
			
		z = zipfile.ZipFile( compressedFile, 'w')
		
		for page in range(1, max_pages + 1):	
			temp_path = os.path.join(self.mangadl_tmp_path, manga_chapter_prefix + '_' + str(page).zfill(3))
			# we got an image file
			if imghdr.what(temp_path) != None:
				z.write( temp_path, manga_chapter_prefix + '_' + str(page).zfill(3) + '.' + imghdr.what(temp_path))
			# site has thrown a 404 because image unavailable or using anti-leeching
			else:
				if manga_chapter_prefix not in self.garbageImages:
					self.garbageImages[manga_chapter_prefix] = [page]
				else:
					self.garbageImages[manga_chapter_prefix].append(page)
				
		z.close()
		
		if self.overwrite_FLAG == True:
			priorPath = os.path.join(self.download_path, manga_chapter_prefix) + self.download_format
			if os.path.exists(priorPath):
				os.remove(priorPath)
		
 		shutil.move( compressedFile, self.download_path)
 		
 		# The object conversionQueue (singleton) stores the path to every compressed file that  
 		# has been downloaded. This object is used by the conversion code to convert the downloaded images
 		# to the format specified by the Device parameter
 		
		compressedFile = os.path.basename(compressedFile)
		compressedFile = os.path.join(self.download_path, compressedFile)
		ConversionQueue.append(compressedFile, self.OutputDir)
	
	def downloadImage(self, page, pageUrl, manga_chapter_prefix, stringQuery):
		"""
		Given a page URL to download from, it searches using stringQuery as a regex to parse out the image URL, 
		and downloads and names it using manga_chapter_prefix and page.
		"""
		
		# while loop to protect against server denies for requests
		# note that disconnects are already handled by getSourceCode, we use a regex to parse out the image URL and filter out garbage denies
		while True:
			try:
				source_code = getSourceCode(pageUrl)
				img_url = re.compile(stringQuery).search(source_code).group(1)
			except AttributeError:
				pass
			else:
				break

		# Line is encoding any special character in the URL must remove the http:// before encoding 
		# because otherwise the :// would be encoded as well				
		img_url = 'http://' + urllib.quote(img_url.split('//')[1])
		
		if self.verbose_FLAG:
			print(img_url)
		
		# while loop to protect against server denies for requests and/or minor disconnects
		while True:
			try:
				temp_path = os.path.join(self.mangadl_tmp_path, manga_chapter_prefix + '_' + str(page).zfill(3))
				urllib.urlretrieve(img_url, temp_path)
			except IOError:
				pass
			else:
				break
	
	def prepareDownload(self, current_chapter, queryString):
		"""
		Calculates some other necessary stuff before actual downloading can begin and does some checking.
		"""
		
		# Do not need to ZeroFill the manga name because this should be consistent 
		manga_chapter_prefix = fixFormatting(self.manga) + '_' +  ZeroFillStr(fixFormatting(self.chapters[current_chapter][1]), 3)
		
		try:
			# create download directory if not found
			if os.path.exists(self.download_path) is False:
				os.mkdir(self.download_path)
		except OSError:
			raise self.NonExistantDownloadPath('Unable to create download directory. There may be a file with the same name, or you may not have permissions to write there.')

		# we already have it
		if os.path.exists(os.path.join(self.download_path, manga_chapter_prefix) + self.download_format) and self.overwrite_FLAG == False:
			print(self.chapters[current_chapter][1] + ' already downloaded, skipping to next chapter...')
			return (None, None, None)
		
		SiteParserBase.DownloadChapterThread.acquireSemaphore()
	
		# get the URL of the chapter homepage
		url = self.chapters[current_chapter][0]
		
		if (self.verbose_FLAG):
			print(url)
		
		source_code = getSourceCode(url)
		
		# legacy code that may be used to calculate a series of image URLs
		# however, this is risky because some uploaders omit pages, double pages may also affect this
		# an alternative to this is os.walk through the temporary download directory
		# edit: this is actually required if you want a progress bar
		max_pages = int(re.compile(queryString).search(source_code).group(1))

		return (manga_chapter_prefix, url, max_pages)
	
	def selectChapters(self, chapters):
		"""
		Prompts user to select list of chapters to be downloaded from total list.
		"""
		
		# this is the array form of the chapters we want
		chapter_list_array_decrypted = []
		
		if(self.all_chapters_FLAG == False):
			chapter_list_string = raw_input('\nDownload which chapters?\n')
			
		if(self.all_chapters_FLAG == True or chapter_list_string.lower() == 'all'):
			print('\nDownloading all chapters...')
			for i in range(0, len(chapters)):
				chapter_list_array_decrypted.append(i)
		else:
			# time to parse the user input
			
			# ignore whitespace, split using comma delimiters
			chapter_list_array = chapter_list_string.replace(' ', '').split(',')
			
			for i in chapter_list_array:
				iteration = re.search('([0-9]*)-([0-9]*)', i)
				
				# it's a range
				if(iteration is not None):
					for j in range((int)(iteration.group(1)), (int)(iteration.group(2)) + 1):
						chapter_list_array_decrypted.append(j - 1)
				# it's a single chapter
				else:
					chapter_list_array_decrypted.append((int)(i) - 1)
		return chapter_list_array_decrypted
	
	def selectFromResults(self, info):
		"""
		Basic error checking for manga titles, queries will return a list of all mangas that 
		include the query, case-insensitively.
		"""
		
		found = False
		
		# info is a 2-tuple
		# info[0] contains a keyword or string that needs to be passed back (generally the URL to the manga homepage)
		# info[1] contains the manga name we'll be using
		# When asking y/n, we pessimistically only accept 'y'
		for notes in info:
			if notes[1].lower().find(self.manga.lower()) != -1:
				# manual mode
				if (not self.auto):
					print(notes[1])
				
				# exact match
				if notes[1].lower() == self.manga.lower():
					self.manga = notes[1]
					keyword = notes[0]
					found = True
					break
				else:
					# only request input in manual mode
					if (not self.auto):
						print('Did you mean: %s? (y/n)' % notes[1])
						answer = raw_input();
	
						if (answer == 'y'):
							self.manga = notes[1]
							keyword = notes[0]
							found = True
							break
		if (not found):
			raise self.MangaNotFound("No strict match found. Check Query.")
		return keyword
	
	gChapterThreadSemaphopre = None
	
	class DownloadChapterThread( threading.Thread ):
		def __init__ ( self, siteParser, chapter):
			threading.Thread.__init__(self)
			self.siteParser = siteParser
			self.chapter = chapter
			
			
		@staticmethod
		def InitializeSemaphore(value):
			global gChapterThreadSemaphopre
			gChapterThreadSemaphopre = threading.Semaphore(value)
			

		@staticmethod
		def acquireSemaphore():
			global gChapterThreadSemaphopre
			
			if (gChapterThreadSemaphopre == None):
				raise FatalError('Semaphore Not Initialized')
				
			gChapterThreadSemaphopre.acquire()
			
		@staticmethod
		def releaseSemaphore():	
			global gChapterThreadSemaphopre
			
			if (gChapterThreadSemaphopre == None):
				raise FatalError('Semaphore Not Initialized')
				
			gChapterThreadSemaphopre.release()
			
		def run (self):
			try:
				self.siteParser.downloadChapter(self.chapter)
			except Exception, (Instance):
				# Assume semaphore has not been release
				# This assumption could be faulty if the error was thrown in the compression function
				# The worst case is that releasing the semaphore would allow one more thread to 
				# begin downloading than it should
				#
				# If the semaphore was not released before the exception, it could cause deadlock
				gChapterThreadSemaphopre.release()
				raise FatalError("DownLoadChapter Thread Crashed: %s" % str(Instance))
				

	
	def downloadChapters(self):
		threadPool = []
		
		SiteParserBase.DownloadChapterThread.InitializeSemaphore(self.maxChapterThreads)
		"""
		for loop that goes through the chapters we selected.
		"""
		
		#i = 0
		for current_chapter in self.chapters_to_download:
			thread = SiteParserBase.DownloadChapterThread(self, current_chapter)
			threadPool.append(thread)
			thread.start()
			#i = i + 1
			#print i
			
				
		while (len(threadPool) > 0):
			thread = threadPool.pop()
			while (thread.isAlive()):
				# Yields control to whoever is waiting 
				time.sleep(0)

	def postDownloadProcessing(self, manga_chapter_prefix, max_pages):
		SiteParserBase.DownloadChapterThread.releaseSemaphore()
		self.compress(manga_chapter_prefix, max_pages)

