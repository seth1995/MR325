import math
import numpy as np
G = np.ones([2, 2], dtype=complex)
G[0, 0] += 1j
G[0, 1] += 2j

test1 = G[0, :].real
test2 = G[0, :].imag
test_n = len(G[0, :])
temp_list = []
print G
test3 = np.divide(test2, test1)
print np.arctan2(test2, test1)


#text = "JGood is a handsome boy, he is cool, clever, and so on..."
# print re.sub(r'\s+', '-', text)
