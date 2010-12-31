#!/usr/bin/env python

#####################
import threading

#####################

from progressbar import ProgressBar, Percentage, Bar, ETA, FileTransferSpeed, \
     RotatingMarker, ReverseBar, SimpleProgress

#####################
     
# Using global variable to act as a static variable
# Use the appropriate static functions in ThreadedProgressBar to modify these values
gDisplayLock = threading.RLock()
gProgressBar = None

class ThreadProgressBar():

	@staticmethod
	def AcquireDisplayLock(title, maxValue, WaitForLock=False):
		global gDisplayLock
		
		if (not gDisplayLock.acquire(WaitForLock)):
			return False
		else:
			ThreadProgressBar.InitializeProgressBar(title, maxValue)
			return True
	
	@staticmethod
	def ReleaseDisplayLock():
		print '\n'
		gDisplayLock.release()
	
	@staticmethod
	def InitializeProgressBar(title, maxValue):
		global gDisplayLock
		global gProgressBar
		
		if (not gDisplayLock.acquire(False)):
			raise FatalError('Failed to aquire: rLock. By Design this lock shouid aways be acquired before this function is called')

		widgets = ['%s: ' % title, Percentage(), ' ', Bar(), ' ', ETA(), ]
		gProgressBar = ProgressBar(widgets=widgets, maxval=maxValue).start()

		gDisplayLock.release()

	@staticmethod
	def UpdateProgressBar(newValue):
		global gDisplayLock
		global gProgressBar
		
		if (not gDisplayLock.acquire(False)):
			raise FatalError('Failed to aquire: rLock. By Design this lock shouid aways be acquired before this function is called')
		
		gProgressBar.update(newValue)
		
		gDisplayLock.release()
