from build import *

class Generator(object):
	def reset(self):
		return 'cpu->Reset()'
	def runBlob(self, load, blob):
		return 'runBlob(0x%08x, %i, {%s})' % (load, len(blob), ', '.join('0x%08x' % x for x in blob))

	def writeGPR(self, gpr, value):
		return 'cpu->GPR[%i] = %s' % (gpr, value)
	def readGPR(self, gpr):
		return 'cpu->GPR[%i]' % gpr

	def writeMemory(self, size, ptr, value):
		return 'cpu->PokeMem%i(%s, %s)' % (size, ptr, value)
	def readMemory(self, size, ptr):
		return 'cpu->PeekMem%i(%s)' % (size, ptr)

	def testStart(self, name):
		return 'testStart(%s)' % cstr(name)
	def testAssert(self, expr):
		return 'testAssert(%s)' % expr
	def testEnd(self):
		return 'testEnd()'

run('template.cpp', 'testrunner.cpp', Generator())
