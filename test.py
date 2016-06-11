# Defaults for tests
name = 'Untitled test'
load = 0x80000000
# End defaults

setup = None
expects = None

class _GPR(object):
	def __init__(self, reg):
		self.reg = reg

	def __eq__(self, rval):
		expects.append(('expectEqual', ('gpr', self.reg), rval))

class GPRs(object):
	def __getitem__(self, reg):
		return _GPR(reg)

	def __setitem__(self, reg, value):
		setup.append(('set', ('gpr', reg), value))

GPR = GPRs()

class MemAccess(object):
	def __init__(self, size, addr):
		self.size = size
		self.addr = addr

	def __eq__(self, rval):
		expects.append(('expectEqual', ('mem', self.size, self.addr), rval))

class Memory(object):
	def __init__(self, size):
		self.size = size

	def __getitem__(self, addr):
		return MemAccess(self.size, addr)

	def __setitem__(self, addr, value):
		setup.append(('set', ('mem', self.size, addr), value))
Mem8  = Memory(8)
Mem16 = Memory(16)
Mem32 = Memory(32)
