#!/usr/bin/env python

# Conversion queue contains the files the need to be converted. The conversion Queue class has
# only static function methods. This way It acts like the singleton design pattern. 
#####################
import threading

#####################

# Using global variable to act as a static variable
# Use the appropriate static functions in ConversionQueue to modify these values
gCompressedFiles = []
gCompressedDict = {}
gCompressedFileLock = threading.Lock()

class ConversionQueue:
	@staticmethod
	def append(FileToConvert, outputDir):
		global gCompressedFileLock
		global gCompressedFiles
		global gCompressedDict
		
		gCompressedFileLock.acquire()
		gCompressedFiles.append(FileToConvert)
		gCompressedDict[FileToConvert] = outputDir
		gCompressedFileLock.release()
	
	@staticmethod
	def pop():
		global gCompressedFileLock
		global gCompressedFiles
		global gCompressedDict
		
		gCompressedFileLock.acquire()
		if (len(gCompressedFiles) > 0):
			ConversionFile = gCompressedFiles.pop()
			outputDir = gCompressedDict[ConversionFile]
		else:
			ConversionFile = None
			outputDir = None
		gCompressedFileLock.release()
		return ConversionFile, outputDir