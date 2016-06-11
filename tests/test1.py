from test import *

name = 'Arithmetic/branching test'
load = 0x80000000

GPR[2] = 0xDEAD
GPR[3] = 0
GPR[5] = 1

code = '''
loop:
	subu $2, $2, $5
	addiu $3, $3, 1
	bgtz $2, loop
	nop
'''

GPR[2] == 0
GPR[3] == 0xDEAD
GPR[5] == 1
