#!/usr/bin/env python

# Copyright (C) 2010  Alex Yatskov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

import image
import imghdr
import string
import unicodedata

from progressbar.threaded import ThreadProgressBar
	
class BookConvert():
    
    def __init__(self, book, directory, verbose):
        self.book = book
        self.directory = directory
        self.verbose = verbose
                    
    def Export(self):

    	if not os.path.isdir(self.directory):
    		os.makedirs(self.directory )
    	
    	hasDisplayLock = False
    	ProgressBarTag = 'Converting ' + self.book.title
    	if (not self.verbose):
			# Function Tries to acquire the lock if it succeeds it initialize the progress bar
			hasDisplayLock = ThreadProgressBar.acquireDisplayLock(ProgressBarTag, len(self.book.images), False )	
			
        for index in range(0,len(self.book.images)):
          directory = os.path.join(unicode(self.directory), unicode(self.book.title))
          source = unicode(self.book.images[index])
          newSource = os.path.join(self.book.images[index]+"."+ imghdr.what(str(source)))    
          target = os.path.join(directory, '%05d.png' % index) 
          
          if index == 0:
            try:
                if not os.path.isdir(directory ):
                    os.makedirs(directory )

            except OSError:
                return

            try:
                base = os.path.join(directory, unicode(self.book.title))
                mangaName = base + '.manga'
                if (self.verbose):
               		print mangaName
                if self.book.overwrite or not os.path.isfile(mangaName):
                    manga = open(mangaName, 'w')
                    manga.write('\x00')
                    manga.close()
                    
                mangaSaveName = base + '.manga_save'
                if self.book.overwrite or not os.path.isfile(mangaSaveName):
                    mangaSave = open(base + '.manga_save', 'w')
                    saveData = u'LAST=/mnt/us/pictures/%s/%s' % (self.book.title, os.path.split(target)[1])
                    mangaSave.write(saveData.encode('utf-8'))
                    mangaSave.close()

            except IOError:
                return False
          
          os.renames(source, newSource)
 
          try:
          	
            if self.book.overwrite or not os.path.isfile(target):
                image.convertImage(newSource, target, str(self.book.device), self.book.imageFlags)
                if (self.verbose):
                	print source + " -> " + target
                else:
				if (not hasDisplayLock):
					hasDisplayLock = ThreadProgressBar.acquireDisplayLock(ProgressBarTag, len(self.book.images), False )
											
				if (hasDisplayLock):
					ThreadProgressBar.updateProgressBar(index + 1)
					
          except RuntimeError, error:
              print "ERROR"
          finally:
          	os.renames(newSource, source)
        
        if (hasDisplayLock):
       	  ThreadProgressBar.releaseDisplayLock()
        else:
          if (not self.verbose):
            ThreadProgressBar.acquireDisplayLock(ProgressBarTag, len(self.book.images), True )
            ThreadProgressBar.updateProgressBar(len(self.book.images))
            ThreadProgressBar.releaseDisplayLock()