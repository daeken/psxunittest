from test import *

# When you're loading something in a register that's already the
# target of the load delay the pending load gets canceled

name = 'Multiple load cancelling'
load = 0x80100000

Mem32[0x0] = 0x07001a7e

GPR[1] = 0x600dc0de

code = '''
	mfc0  $1, $12
	lw    $1, 0($0)
	mfc0  $1, $15
	lw    $1, 0($0)
	lw    $1, 0($0)
	addu  $2, $1, 0
'''

GPR[1] == 0x07001a7e
GPR[2] == 0x600dc0de
