#a circuit has diode  OFF A F O-
V1 0 1 0 sin 0 1 10M 0
r2 1 2 0.001
d1 2 0 DNOM
d2 1 0 DNOM
c1 2 0 5p

.TRAN  TR 0 1u 1n
.PRINT tran V(2) V(1)
.end