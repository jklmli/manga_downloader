#!/usr/bin/env python

import os, zipfile
import imghdr
import shutil

from book import Book
from convert import BookConvert

class convertFile():
	
	def __init__(self):
		pass
		
	@staticmethod	
	def convert(outputMgr, filePath, outDir, Device, verbose):
		kindleDir = 'images' if Device == 'Kindle 5' else 'Pictures'
		listDir = []
		isDir = os.path.isdir(filePath)

		if (isDir):
			title = os.path.basename(filePath)
			listDir = os.listdir(filePath)
		else:
			listDir.append(filePath)
			title = kindleDir
			
		
		outputBook = Book()
		outputBook.device = Device
		
		if (title == None or title == ""):
			title = kindleDir
		
		files = []
		directories = []
		compressedFiles = []
		

		# Recursively loop through the filesystem
		for filename in listDir:
			if (isDir):
				filename = os.path.join(filePath, filename)
			if (verbose):
				print("Pre-Processing %s." % filename)
			if (os.path.isdir(str(filename))):	
				directories.append(filename)
			else:
				if (outputBook.isImageFile(filename)):
					if (verbose):
						print("ConvertPkg: Found Image %s" % filename)
					files.append(filename)
				else:
					imageExts = ['.cbz', '.zip']
					
					if os.path.splitext(filename)[1].lower() in imageExts:
						compressedFiles.append(filename)
		
				
		if (len(files) > 0):
			files.sort()
			outputBook.addImageFiles(files)
			outputBook.title = title
			bookConvert = BookConvert(outputBook, outputMgr, os.path.abspath(outDir), verbose)
			bookConvert.Export()			
		
		outDir = os.path.join(outDir, title)	
			
		for directory in directories:
			if(verbose):
				print("Converting %s", directory)
			convertFile.convert(outputMgr, directory, outDir, Device, verbose)
		
		for compressedFile in compressedFiles:
			try:
				if(verbose):
					print("Uncompressing %s" % compressedFile)
				z = zipfile.ZipFile(compressedFile, 'r')
			except:
				if (verbose):
					print("Failed to convert %s. Check if it is a valid zipFile." % compressedFile)
				continue
				
			if (isDir):
				temp_dir = os.path.join(filePath, os.path.splitext(os.path.basename(compressedFile))[0])
			else:
				temp_dir = os.path.splitext(compressedFile)[0]
			
			try:			
				os.mkdir(temp_dir)
			except:
				continue
				
			for name in z.namelist():
				tempName = os.path.join(temp_dir, name)
				convertFile.extract_from_zip(name, tempName, z)
			z.close
			convertFile.convert(outputMgr, temp_dir, outDir, Device, verbose)
			if os.path.exists(temp_dir):
				shutil.rmtree(temp_dir)
	
	@staticmethod
	def extract_from_zip( name, dest_path, zip_file ):
		dest_file = open(dest_path, 'wb')
		dest_file.write(zip_file.read(name))
		dest_file.close()
