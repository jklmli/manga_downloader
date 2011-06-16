#!/usr/bin/env python

# The outputManager synchronizes the output display for all the various threads

#####################
import threading

class outputStruct():
	def __init__( self ):
		self.id = 0
		self.updateObjSem = None
		self.title = ""
		self.numOfInc = 0	

class outputManager( threading.Thread ):
	def __init__( self ):
		threading.Thread.__init__(self)
		self.outputObjs = dict()
		self.outputListLock = threading.Lock()
		
		# Used to assign the next id for an output object
		self.nextId = 0  
		
		self.isAlive = True
		
	def createOutputObj( self, name, numberOfIncrements ):
		raise NotImplementedError('Should have implemented this')	
	
	def updateOutputObj( self, objectId ):
		raise NotImplementedError('Should have implemented this')	
	
	def run (self):
		raise NotImplementedError('Should have implemented this')
	
	def stop(self):
		self.isAlive = False
	