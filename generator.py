from cStringIO import StringIO

def toCode(expr):
	if isinstance(expr, str) or isinstance(expr, unicode):
		return expr
	elif isinstance(expr, int):
		return str(expr)

	if expr[0] == 'set':
		if expr[1][0] == 'gpr':
			return gen.writeGPR(expr[1][1], toCode(expr[2]))
		elif expr[1][0] == 'mem':
			return gen.writeMemory(expr[1][1], toCode(expr[1][2]), toCode(expr[2]))
		else:
			print 'Unknown set expression:', expr
	elif expr[0] == 'assert':
		return gen.testAssert(toCode(expr[1]))
	elif expr[0] == 'eq':
		return '%s == %s' % (toCode(expr[1]), toCode(expr[2]))
	elif expr[0] == 'neq':
		return '%s != %s' % (toCode(expr[1]), toCode(expr[2]))
	elif expr[0] == 'gpr':
		return gen.readGPR(expr[1])
	elif expr[0] == 'mem':
		return gen.readMemory(expr[1], toCode(expr[2]))
	else:
		print 'Unknown expression:', expr

tempi = 0
def tempname(prefix='temp'):
	global tempi
	tempi += 1
	return '%s_%i' % (prefix, tempi)

def generateTest(fp, (name, setup, asserts, load, blob)):
	print >>fp, '\t%s;' % gen.testStart(name)
	print >>fp, '\t%s;' % gen.reset()
	for expr in setup:
		print >>fp, '\t%s;' % toCode(expr)
	print >>fp
	name = tempname('blob')
	print >>fp, '\t%s;' % gen.storeBlobArray(name, blob)
	print >>fp, '\t%s;' % gen.runBlob(load, name, blob)
	print >>fp
	for expr in asserts:
		print >>fp, '\t%s;' % toCode(expr)
	print >>fp, '\t%s;' % gen.testEnd()

gen = None

def generate(tpl, out, genobj, tests):
	global gen
	gen = genobj
	sio = StringIO()
	for test in tests:
		generateTest(sio, test)
	testcode = sio.getvalue()
	with file(out, 'w') as fp:
		with file(tpl, 'r') as tfp:
			fp.write(tfp.read().replace('$TESTS$', testcode))
