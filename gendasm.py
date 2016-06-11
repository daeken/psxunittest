import json, re, struct
import os.path
from tblgen import interpret, Dag, TableGenBits

def dag2expr(dag):
	def clean(value):
		if isinstance(value, tuple) and len(value) == 2 and value[0] == 'defref':
			return value[1]
		return value
	def sep((name, value)):
		if name is None:
			return clean(value)
		return name
	if isinstance(dag, Dag):
		return [dag2expr(sep(elem)) for elem in dag.elements]
	else:
		return dag

if not os.path.exists('dinsts.td.cache') or os.path.getmtime('insts.td') > os.path.getmtime('insts.td.cache'):
	print 'Rebuilding instruction cache'
	insts = interpret('insts.td').deriving('BaseInst')
	ops = []
	for name, (bases, data) in insts:
		ops.append((name, bases[1], data['Opcode'][1], data['Function'][1] if 'Function' in data else None, data['Disasm'][1], dag2expr(data['Eval'][1])))
	with file('dinsts.td.cache', 'w') as fp:
		json.dump(ops, fp)
else:
	ops = json.load(file('dinsts.td.cache'))

toplevel = {}

for name, type, op, funct, dasm, dag in ops:
	if funct is None:
		assert op not in toplevel
		toplevel[op] = name, type, dasm, dag
	else:
		if op not in toplevel:
			toplevel[op] = [type, {}]
		toplevel[op][1][funct] = name, type, dasm, dag

def generate(gfunc):
	switch = []
	for op, body in toplevel.items():
		if isinstance(body, list):
			type, body = body
			subswitch = []
			for funct, sub in body.items():
				subswitch.append(('case', funct, gfunc(sub)))
			if type == 'CFType':
				when = ('&', ('>>', 'inst', 21), 0x1F)
			elif type == 'RIType':
				when = ('&', ('>>', 'inst', 16), 0x1F)
			else:
				when = ('&', 'inst', 0x3F)
			switch.append(('case', op, ('switch', when, subswitch)))
		else:
			switch.append(('case', op, gfunc(body)))
	return ('switch', ('>>', 'inst', 26), switch)

def indent(str, single=True):
	if single and '\n' not in str:
		return ' %s ' % str
	else:
		return '\n%s\n' % '\n'.join('\t' + x for x in str.split('\n'))

def output(expr, top=True, emitting=False):
	if isinstance(expr, list):
		return '\n'.join(output(x, top=top, emitting=emitting) for x in expr)
	elif isinstance(expr, int) or isinstance(expr, long):
		return '0x%x' % expr
	elif isinstance(expr, str) or isinstance(expr, unicode):
		if emitting and expr.startswith('$') and not expr.startswith('$_'):
			return '" + %s + "' % expr
		else:
			return expr.replace('$', '')

	op = expr[0]
	if op == 'switch':
		lval = output(expr[1], emitting=emitting)
		first = True
		code = ''
		for elem in expr[2]:
			code += '%s %s == %s:%s' % ('if' if first else 'elif', lval, output(elem[1]), indent(output(elem[2])))
			first = False
		return code
	elif op in ('+', '-', '*', '/', '%', '<<', '>>', '>>', '&', '|', '^', '==', '!=', '<', '<=', '>', '>='):
		return '(%s) %s (%s)' % (output(expr[1], top=False, emitting=emitting), op, output(expr[2], top=False, emitting=emitting))
	elif op == '!':
		return '!(%s)' % output(expr[1], top=False, emitting=emitting)
	elif op == '=':
		return '%s %s %s;' % (output(expr[1], top=False, emitting=emitting), op, output(expr[2], top=False, emitting=emitting))
	elif op == 'if':
		return 'if(%s) {%s} else {%s}' % (output(expr[1], top=False, emitting=emitting), indent(output(expr[2], emitting=emitting), single=False), indent(output(expr[3], emitting=emitting), single=False))
	elif op == 'when':
		return 'if(%s) {%s}' % (output(expr[1], top=False, emitting=emitting), indent(output(expr[2], emitting=emitting)))
	elif op == 'comment':
		return '# %s ' % indent(output(expr[1], emitting=emitting))
	elif op == 'str':
		return `str(expr[1])`
	elif op == 'index':
		return '(%s)[%s]' % (output(expr[1], top=False, emitting=emitting), output(expr[2], top=False, emitting=emitting))
	elif op == 'emit':
		if emitting:
			return output(expr[1], top=False, emitting=True)
		else:
			return 'emit("%s");' % (output(expr[1], top=True, emitting=True).replace('\n', '\\n').replace('"" + ', '').replace(' + ""', ''))
	else:
		return '%s(%s)%s' % (op, ', '.join(output(x, top=False, emitting=emitting) for x in expr[1:]), ';' if top else '')

gops = {
	'add' : lambda a, b: ('+', a, b), 
	'sub' : lambda a, b: ('-', a, b), 
	'and' : lambda a, b: ('>>', ('&', a, b), 0), 
	'or' : lambda a, b: ('>>', ('|', a, b), 0), 
	'nor' : lambda a, b: ('>>', ('~', ('|', a, b)), 0), 
	'xor' : lambda a, b: ('>>', ('^', a, b), 0), 
	'mul' : lambda a, b: ('*', a, b), # XXX: This needs to be a 64-bit mul!
	'div' : lambda a, b: ('>>', ('/', a, b), 0), 
	'mod' : lambda a, b: ('>>', ('%', a, b), 0), 
	'shl' : lambda a, b: ('>>', ('<<', a, b), 0), 
	'shra' : lambda a, b: ('>>', a, b), 
	'shrl' : lambda a, b: ('>>', a, b), 

	'eq' : lambda a, b: ('==', a, b), 
	'ge' : lambda a, b: ('>=', a, b), 
	'gt' : lambda a, b: ('>', a, b), 
	'le' : lambda a, b: ('<=', a, b), 
	'lt' : lambda a, b: ('<', a, b), 
	'neq' : lambda a, b: ('!=', a, b), 
}

