#!/usr/bin/env python

import os
import re
import shutil
import zipfile
from fileinput import filename

class Tankoubon:
	'''
	classdocs
	'''


	def __init__( self, manga = None, chapters = [], chaptersLocation = {},
				volumeNumber = 1, fileFormat = ".cbz" ):
		'''
		Constructor
		'''
		self.manga = manga
		self.chapters = chapters
		self.chaptersLocation = chaptersLocation
		self.volumeNumber = volumeNumber
		self.volumeName = self.buildVolumeName( self.manga, self.chapters,
											 self.volumeNumber )
		self.fileFormat = fileFormat
		
	def buildVolumeName( self, manga, chapters, volumeNumber ):
		volumeName = None
		
		if( manga ):
			volumeName = str( manga )
		else:
			volumeName = ""
			
		if( volumeNumber ):
			volumeName += ".Vol " + str( volumeNumber )
			
		if( chapters ):
			non_numbers = re.compile( r'[^\d]+' )
			numberOfChapters = len( chapters )
			volumeName += ".Ch" + non_numbers.sub( "", str( chapters[0] ) )
			
			if( numberOfChapters > 1 ):
				volumeName += " - " + non_numbers.sub( "", str( chapters[numberOfChapters - 1] ) )
			
		return volumeName

def createTankoubonFiles( tankoubonsToCreate, siteParser ):
	for t in tankoubonsToCreate:
		print( "Creating Tankoubon %s ..." % t.volumeNumber )
		# Create temp folder
		filePath = os.path.join( siteParser.tempFolder, t.volumeName ) + t.fileFormat
		
		# Create Zip file and be ready to put files in it
		with zipfile.ZipFile( filePath, 'w' ) as tankZ:
			# Loop through the chapters
			for chapterName in t.chapters:
				#  write every chapter file to the Tankoubon Zip file
				#  close chapter
				chapterLocation =  t.chaptersLocation.get( chapterName )
				with zipfile.ZipFile( chapterLocation, "r" ) as chapZ:
					imageNamelist = [( s, chapZ.read( s ) ) for s in chapZ.namelist()]
					
					for image in imageNamelist:
						filename = image[0]
						actualFile = image[1]
						tankZ.writestr( filename, actualFile )
						
				if (siteParser.cleanChaptersAfterBuildingTankoubon):
					os.remove(chapterLocation)
		
		# Move Zip file to DownloadLocation specified
		if ( siteParser.overwrite_FLAG == True ):
			priorPath = os.path.join( siteParser.downloadPath, t.volumeName ) + t.fileFormat
			if ( os.path.exists( priorPath ) ):
				os.remove( priorPath )
		
		shutil.move( filePath, siteParser.downloadPath )
	
	print( "Finished building tankoubon!" )
