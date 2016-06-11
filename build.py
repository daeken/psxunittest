import struct, test
from disasm import disassemble
from generator import generate
from glob import glob
from importlib import import_module
from mips_assembler import MIPSProgram

def build(base, asm):
	mp = MIPSProgram(text_base=base)
	mp.AddLines(asm.split('\n'))
	bytes = mp.Bytes(endian='little')
	code = ''.join(map(chr, bytes))
	return code, [struct.unpack('<I', code[i:i+4])[0] for i in xrange(0, len(code), 4)]

tests = []
for fn in glob('tests/*.py'):
	if fn == 'tests/__init__.py':
		continue

	test.setup = []
	test.asserts = []
	testmod = import_module('tests.' + fn[6:-3])
	testmod.setup = test.setup
	testmod.asserts = test.asserts

	print 'Building test:', testmod.name

	code, insns = build(testmod.load, testmod.code + '\nj 0xEADBEE0')

	for i, insn in enumerate(insns):
		print '%08x    %s' % (testmod.load + i * 4, disassemble(testmod.load + i * 4, insn))

	print 'Setup:'
	for expr in test.setup:
		print expr

	print 'Asserts:'
	for expr in test.asserts:
		print expr

	tests.append((testmod.name, testmod.setup, testmod.asserts, testmod.load, insns))

generate(tests)
