from test import *

name = 'LWR and LWR'
load = 0x80100000

Mem32[0x0] = 0x76543210
Mem32[0x4] = 0xfedcba98

code = '''
	lwr $1, 0($0)
	lwl $1, 3($0)

	lwr $2, 1($0)
	lwl $2, 4($0)

	lwr $3, 2($0)
	lwl $3, 5($0)

	lwr $4, 3($0)
	lwl $4, 6($0)

	lwr $5, 4($0)
	lwl $5, 7($0)

	lwl $6, 3($0)
	lwr $6, 0($0)

	lwl $7, 4($0)
	lwr $7, 1($0)

	lwl $8, 5($0)
	lwr $8, 2($0)

	lwl $9, 6($0)
	lwr $9, 3($0)

	lwl $10, 7($0)
	lwr $10, 4($0)

	addiu $11, $0, -1
	lwl   $11, 0($0)

	addiu $12, $0, -1
	lwr   $12, 0($0)

	addiu $13, $0, -1
	lwl   $13, 1($0)

	addiu $14, $0, -1
	lwr   $14, 1($0)

	addiu $15, $0, -1
	lwl   $15, 2($0)

	addiu $16, $0, -1
	lwr   $16, 2($0)

	addiu $17, $0, -1
	lwl   $17, 3($0)

	addiu $18, $0, -1
	lwr   $18, 3($0)
'''

GPR[1]  == 0x76543210
GPR[2]  == 0x98765432
GPR[3]  == 0xba987654
GPR[4]  == 0xdcba9876
GPR[5]  == 0xfedcba98
GPR[6]  == 0x76543210
GPR[7]  == 0x98765432
GPR[8]  == 0xba987654
GPR[9]  == 0xdcba9876
GPR[10] == 0xfedcba98
GPR[11] == 0x10ffffff
GPR[12] == 0x76543210
GPR[13] == 0x3210ffff
GPR[14] == 0xff765432
GPR[15] == 0x543210ff
GPR[16] == 0xffff7654
GPR[17] == 0x76543210
GPR[18] == 0xffffff76
