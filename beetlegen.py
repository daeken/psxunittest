from build import *

class Generator(object):
	cases = 0

	def reset(self):
		return 'cpu->Power()'
	def storeBlobArray(self, name, blob):
		return 'uint32_t %s[] = {%s}' % (name, ', '.join('0x%08x' % x for x in blob))
	def loadBlob(self, load, name, blob):
		return 'pc = loadBlob(0x%08x, %i, %s)' % (load, len(blob), name)

	def writeGPR(self, gpr, value):
		return 'SetGPR(%i, %s)' % (gpr, value)
	def readGPR(self, gpr):
		return 'GetGPR(%i)' % gpr

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

	def generateTest(self, fp, (name, setup, expects, load, blob)):
		if self.cases == 0:
			print >>fp, '%s' % self.case(self.cases)
			self.cases += 1
		else:
			print >>fp
		print >>fp, '\t%s;' % self.testStart(name)
		print >>fp, '\t%s;' % self.reset()
		for expr in setup:
			print >>fp, '\t%s;' % toCode(expr)
		print >>fp
		name = tempname('blob')
		print >>fp, '\t%s;' % self.storeBlobArray(name, blob)
		print >>fp, '\t%s;' % self.loadBlob(load, name, blob)
		print >>fp, '%s' % self.caseEnd()
		print >>fp

		print >>fp, '%s' % self.case(self.cases)
		for expr in expects:
			print >>fp, '\t%s;' % toCode(expr)
		print >>fp, '\t%s;' % self.testEnd()

		self.cases += 1

	def generateEnd(self, fp):
		print >>fp, '%s' % self.caseEnd()

run('beetletemplate.cpp', 'cputest.cpp', Generator())
