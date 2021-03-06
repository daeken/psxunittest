from test import *

name = 'Branch in branch delay'
load = 0x80100000

code = '''
	beq $0, $0, part1
	beq $0, $0, part2
	addi $3, $0, 1

part1:
	addi $1, $0, 1
	beq $0, $0, end
	nop

part2:
	addi $2, $0, 1

end:
	nop
'''

GPR[1] == 1
GPR[2] == 0
GPR[3] == 0
