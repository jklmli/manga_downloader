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
from image import ImageFlags
from convert import BookConvert
import shutil

class Book:
    DefaultDevice = 'Kindle 3'
    DefaultOverwrite = True
    DefaultImageFlags = ImageFlags.Orient | ImageFlags.Resize | ImageFlags.Quantize


    def __init__(self):
        self.images = []
        self.filename = None
        self.modified = False
        self.title = None
        self.device = Book.DefaultDevice
        self.overwrite = Book.DefaultOverwrite
        self.imageFlags = Book.DefaultImageFlags


    def save(self, filename):
        document = QtXml.QDomDocument()

        root = document.createElement('book')
        document.appendChild(root)

        root.setAttribute('title', self.title)
        root.setAttribute('overwrite', 'true' if self.overwrite else 'false')
        root.setAttribute('device', self.device)
        root.setAttribute('imageFlags', self.imageFlags)

        for filenameImg in self.images:
            itemImg = document.createElement('image')
            root.appendChild(itemImg)
            itemImg.setAttribute('filename', filenameImg)

        textXml = document.toString(4).toUtf8()

        try:
            fileXml = open(unicode(filename), 'w')
            fileXml.write(textXml)
            fileXml.close()
        except IOError:
            raise RuntimeError('Cannot create book file %s' % filename)

        self.filename = filename
        self.modified = False


    def load(self, filename):
        try:
            fileXml = open(unicode(filename), 'r')
            textXml = fileXml.read()
            fileXml.close()
        except IOError:
            raise RuntimeError('Cannot open book file %s' % filename)

        document = QtXml.QDomDocument()

        if not document.setContent(QtCore.QString.fromUtf8(textXml)):
            raise RuntimeError('Error parsing book file %s' % filename)

        root = document.documentElement()
        if root.tagName() != 'book':
            raise RuntimeError('Unexpected book format in file %s' % filename)

        self.title = root.attribute('title', 'Untitled')
        self.overwrite = root.attribute('overwrite', 'true' if Book.DefaultOverwrite else 'false') == 'true'
        self.device = root.attribute('device', Book.DefaultDevice)
        self.imageFlags = int(root.attribute('imageFlags', str(Book.DefaultImageFlags)))
        self.filename = filename
        self.modified = False
        self.images = []

        items = root.elementsByTagName('image')
        if items == None:
            return

        for i in xrange(0, len(items)):
            item = items.at(i).toElement()
            if item.hasAttribute('filename'):
                self.images.append(item.attribute('filename'))

    def addImageDirs(self, directories):
        filenames = []

        for directory in directories:
             for root, subdirs, subfiles in os.walk(unicode(directory)):
                for filename in subfiles:
                    path = os.path.join(root, filename)
                    if self.isImageFile(path):
                        filenames.append(path)
        filenames.sort()
        self.addImageFiles(filenames)
        return filenames


    def addImageFiles(self, filenames):
		#print len(filenames)
		for filename in filenames:
			if filename not in self.images:
				self.images.append(filename)
				self.modified = True
                
                
    def isImageFile(self, filename):
        imageExts = ['jpeg', 'jpg', 'gif', 'png']

        filetype = None
        
        try:
        	filetype = imghdr.what(str(filename))
        except:
        	return False
        	     
        return (
            os.path.isfile(filename) and
            filetype in imageExts
        )
        
