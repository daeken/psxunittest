from test import *

name = 'LWR and LWR load delay'
load = 0x80100000

Mem32[0x0] = 0x76543210
Mem32[0x4] = 0xfedcba98

# LWR/LWL are a bit peculiar because they ignore the load delay, they
# "catch" the loaded value before it reaches the register. That means
# that it can use a value that's never actually stored in the register
# because of a load cancelling.

code = '''
	addiu $1, $0, -1
	lwr   $1, 2($0)
	lwl   $1, 5($0)
	move  $2, $1

	addiu $3, $0, -1
	lwr   $3, 2($0)
	nop
	lwl   $3, 5($0)
	move  $4, $3

	addiu $5, $0, -1
	lwl   $5, 5($0)
	nop
	lwr   $5, 2($0)
	move  $6, $5

	addiu $7, $0, -1
	lw    $7, 4($0)
	lwl   $7, 2($0)
	move  $8, $7

	addiu $9, $0, -1
	lw    $9, 4($0)
	nop
	lwl   $9, 2($0)
	move  $10, $9

	addiu $11, $0, -1
	lw    $11, 4($0)
	lwr   $11, 2($0)
	move  $12, $11

	addiu $13, $0, -1
	lw    $13, 4($0)
	nop
	lwr   $13, 2($0)
	move  $14, $13

	lui   $15, 0x67e
	ori   $15, $15, 0x67e
	mtc2  $15, $25

	addiu $15, $0, -1
	mfc2  $15, $25
	lwl   $15, 1($0)
	move  $16, $15

	addiu $17, $0, -1
	mfc2  $17, $25
	nop
	lwr   $17, 1($0)
	move  $18, $17
'''

GPR[1]  == 0xba987654
GPR[2]  == 0xffffffff
GPR[3]  == 0xba987654
GPR[4]  == 0xffff7654
GPR[5]  == 0xba987654
GPR[6]  == 0xba98ffff
GPR[7]  == 0x54321098
GPR[8]  == 0xffffffff
GPR[9]  == 0x54321098
GPR[10] == 0xfedcba98
GPR[11] == 0xfedc7654
GPR[12] == 0xffffffff
GPR[13] == 0xfedc7654
GPR[14] == 0xfedcba98
GPR[15] == 0x3210067e
GPR[16] == 0xffffffff
GPR[17] == 0x06765432
GPR[18] == 0x067e067e
