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
	elif expr[0] == 'expectEqual':
		return gen.testExpectEqual(toCode(expr[1]), toCode(expr[2]))
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

cases = 0
def generateTest(fp, (name, setup, expects, load, blob)):
	global cases
	if cases == 0:
		print >>fp, '%s' % gen.case(cases)
	else:
		print >>fp
	print >>fp, '\t%s;' % gen.testStart(name)
	print >>fp, '\t%s;' % gen.reset()
	for expr in setup:
		print >>fp, '\t%s;' % toCode(expr)
	print >>fp
	name = tempname('blob')
	print >>fp, '\t%s;' % gen.storeBlobArray(name, blob)
	print >>fp, '\t%s;' % gen.loadBlob(load, name, blob)
	print >>fp, '%s' % gen.caseEnd()
	print >>fp

	print >>fp, '%s' % gen.case(cases+1)
	for expr in expects:
		print >>fp, '\t%s;' % toCode(expr)
	print >>fp, '\t%s;' % gen.testEnd()

	if cases == 0:
		cases = 2
	else:
		cases += 1

gen = None

def generate(tpl, out, genobj, tests):
	global gen
	gen = genobj
	sio = StringIO()
	for test in tests:
		generateTest(sio, test)
	print >>sio, '%s' % gen.caseEnd()
	testcode = sio.getvalue().rstrip()
	with file(out, 'w') as fp:
		with file(tpl, 'r') as tfp:
			tpl = tfp.read().replace('$LASTSTATE$', str(len(tests) + 1))
			for line in tpl.split('\n'):
				if line.endswith('$TESTS$'):
					ws = line[:-7]
					for line in testcode.split('\n'):
						print >>fp, ws + line
				else:
					print >>fp, line
