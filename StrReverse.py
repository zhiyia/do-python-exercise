#颠倒整数
#只能处理32bit范围的整数,颠倒之后超过这个范围,返回0

#只有算法思路
if -10<x<10:
	return x
	b =str(abs(n))
	if len(b)>10:
		return 0
	reverse = int(b[::-1])
	if x<0:
		reverse = -reverse
	if -2147483648<reverse<2147483648:
		return reverse
	else:
		return 0