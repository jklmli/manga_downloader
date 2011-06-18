#!/usr/bin/env python

# The progressBarManager synchronizes the progress bars for the program

#####################

from outputManager.base import *
from outputManager.progressbar import *
import time

class progressBarManager(outputManager):
	def __init__( self ):
		outputManager.__init__(self)
		
	def createOutputObj( self, title, numberOfPages ):
		outputObj = outputStruct()
		outputObj.updateObjSem = threading.Semaphore(0)
		outputObj.title = title

		outputObj.numOfInc = numberOfPages
		
		# Aquiring the List Lock to protect the dictionary structured
		self.outputListLock.acquire(True)
		
		id = self.nextId 
		self.nextId = self.nextId + 1
		outputObj.id = id
		self.outputObjs[id] = outputObj
		
		#  Releasing lock
		self.outputListLock.release()
		
		return id
		
	def updateOutputObj( self, objectId ):
		self.outputObjs[objectId].updateObjSem.release()	
	
	def getNextIdx(self):
		index = None
		
		self.outputListLock.acquire(True)
		if (len(self.outputObjs) > 0):
			keys = self.outputObjs.iterkeys()
			for key in keys:
				index = key
				break 
		self.outputListLock.release()
		
		return index
		
	def removeOuputObj(self, index):
		self.outputListLock.acquire(True)
		del self.outputObjs[index]
		self.outputListLock.release()
	
	def run (self):
		while(self.isAlive):
			# Sleep to give priority to another thread
			time.sleep(0)
			index = self.getNextIdx()
			if (index != None):
				widgets = ['%s: ' % self.outputObjs[index].title, Percentage(), ' ', Bar(), ' ', ETA(), ]
				progressBar = ProgressBar(widgets=widgets, maxval=self.outputObjs[index].numOfInc).start()
				
				for i in range(self.outputObjs[index].numOfInc):
					self.outputObjs[index].updateObjSem.acquire()
					progressBar.update( i + 1 )
				print "\n"
				self.removeOuputObj(index)
					
			
			
			
