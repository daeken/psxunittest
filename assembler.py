import re
def regex(pattern, flags=0):
	def sub(text):
		match = pattern.match(text)
		if match == None:
			return False
		return match.groups()
	pattern = re.compile(pattern, flags)
	return sub

labels = {}
mlabel = regex(r'^\s*([a-zA-Z0-9.]+):\s*$')
mint = regex(r'^(-?(0x)?[0-9a-fA-F]+)$')
mref = regex(r'^(-?[x0-9a-fA-F]+)\(\$([0-9]+)\)$')

def parseOperand(op):
	if op in labels: return [labels[op]]
	elif op.startswith('$'): return [int(op[1:])]
	elif mint(op): return [eval(op)]
	elif mref(op): return list(map(eval, mref(op)))

def hexify(size, val):
	if val >= 0: return ('0x%%0%ix' % size) % val
	else: return ('-0x%%0%ix' % size) % -val

def processInsn(mnem, ops):
	if mnem == 'nop':
		return [('sll', ('0', '0', '0'))]
	elif mnem == 'rfe':
		return [('cop0', ('16', ))]
	elif mnem == 'li':
		ret, imm = [], parseOperand(ops[1])[0]
		if (imm & 0xFFFF0000) != 0: ret.append(('lui', (ops[0], hexify(4, (imm >> 16)))))
		if (imm & 0xFFFF) != 0: ret.append(('addi', (ops[0], ops[0] if ((imm & 0xFFFF0000) != 0) else '$0', hexify(4, (imm & 0xFFFF)))))
		return ret
	elif mnem == 'move':
		return [('addu', (ops[0], ops[1], '$0'))]
	return [(mnem, ops)]

def assemble(base, code):
	insns = []
	for line in code.split('\n'):
		line = line.split('#', 1)[0]
		match = mlabel(line)
		if match:
			label = match[0]
			labels[label] = base + len(insns) * 4
		elif line.strip():
			line = line.strip().split(' ', 1)
			if len(line) == 1:
				mnem, rest = line[0], ''
			else:
				mnem, rest = line
			ops = [x.strip() for x in rest.split(',') if x.strip()]
			insns += processInsn(mnem.lower(), ops)

	out = []
	for i, (mnem, ops) in enumerate(insns):
		ops = reduce(lambda a, b: a+b, map(parseOperand, ops)) if ops else []
		out.append(buildInsn(base + i * 4, mnem, ops))
	return out

def unsigned(val, size):
	return val if val >= 0 else (1 << size) + val

def buildInsn(addr, mnem, ops):
	def put(name, pos, size=None, val=None):
		val = val(ops[i]) if val is not None else ops[i]
		if params[i] == name:
			inst[0] |= (unsigned(val, size) if size else val) << pos
	if mnem not in indefs:
		print 'Unknown instruction:', mnem, ops
		return 0

	inst = [0]

	type, odef, params = indefs[mnem]
	if type == CType:
		inst[0] |= odef[0] << 26
		inst[0] |= odef[1] << 21
		for i in range(len(params)):
			put(rt, 16, 5)
			put(rd, 11, 5)
			put(cofun, 0, 24)
	elif type == IType:
		if isinstance(odef, tuple):
			inst[0] |= odef[0] << 26
			inst[0] |= odef[1] << 16
		else:
			inst[0] |= odef << 26
		for i in range(len(params)):
			put(rs, 21, 5)
			put(rt, 16, 5)
			put(imm, 0, 16); put(offset, 0, 16)
			put(target, 0, 16, lambda val: (val - (addr + 4)) >> 2)
	elif type == JType:
		inst[0] |= odef << 26
		for i in range(len(params)):
			put(target, 0, val=lambda val: (val & 0x0FFFFFFF) >> 2)
	elif type == PType: # Special case for COPz
		inst[0] |= odef << 26
		inst[0] |= 1 << 25
		for i in range(len(params)):
			put(cofun, 0)
	elif type == RType:
		inst[0] |= odef
		for i in range(len(params)):
			put(rs, 21, 5)
			put(rt, 16, 5)
			put(rd, 11, 5)
			put(shamt, 6, 5)
	elif type == SType:
		inst[0] |= odef
		for i in range(len(params)):
			put(code, 6, 20)
	return inst[0]

CType, IType, JType, PType, RType, RIType, SType = 'ctype', 'itype', 'jtype', 'ptype', 'rtype', 'ritype', 'stype'
code, cofun, imm, offset, rd, rs, rt, shamt, target = 'code', 'cofun', 'imm', 'offset', 'rd', 'rs', 'rt', 'shamt', 'target'

