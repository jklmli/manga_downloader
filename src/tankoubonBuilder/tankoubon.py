#!/usr/bin/env python

import re


class Tankoubon:
	'''
	classdocs
	'''


	def __init__(self, manga = None, chapters = [], chaptersLocation = {}, 
				volumeNumber = 1):
		'''
		Constructor
		'''
		self.manga = manga
		self.chapters = chapters
		self.chaptersLocation = chaptersLocation
		self.volumeNumber = volumeNumber
		self.volumeName = self.buildVolumeName(self.manga, self.chapters,
											 self.volumeNumber)
		
	def buildVolumeName(self, manga, chapters, volumeNumber):
		volumeName = None
		
		if(manga):
			volumeName = str(manga)
		else:
			volumeName = ""
			
		if(volumeNumber):
			volumeName += ".Vol " + str(volumeNumber)
			
		if(chapters):
			non_numbers = re.compile(r'[^\d]+')
			numberOfChapters = len(chapters)
			volumeName += ".Ch" + non_numbers.sub("", str(chapters[0]))
			
			if(numberOfChapters > 1):
				volumeName += " - " + non_numbers.sub("", str(chapters[numberOfChapters - 1]))
			
		return volumeName