from test import *

name = 'Load delay for COP'
load = 0x80100000

GPR[2] = 0x80110000
Mem32[0x80110000] = 0xDEADBEEF

code = '''
	lw $3, 0($2)
	nop
	mfc2 $3, $25
	beq $3, $0, .zero
	nop
	addi $1, $0, 1
	j .end
	nop

.zero:
	addi $1, $0, 2
	j .end

.end:
'''

GPR[3] == 0
GPR[1] == 1
