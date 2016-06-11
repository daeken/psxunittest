from cStringIO import StringIO

# Emulator-specific
def reset():
	return 'cpu->Reset()'
def runBlob(load, blob):
	return 'runBlob(0x%08x, %i, {%s})' % (load, len(blob), ', '.join('0x%02x' % ord(x) for x in blob))

def writeGPR(gpr, value):
	return 'cpu->GPR[%i] = %s' % (gpr, value)
def readGPR(gpr):
	return 'cpu->GPR[%i]' % gpr

def writeMemory(size, ptr, value):
	return 'cpu->PokeMem%i(%s, %s)' % (size, ptr, value)
def readMemory(size, ptr):
	return 'cpu->PeekMem%i(%s)' % (size, ptr)

def testStart(name):
	return 'testStart(%s)' % cstr(name)
def testAssert(expr):
	return 'testAssert(%s)' % expr
def testEnd():
	return 'testEnd()'
# /Emulator-specific

def cstr(val):
	val = `val + "'"`[:-2] + '"'
	assert val[0] == '"'
	return val

def toCode(expr):
	if isinstance(expr, str) or isinstance(expr, unicode):
		return expr
	elif isinstance(expr, int):
		return str(expr)

	if expr[0] == 'set':
		if expr[1][0] == 'gpr':
			return writeGPR(expr[1][1], toCode(expr[2]))
		elif expr[1][0] == 'mem':
			return writeMemory(expr[1][1], toCode(expr[1][2]), toCode(expr[2]))
		else:
			print 'Unknown set expression:', expr
	elif expr[0] == 'assert':
		return testAssert(toCode(expr[1]))
	elif expr[0] == 'eq':
		return '%s == %s' % (toCode(expr[1]), toCode(expr[2]))
	elif expr[0] == 'neq':
		return '%s != %s' % (toCode(expr[1]), toCode(expr[2]))
	elif expr[0] == 'gpr':
		return readGPR(expr[1])
	elif expr[0] == 'mem':
		return readMemory(expr[1], toCode(expr[2]))
	else:
		print 'Unknown expression:', expr

def generateTest(fp, (name, setup, asserts, load, blob)):
	print >>fp, '\t%s;' % testStart(name)
	print >>fp, '\t%s;' % reset()
	for expr in setup:
		print >>fp, '\t%s;' % toCode(expr)
	print >>fp
	print >>fp, '\t%s;' % runBlob(load, blob)
	print >>fp
	for expr in asserts:
		print >>fp, '\t%s;' % toCode(expr)
	print >>fp, '\t%s;' % testEnd()

def generate(tests):
	sio = StringIO()
	for test in tests:
		generateTest(sio, test)
	testcode = sio.getvalue()
	with file('testrunner.cpp', 'w') as fp:
		with file('template.cpp', 'r') as tfp:
			fp.write(tfp.read().replace('$TESTS$', testcode))
