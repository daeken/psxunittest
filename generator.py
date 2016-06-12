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

gen = None

def generate(tpl, out, genobj, tests):
	global gen
	gen = genobj
	sio = StringIO()
	for test in tests:
		gen.generateTest(sio, test)
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
