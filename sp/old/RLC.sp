#test4.sp RLC circuit
VS 1 0 5 
R1 1 2 5
L1 1 2 0.1
C1 2 0 200m
.TRAN BE 0 8 40m
.PRINT tran V(3)
.end