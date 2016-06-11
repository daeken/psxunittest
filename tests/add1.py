from test import *

name = 'ADD 1'
load = 0x80000000

GPR[1] = 10
GPR[2] = -15

code = '''
	add $3, $1, $0
	add $4, $1, $2
	add $5, $2, $1
	add $6, $2, $2
'''

GPR[1] == 10
GPR[2] == -15
GPR[3] == 10
GPR[4] == -5
GPR[5] == -5
GPR[6] == -30
