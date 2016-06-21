import re;

from build import *

class Generator(object):
	def generateTest(self, fp, (name, setup, expects, load, blob)):
		# Generate the function name
		sym = re.sub(r'[^a-zA-Z_0-9]', '_', name).lower()
		print >>fp, '#[test]'
		print >>fp, 'fn test_%s() {' % sym
		print >>fp, '    let bios = Bios::dummy();'
		print >>fp, '    let gpu = Gpu::new(VideoClock::Ntsc);'
		print >>fp, '    let inter = Interconnect::new(bios, gpu, None);'
		print >>fp, '    let mut cpu = Cpu::new(inter);'
		print >>fp, '    let mut shared = SharedState::new();'
		print >>fp, '    let mut debugger = DummyDebugger;'
		print >>fp, '    let mut renderer = DummyRenderer;'
		print >>fp, ''
		print >>fp, '    for r in 0..31 {'
		print >>fp, '        cpu.set_reg(RegisterIndex(r), 0);'
		print >>fp, '    }'
		print >>fp, ''

		for expr in setup:
			print >>fp, toCode(expr)

		print >>fp, ''

		load_address = rust_u32(load)

		print >>fp, '    write_blob(&mut cpu, %s,' % load_address
		print >>fp, '               &[%s]);' % ',\n                 '.join('0x%08x' % x for x in blob)
		print >>fp, ''

		print >>fp, '    cpu.set_pc(%s);' % load_address
		print >>fp, ''

		print >>fp, '    let mut timeout = true;'

		print >>fp, '    for _ in 0..TIMEOUT {'
		print >>fp, '        if (cpu.pc & 0x0fffffff) == 0xeadbee0 {'
		print >>fp, '            timeout = false;'
		print >>fp, '            break;'
		print >>fp, '        }'
		print >>fp, '        cpu.run_next_instruction(&mut debugger, &mut shared, &mut renderer);'
		print >>fp, '    }'
		print >>fp, '    assert!(timeout == false);'
		print >>fp, ''

		for expr in expects:
			print >>fp, '    %s;' % toCode(expr)

		print >>fp, '}'
		print >>fp, ''

	def generateEnd(self, fp):
		pass

	def writeGPR(self, gpr, value):
		return '    cpu.set_reg(RegisterIndex(%s), %s);' % (gpr, rust_u32(value))

	def readGPR(self, gpr):
		return 'cpu.regs[%s]' % gpr

	def writeMemory(self, size, ptr, value):
		access_width = "";

		if size == 32:
			access_width = "Word"
		elif size == 16:
			access_width = "HalfWord"
		elif size == 8:
			access_width = "Byte"

		return '    write::<memory::%s>(&mut cpu, %s, %s);' % (access_width, rust_u32(ptr), rust_u32(value))

	def readMemory(self, size, ptr):
		access_width = "";

		if size == 32:
			access_width = "Word"
		elif size == 16:
			access_width = "HalfWord"
		elif size == 8:
			access_width = "Byte"

		return 'read::<memory::%s>(&mut cpu, %s)' % (access_width, rust_u32(ptr))


	def testExpectEqual(self, state, expect):
		return 'assert!(%s == %s)' % (state, rust_u32(expect))

def rust_u32(val):
	val = int(val)

	if val == 0:
		return "0"
	if val < 0:
		return "%di32 as u32" % val
	return "0x%x" % int(val)

run('rustationtemplate.rs', 'test.rs', Generator())
