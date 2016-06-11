from build import *

class Generator(object):
	def reset(self):
		return 'cpu->Reset()'
	def storeBlobArray(self, name, blob):
		return 'uint32_t %s[] = {%s}' % (name, ', '.join('0x%08x' % x for x in blob))
	def loadBlob(self, load, name, blob):
		return 'loadBlob(0x%08x, %i, %s)' % (load, len(blob), name)

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
	def testExpectEqual(self, state, expect):
		return 'testExpectEqual(%s, %s)' % (state, expect)
	def testEnd(self):
		return 'testEnd()'

	def case(self, i):
		return 'case %i: {' % i

	def caseEnd(self):
		return '\tbreak;\n}'

run('template.cpp', 'testrunner.cpp', Generator())
