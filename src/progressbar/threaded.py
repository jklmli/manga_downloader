#!/usr/bin/env python

# The ThreadProgressBar class has only static function methods. This way It acts like the singleton design pattern. 

#####################
import threading

#####################

from base import ProgressBar, Percentage, Bar, ETA
from util import FatalError

#####################

# Using global variable to act as a static variable
# Use the appropriate static functions in ThreadedProgressBar to modify these values
displayLock = threading.RLock()
progressBar = None

class ThreadProgressBar():

	@staticmethod
	def acquireDisplayLock(title, maxValue, WaitForLock=False):
		global displayLock
		
		if (not displayLock.acquire(WaitForLock)):
			return False
		else:
			ThreadProgressBar.initProgressBar(title, maxValue)
			return True
	
	@staticmethod
	def releaseDisplayLock():
		global displayLock
		print('\n')
		displayLock.release()
	
	@staticmethod
	def initProgressBar(title, maxValue):
		global displayLock
		global progressBar
		
		if (not displayLock.acquire(False)):
			raise FatalError('Failed to acquire: rLock. By design this lock should always be acquired before this function is called')

		widgets = ['%s: ' % title, Percentage(), ' ', Bar(), ' ', ETA(), ]
		progressBar = ProgressBar(widgets=widgets, maxval=maxValue).start()

		displayLock.release()

	@staticmethod
	def updateProgressBar(newValue):
		global displayLock
		global progressBar
		
		if (not displayLock.acquire(False)):
			raise FatalError('Failed to acquire: rLock. By design this lock should always be acquired before this function is called')
		
		progressBar.update(newValue)
		
		displayLock.release()
