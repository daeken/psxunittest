from test import *

name = 'LH and LB sign extension'
load = 0x80100000

Mem32[0x0] = 0x00008080;

code = '''
	lh   $1, 0($0)
        lhu  $2, 0($0)
        lb   $3, 0($0)
        lbu  $4, 0($0)
        nop
'''

GPR[1] == 0xffff8080
GPR[2] == 0x00008080
GPR[3] == 0xffffff80
GPR[4] == 0x00000080