def cleansexp(sexp):
	if isinstance(sexp, list):
		return [cleansexp(x) for x in sexp if x != []]
	elif isinstance(sexp, tuple):
		return tuple([cleansexp(x) for x in sexp if x != []])
	else:
		return sexp

def find_deps(dag):
	if isinstance(dag, str) or isinstance(dag, unicode):
		return set([dag])
	elif not isinstance(dag, list):
		return set()

	return reduce(lambda a, b: a|b, map(find_deps, dag[1:])) if len(dag) != 1 else set()

def decoder(code, vars, type, dag):
	def decl(name, val):
		if name in deps:
			vars.append(name)
			code.append(('=', name, val))
	deps = find_deps(dag)
	if type == 'IType' or type == 'RIType':
		decl('$rs', ('&', ('>>', 'inst', 21), 0x1F))
		decl('$rt', ('&', ('>>', 'inst', 16), 0x1F))
		decl('$imm', ('&', 'inst', 0xFFFF))
	elif type == 'JType':
		decl('$imm', ('&', 'inst', 0x3FFFFFF))
	elif type == 'RType':
		decl('$rs', ('&', ('>>', 'inst', 21), 0x1F))
		decl('$rt', ('&', ('>>', 'inst', 16), 0x1F))
		decl('$rd', ('&', ('>>', 'inst', 11), 0x1F))
		decl('$shamt', ('&', ('>>', 'inst', 6), 0x1F))
	elif type == 'SType':
		decl('$code', ('&', ('>>', 'inst', 6), 0x0FFFFF))
	elif type == 'CFType':
		decl('$cop', ('&', ('>>', 'inst', 26), 3))
		decl('$rt', ('&', ('>>', 'inst', 16), 0x1F))
		decl('$rd', ('&', ('>>', 'inst', 11), 0x1F))
		decl('$cofun', ('&', 'inst', 0x01FFFFFF))
	else:
		print 'Unknown instruction type:', type
		assert False

def genDisasm((name, type, dasm, dag)):
	code = [('comment', name)]
	vars = []
	decoder(code, vars, type, dag)

	def subgen(dag):
		if isinstance(dag, str) or isinstance(dag, unicode):
			return dag
		elif isinstance(dag, int) or isinstance(dag, long):
			return dag
		elif not isinstance(dag, list):
			print 'Fail', `dag`
			assert False
		op = dag[0]
		if op in ('let', 'rlet'):
			# Ignore any leading underscore vars
			if dag[1].startswith('$_'):
				return []
			if dag[1] not in vars:
				vars.append(dag[1])
			return [('=', dag[1], subgen(dag[2]))] + subgen(dag[3])
		elif op in ('branch', 'break', 'copfun', 'raise', 'set', 'store', 'syscall'): # Catch toplevel exprs
			return []
		elif op == 'if':
			return list(map(subgen, dag[2:]))
		elif op == 'when':
			return list(map(subgen, dag[2:]))
		elif op in gops:
			return gops[op](subgen(dag[1]), subgen(dag[2]))
		elif op in ('signext', 'zeroext'):
			return (op, dag[1], subgen(dag[2]))
		elif op in ('pc', 'hi', 'lo'):
			return [op]
		elif op == 'pcd':
			return ('+', '$pc', 4) # Return the delay slot position
		elif op == 'gpr':
			return ('gpr', subgen(dag[1]))
		elif op == 'copreg':
			return ('copreg', subgen(dag[1]), subgen(dag[2]))
		elif op == 'copcreg':
			return ('copcreg', subgen(dag[1]), subgen(dag[2]))
		elif op == 'block':
			return list(map(subgen, dag[1:]))
		elif op == 'unsigned':
			return ('>>', subgen(dag[1]), 0)
		else:
			print 'Unknown op:', op
			return []

	code += cleansexp(subgen(dag))

	def format(dasm):
		shortest = (len(dasm), None)
		for var in vars:
			match = re.match(r'^(.*?)' + var.replace('$', '\\$') + '([^a-zA-Z0-9_].*$|$)', dasm)
			if match:
				match = match.groups()
				if len(match[0]) < shortest[0]:
					shortest = len(match[0]), var
		if shortest[1] is None:
			return ('str', dasm)
		
		var = shortest[1]
		match = re.match(r'^(.*?)(%?)' + var.replace('$', '\\$') + '([^a-zA-Z0-9_].*$|$)', dasm).groups()
		if match[1] == '%':
			out = ('regname', var)
		else:
			out = ('hexify', var)
		if match[0]:
			out = ('+', ('str', match[0]), out)
		if match[2]:
			out = ('+', out, format(match[2]))
		return out
	
	code.append(('return', format(dasm)))

	return code

def build():
	print 'Rebuilding from tables'
	with file('disasm.py', 'w') as fp:
		print >>fp, '# Autogenerated from insts.td. DO NOT EDIT'
		print >>fp, file('disasmstub.py', 'r').read()
		print >>fp, 'def disassemble(pc, inst):\n%s\treturn \'Unknown instruction. Op=0b%%06b (Funct=0b Cofunct=0b)\';\n' % indent(output(generate(genDisasm)))

if __name__=='__main__':
	build()
