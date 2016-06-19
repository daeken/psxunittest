from assembler import assemble, hexify
from cStringIO import StringIO
from glob import glob
from importlib import import_module
import test

tests = []
for fn in glob('tests/*.py'):
	if fn == 'tests/__init__.py':
		continue

	test.setup = []
	test.expects = []
	testmod = import_module('tests.' + fn[6:-3])
	testmod.setup = test.setup
	testmod.expects = test.expects

	tests.append((testmod.name, testmod.setup, testmod.expects, testmod.load, testmod.code))

fp = StringIO()

database = 0x80010000

data = ''
def stash(str):
	global data
	data += str + '\0'
	return len(data) - len(str) - 1 + database

def printf(str):
	addr = stash(str)
	print >>fp, '\tli $4, %s' % hexify(8, addr)
	print >>fp, '\tjal 0xa0'
	print >>fp, '\tli $9, 0x3f'

storesizes = {
	8: 'sb', 
	16: 'sh', 
	32: 'sw'
}

for name, setup, expects, load, code in tests:
	print >>fp, '# Test: %s' % name
	printf("Running test: %s" % name)
	print >>fp, '# Setup'
	gprvals = [0] * 32
	for expr in setup:
		if expr[1][0] == 'gpr':
			gprvals[expr[1][1]] = expr[2]
		elif expr[1][0] == 'mem':
			print >>fp, '\tli $5, %s' % hexify(8, expr[1][2])
			print >>fp, '\tli $6, %s' % hexify(8, expr[2])
			print >>fp, '\t%s $6, 0($5)' % storesizes[expr[1][1]]
	for i in xrange(1, 32):
		print >>fp, '\tli $%i, %s' % (i, hexify(8, gprvals[i]))
	print >>fp, '# Code'
	print >>fp, code
	print >>fp, '# Checks'

asm = fp.getvalue()
print asm
code = assemble(0x80080000, asm)
