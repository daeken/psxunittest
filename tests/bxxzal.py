from test import *

name = 'BLTZAL and BGEZAL'
load = 0x80100000

# Those instructions link the next PC in RA even if the condition is
# not true (i.e. the branch doesn't take place).

code = '''
li     $5, -1

	move   $1, $0
	move   $31, $0
	bltzal $0, .nottaken0
	nop

	li     $1, 1

.nottaken0:
	sltu   $2, $0, $31

	li     $3, -1
	move   $31, $0
	bgezal $3, .nottaken1
	nop

	li     $3, 1

.nottaken1:
	sltu   $4, $0, $31

	li     $5, -1
	move   $31, $0
	bltzal $5, .taken0
	nop

	li     $5, 1

.taken0:

	sltu   $6, $0, $31

	move   $7, $0
	move   $31, $0
	bgezal $0, .taken1
	nop

	li     $7, 1

.taken1:
	sltu   $8, $0, $31
'''

GPR[1] == 1
GPR[2] == 1
GPR[3] == 1
GPR[4] == 1
GPR[5] == -1
GPR[6] == 1
GPR[7] == 0
GPR[8] == 1
