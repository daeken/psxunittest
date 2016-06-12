from test import *

name = 'BEQ'
load = 0x80100000

GPR[1] = 1
GPR[2] = 2
GPR[3] = -1
GPR[4] = 0xFFFFFFFF

code = '''
	beq $1, $2, nt
	nop
	addi $10, $0, 1
	beq $3, $4, end
	nop
	addi $11, $0, 1

nt:
	addi $10, $0, 2
	nop

end:
	nop
'''

GPR[10] == 1
GPR[11] == 0
