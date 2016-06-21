from test import *

name = 'SWL and SWR'
load = 0x80100000

GPR[1] = 0
GPR[2] = 0x76543210
GPR[3] = 0xfedcba98

code = '''
	sw    $2, 0($1)
	swl   $3, 0($1)

	addiu $1, $1, 4

	sw    $2, 0($1)
	swl   $3, 1($1)	

	addiu $1, $1, 4

	sw    $2, 0($1)
	swl   $3, 2($1)	

	addiu $1, $1, 4

	sw    $2, 0($1)
	swl   $3, 3($1)

	addiu $1, $1, 4

	sw    $2, 0($1)
	swr   $3, 0($1)

	addiu $1, $1, 4

	sw    $2, 0($1)
	swr   $3, 1($1)	

	addiu $1, $1, 4

	sw    $2, 0($1)
	swr   $3, 2($1)	

	addiu $1, $1, 4

	sw    $2, 0($1)
	swr   $3, 3($1)
'''

Mem32[0]  == 0x765432fe
Mem32[4]  == 0x7654fedc
Mem32[8]  == 0x76fedcba
Mem32[12] == 0xfedcba98
Mem32[16] == 0xfedcba98
Mem32[20] == 0xdcba9810
Mem32[24] == 0xba983210
Mem32[28] == 0x98543210
