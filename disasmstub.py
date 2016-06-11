def hexify(v):
	if v >= 0:
		return '0x%x' % v
	else:
		return '-0x%x' % -v

def regname(r):
	return '$%i' % r

def signext(size, v):
	if v & (1 << (size - 1)):
		return v - (1 << size)
	return v

def zeroext(size, v):
	return v
