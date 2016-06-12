from test import *

name = 'Unaligned loads'
load = 0x80100000

Mem32[0xBEE0] = 0xDEADBEEF

GPR[30] = 0xBEE1

code = '''
	lb $1, 0($30)
	lbu $2, 0($30)
	#lh $3, 0($30)
	#lw $4, 0($30)
'''

GPR[1] == -66
GPR[2] == 0xBE
GPR[3] == 0
GPR[4] == 0