indefs = dict(
	add    =(RType, 0b100000, (rd, rs, rt)), 
	addi   =(IType, 0b001000, (rt, rs, imm)), 
	addiu  =(IType, 0b001001, (rt, rs, imm)), 
	addu   =(RType, 0b100001, (rd, rs, rt)), 
	and_   =(RType, 0b100100, (rd, rs, rt)), 
	andi   =(IType, 0b001100, (rt, rs, imm)), 
	beq    =(IType, 0b000100, (rs, rt, target)), 
	bgez   =(IType, (0b000001, 0b00001), (rs, target)), 
	bgezal =(IType, (0b000001, 0b10001), (rs, target)), 
	bgtz   =(IType, (0b000111, 0b00000), (rs, target)), 
	blez   =(IType, (0b000110, 0b00000), (rs, target)), 
	bltz   =(IType, (0b000001, 0b00000), (rs, target)), 
	bltzal =(IType, (0b000001, 0b10000), (rs, target)), 
	bne    =(IType, 0b000101, (rs, rt, target)), 
	break_ =(SType, 0b001101, (code, )), 
	cfc0   =(CType, (0b010000, 0b00010), (rt, rd)), 
	cfc1   =(CType, (0b010001, 0b00010), (rt, rd)), 
	cfc2   =(CType, (0b010010, 0b00010), (rt, rd)), 
	cfc3   =(CType, (0b010011, 0b00010), (rt, rd)), 
	cop0   =(PType, 0b010000, (cofun, )), 
	cop1   =(PType, 0b010001, (cofun, )), 
	cop2   =(PType, 0b010010, (cofun, )), 
	cop3   =(PType, 0b010011, (cofun, )), 
	ctc0   =(CType, (0b010000, 0b00110), (rt, rd)), 
	ctc1   =(CType, (0b010001, 0b00110), (rt, rd)), 
	ctc2   =(CType, (0b010010, 0b00110), (rt, rd)), 
	ctc3   =(CType, (0b010011, 0b00110), (rt, rd)), 
	div    =(RType, 0b011010, (rs, rt)), 
	divu   =(RType, 0b011011, (rs, rt)), 
	j      =(JType, 0b000010, (target, )), 
	jal    =(JType, 0b000011, (target, )), 
	jalr   =(RType, 0b001001, (rd, rs)), 
	jr     =(RType, 0b001000, (rs, )), 
	lb     =(IType, 0b100000, (rt, offset, rs)), 
	lbu    =(IType, 0b100100, (rt, offset, rs)), 
	lh     =(IType, 0b100001, (rt, offset, rs)), 
	lhu    =(IType, 0b100101, (rt, offset, rs)), 
	lui    =(IType, 0b001111, (rt, imm)), 
	lw     =(IType, 0b100011, (rt, offset, rs)), 
	lwl    =(IType, 0b100010, (rt, offset, rs)), 
	lwr    =(IType, 0b100110, (rt, offset, rs)), 
	lwc0   =(IType, 0b110000, (rt, offset, rs)), 
	lwc1   =(IType, 0b110001, (rt, offset, rs)), 
	lwc2   =(IType, 0b110010, (rt, offset, rs)), 
	lwc3   =(IType, 0b110011, (rt, offset, rs)), 
	mfc0   =(CType, (0b010000, 0b00000), (rt, rd)), 
	mfc1   =(CType, (0b010001, 0b00000), (rt, rd)), 
	mfc2   =(CType, (0b010010, 0b00000), (rt, rd)), 
	mfc3   =(CType, (0b010011, 0b00000), (rt, rd)), 
	mfhi   =(RType, 0b010000, (rd, )), 
	mflo   =(RType, 0b010010, (rd, )), 
	mtc0   =(CType, (0b010000, 0b00100), (rt, rd)), 
	mtc1   =(CType, (0b010001, 0b00100), (rt, rd)), 
	mtc2   =(CType, (0b010010, 0b00100), (rt, rd)), 
	mtc3   =(CType, (0b010011, 0b00100), (rt, rd)), 
	mthi   =(RType, 0b010001, (rd, )), 
	mtlo   =(RType, 0b010011, (rd, )), 
	mult   =(RType, 0b011000, (rs, rt)), 
	multu  =(RType, 0b011001, (rs, rt)), 
	nor    =(RType, 0b100111, (rd, rs, rt)), 
	or_    =(RType, 0b100101, (rd, rs, rt)), 
	ori    =(IType, 0b001101, (rt, rs, imm)), 
	sb     =(IType, 0b101000, (rt, offset, rs)), 
	sh     =(IType, 0b101001, (rt, offset, rs)), 
	sll    =(RType, 0b000000, (rd, rt, shamt)), 
	sllv   =(RType, 0b000100, (rd, rt, rs)), 
	slt    =(RType, 0b101010, (rd, rs, rt)), 
	slti   =(IType, 0b001010, (rt, rs, imm)), 
	sltiu  =(IType, 0b001011, (rt, rs, imm)), 
	sltu   =(RType, 0b101011, (rd, rs, rt)), 
	sra    =(RType, 0b000011, (rd, rt, shamt)), 
	srav   =(RType, 0b000111, (rd, rt, rs)), 
	srl    =(RType, 0b000010, (rd, rt, shamt)), 
	srlv   =(RType, 0b000110, (rd, rt, rs)), 
	sub    =(RType, 0b100010, (rd, rs, rt)), 
	subu   =(RType, 0b100011, (rd, rs, rt)), 
	sw     =(IType, 0b101011, (rt, offset, rs)), 
	swl    =(IType, 0b101010, (rt, offset, rs)), 
	swr    =(IType, 0b101110, (rt, offset, rs)), 
	syscall=(SType, 0b001100, (code, )), 
	xor    =(RType, 0b100110, (rd, rs, rt)), 
	xori   =(IType, 0b001110, (rt, rs, imm)), 
)
for k, v in indefs.items():
	indefs[k.replace('_', '')] = v
